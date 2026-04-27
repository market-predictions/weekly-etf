# ETF optimization lab

This document describes the first **lab-only ETF optimization integration** in `weekly-etf`.

## Purpose

The goal is to add a separate portfolio-optimization layer without changing the existing production ETF review flow.

This layer is intentionally:
- non-destructive
- manual to run
- separate from `send_report.py`
- separate from the client-facing Weekly ETF Review markdown
- separate from subscriber email delivery
- explicitly **not** a production allocation engine

## First iteration scope

The first pass uses **PyPortfolioOpt** as the optimization engine.

It currently evaluates:
- max Sharpe allocation
- minimum-volatility allocation
- hierarchical risk parity allocation
- optional Black-Litterman max-Sharpe allocation when absolute views are provided in the lab input

## Price-source path

The optimization workflow can now **auto-populate a longer ETF price history with yfinance** before running the optimizer.

That fetch layer is still lab-only.
It does not change production ETF pricing authority.

The current auto-fetch flow is:
1. read `lab_inputs/etf_optimizer_fetch_config.json`
2. fetch the configured ETF daily history with `yfinance`
3. write the fetched history into `lab_inputs/etf_optimizer_prices.csv`
4. run the optimizer on that freshly populated file

## Why explicit lab inputs are still kept

ETF does not yet have a fully explicit production implementation-state layer equivalent to FX.

So this optimization lab still uses an explicit lab input contract instead of silently inventing state authority from incomplete production artifacts.

The difference now is that the main lab price file can be **generated automatically** from the fetch config instead of being populated by hand each time.

That keeps the lab honest and reversible while reducing friction.

## Input files

The workflow now uses these files in `lab_inputs/`:
- `etf_optimizer_fetch_config.json` — active fetch configuration for yfinance history
- `etf_optimizer_prices.csv` — generated or manually supplied ETF price history
- `etf_optimizer_constraints.json` — optional
- `etf_optimizer_views.json` — optional

Templates are provided as:
- `etf_optimizer_prices_template.csv`
- `etf_optimizer_constraints_template.json`
- `etf_optimizer_views_template.json`

## Output files

Artifacts are generated into:
- `lab_outputs/optimization/`

The workflow currently produces:
- `etf_optimizer_cleaned_prices.csv`
- `etf_optimizer_strategy_results.csv`
- `etf_optimizer_weights.csv`
- `etf_optimizer_summary.json`
- `etf_optimizer_summary.md`
- `etf_optimizer_manifest.json`

## Interpretation rules

- Treat this as a **research and QA layer**, not as automatic ETF allocation advice.
- The results are only as good as the supplied input universe, fetched history, and constraints.
- A high-Sharpe optimized portfolio does **not** automatically deserve production promotion.
- Compare optimizer output against the ETF decision framework and breadth discipline, not instead of them.

## Safety rules

- Do not wire this into the production client email workflow.
- Do not replace the production ETF decision framework with the top optimization output.
- Do not promote an optimizer weight vector into production without explicit review.
- Do not treat the lab input universe as if it were the full ETF opportunity set.
- Do not treat yfinance-fetched lab history as the same thing as a production pricing-pass authority layer.

## Next likely extension

If this first PyPortfolioOpt layer proves useful, the next candidate extension is a **Riskfolio-Lib comparison layer** for richer risk-measure and constrained-allocation research.
