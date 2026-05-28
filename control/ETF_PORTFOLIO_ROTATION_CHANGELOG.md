# ETF Portfolio Rotation Engine — Changelog

**Repository:** `market-predictions/weekly-etf`  
**Authority:** `control/ETF_PORTFOLIO_ROTATION_CONTRACT_V1.md`

---

## 2026-05-28 — Contract, roadmap and skeleton start

Created central build authority and roadmap:

- `control/ETF_PORTFOLIO_ROTATION_CONTRACT_V1.md`
- `control/ETF_PORTFOLIO_ROTATION_ROADMAP.md`

Created initial implementation skeleton:

- `runtime/portfolio_rotation_engine.py`
- `tools/validate_etf_rotation_output_contract.py`
- `tools/validate_etf_rotation_discipline.py`

Design decisions:

- no ticker-specific rotation rules;
- every incumbent position must re-earn capital generically;
- rotation plan becomes a machine-readable artifact under `output/runtime/`;
- `trade_intents[]` will become the canonical upstream source for trade-ledger writes;
- validators start warning/non-blocking before becoming delivery gates.

---

## 2026-05-28 — Runtime-state integration start

Planned next change:

- `runtime/build_etf_report_state.py` accepts optional `--rotation-plan`;
- runtime state includes `rotation_plan`, `target_weights`, `trade_intents`, and `rotation_decisions` when supplied;
- absence of a rotation plan is warning/non-blocking during v1 buildout.
