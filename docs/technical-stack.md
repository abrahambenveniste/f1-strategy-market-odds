# Technical stack

**Status:** Selected implementation plan, 20 October 2026. The first collector is already implemented with Python's standard library; the analysis dependencies below are planned and will be pinned after the market-coverage audit establishes the smallest useful stack.

## Language and environment

- **Python 3.11+** for ingestion, cleaning, feature construction, probabilistic models, simulation, and reporting.
- **SQL** through DuckDB for transparent joins, event-level dataset checks, and compact analytical queries.
- **uv** for virtual environments, dependency management, and a committed lockfile once dependencies are introduced.
- **Git and GitHub** for version history, issue tracking, documentation, and public review.

The initial read-only Polymarket Gamma collector, `scripts/audit_polymarket_f1_markets.py`, currently uses only the Python standard library (`urllib`, `json`, `csv`, `argparse`, and related modules). It runs without installing a third-party package.

## Planned packages

| Package | Planned role |
|---|---|
| [FastF1](https://docs.fastf1.dev/) | Read F1 session timing, laps, telemetry, tire/stint information, weather observations, race-control messages, and results where available. |
| [httpx](https://www.python-httpx.org/) | Make REST requests with explicit timeouts, headers, and retry handling for sources that do not need a specialized client. |
| [pandas](https://pandas.pydata.org/docs/) and [NumPy](https://numpy.org/doc/) | Normalize tabular source data, build features, and perform numerical analysis. |
| [DuckDB](https://duckdb.org/docs/) and [PyArrow](https://arrow.apache.org/docs/python/) | Query local analytical tables and store columnar Parquet data efficiently. |
| [SciPy](https://docs.scipy.org/doc/scipy/) and [scikit-learn](https://scikit-learn.org/stable/user_guide.html) | Statistical baselines, probability calibration, evaluation metrics, and established machine-learning methods. Start with interpretable baselines; add model complexity only when walk-forward results justify it. |
| [Matplotlib](https://matplotlib.org/stable/) and [Seaborn](https://seaborn.pydata.org/) | Create static, reproducible charts for calibration, forecast comparisons, strategy scenarios, and the final report. |
| [JupyterLab](https://jupyterlab.readthedocs.io/) | Optional exploratory workspace. Final results should be reproducible from versioned scripts/configuration rather than depending on notebook state. |
| [Ruff](https://docs.astral.sh/ruff/) | Python formatting and linting. |

No package versions are asserted here. The dependency file and lockfile will record exact versions at the point the analysis environment is created.

## Project workflow

1. Run source collectors from the repository root with explicit arguments and a descriptive user agent where required.
2. Keep source captures, normalized data, features, and results in separate local layers; store timestamps in UTC and record source/retrieval provenance.
3. Query local tabular data with DuckDB; use notebooks only for exploration and figures that can be regenerated from committed code.
4. Track source/schema changes, feature decisions, exclusions, and experiment outcomes in GitHub. Do not commit API credentials, local caches, or raw data unless the source's terms allow redistribution.
5. Publish a concise report with methods, coverage, out-of-sample evaluation, limitations, and negative or inconclusive findings.

## Tooling boundaries

The project is a read-only data-research and paper-analysis workflow. It will use public market data and model hypothetical execution costs; it will not connect a wallet, submit orders, or run a live trading bot.
