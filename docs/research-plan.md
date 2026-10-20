# Research plan

**Protocol status:** Draft, version 0.1, 20 October 2026. The protocol will be revised in this file and changes recorded in the experiment log before results are inspected.

## 1. Question and hypotheses

**Question:** Can public F1 data available at a defined pre-event cutoff improve race-winner probability forecasts relative to Polymarket's contemporaneous prices, and can any forecast improvement translate to positive hypothetical returns after execution costs?

- **H1 — predictive information:** adding F1 performance and race-context features reduces out-of-sample proper scoring loss versus the market benchmark.
- **H2 — economic value:** trades triggered only by a pre-specified forecast-versus-executable-price edge have positive paper-trading returns after conservative fees, spread, slippage, and fill assumptions.
- **Null / useful result:** the market benchmark is as good or better, or apparent model edge disappears after costs. This is a valid research outcome.

H1 and H2 are separate claims. A better probability forecast does not automatically imply a tradable edge.

## 2. Market universe and outcome

The initial target is **Polymarket F1 Grand Prix race-winner markets**. The market audit will establish, before modeling:

- Which seasons and races have markets and retrievable historical prices.
- Whether all race entrants have a corresponding outcome contract; any missing outcomes and market structure.
- Contract text, resolution source, event close time, result mapping, market/token IDs, and price-history granularity.
- Whether prices represent last trades or executable quotes, and what liquidity/volume information is available.

Include only contracts whose resolution rules map unambiguously to the official race winner. Log all exclusions and their reasons. If historical market coverage is too sparse or prices are too coarse for a credible backtest, report that limitation and use a prospective quote-collection period; do not fill the gap with invented historical prices.

The modeling unit is a race event and the outcome is the winning driver. Where a complete field is listed, benchmark the market as a categorical distribution; document how prices are normalized and handle incomplete fields explicitly.

## 3. Information cutoffs

Evaluate two forecast horizons, if the audited market data support them:

1. **Pre-qualifying:** immediately before qualifying starts. Only practice, historical, and other information genuinely available by this cutoff may be used.
2. **Pre-race:** five minutes before scheduled race start. Qualifying, grid, practice, and available race-weekend information may be used.

For every feature, record its source timestamp and earliest public availability. Use the last market observation at or before the cutoff; do not interpolate from a later quote. Record quote age and reject stale prices under an exclusion threshold fixed during the coverage audit.

For weather, use archived forecast runs published by the cutoff. Reanalysis and observed race weather may be used to describe conditions or for a separate hindsight analysis, but never as a predictive feature.

## 4. Data and feature groups

Candidate groups, subject to data-quality checks:

- **Historical prior:** driver and constructor performance, recent form, circuit and season context.
- **Qualifying:** grid position and relative lap/sector pace.
- **Practice pace:** representative long-run pace, lap consistency, stint length, tire compound and age. Exclude pit, out, yellow-flag, Safety Car, deleted, and otherwise non-representative laps using documented rules.
- **Race context:** weather forecasts, circuit characteristics, expected tire strategy and pit-loss context.
- **Race scenarios:** pace uncertainty, pit strategies, retirements, Safety Car / Virtual Safety Car, and weather transitions in a Monte Carlo simulator.

Feature definitions, missingness, filters, and transformations will be versioned. The model will not use post-cutoff events such as actual pit calls, realized weather, race control messages, or race results.

## 5. Models and baselines

1. **Market baseline:** contemporaneous Polymarket prices, with the market snapshot and any probability normalization fully recorded.
2. **Simple F1 baseline:** historical driver / constructor strength and grid position.
3. **Pace model:** a regularized or hierarchical estimate of driver and team pace with qualifying and practice information.
4. **Race simulator:** sample race outcomes from calibrated pace and explicitly modeled strategic/incident scenarios. Report assumptions and scenario sensitivity.

Prefer interpretable baselines before more complex methods. Add feature groups one at a time and keep them only if they improve chronological out-of-sample performance. Hyperparameter selection must use training data only.

## 6. Validation and metrics

Use chronological walk-forward evaluation by **race**, never random row splits. All drivers and contracts for one race stay in the same fold. Use earlier events to fit/tune and later events to evaluate; report season boundaries and sample sizes. Avoid mixing adjacent observations from the same race across splits.

Forecast metrics:

- Multiclass Brier score and log loss where the outcome field is complete.
- Per-driver binary Brier/log loss and reliability plots as supporting diagnostics.
- Calibration by probability bucket and by forecast horizon.
- Coverage, missingness, and market quote staleness.
- Event-level bootstrap intervals to show uncertainty; do not treat each driver's contract as an independent race.

Economic simulation, reported separately:

- Compare model probability with the available **buy-side executable price** for a hypothetical purchase.
- Include published fees where applicable, spread, slippage, liquidity/depth limits, and conservative fill assumptions.
- Show number of signals, turnover, average edge, net P&L, ROI, maximum drawdown, and uncertainty.
- Use pre-specified thresholds and sizing rules; include sensitivity to threshold and costs.
- Historical chart / last-trade prices are not executable. Until quote/depth data are collected, any price-based return calculation is labeled indicative, not a backtest.

No live orders or financial transactions are part of this project.

## 7. Robustness and failure checks

- Compare model probabilities with market probabilities at identical cutoffs.
- Ablate each data group and compare with simple baselines.
- Test event/season splits and major regulation-era changes.
- Re-run at more conservative quote staleness, spread, slippage, and fill assumptions.
- Preserve a final event window untouched until the analysis pipeline is fixed.
- Publish failures, data gaps, and negative results alongside positive ones.

## 8. Decision gates

1. **Coverage gate:** enough resolvable events, entrant coverage, timestamped price history, and market snapshots to support the proposed evaluation. Define numerical inclusion thresholds after inspecting the source coverage, then record them here before model comparison.
2. **Forecast gate:** a feature group shows repeatable out-of-sample improvement with calibration and uncertainty reported.
3. **Tradability gate:** any simulated edge remains positive under conservative executable-price and cost assumptions. Passing this gate is not a guarantee of future performance.

If a gate fails, narrow the claim, collect prospective data, or conclude that available data do not support the hypothesis.

## 9. Reproducibility

Each dataset and run should record:

- Source URL/API and version or endpoint, request parameters, retrieval time (UTC), event time, schema, and license / terms notes.
- Raw-to-clean transformation, feature definitions, exclusions, and feature availability cutoff.
- Code revision, environment lock, configuration, random seed, fold boundaries, and output hashes.
- Separate raw, cleaned, feature, and result layers; exclude caches, credentials, and restricted raw data from Git.

Detailed source notes live in [data-sources.md](data-sources.md).