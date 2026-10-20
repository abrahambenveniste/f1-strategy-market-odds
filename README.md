# F1 Strategy Simulator vs. Market Odds

A reproducible research project asking whether public F1 performance and race-context data can improve race-winner probabilities beyond Polymarket prices—and whether any measured difference survives executable prices and trading frictions.

> **Status:** Research design, source/stack documentation, and a read-only Gamma market-audit collector are in place. OpenF1, Jolpica-F1, and Open-Meteo sample data are accessible; official Polymarket API calls currently fail TLS validation. A small public archive sample confirms resolved F1 winner-market trade data for 2025 Bahrain, but full coverage and executable quotes are not yet audited. No joined model dataset, model results, paper returns, or profitability evidence have been produced.

## Research question

For a Formula 1 Grand Prix, do information available before qualifying or before the race improve the probability forecast for the race winner relative to the contemporaneous Polymarket market? If they do, is the improvement large enough to overcome spread, fees, slippage, liquidity limits, and forecast uncertainty?

The primary unit will be a **race event**, with the field of drivers treated jointly. The first milestone is to audit historical market coverage, contract rules, timestamps, and price-history quality. Target markets and forecast cutoffs will be fixed in that audit before modeling.

## Approach

1. **Audit the market universe.** Find F1 race-winner markets, record their rules, outcomes, token IDs, timestamps, liquidity proxies, and available price history. Check that all candidate drivers and resolution outcomes map cleanly to official results.
2. **Build a point-in-time dataset.** Join market observations to F1 session data, historical results, and weather information. Store source, retrieval time, event time, and feature-availability cutoff. Use archived forecasts for predictive features; use realized weather only for retrospective description.
3. **Establish benchmarks.** Compare the market-implied probability with simple F1 baselines, then with a calibrated pace/strategy model and Monte Carlo race simulator.
4. **Validate chronologically.** Use walk-forward, race-level splits. Report multiclass Brier score, log loss, calibration, coverage, and uncertainty. Keep every driver-market for a race in the same split.
5. **Estimate tradability separately.** Use executable order-book prices and conservative fill assumptions where captured. Historical chart prices alone will not be treated as executable. Publish hypothetical paper-trading results with costs and drawdowns; do not place live trades.

## Candidate signals

- Qualifying pace and grid position
- Practice long-run pace, tire compound/age, stint lengths, and pit-stop history
- Driver and constructor strength, with track-specific and season-regime adjustments
- Circuit characteristics, race conditions, and weather forecasts available at the prediction cutoff
- Incident and Safety Car scenarios in the race simulator

Feature availability will be audited carefully to prevent look-ahead leakage. Complex telemetry and strategy features will only be retained if the data are reliable and add out-of-sample value.

## Data sources

- [OpenF1](https://openf1.org/docs/): primary candidate for historical F1 session, lap, grid/results, stint, pit-stop, race-control, weather, and telemetry data from 2023 onward.
- [Jolpica-F1](https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md): historical schedules and results through an Ergast-compatible API.
- [Open-Meteo Single Runs API](https://open-meteo.com/en/docs/single-runs-api) and [Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api): archived forecast runs for point-in-time weather features. The [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) provides reanalysis and is not a substitute for a forecast that was actually available at the time.
- [Polymarket Gamma API](https://gamma-api.polymarket.com/docs), [CLOB and Data APIs](https://data-api.polymarket.com/v2/docs): market discovery, metadata, historical prices, and public market data.
- [Polymarket-v1 public archive](https://huggingface.co/datasets/TimeSeventeen/Polymarket-v1): independent, CC-BY-4.0 historical trade fills and resolved labels. One 2025 Bahrain winner-market sample is verified; it has no order-book snapshots, so it supports price-probability research but not executable fill claims.
- [FastF1](https://docs.fastf1.dev/) remains an optional alternative. Its live timing archive currently returns HTTP 401 without authentication; see the [availability log](docs/experiment-log.md).

See [docs/data-sources.md](docs/data-sources.md) for the source-to-field plan and availability checks, [docs/technical-stack.md](docs/technical-stack.md) for language, packages, and tools, [docs/mcp-evaluation.md](docs/mcp-evaluation.md) for the MCP assessment, and [docs/research-plan.md](docs/research-plan.md) for the detailed protocol.

## Current access check

Read-only sample requests on 20–21 October 2026 returned data from OpenF1, Jolpica-F1, and Open-Meteo. Polymarket Gamma, CLOB, and Data API calls fail TLS validation in this environment; the user reproduced `ERR_CERT_COMMON_NAME_INVALID` for Gamma in the in-app browser. A public Polymarket-v1 archive sample confirms resolved trade data for the 2025 Bahrain winner market and pre-race last-trade prices for 13 candidate outcomes, but the archive has no book or quote history. Historical F1-market coverage across seasons remains under audit. F1 and weather samples plus one historical Polymarket trade sample are available; the official Polymarket APIs and executable quote data are not connected. No certificate checks were disabled.

## First market audit

The read-only collector uses Python 3.10+ and only the standard library:

```bash
python scripts/audit_polymarket_f1_markets.py
```

It writes a local JSON inventory under `data/metadata/` with event/market metadata, outcome and token IDs, and heuristic classification hints for manual review. Generated data are git-ignored by default. This metadata inventory is not a quote history, executable price, or backtest. Its API request currently fails in this environment because of the TLS issue above.

## Reproducibility and data policy

- All timestamps will be stored in UTC; raw observations will be separated from derived features.
- API requests, retrieval times, schema versions, transformations, exclusions, and experiment configurations will be documented.
- Credentials and unlicensed or restricted raw data will not be committed. The repository will contain code, docs, permitted metadata, and derived outputs only where redistribution is allowed.
- Code and results are for research and education. No live trading is planned.

## Project status and roadmap

- [x] Create public repository and record the initial research design.
- [x] Add the first read-only market-universe audit collector.
- [x] Document the source-to-field map and planned Python analysis stack.
- [x] Check sample availability for F1 historical data, results, and archived weather.
- [x] Confirm one resolved 2025 F1 winner-market sample through the public Polymarket-v1 archive.
- [ ] Complete the archive-wide F1 market and cutoff-price coverage audit; restore valid Polymarket API access for prospective quote and order-book capture.
- [ ] Build a source inventory and point-in-time data model.
- [ ] Implement transparent market and F1 baselines.
- [ ] Add calibrated race simulation and walk-forward evaluation.
- [ ] Capture public quotes prospectively for paper-trading analysis.
- [ ] Publish a results report, including negative or inconclusive findings.

Research decisions and milestones are tracked in [docs/experiment-log.md](docs/experiment-log.md).
