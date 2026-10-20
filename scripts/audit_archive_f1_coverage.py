#!/usr/bin/env python3
"""Audit recent Polymarket-v1 trade-print coverage for F1 Grand Prix winner markets.

This is a market-coverage screen, not an executable-price backtest. It scans the
archive's daily_aligned_multi partitions from a configurable number of days
before qualifying through each scheduled race day. Candidate market slugs need
manual review before they enter the research dataset.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, datetime, time as dt_time, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    import duckdb
except ImportError as exc:  # pragma: no cover - exercised by the CLI
    raise SystemExit("Install the project requirements first: python -m pip install -r requirements.txt") from exc


DATASET_ID = "TimeSeventeen/Polymarket-v1"
DATASET_TREE = f"https://huggingface.co/api/datasets/{DATASET_ID}/tree"
DATASET_INFO = f"https://huggingface.co/api/datasets/{DATASET_ID}"
DATASET_RESOLVE = f"https://huggingface.co/datasets/{DATASET_ID}/resolve"
JOLPICA = "https://api.jolpi.ca/ergast/f1"
OPENF1 = "https://api.openf1.org/v1/sessions"
USER_AGENT = "f1-strategy-market-odds/0.1 (public research; contact via GitHub)"
DATE_IN_PARTITION = re.compile(r"(?P<year>\d{4})_(?P<month>\d{2})_(?P<day>\d{2})\.parquet$")
WINNER_LANGUAGE = r"(^|-)(win|wins|winner|victory)(-|$)"
EXCLUDED_MARKET_LANGUAGE = r"(^|-)(f2|f3|academy|champion|championship|constructor|constructors|qualifying|podium|fastest-lap|sprint|team)(-|$)"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def fetch_json(url: str, retries: int = 3) -> tuple[Any, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response), response.headers
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(1 + attempt)
    raise RuntimeError(f"Request failed after {retries} attempts: {url}: {last_error}")


def next_link(link_header: str) -> str | None:
    match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
    return match.group(1) if match else None


def load_archive_index(revision: str | None) -> tuple[str, dict[date, dict[str, Any]]]:
    info, _ = fetch_json(DATASET_INFO)
    pinned_revision = revision or info["sha"]
    page_url = f"{DATASET_TREE}/{pinned_revision}/daily_aligned_multi?recursive=true&expand=true"
    partitions: dict[date, dict[str, Any]] = {}
    while page_url:
        entries, headers = fetch_json(page_url)
        for entry in entries:
            if entry.get("type") != "file" or not entry.get("path", "").endswith(".parquet"):
                continue
            match = DATE_IN_PARTITION.search(entry["path"])
            if not match:
                continue
            partition_date = date(int(match["year"]), int(match["month"]), int(match["day"]))
            partitions[partition_date] = entry
        page_url = next_link(headers.get("Link", ""))
    if not partitions:
        raise RuntimeError("No dated Parquet partitions found in daily_aligned_multi")
    return pinned_revision, partitions


def parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", normalized.lower())).strip("-")


def event_aliases(race: dict[str, Any]) -> list[str]:
    circuit = race.get("Circuit", {})
    location = circuit.get("Location", {})
    name = re.sub(r"\s+Grand Prix$", "", race.get("raceName", ""), flags=re.IGNORECASE)
    circuit_name = re.sub(r"\s+Circuit$", "", circuit.get("circuitName", ""), flags=re.IGNORECASE)
    candidates = [name, location.get("locality", ""), circuit_name]
    aliases = []
    for candidate in candidates:
        alias = slugify(candidate)
        if len(alias) >= 4 and alias not in aliases:
            aliases.append(alias)
    return aliases


def load_races(year: int) -> list[dict[str, Any]]:
    url = f"{JOLPICA}/{year}/races.json?limit=100"
    payload, _ = fetch_json(url)
    raw_races = payload["MRData"]["RaceTable"]["Races"]
    races = []
    for raw in raw_races:
        race_start = parse_utc(f"{raw['date']}T{raw.get('time', '15:00:00Z')}")
        if race_start is None:
            continue
        circuit = raw.get("Circuit", {})
        location = circuit.get("Location", {})
        races.append(
            {
                "event_id": f"{year}-{int(raw['round']):02d}",
                "year": year,
                "round": int(raw["round"]),
                "race_name": raw["raceName"],
                "race_date_utc": raw["date"],
                "race_start_utc": race_start,
                "race_cutoff_utc": race_start - timedelta(minutes=5),
                "circuit_name": circuit.get("circuitName"),
                "locality": location.get("locality"),
                "country": location.get("country"),
                "aliases": event_aliases(raw),
            }
        )
    return races


def attach_qualifying_cutoffs(races: list[dict[str, Any]], source_errors: list[str]) -> None:
    years = sorted({race["year"] for race in races})
    all_sessions: dict[int, list[dict[str, Any]]] = {}
    for year in years:
        try:
            sessions, _ = fetch_json(f"{OPENF1}?year={year}&session_name=Qualifying")
            all_sessions[year] = [s for s in sessions if not s.get("is_cancelled", False)]
        except Exception as exc:  # qualifying cutoffs are useful but not required for race coverage
            source_errors.append(f"OpenF1 {year} qualifying sessions unavailable: {exc}")
            all_sessions[year] = []

    for race in races:
        location = slugify(race.get("locality") or "")
        country = slugify(race.get("country") or "")
        candidates = []
        for session in all_sessions.get(race["year"], []):
            session_start = parse_utc(session.get("date_start"))
            if not session_start or session_start > race["race_start_utc"]:
                continue
            day_gap = (race["race_start_utc"].date() - session_start.date()).days
            if day_gap < 0 or day_gap > 3:
                continue
            session_location = slugify(session.get("location") or "")
            session_circuit = slugify(session.get("circuit_short_name") or "")
            session_country = slugify(session.get("country_name") or "")
            location_match = bool(location) and (
                location == session_location
                or location in session_circuit
                or session_location in location
            )
            country_match = bool(country) and country == session_country
            if location_match or country_match:
                score = (10 if location_match else 0) + (3 if country_match else 0) - day_gap
                candidates.append((score, session_start, session))
        if candidates:
            _, session_start, session = max(candidates, key=lambda item: (item[0], -item[1].timestamp()))
            race["qualifying_start_utc"] = session_start
            race["qualifying_cutoff_utc"] = session_start - timedelta(minutes=5)
            race["qualifying_match"] = {
                "session_key": session.get("session_key"),
                "location": session.get("location"),
                "country_name": session.get("country_name"),
                "match_method": "location/country and scheduled date proximity",
            }
        else:
            race["qualifying_start_utc"] = None
            race["qualifying_cutoff_utc"] = None
            race["qualifying_match"] = None


def datetime_string(value: datetime | None) -> str | None:
    return value.isoformat().replace("+00:00", "Z") if value else None


def build_query(races: list[dict[str, Any]]) -> tuple[str, list[str]]:
    event_terms = []
    params: list[str] = []
    for race in races:
        terms = []
        for alias in race["aliases"]:
            terms.append("contains(lower(market_slug), ?)")
            params.append(alias)
        if not terms:
            continue
        event_terms.append(
            f"(contains(lower(market_slug), ?) AND ({' OR '.join(terms)}))"
        )
        params.insert(len(params) - len(terms), str(race["year"]))
    if not event_terms:
        raise RuntimeError("No event aliases could be formed from the race schedules")
    predicate = (
        " AND ".join(
            [
                f"({' OR '.join(event_terms)})",
                "regexp_matches(lower(market_slug), ?)",
                "NOT regexp_matches(lower(market_slug), ?)",
            ]
        )
    )
    params.extend([WINNER_LANGUAGE, EXCLUDED_MARKET_LANGUAGE])
    query = f"""
        SELECT market_slug, asset_id, block_timestamp, price, p_event, usdc_amount,
               fee_usdc, condition_id, category, category_refined, outcome_label,
               winning_outcome_label, resolution_status,
               CAST(opens_at AS VARCHAR) AS opens_at,
               CAST(close_at AS VARCHAR) AS close_at,
               CAST(resolved_at AS VARCHAR) AS resolved_at,
               neg_risk_market_id, filename
        FROM read_parquet(?, filename=true)
        WHERE market_slug IS NOT NULL AND {predicate}
    """
    return query, params


def matching_races(slug: str, races: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = slug.lower()
    if not re.search(WINNER_LANGUAGE, normalized) or re.search(EXCLUDED_MARKET_LANGUAGE, normalized):
        return []
    matches = []
    for race in races:
        if str(race["year"]) not in normalized:
            continue
        matched_aliases = [alias for alias in race["aliases"] if alias in normalized]
        if matched_aliases:
            match = dict(race)
            match["matched_aliases"] = matched_aliases
            matches.append(match)
    return matches


def market_snapshot(rows: list[dict[str, Any]], cutoff: datetime | None) -> dict[str, Any]:
    if cutoff is None:
        return {"status": "cutoff_unavailable"}
    cutoff_ts = int(cutoff.timestamp())
    prior = [row for row in rows if row["block_timestamp"] <= cutoff_ts]
    if not prior:
        return {"status": "no_trade_observed_in_scan_window"}
    latest_ts = max(row["block_timestamp"] for row in prior)
    latest = [row for row in prior if row["block_timestamp"] == latest_ts]
    p_values = sorted(
        {round(float(row["p_event"]), 8) for row in latest if row["p_event"] is not None}
    )
    age_minutes = max(0.0, (cutoff_ts - latest_ts) / 60.0)
    return {
        "status": "trade_print_observed",
        "last_trade_utc": datetime.fromtimestamp(latest_ts, timezone.utc).isoformat().replace("+00:00", "Z"),
        "age_minutes_at_cutoff": round(age_minutes, 2),
        "last_trade_p_event_values": p_values,
        "p_event_is_unique_at_last_timestamp": len(p_values) == 1,
        "outcome_sides_at_last_timestamp": sorted({str(row["outcome_label"]) for row in latest if row["outcome_label"]}),
    }


def summarize_market(rows: list[dict[str, Any]], race: dict[str, Any]) -> dict[str, Any]:
    first = rows[0]
    return {
        "market_slug": first["market_slug"],
        "matched_aliases": sorted({alias for row in rows for alias in row["matched_aliases"]}),
        "categories": sorted({str(row["category"]) for row in rows if row["category"]}),
        "category_refined": sorted({str(row["category_refined"]) for row in rows if row["category_refined"]}),
        "neg_risk_market_ids": sorted({str(row["neg_risk_market_id"]) for row in rows if row["neg_risk_market_id"]}),
        "condition_ids": sorted({str(row["condition_id"]) for row in rows if row["condition_id"]}),
        "asset_ids": sorted({str(row["asset_id"]) for row in rows if row["asset_id"]}),
        "outcome_sides": sorted({str(row["outcome_label"]) for row in rows if row["outcome_label"]}),
        "winning_outcome_labels": sorted({str(row["winning_outcome_label"]) for row in rows if row["winning_outcome_label"]}),
        "resolution_statuses": sorted({str(row["resolution_status"]) for row in rows if row["resolution_status"]}),
        "opens_at_utc": sorted({str(row["opens_at"]) for row in rows if row["opens_at"]}),
        "close_at_utc": sorted({str(row["close_at"]) for row in rows if row["close_at"]}),
        "resolved_at_utc": sorted({str(row["resolved_at"]) for row in rows if row["resolved_at"]}),
        "trade_records_in_scan_window": len(rows),
        "distinct_trade_timestamps": len({row["block_timestamp"] for row in rows}),
        "last_prequalifying_trade": market_snapshot(rows, race.get("qualifying_cutoff_utc")),
        "last_pre_race_trade": market_snapshot(rows, race.get("race_cutoff_utc")),
        "scope_note": "Trade prints are not executable quotes; no historical book depth is present.",
    }


def scan(args: argparse.Namespace) -> dict[str, Any]:
    started_at = utc_now()
    revision, partitions = load_archive_index(args.revision)
    archive_dates = sorted(partitions)
    archive_start, archive_end = archive_dates[0], archive_dates[-1]
    print(
        f"Archive index: {len(partitions)} partitions, {sum(int(item.get('size', 0)) for item in partitions.values()):,} bytes; revision {revision}",
        flush=True,
    )
    source_errors: list[str] = []

    races = []
    for year in args.years:
        races.extend(load_races(year))
    attach_qualifying_cutoffs(races, source_errors)

    eligible_races = []
    date_to_races: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for race in races:
        race_day = race["race_start_utc"].date()
        if race_day < archive_start or race_day > archive_end:
            race["audit_status"] = "outside_archive_date_range"
            continue
        cutoffs = [race["race_cutoff_utc"]]
        if race.get("qualifying_cutoff_utc"):
            cutoffs.append(race["qualifying_cutoff_utc"])
        first_cutoff_day = min(cutoffs).date()
        window_start = first_cutoff_day - timedelta(days=args.lookback_days)
        window_end = race_day
        race["scan_window_start_utc"] = datetime.combine(window_start, dt_time.min, timezone.utc)
        race["scan_window_end_utc"] = datetime.combine(window_end + timedelta(days=1), dt_time.min, timezone.utc)
        race["audit_status"] = "pending_scan"
        eligible_races.append(race)
        day = window_start
        while day <= window_end:
            if day in partitions:
                date_to_races[day].append(race)
            day += timedelta(days=1)

    selected_dates = sorted(date_to_races)
    if not selected_dates:
        raise RuntimeError("No archive partitions overlap the selected F1 schedules")
    selected_entries = [partitions[day] for day in selected_dates]
    scanned_bytes = sum(int(partitions[day].get("size", 0)) for day in selected_dates)
    print(
        f"Scanning {len(selected_dates)} selected partitions ({scanned_bytes:,} compressed bytes) with DuckDB over HTTPS...",
        flush=True,
    )
    urls = [
        f"{DATASET_RESOLVE}/{revision}/{urllib.parse.quote(entry['path'], safe='/')}"
        for entry in selected_entries
    ]
    query, query_params = build_query(eligible_races)

    connection = duckdb.connect(database=":memory:")
    connection.execute("SET threads = 4")
    query_rows = []
    column_names: list[str] = []
    failed_partition_dates: list[str] = []
    try:
        batch_count = (len(urls) + args.batch_size - 1) // args.batch_size
        for batch_number, start in enumerate(range(0, len(urls), args.batch_size), start=1):
            batch_urls = urls[start : start + args.batch_size]
            batch_dates = selected_dates[start : start + args.batch_size]
            try:
                result_cursor = connection.execute(query, [batch_urls, *query_params])
                if not column_names:
                    column_names = [column[0] for column in result_cursor.description]
                query_rows.extend(result_cursor.fetchall())
            except Exception as exc:
                failed_partition_dates.extend(day.isoformat() for day in batch_dates)
                source_errors.append(
                    f"DuckDB scan failed for batch {batch_number}/{batch_count} "
                    f"({batch_dates[0]} through {batch_dates[-1]}): {exc}"
                )
            print(
                f"Scanned batch {batch_number}/{batch_count}; "
                f"candidate rows accumulated: {len(query_rows):,}",
                flush=True,
            )
    finally:
        connection.close()
    if not column_names:
        raise RuntimeError("No Parquet batch could be scanned; see prior error output")
    print(f"Candidate trade rows returned: {len(query_rows):,}", flush=True)

    market_rows: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    event_by_id = {race["event_id"]: race for race in eligible_races}
    for values in query_rows:
        row = dict(zip(column_names, values))
        slug = row["market_slug"].lower()
        row_ts = int(row["block_timestamp"])
        for match in matching_races(slug, eligible_races):
            race = event_by_id[match["event_id"]]
            if row_ts < int(race["scan_window_start_utc"].timestamp()):
                continue
            if row_ts >= int(race["scan_window_end_utc"].timestamp()):
                continue
            row_copy = dict(row)
            row_copy["matched_aliases"] = match["matched_aliases"]
            market_rows[(race["event_id"], slug)].append(row_copy)

    event_results = []
    for race in races:
        base = {
            "event_id": race["event_id"],
            "round": race["round"],
            "race_name": race["race_name"],
            "race_date_utc": race["race_date_utc"],
            "race_start_utc": datetime_string(race["race_start_utc"]),
            "race_cutoff_utc": datetime_string(race["race_cutoff_utc"]),
            "qualifying_start_utc": datetime_string(race.get("qualifying_start_utc")),
            "qualifying_cutoff_utc": datetime_string(race.get("qualifying_cutoff_utc")),
            "qualifying_match": race.get("qualifying_match"),
            "aliases_used_for_search": race["aliases"],
            "audit_status": race.get("audit_status"),
        }
        if race not in eligible_races:
            base.update({"candidate_market_count": 0, "markets": []})
            event_results.append(base)
            continue
        candidates = []
        for (event_id, slug), rows in market_rows.items():
            if event_id == race["event_id"]:
                candidates.append(summarize_market(rows, race))
        candidates.sort(key=lambda market: market["market_slug"])
        prequal_count = sum(market["last_prequalifying_trade"]["status"] == "trade_print_observed" for market in candidates)
        race_count = sum(market["last_pre_race_trade"]["status"] == "trade_print_observed" for market in candidates)
        fresh_race_count = sum(
            market["last_pre_race_trade"].get("age_minutes_at_cutoff", float("inf")) <= 60
            for market in candidates
        )
        base.update(
            {
                "scan_window_start_utc": datetime_string(race["scan_window_start_utc"]),
                "scan_window_end_utc_exclusive": datetime_string(race["scan_window_end_utc"]),
                "candidate_market_count": len(candidates),
                "markets_with_prequalifying_print": prequal_count,
                "markets_with_pre_race_print": race_count,
                "markets_with_pre_race_print_within_60m": fresh_race_count,
                "markets": candidates,
            }
        )
        base["audit_status"] = "candidate_markets_found_manual_review" if candidates else "no_candidate_market_observed_in_scan_window"
        event_results.append(base)

    result = {
        "project": "F1 Strategy Simulator vs. Market Odds",
        "created_at_utc": started_at,
        "method": "Search event-specific winner-language slugs in daily_aligned_multi trade partitions from N days before the OpenF1 qualifying cutoff (or race cutoff) through race day.",
        "dataset": {
            "id": DATASET_ID,
            "revision": revision,
            "license": "CC-BY-4.0 (dataset card; attribute the dataset authors in shared derivatives)",
            "archive_start_date": archive_start.isoformat(),
            "archive_end_date": archive_end.isoformat(),
            "partition_count": len(partitions),
            "partition_bytes": sum(int(item.get("size", 0)) for item in partitions.values()),
            "partitions_scanned": len(selected_dates),
            "scanned_partition_bytes": sum(int(partitions[day].get("size", 0)) for day in selected_dates),
            "selected_dates": [day.isoformat() for day in selected_dates],
            "failed_partition_dates": failed_partition_dates,
            "attribution": "Source: TimeSeventeen, Polymarket-v1, https://huggingface.co/datasets/TimeSeventeen/Polymarket-v1, CC-BY-4.0.",
        },
        "cutoffs": {
            "prequalifying": "OpenF1 scheduled Qualifying session start minus 5 minutes where a location/date match is found.",
            "pre_race": "Jolpica-F1 scheduled race start minus 5 minutes.",
            "lookback_days": args.lookback_days,
            "race_day_included": True,
        },
        "limitations": [
            "Market discovery relies on heuristic matching of year, location/race aliases, and winner language in market_slug; every candidate requires manual rule and event review.",
            "Only trades in the configured lookback window are scanned. A market with no observed print in that window is not proof that no historical market existed.",
            "The archive contains trade prints and normalized event probabilities, not historical order-book snapshots or executable quotes.",
            "Archived last-trade prices may be stale and do not establish a fillable price or profitable strategy.",
            "OpenF1 and Jolpica provide schedules used for cutoffs; schedule revisions and naming differences may affect joins.",
        ],
        "source_errors": source_errors,
        "schedule_event_count": len(races),
        "events_in_archive_range": len(eligible_races),
        "candidate_contract_count": sum(event.get("candidate_market_count", 0) for event in event_results),
        "events": event_results,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--years", nargs="+", type=int, default=[2024, 2025, 2026], help="F1 seasons to audit")
    parser.add_argument("--lookback-days", type=int, default=7, help="Calendar days before each cutoff to include")
    parser.add_argument("--batch-size", type=int, default=20, help="Remote Parquet partitions to scan per batch")
    parser.add_argument("--revision", default=None, help="Hugging Face dataset commit; defaults to current repository SHA")
    parser.add_argument("--output", default="reports/archive-f1-coverage.json", help="Output path for aggregated results")
    args = parser.parse_args()
    if args.lookback_days < 0:
        parser.error("--lookback-days must be zero or greater")
    if args.batch_size < 1:
        parser.error("--batch-size must be at least 1")

    result = scan(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "dataset_revision": result["dataset"]["revision"],
        "archive_partitions": result["dataset"]["partition_count"],
        "scanned_partitions": result["dataset"]["partitions_scanned"],
        "scanned_partition_bytes": result["dataset"]["scanned_partition_bytes"],
        "events_in_archive_range": result["events_in_archive_range"],
        "candidate_contract_count": result["candidate_contract_count"],
        "source_errors": result["source_errors"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
