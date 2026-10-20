# Research and implementation log

This is the project diary. Add an entry whenever a decision, data audit, experiment, or result changes the research direction. Keep failed attempts and negative findings.

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