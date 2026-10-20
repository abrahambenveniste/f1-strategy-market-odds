"""Create a read-only inventory of Polymarket F1 events and their embedded markets.

This is a coverage-audit tool, not a trading bot. It calls Gamma's public metadata API
only; it does not authenticate, submit orders, or infer executable prices.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_BASE = "https://gamma-api.polymarket.com"
USER_AGENT = (
    "f1-strategy-market-odds/0.1 "
    "(https://github.com/abrahambenveniste/f1-strategy-market-odds)"
)
PAGE_SIZE = 100
F1_TAG_SLUGS = {"f1", "formula-1", "formula1", "formula-one"}
F1_LABEL = re.compile(r"\bformula\s*1\b|\bf1\b", re.IGNORECASE)
CHAMPIONSHIP = re.compile(r"champion|championship|world title", re.IGNORECASE)
WINNER = re.compile(r"\bwin(?:s|ner)?\b", re.IGNORECASE)
GRAND_PRIX = re.compile(r"grand prix|\bgp\b", re.IGNORECASE)


def request_json(path: str, params: dict[str, Any] | None = None) -> Any:
    query = urlencode(params or {}, doseq=True)
    url = f"{API_BASE}{path}" + (f"?{query}" if query else "")
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )

    for attempt in range(4):
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            retryable = exc.code == 429 or 500 <= exc.code < 600
            if not retryable or attempt == 3:
                raise RuntimeError(f"Gamma request failed ({exc.code}): {url}") from exc
            retry_after = exc.headers.get("Retry-After")
            delay = float(retry_after) if retry_after and retry_after.isdigit() else 2**attempt
            time.sleep(min(delay, 30))
        except URLError as exc:
            if attempt == 3:
                raise RuntimeError(f"Gamma request failed: {url}: {exc.reason}") from exc
            time.sleep(2**attempt)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Gamma returned invalid JSON: {url}") from exc

    raise RuntimeError(f"Gamma request failed after retries: {url}")


def as_records(payload: Any, *candidate_keys: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in candidate_keys:
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        for key in ("data", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def parse_json_field(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def is_formula_one_tag(tag: dict[str, Any]) -> bool:
    slug = str(tag.get("slug", "")).strip().lower()
    label = str(tag.get("label", tag.get("name", ""))).strip()
    return slug in F1_TAG_SLUGS or bool(F1_LABEL.search(label))


def fetch_tag_events(tag: dict[str, Any]) -> list[dict[str, Any]]:
    tag_id = tag.get("id")
    if tag_id is None:
        return []
    events: list[dict[str, Any]] = []
    offset = 0
    while True:
        page = as_records(
            request_json(
                "/events",
                {"tag_id": tag_id, "limit": PAGE_SIZE, "offset": offset},
            ),
            "events",
        )
        events.extend(page)
        if len(page) < PAGE_SIZE:
            return events
        offset += PAGE_SIZE
        time.sleep(0.15)


def classify_market(event: dict[str, Any], market: dict[str, Any]) -> str:
    event_text = " ".join(
        str(event.get(key, "")) for key in ("title", "slug", "description")
    )
    market_text = " ".join(
        str(market.get(key, "")) for key in ("question", "title", "slug")
    )
    if CHAMPIONSHIP.search(market_text):
        return "championship"
    if GRAND_PRIX.search(event_text) and WINNER.search(market_text):
        return "race_winner_candidate"
    if "winner" in market_text.lower() and ("f1" in event_text.lower()):
        return "winner_candidate_review"
    return "other"


def summarize_market(event: dict[str, Any], market: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": event.get("id"),
        "event_title": event.get("title"),
        "event_slug": event.get("slug"),
        "event_start_date": event.get("startDate"),
        "event_end_date": event.get("endDate"),
        "event_active": event.get("active"),
        "event_closed": event.get("closed"),
        "market_id": market.get("id"),
        "market_question": market.get("question", market.get("title")),
        "market_slug": market.get("slug"),
        "condition_id": market.get("conditionId", market.get("condition_id")),
        "outcomes": parse_json_field(market.get("outcomes")),
        "outcome_prices": parse_json_field(
            market.get("outcomePrices", market.get("outcome_prices"))
        ),
        "clob_token_ids": parse_json_field(
            market.get("clobTokenIds", market.get("clob_token_ids"))
        ),
        "market_start_date": market.get("startDate", market.get("start_date")),
        "market_end_date": market.get("endDate", market.get("end_date")),
        "active": market.get("active"),
        "closed": market.get("closed"),
        "archived": market.get("archived"),
        "accepting_orders": market.get(
            "acceptingOrders", market.get("accepting_orders")
        ),
        "enable_order_book": market.get(
            "enableOrderBook", market.get("enable_order_book")
        ),
        "volume": market.get("volume"),
        "liquidity": market.get("liquidity"),
        "classification_hint": classify_market(event, market),
        "human_rules_review_required": True,
    }


def build_inventory() -> dict[str, Any]:
    raw_tags = request_json("/tags")
    tags = as_records(raw_tags, "tags")
    matched_tags = [tag for tag in tags if is_formula_one_tag(tag)]
    if not matched_tags:
        examples = [
            {"id": tag.get("id"), "slug": tag.get("slug"), "label": tag.get("label")}
            for tag in tags[:20]
        ]
        raise RuntimeError(
            "No Formula 1 tag found in Gamma /tags. Inspect returned tag schema "
            f"and update F1_TAG_SLUGS / F1_LABEL. First tags: {examples}"
        )

    events_by_id: dict[str, dict[str, Any]] = {}
    for tag in matched_tags:
        for event in fetch_tag_events(tag):
            key = str(event.get("id", event.get("slug", "")))
            if key:
                events_by_id[key] = event

    event_records = []
    market_records = []
    for event in sorted(
        events_by_id.values(),
        key=lambda item: (str(item.get("startDate", "")), str(item.get("slug", ""))),
    ):
        embedded = event.get("markets")
        markets = as_records(embedded, "markets") if embedded is not None else []
        event_records.append(
            {
                "event_id": event.get("id"),
                "title": event.get("title"),
                "slug": event.get("slug"),
                "description": event.get("description"),
                "start_date": event.get("startDate"),
                "end_date": event.get("endDate"),
                "active": event.get("active"),
                "closed": event.get("closed"),
                "market_count_embedded": len(markets),
                "market_list_embedded": embedded is not None,
                "tag_ids": [tag.get("id") for tag in matched_tags],
            }
        )
        market_records.extend(summarize_market(event, market) for market in markets)

    return {
        "audit": {
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "api_base": API_BASE,
            "scope": "Gamma public event and market metadata; no trading endpoints",
            "matched_tags": [
                {
                    "id": tag.get("id"),
                    "slug": tag.get("slug"),
                    "label": tag.get("label", tag.get("name")),
                }
                for tag in matched_tags
            ],
            "event_count": len(event_records),
            "embedded_market_count": len(market_records),
            "events_without_embedded_markets": sum(
                not event["market_list_embedded"] for event in event_records
            ),
            "limitations": [
                "This is a metadata coverage inventory, not a complete trade or quote history.",
                "Classification hints are heuristic; manually verify full market rules.",
                "No market is considered executable from metadata or chart prices alone.",
            ],
        },
        "events": event_records,
        "markets": market_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("data/metadata/polymarket_f1_market_audit.json"),
        help="Output path; generated market metadata should not be committed by default.",
    )
    args = parser.parse_args()

    try:
        inventory = build_inventory()
    except (RuntimeError, OSError) as exc:
        print(f"Market audit failed: {exc}", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    summary = inventory["audit"]
    print(
        f"Wrote {summary['event_count']} events and "
        f"{summary['embedded_market_count']} embedded markets to {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
