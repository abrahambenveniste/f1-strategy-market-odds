# Polymarket MCP evaluation

**Reviewed:** 21 October 2026  
**Decision:** Do not add a Polymarket MCP server as a project dependency. Use direct, documented Python clients for the reproducible research pipeline.

An MCP server is an AI-tool interface around APIs; it does not itself provide the historical dataset, remove the need to audit source coverage, or repair a TLS certificate error. The project can continue with the independent Polymarket-v1 archive for retrospective trade-price and resolution-label research. It still lacks historical order-book snapshots, so prospective quote/depth capture requires a valid connection to an official endpoint or a verified data provider.

## Candidate 1: `fernandezpablo85/polymarket-mcp`

- The server exposes three read-only tools: trending topics, markets by topic, and text search.
- It returns current market titles, volumes, outcomes, and probabilities. It does not provide historical prices, trade prints, or order-book history needed for our backtest.
- Its market-by-topic function calls Gamma; its search function calls Polymarket's website search endpoint. The implementation uses ordinary HTTPS clients and does not disable certificate validation, so it is not a workaround for the current certificate-name error.
- Its README says Python 3.8+, while `pyproject.toml` requires Python 3.13 or newer, so installation guidance is inconsistent.

Sources: [repository](https://github.com/fernandezpablo85/polymarket-mcp), [tool definitions](https://github.com/fernandezpablo85/polymarket-mcp/blob/main/main.py), [API calls](https://github.com/fernandezpablo85/polymarket-mcp/blob/main/polymarket.py), [declared Python version](https://github.com/fernandezpablo85/polymarket-mcp/blob/main/pyproject.toml).

## Candidate 2: `caiovicentino/polymarket-mcp-server`

- The README describes 45 tools spanning market discovery and analysis, real-time updates, portfolio functions, and order placement/management.
- Its market-analysis interface advertises historical OHLC prices, but the inspected implementation currently returns a placeholder saying historical prices are unavailable through the public Polymarket API. It therefore does not supply the historical time series this project needs.
- It calls the same official Gamma/CLOB APIs that are failing TLS validation here. Its source uses normal HTTPS clients and contains no certificate-verification bypass; adding this wrapper is not expected to fix the error.
- The project contains order-entry, cancellation, and wallet-authentication code. Its own committed security audit documents safety-limit and read-only-mode enforcement concerns; this project needs none of those capabilities. Do not provide it wallet credentials or rely on a demo-mode setting as an execution safeguard.

Sources: [repository and tool overview](https://github.com/caiovicentino/polymarket-mcp-server), [installation/mode documentation](https://github.com/caiovicentino/polymarket-mcp-server#quick-start), [historical-price implementation](https://github.com/caiovicentino/polymarket-mcp-server/blob/main/src/polymarket_mcp/tools/market_analysis.py#L390-L434), [security audit](https://github.com/caiovicentino/polymarket-mcp-server/blob/main/docs/security-audit-T-0045.md). The source tree was reviewed at commit `21f65f319ff0fc4250ea1e5094581761906839e1` (20 Sep 2026).

## Project decision

1. Keep the ingestion, normalization, and model inputs in this repository's Python code. This makes request URLs, parameters, timestamps, retries, schemas, and failures explicit and reproducible.
2. Use the Polymarket-v1 archive for historical trade-price/probability benchmarks and resolution labels, with the archive's CC-BY-4.0 attribution and the documented limitation that trades are not executable quotes.
3. Restore a normally validated TLS connection to Gamma/CLOB, or verify a provider's specific F1 coverage and cost, before collecting prospective market quotes or depth.
4. Reconsider an MCP only if an AI assistant interface becomes a project deliverable. If so, expose a narrow read-only tool set and keep trading/wallet functions out of scope.

**No MCP server was installed or run for this evaluation. No wallet, API secret, or trading credential was requested or used. Certificate verification remains enabled.**
