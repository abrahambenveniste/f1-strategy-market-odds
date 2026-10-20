# Technical stack

**Status:** Updated 20 October 2026 after checking API access. Python is the analysis language; SQL through DuckDB supports local queries. The first Polymarket collector uses Python's standard library, but it could not reach Gamma due to TLS validation. The environment currently runs Python 3.13.15 and does not have FastF1 installed. Planned dependencies will be locked only after data access and coverage are confirmed.

## Language and environment

- **Python 3.11+** for ingestion, cleaning, feature construction, probabilistic models, simulation, and reporting. Python 3.13.15 is available in the current runtime.
- **SQL** through DuckDB for transparent joins, event-level dataset checks, and compact analytical queries.
- **uv** for virtual environments, dependency management, and a committed lockfile once dependencies are introduced.
- **Git and GitHub** for version history, issue tracking, documentation, and public review.

The initial read-only Polymarket Gamma collector, `scripts/audit_polymarket_f1_markets.py`, currently uses only Python's standard library (`urllib`, `json`, `csv`, `argparse`, and related modules). It does not require third-party packages.

## Planned packages and APIs

| Tool/package | Planned role |
|---|---|
| [OpenF1 API](https://openf1.org/docs/) | Primary candidate for historical F1 sessions from 2023 onward, including lap timing, grid/results, stints, pit stops, race-control messages, weather observations, and selected telemetry. Historical access is documented as free and unauthenticated; sample session, lap, and stint queries returned data in the 20 Oct 2026 connectivity check. |
| [FastF1](https://docs.fastf1.dev/) | Optional alternative for F1 timing and telemetry if authenticated F1 TV access is available. The archive now returns 401 to unauthenticated requests; the current project environment does not have FastF1 installed. |
| [httpx](https://www.python-httpx.org/) | REST requests with explicit timeouts, headers, and retry handling for APIs without a specialized client. The current starter collector uses `urllib`; this may remain sufficient if it meets our logging/retry needs. |
| [pandas](https://pandas.pydata.org/docs/) and [NumPy](https://numpy.org/doc/) | Normalize tabular source data, build features, and perform numerical analysis. |
| [DuckDB](https://duckdb.org/docs/) and [PyArrow](https://arrow.apache.org/docs/python/) | Query local analytical tables and store columnar Parquet data efficiently. |
| [SciPy](https://docs.scipy.org/doc/scipy/) and [scikit-learn](https://scikit-learn.org/stable/user_guide.html) | Statistical baselines, probability calibration, evaluation metrics, and established machine-learning methods. Start with interpretable baselines; add model complexity only when walk-forward results justify it. |
| [Matplotlib](https://matplotlib.org/stable/) and [Seaborn](https://seaborn.pydata.org/) | Create static, reproducible charts for calibration, forecast comparisons, strategy scenarios, and the final report. |
| [JupyterLab](https://jupyterlab.readthedocs.io/) | Optional exploratory workspace. Final results should be reproducible from versioned scripts/configuration rather than depending on notebook state. |
| [Ruff](https://docs.astral.sh/ruff/) | Python formatting and linting. |

No package versions are asserted here. The dependency file and lockfile will record exact versions when the analysis environment is created. No third-party packages have been installed as part of the connectivity check.

## Project workflow

1. Run source collectors from the repository root with explicit arguments and a descriptive user agent where required.
2. Keep source captures, normalized data, features, and results in separate local layers; store timestamps in UTC and record source/retrieval provenance.
3. Query local tabular data with DuckDB; use notebooks only for exploration and figures that can be regenerated from committed code.
4. Track source/schema changes, feature decisions, exclusions, and experiment outcomes in GitHub. Do not commit API credentials, local caches, or raw data unless the source's terms allow redistribution.
5. Publish a concise report with methods, coverage, out-of-sample evaluation, limitations, and negative or inconclusive findings.

## Tooling boundaries

The project is a read-only data-research and paper-analysis workflow. It will use public market data and model hypothetical execution costs; it will not connect a wallet, submit orders, or run a live trading bot.
