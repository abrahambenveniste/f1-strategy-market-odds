# Data-source register

**Status:** Availability check updated 21 October 2026. OpenF1, Jolpica-F1, and Open-Meteo returned usable sample data. The official Gamma API fails TLS validation in this environment; the user reports the same `ERR_CERT_COMMON_NAME_INVALID` in the in-app browser. A small sample of an independent public archive confirms resolved 2025 F1 winner-market trades, but full season/cutoff coverage and executable quote/depth data remain unaudited. No source data are committed to the repository.

## Source-to-field plan and current access

| Source | Data we plan to collect | Access status and constraints |
|---|---|---|
| [OpenF1](https://openf1.org/docs/) | Meetings/sessions and identifiers; session start/end; driver/team identity; lap and sector times; speed traps; starting grid and session results; tire compounds/age and stint laps; pit stops; race-control messages; weather observations; car telemetry if needed. | **Primary F1 timing source candidate.** Historical data from 2023 onward is documented as free and unauthenticated. On 20 Oct 2026, the sessions endpoint returned 24 race sessions for 2024; a Bahrain 2024 race lap query returned a sample lap and a stint query returned three stints for one driver. Coverage and field completeness still need a full audit. OpenF1 is unofficial; review terms and use limits before publishing data. |
| [FastF1](https://docs.fastf1.dev/) | Potential alternative access to F1 timing, laps, telemetry, tires/stints, weather observations, race-control messages, and session results. | **Not currently usable without authenticated F1 TV access.** The F1 timing archive returned HTTP 401 for an unauthenticated session-data request on 20 Oct 2026. FastF1's maintainer confirms the archive now requires an F1 TV Access subscription (or higher); authentication support is in a 3.9.0 alpha release. Keep FastF1 optional unless credentials/subscription are available and the stable connector is verified. |
| [Jolpica-F1](https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md) | Season/round calendar, circuit IDs, driver and constructor IDs, qualifying classifications, starting grid, race classifications/status, lap results, pit stops, and standings. | **Reachable.** On 20 Oct 2026, the current calendar request returned HTTP 200 and 23 scheduled race records for 2026; a 2024 round 1 results request returned HTTP 200 and 20 classifications. Endpoints paginate; follow documented limits and send the required identifying User-Agent. |
| [Polymarket Gamma API](https://gamma-api.polymarket.com/docs) | F1 event and market IDs; slug/title/question; full description and resolution rules; market start/close/end fields where present; active/closed/resolved status; outcome labels; CLOB token IDs; volume/liquidity fields when returned; retrieval timestamp. | **Blocked in this environment.** Gamma event discovery failed TLS validation on 20 Oct 2026 (certificate name mismatch and chain errors). No API data, market inventory, historical coverage, or user-specific credentials have been obtained. Do not disable certificate verification. Public read access is expected to require no user trading credentials; confirm access from a trusted network before proceeding. |
| [Polymarket CLOB market data](https://docs.polymarket.com/) and [Data API v2](https://data-api.polymarket.com/v2/docs) | Per-token historical price points where available; prospective public order-book snapshots with best bid/ask and available depth; trade/market metadata if needed; retrieval time and token ID. | **Blocked in this environment** by SSL connection failures on 20 Oct 2026. Historical prices and executable quote/depth coverage therefore remain unknown. A successful market-discovery audit is a prerequisite to modeling and any paper-trading analysis. Read-only only; no order placement. |
| [Polymarket-v1 public archive](https://huggingface.co/datasets/TimeSeventeen/Polymarket-v1) | Matched trade prices/quantities/fees and taker direction; market slug/category; candidate and resolution labels; open/close/resolution times; normalized `p_event` and multi-outcome group ID. | **Reachable via selective Parquet downloads.** The independent dataset is licensed CC-BY-4.0 and covers 21 Nov 2022–28 Apr 2026. Four daily partitions were inspected. The 2025 Bahrain race-date files contain 14 resolved winner-candidate markets in one multi-outcome group and 1,495 trade records (~80,440 USDC.e notional). At the five-minute pre-race cutoff, 13 candidates had trades; 11 had a last print within one hour. This is one event sample, not a full coverage audit. The archive contains trade prints but no book snapshots, quote updates, cancellations, or off-chain depth, so it cannot establish executable PnL. |
| [Open-Meteo Single Runs API](https://open-meteo.com/en/docs/single-runs-api) and [Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api) | Circuit latitude/longitude; model; run initialization; hourly forecast valid time/lead; temperature, humidity, precipitation probability/amount, cloud cover, wind speed/direction/gusts; units and retrieval time. | **Reachable.** Live forecast and historical-forecast requests returned HTTP 200. A historical-forecast query at Circuit of The Americas coordinates for 17–19 Oct 2025 returned 72 hourly observations for temperature, precipitation probability/amount, and wind speed. The Single Runs archive indicates ECMWF IFS HRES from March 2024 and other models from April 2026, so historical archived-run coverage may limit older events. Keep forecasts separate from realized weather and use only runs available by each cutoff. |
| [Formula 1 official results](https://www.formula1.com/en/results.html) | Final race classification, winner, driver/team names, race date, and later classification amendments. | Manual reference for result and resolution cross-checks. No structured endpoint connection was established in this check. |

## Public historical Polymarket archive

[Polymarket-v1](https://huggingface.co/datasets/TimeSeventeen/Polymarket-v1) is an independent public archive of Polymarket v1 on-chain fills and lifecycle events, with data through 28 Apr 2026 under CC-BY-4.0. Its `daily_aligned_multi/` layer is relevant to multi-outcome F1 winner markets. It includes matched trade prices, timestamps, fees, outcome and resolution labels, market slugs, and an event-normalized probability field. The dataset is not affiliated with or endorsed by Polymarket.

**21 Oct 2026 sample audit:** The Hub tree listing returned 857 daily partitions from 22 Dec 2023 to 28 Apr 2026. Four files were downloaded with normal TLS validation (2 and 3 Mar 2024; 13 and 14 Apr 2025; 3,495,035 bytes total) and queried locally. The 2024 Bahrain race-date files had no F1 winner-market matches; this does not establish absence elsewhere in the season. The 2025 Bahrain race-date files contained 14 resolved winner-candidate markets in one event group, 1,495 trade records, and 80,439.91 USDC.e notional. Jolpica lists the race at 15:00 UTC; five minutes before the start, 13 candidates had trades (675 records, 25,544.34 USDC.e notional), and 11 of the 13 most recent prints were at most one hour old. The sample shows both useful pre-race prints and stale-print risk.

**Limits and route:** The dataset card states that none of its layers contain order-book snapshots, quote updates, cancellations, or off-chain resting-order depth. Use the archive to test whether F1 data improve forecasts relative to historical trade prices and resolved outcomes; do not treat its last trade as an executable quote. Full-season and pre-qualifying coverage have not yet been measured. The Hugging Face `/search` request returned 502 and `/filter` reported that the dataset index was loading, while direct small-file downloads worked. Use selective partitions for the next coverage pass instead of downloading the full archive. Include an attribution to the dataset authors in any shared derivative output.

## Independent data-provider fallback under review

[PolymarketData](https://docs.polymarketdata.co/) is an independent provider, not affiliated with Polymarket. Its documentation claims minute-level prices, liquidity metrics, and historical Level 2 book snapshots, with standard history starting in August 2025; older history is offered on enterprise plans. Its API host passed TLS from this environment, but `GET /v1/markets?limit=1` returned HTTP 401 without an API key, as the docs require. No account, key, or purchase has been made. Whether its archive contains the specific historical F1 markets and whether the price/depth sample is sufficient remain unverified. Verify those points and current cost before choosing this route.

### Forecast horizons

The protocol currently targets:

1. **Pre-qualifying:** immediately before qualifying starts.
2. **Pre-race:** five minutes before scheduled race start.

For every candidate input, retain its source timestamp and earliest known availability. Join only data available by the relevant cutoff. For market prices, use the last observation at or before cutoff; do not interpolate from a later point. Record quote age and set the stale-quote rule during the coverage audit. For Open-Meteo, preserve both run-initialization and forecast-valid timestamps so later runs cannot leak into earlier forecasts.

### Point-in-time caution

Historical APIs expose data after a race; that does not make every field valid as a pre-race feature. Use the timestamp to reconstruct what was known by each cutoff. Post-cutoff timing, weather, race control, pit calls, and results are labels or retrospective descriptions only.

## Normalized data fields

Every retained observation should include, where applicable:

- Stable `source`, `source_record_id`, `event_key`, `session_key`, `market_id`, `token_id`, and outcome/driver key.
- `event_time_utc`, `source_timestamp_utc`, `retrieved_at_utc`, and the applicable `forecast_cutoff_utc`.
- Original source values and units, normalized values, request endpoint/parameters, and parser/schema version.
- Missingness, quality/filter flags, and an inclusion/exclusion reason.

The canonical event key will be season + round, checked against source IDs and human-readable event names. Keep driver/constructor aliases in an explicit mapping table with provenance.

## Ingestion and storage

For each source request, record the exact endpoint and query parameters, UTC retrieval time, response status/schema, pagination, coverage, errors, client version, and terms review. Keep separate layers:

1. `data/raw/`: local immutable source captures, only when permitted.
2. `data/interim/`: normalized and joined source tables.
3. `data/processed/`: cutoff-safe features and modeling tables.
4. `reports/` or `results/`: generated metrics, charts, configurations, and output hashes.

The repository currently ignores raw/interim/processed data and local caches. Commit code, source notes, data dictionaries, permitted small examples, and derived outputs only where source terms allow. Never commit credentials, tokens, or `.env` files. Preserve a content hash and code revision for retained artifacts.

## Source references

- Polymarket-v1 archive card and license/schema: https://huggingface.co/datasets/TimeSeventeen/Polymarket-v1
- Polymarket-v1 paper: https://arxiv.org/abs/2606.04217
- Hugging Face Dataset Viewer search API: https://huggingface.co/docs/dataset-viewer/search
- OpenF1 API and field documentation: https://openf1.org/docs/
- FastF1 documentation: https://docs.fastf1.dev/
- FastF1 archive-authentication status: https://github.com/theOehrly/Fast-F1/issues/978
- Jolpica endpoint documentation and pagination: https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md
- Jolpica rate limits: https://github.com/jolpica/jolpica-f1/blob/main/docs/rate_limits.md
- Polymarket Gamma API schema: https://gamma-api.polymarket.com/docs
- Polymarket Data API v2: https://data-api.polymarket.com/v2/docs
- Open-Meteo Single Runs API: https://open-meteo.com/en/docs/single-runs-api
- Open-Meteo Historical Forecast API: https://open-meteo.com/en/docs/historical-forecast-api
- Open-Meteo Historical Weather API: https://open-meteo.com/en/docs/historical-weather-api

Confirm current terms, schemas, and field coverage as each connector is implemented. Public availability does not imply permission to republish raw data.
