# ETF optimization lab inputs

These files are used only by the **lab-only ETF optimization workflow**.

They do **not** drive the production Weekly ETF Review.

## Required active input
Before running the optimization workflow, create:
- `lab_inputs/etf_optimizer_prices.csv`

The easiest way is:
1. copy `lab_inputs/etf_optimizer_prices_template.csv`
2. save it as `lab_inputs/etf_optimizer_prices.csv`
3. replace the sample prices with real ETF price history

## Optional inputs
You may also create:
- `lab_inputs/etf_optimizer_constraints.json`
- `lab_inputs/etf_optimizer_views.json`

If these files do not exist, the lab uses defaults.

## Price CSV format
Use a wide table:

| date | ETF1 | ETF2 | ETF3 |
|---|---:|---:|---:|
| 2026-01-02 | ... | ... | ... |
| 2026-01-03 | ... | ... | ... |

Rules:
- first column must be `date`
- all other columns must be ETF tickers
- values must be prices, not returns
- keep one row per date
- use chronological order
- at least 20 observations
- at least 2 ETFs

## Constraints JSON format
See `etf_optimizer_constraints_template.json`.

Supported first-pass keys:
- `default_min_weight`
- `default_max_weight`
- `exclude_tickers`
- `per_ticker_bounds`

## Views JSON format
See `etf_optimizer_views_template.json`.

Supported first-pass keys:
- `absolute_views`
- `prior_returns`

This is only used for the optional Black-Litterman lab run.
