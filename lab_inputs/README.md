# ETF optimization lab inputs

These files are used only by the **lab-only ETF optimization workflow**.

They do **not** drive the production Weekly ETF Review.

## Auto-fetch path

The optimization workflow can now fetch ETF history automatically with **yfinance** before running the optimizer.

The active fetch config is:
- `lab_inputs/etf_optimizer_fetch_config.json`

The workflow uses that config to populate:
- `lab_inputs/etf_optimizer_prices.csv`

So in normal use, you usually only need to review or edit the fetch config rather than hand-build the prices CSV each time.

## Manual override path

You may still manually maintain:
- `lab_inputs/etf_optimizer_prices.csv`

But the current lab workflow overwrites that file in the runner workspace using the fetch config before optimization.

## Optional inputs
You may also create:
- `lab_inputs/etf_optimizer_constraints.json`
- `lab_inputs/etf_optimizer_views.json`

If these files do not exist, the lab uses defaults.

## Fetch config format

Example structure:

```json
{
  "tickers": ["SPY", "SMH", "PPA", "PAVE", "URNM", "GLD"],
  "period": "1y",
  "interval": "1d",
  "auto_adjust": false,
  "prefer_adjusted_close": true,
  "threads": true
}
```

Supported first-pass keys:
- `tickers`
- `period`
- `start_date`
- `end_date`
- `interval`
- `auto_adjust`
- `prefer_adjusted_close`
- `threads`

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
- at least 7 observations for the current starter optimizer setup
- at least 2 ETFs
- longer daily history is strongly preferred over short report-derived snapshots

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
