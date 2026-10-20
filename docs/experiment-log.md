# Research and implementation log

This is the project diary. Add an entry whenever a decision, data audit, experiment, or result changes the research direction. Keep failed attempts and negative findings.

## 2026-10-21 — Gamma certificate error and Polymarket-v1 sample audit

**Browser/network finding:** The user reports that the in-app browser cannot verify the certificate for `gamma-api.polymarket.com` and shows `ERR_CERT_COMMON_NAME_INVALID`. This confirms a certificate-name validation failure in the browser as well as the earlier client requests; it does not identify whether the cause is the endpoint, DNS routing, or network inspection. TLS verification stayed enabled.

**Alternative dataset:** Reviewed the independent [Polymarket-v1 archive](https://huggingface.co/datasets/TimeSeventeen/Polymarket-v1). Its Hub tree API lists 857 `daily_aligned_multi` date partitions spanning 22 Dec 2023–28 Apr 2026. The dataset card reports CC-BY-4.0 and documents trade records, normalized event probabilities, market slugs, resolution labels, and no order-book snapshots.

**Small sample method:** The Hugging Face Dataset Viewer `/search` call returned HTTP 502; `/filter` returned HTTP 500 with “the dataset index is loading”. Direct downloads of four date partitions succeeded using normal certificate validation: `2024_03_02`, `2024_03_03`, `2025_04_13`, and `2025_04_14` (3,495,035 bytes total). DuckDB 1.5.6 was installed only under the local `work/hfdiag/pkgs` scratch folder to inspect the Parquet files; no project dependencies or lockfile were changed, and no downloaded data were committed.

**Results:** The two 2024 Bahrain race-date files produced no F1 winner-market matches; that narrow check does not establish 2024-wide absence. The 2025 Bahrain race-date files contained 14 resolved driver/“another driver” winner-market contracts in one multi-outcome event group, 1,495 trade records, and 80,439.91 USDC.e notional. The Jolpica schedule returned a 15:00 UTC race start. At the five-minute pre-race cutoff (14:55 UTC), 13 candidate markets had at least one trade (675 records, 25,544.34 USDC.e notional); 11 of their most recent prints were within one hour, while two were stale. This validates one useful historical event sample and makes staleness a required feature of the market-data audit.

**Decision and next step:** The archive provides a no-cost route for retrospective trade-price benchmark and resolution-label research, so work can continue while official Polymarket TLS access remains broken. It cannot support order-book-aware execution or prove fillable profitability. Finish a selective F1 market/season and cutoff-coverage audit across the archive. Keep official Polymarket public APIs or a verified provider as a requirement for prospective quote/depth collection and realistic paper execution. Never disable certificate checks.

## 2026-10-20 — Polymarket browser failure and alternate provider check

**User confirmation:** The Gamma API URL also fails in the user's in-app browser with `ERR_CERT_COMMON_NAME_INVALID` and a browser message that the certificate for `gamma-api.polymarket.com` cannot be verified. This confirms the official API issue is not limited to the Python collector or shell request.

**Fallback check:** The independent PolymarketData provider's documentation advertises minute-level prices, liquidity metrics, and historical Level 2 books, with standard coverage from August 2025 and earlier history on enterprise plans. Its API host completed TLS successfully from this environment, but an unauthenticated `/v1/markets?limit=1` request returned HTTP 401, consistent with the provider's requirement for an API key. Its specific F1 market coverage, usable sample depth, pricing, and terms have not been verified. No account, key, or purchase was made.

**Decision:** Do not disable TLS checks or scrape through an unverified certificate. Keep the official Polymarket APIs as the preferred source if a valid network route can be restored. Treat the third-party API as a possible paid fallback only after verifying F1 market coverage, suitable historic timestamps, and cost.

**Next step:** Choose whether to try the official API from a different trusted network or evaluate a time-limited sample/trial from the independent provider. Public F1/results/weather work can continue while this is decided, but market modelling cannot.

## 2026-10-20 — Read-only API and dataset availability check

**Action:** Checked public source connectivity using standard certificate validation, then queried small sample records. No certificates were ignored, packages were not installed, and no source files or API credentials were saved. Updated the source plan and README with the findings.

**Results by source:**

- **Jolpica-F1 — reachable.** `/ergast/f1/current.json?limit=1` returned HTTP 200 and reported 23 scheduled records for the 2026 season. `/ergast/f1/2024/1/results.json?limit=1` returned HTTP 200; the response reported 20 race classifications and listed Max Verstappen first.
- **OpenF1 — usable historical sample confirmed.** Its API documentation says historical sessions from 2023 onward are free and require no authentication. `/v1/sessions?year=2024&session_name=Race` returned 24 sessions. The 2024 Bahrain race session key 9472 returned a lap record for driver 1 / lap 8 and three stint records for that driver. The first sample attempt included an unsupported `limit` query and produced errors; the follow-up used documented field filters and succeeded. A full coverage/missingness audit remains necessary.
- **Open-Meteo — reachable.** Live forecast and historical-forecast endpoints returned HTTP 200. A historical-forecast request at Circuit of The Americas coordinates for 17–19 Oct 2025 returned 72 hourly observations for temperature, precipitation probability/amount, and wind speed. This proves a usable example, not full archived-run coverage.
- **FastF1 / F1 Live Timing archive — unauthenticated access currently unavailable.** A direct 2024 session-data request returned HTTP 401; the timing host root returned HTTP 403. The FastF1 maintainer's open issue reports that the archive began requiring authentication around 15 Oct 2026 and that F1 TV Access (or higher) is now needed; the maintainer released a 3.9.0 alpha with authentication support. The local runtime has Python 3.13.15 and FastF1 is not installed. Use OpenF1 as the default historical source unless authenticated FastF1 access is specifically available and verified.
- **Polymarket Gamma, CLOB, and Data APIs — blocked by TLS in this environment.** Small public read requests to Gamma event discovery, CLOB time, and Data API markets did not complete. Gamma's TLS error identified a certificate name mismatch and certificate-chain errors; CLOB/Data API requests also failed the SSL handshake. The API docs and browser retrieval did not provide an alternate route. Certificate verification was not disabled. No API market inventory or Polymarket price data have been collected.

**Dataset status:** No raw or processed dataset has been retained in Git or locally by this check. F1 results/session samples and weather data can be queried; however, the central Polymarket market/price-history dataset is unavailable until API access works. The project is not ready for market-versus-model fitting or paper-return analysis.

**Decision:** Use OpenF1 historical data from 2023 onward as the primary F1 timing candidate; keep FastF1 optional if authenticated access is available. Continue with feature/data-quality planning, but do not model or claim trading edge until Polymarket market coverage, resolution rules, and historical prices are audited.

**Next step:** Ask whether the Gamma API endpoint opens from the user's normal browser/network. If so, isolate the failure to this execution environment and establish a valid read-only route; if not, resolve the network/certificate issue. No Polymarket credentials are needed for public read-only endpoints.

## 2026-10-20 — Source-to-field map and technical stack

**Action:** Expanded `docs/data-sources.md` into a source-to-field plan, created `docs/technical-stack.md`, and linked both from the README. Recorded which fields are candidates, how they will be used, what availability constraints matter, and which package/tool will support each step.

**Data plan:** FastF1 for session timing, laps, tires/stints, telemetry where available, weather observations, and race-control context; Jolpica-F1 for event/session identifiers, schedule, qualifying/grid/results, laps, pit stops, and historical context; Polymarket Gamma for event and contract discovery, rules, outcomes, token IDs, and available market metadata; Polymarket CLOB data for historical token-price points and prospective public bid/ask/depth snapshots; Open-Meteo single model runs for archived pre-cutoff forecasts; Formula 1's official results for classification and label cross-checks. The docs distinguish candidate semantic fields from confirmed endpoint schemas: actual coverage and field mappings await a successful audit.

**Language and tools:** Python 3.11+ for the analysis workflow and SQL through DuckDB for local analytical queries. The current collector remains dependency-free on Python's standard library. Planned packages are FastF1, httpx, pandas, NumPy, DuckDB, PyArrow, SciPy, scikit-learn, Matplotlib, Seaborn, optional JupyterLab, and Ruff; exact versions and a uv lockfile will be set when the analysis environment is created.

**Source checks:** Jolpica documentation lists calendar, qualifying, results, laps, and pit-stop endpoints, supports pagination, and requires a descriptive User-Agent. Open-Meteo's Single Runs documentation provides model-run initialization and hourly forecast variables; its current archive notes ECMWF IFS HRES from March 2024 and other models from April 2026, so older weather forecast coverage may be limited. This limitation is now explicit in the source plan.

**Execution status:** Documentation and source planning only. No market data have been collected, no packages have been installed, and no model or trading simulation has run. The earlier API failure remains unresolved: local direct requests failed TLS certificate validation, including a Node diagnostic reporting an expired certificate. Certificate validation has not been bypassed.

**Next step:** Establish a valid TLS path to the public Gamma API, run the read-only collector, inspect real payload schemas and coverage, and then lock the inclusion criteria and minimal dependency versions before building the joined dataset.

## 2026-10-20 — First market-audit collector

**Action:** Added a read-only Python collector for public Polymarket Gamma tags and F1 event/market metadata at `scripts/audit_polymarket_f1_markets.py`. Added local-data/cache exclusions to `.gitignore` and documented the run command in the README.

**Collector scope:** Discover Formula 1 tags, page through associated events, record embedded market metadata and outcomes/token IDs, and emit heuristic classification hints for manual review. It does not request order books, place trades, or produce prices/returns. The generated JSON is ignored by Git pending the data-terms review.

**Source/API check:** The official Gamma API schema exposes event and market discovery. Polymarket's official F1 page lists F1 markets, including Grand Prix winner markets, so the project has a plausible market universe; the historical coverage and point-in-time price quality remain unknown. The source register contains links to the API documentation.

**Execution status:** The collector has not run and no market dataset has been retrieved. A direct API request from the current shell failed TLS certificate validation; opening the API endpoint in the browser also returned a certificate-name error. Certificate verification was not disabled. No coverage count, market inclusion decision, model result, or profitability claim is available yet.

**Next step:** Run the documented collector in an environment with a valid connection to the public Gamma API, inspect event/market payload schemas, and record coverage, market rules, candidate inclusion/exclusion reasons, and historical quote granularity. Then revise the protocol's numerical coverage thresholds before fitting any model.

## 2026-10-20 — Project bootstrap

**Action:** Created the public repository and added the README, protocol draft, and source register.

**Initial scope:** Test whether pre-event F1 information adds race-winner forecast value beyond contemporaneous Polymarket market prices, then separately test whether any edge survives hypothetical execution costs.

**Decisions recorded:**

- Start with Grand Prix race-winner markets; audit contract rules, full-field coverage, timestamps, historical price granularity, and quote quality before selecting the final event sample.
- Treat races—not driver-market rows—as the chronological validation unit.
- Compare forecast quality and hypothetical trading economics as separate questions.
- Use archived point-in-time forecasts and session data available by a fixed prediction cutoff. Do not use realized weather or later race events as predictive inputs.
- Use historical chart prices for probability benchmarking only when their timestamps are suitable. Do not call them executable prices; collect public order-book snapshots prospectively if necessary.
- Keep work to public-data research and paper analysis. No live trades.
- Do not publish raw source data unless terms permit redistribution.

**Evidence/source checks:** The source register links the primary project/API documentation consulted for FastF1, Jolpica-F1, Polymarket, and Open-Meteo. The Open-Meteo documentation distinguishes archived operational forecasts from historical reanalysis. The Polymarket API documentation distinguishes market/token identifiers and provides public price-history and market-data routes. API availability and coverage still require a reproducible audit in code.

**Results:** None yet. No dataset has been collected, no model has been fitted, and no profitability claim is made.

**Next step:** Implement a market-universe and coverage audit that produces a versioned, privacy-safe inventory of F1 events, race-winner contracts, outcomes, tokens, rules, price timestamps, and inclusion/exclusion reasons.
