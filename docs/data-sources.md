# Data-source register

**Status:** Initial source inventory, 20 October 2026. Availability, schemas, terms, and redistribution rights must be checked when each connector is implemented. This register is not evidence that every historical race or market is covered.

| Source | Intended use | Point-in-time / quality notes | Access and publication notes |
|---|---|---|---|
| [FastF1](https://docs.fastf1.dev/) | Session schedule, lap and sector timing, telemetry, tire/stint data, weather observations, race-control messages, and session results. | Audit coverage and fields by session. Data can be incomplete, delayed, revised, or absent; lap filtering and the source timestamp must be preserved. Only use fields available by the forecast cutoff. | The Python library uses F1 live timing data. Check current source terms and FastF1 documentation before use; do not assume public access implies unrestricted redistribution. Keep local caches out of Git. |
| [Jolpica-F1](https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md) | Historical race calendar, circuits, qualifying, results, and standings; cross-check identifiers and outcomes. | Ergast-compatible endpoints are paginated and have documented differences/rate limits. Send the required identifying User-Agent and log endpoint, query, response time, and version. Validate all joins to race and driver keys. | Respect the API's [terms and rate limits](https://github.com/jolpica/jolpica-f1/blob/main/docs/rate_limits.md). Store only necessary derived tables unless redistribution is permitted. |
| [Polymarket Gamma API](https://gamma-api.polymarket.com/docs) | Discover F1 events/markets and retrieve contract text, status, event/market IDs, outcome labels, and CLOB token IDs. | Treat the displayed market question and full resolution rules as authoritative for inclusion. Fuzzy name matching is not sufficient to map a driver or race. Record retrieval time and revisions. | Public API; read current platform documentation and terms. No authenticated trading endpoints are in scope. |
| [Polymarket Data API v2](https://data-api.polymarket.com/v2/docs) and [CLOB market data](https://docs.polymarket.com/) | Retrieve token price history and available market/trade metadata; collect public order-book snapshots prospectively for executable bid/ask and depth. | Price histories may be sparse or represent a reference/last-traded price rather than an executable quote. Audit timestamp granularity and coverage per market. For economic analysis, prefer captured order-book asks for hypothetical buys and model fills conservatively. | Market data only. No order placement, wallet use, or live trading. Follow current API rate limits and platform terms. |
| [Open-Meteo Single Runs API](https://open-meteo.com/en/docs/single-runs-api) | Reconstruct archived forecast runs initialized before the prediction cutoff, for race venue coordinates and forecast hours. | Prefer a model run whose initialization and publication time precede the cutoff. Coverage depends on model and date. The [Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api) stitches model runs into a continuous series; the [Previous Runs API](https://open-meteo.com/en/docs/previous-runs-api) exposes fixed lead-time forecasts. Audit whether the selected archive matches the forecast information actually available at the cutoff. | Record model, run initialization, lead time, coordinates, units, endpoint, and retrieval timestamp. Review attribution and service-use requirements before publishing derived data. |
| [Formula 1 official results](https://www.formula1.com/en/results.html) | Human verification of official race classification and resolution mapping. | Store the official classification timestamp and any later amendment. If Jolpica and official classification differ, investigate and document the resolution used. | Link to source; do not republish material without checking its terms. |

## Ingestion record required for every source

For each request or file, record:

- Stable source name, exact URL/endpoint, query parameters, retrieval timestamp in UTC, and request/client version.
- Event key, session or market key, source timestamp, event timestamp, and time zone.
- Response schema/version, pagination, coverage, missing fields, and any status/errors.
- Data-license/terms review and whether raw data may be kept, shared, or only transformed.
- Content hash for retained artifacts and code revision for transformations.

Keep data in separate layers: immutable source capture, normalized tables, model features, and results. Never overwrite raw responses during cleaning.

## Storage and Git policy

Do not commit credentials, **.env** files, API tokens, local cache files, or large vendor/API dumps. Publish the collector and transformations, data dictionaries, non-sensitive metadata, and small samples only if the source permits redistribution. Before publishing derived tables or figures, check whether the source requires attribution or imposes other terms.