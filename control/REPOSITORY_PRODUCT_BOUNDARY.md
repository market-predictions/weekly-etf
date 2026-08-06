# Weekly ETF repository product boundary

This repository produces the Weekly ETF review. Daily or weekly FX predictions, TwelveData currency-pair generators, MT5 ranking packs, DailyTradeBias artifacts and `daily-fx` master prompts are separate products.

The inherited FX workflow, runner and output trees are removed by the current cleanup. `tools/validate_etf_repository_boundary.py` and `.github/workflows/validate-etf-repository-boundary.yml` prevent their reintroduction into active repository surfaces.

Git history remains the provenance archive. Current production code and workflows must remain ETF-specific.
