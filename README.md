# F1 Strategy Simulator vs. Market Odds

A reproducible research project asking whether public F1 performance and race-context data can improve race-winner probabilities beyond Polymarket prices—and whether any measured difference survives executable prices and trading frictions.

> **Status:** Project setup and research design. No model results, paper-trading results, or evidence of profitability have been produced. The work will be evaluated honestly, including the possibility that the market is already efficient or that no usable edge exists.

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

- [FastF1](https://docs.fastf1.dev/): F1 timing, laps, telemetry, tires, weather, race-control messages, and session results.
- [Jolpica-F1](https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md): historical schedules and results through an Ergast-compatible API.
- [Open-Meteo Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api): archived forecast runs for point-in-time weather features. The [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) provides reanalysis and is not a substitute for a forecast that was actually available at the time.
- [Polymarket Gamma API](https://gamma-api.polymarket.com/docs), [CLOB price history and order-book data](https://docs.polymarket.com/), and [Data API](https://data-api.polymarket.com/v2/docs): market discovery, metadata, historical prices, and public market/trade data.

See [docs/data-sources.md](docs/data-sources.md) for the source register and [docs/research-plan.md](docs/research-plan.md) for the detailed protocol.

## Reproducibility and data policy

- All timestamps will be stored in UTC; raw observations will be separated from derived features.
- API requests, retrieval times, schema versions, transformations, exclusions, and experiment configurations will be documented.
- Credentials and unlicensed or restricted raw data will not be committed. The repository will contain code, metadata, small permitted samples, and derived outputs only where redistribution is allowed.
- Code and results are for research and education. No live trading is planned.

## Project status and roadmap

- [x] Create public repository and record the initial research design.
- [ ] Audit F1 market availability, contract resolution rules, and historical quote coverage.
- [ ] Build a source inventory and point-in-time data model.
- [ ] Implement transparent market and F1 baselines.
- [ ] Add calibrated race simulation and walk-forward evaluation.
- [ ] Capture live public quotes prospectively for paper-trading analysis.
- [ ] Publish a results report, including negative or inconclusive findings.

Research decisions and milestones are tracked in [docs/experiment-log.md](docs/experiment-log.md).