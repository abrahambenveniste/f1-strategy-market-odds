# Data-source register

**Status:** Source plan updated 20 October 2026. The market audit has not run successfully, so coverage, historical depth, field availability, current response schemas, and rights to redistribute data are not yet confirmed. Fields below are the target semantic fields to inspect and map, not a claim that every endpoint supplies every field.

## Source-to-field plan

| Source | Data we plan to collect | Main use and constraints |
|---|---|---|
| [FastF1](https://docs.fastf1.dev/) | Season, event, session, driver and constructor identifiers; session start/end times; lap and sector times; speed-trap / telemetry channels where available; position; compound and tire age; stint; pit-in/pit-out; track status; session weather observations; race-control messages; session results. | Practice and qualifying pace, grid context, pit/tyre context, and official session identifiers. Check field/session coverage before feature selection. Derive representative long-run pace only after excluding invalid, deleted, in-lap/out-lap, pit, and affected yellow / Safety Car laps under a documented rule. Do not use messages or observations that occurred after the forecast cutoff. |
| [Jolpica-F1](https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md) | Season/round calendar, UTC/local schedule where provided, circuit IDs, driver and constructor IDs, qualifying classifications, starting grid, race classifications/status, lap results, pit stops, and standings. | Stable join keys, historical prior and season context, grid/result cross-checks, and resolution-label validation. Endpoints paginate; follow the documented limits and send the required identifying User-Agent. Use official Formula 1 classification to resolve discrepancies. |
| [Polymarket Gamma API](https://gamma-api.polymarket.com/docs) | F1 event and market IDs; slug/title/question; full description and resolution rules; market start/close/end fields where present; active/closed/resolved status; outcome labels; CLOB token IDs; volume/liquidity fields when returned; retrieval timestamp. | Discover the event/market universe and manually map each candidate contract to season, round, and driver. Keep raw payloads locally during schema review; write a normalized, privacy-safe market inventory with inclusion/exclusion reason. Never rely on fuzzy title matching alone. |
| [Polymarket CLOB market data](https://docs.polymarket.com/) | Per-token historical price points (time and price) where available; prospective public book snapshots with best bid/ask and available depth; retrieval time and token ID. | Historical prices support probability benchmarking only after granularity, staleness, and price meaning are checked. They may be last/reference prices rather than executable quotes. Use prospective order-book observations for hypothetical execution analysis; model a buy at the ask and cap size by displayed depth. Read-only only; no order placement. Verify endpoint schemas and rate limits during implementation. |
| [Open-Meteo Single Runs API](https://open-meteo.com/en/docs/single-runs-api) | Circuit latitude/longitude; model identifier; forecast run initialization; hourly valid time / lead; 2 m temperature and relative humidity; precipitation probability and amount; cloud cover; 10 m wind speed, direction, and gusts; units; retrieval timestamp. | Weather forecasts at each defined cutoff, sourced only from a model run initialized and available before that cutoff. Keep run initialization separate from forecast valid time. The archive's model/date coverage is a gating issue: the docs indicate ECMWF IFS HRES archive from March 2024 and other models from April 2026. Use older historical weather or reanalysis only for descriptive analysis, never as a forecast feature. |
| [Formula 1 official results](https://www.formula1.com/en/results.html) | Final race classification, winner, driver/team names, race date, and any classification amendment. | Human/source cross-check of race winner and market resolution mapping. Record source link and when the classification was checked; investigate disagreements with Jolpica before labeling. |

### Forecast horizons

The protocol currently targets:

1. **Pre-qualifying:** immediately before qualifying starts.
2. **Pre-race:** five minutes before scheduled race start.

For every candidate input, retain its source timestamp and earliest known availability. Join only data that were available at or before the relevant cutoff. For market prices, use the last observation at or before cutoff; do not interpolate from a later point. Record quote age and the audit's pre-set stale-quote rule. For Open-Meteo, preserve both run-initialization and forecast-valid timestamps so later runs cannot leak into earlier forecasts.

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

- FastF1 documentation: https://docs.fastf1.dev/
- Jolpica endpoint documentation and pagination: https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md
- Jolpica rate limits: https://github.com/jolpica/jolpica-f1/blob/main/docs/rate_limits.md
- Polymarket Gamma API schema: https://gamma-api.polymarket.com/docs
- Polymarket Data API v2: https://data-api.polymarket.com/v2/docs
- Open-Meteo Single Runs API: https://open-meteo.com/en/docs/single-runs-api
- Open-Meteo Historical Weather: https://open-meteo.com/en/docs/historical-weather-api

Confirm current terms, schemas, and field coverage as each connector is implemented. Public availability does not imply permission to republish raw data.
