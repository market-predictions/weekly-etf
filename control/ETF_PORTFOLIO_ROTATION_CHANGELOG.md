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

---

## 2026-05-29 — Client-facing rotation wording cleanup started

Implemented first cleanup in `runtime/rotation_render_tables.py`:

- translated internal reason codes to investor-facing language;
- renamed `Reason codes` / `Redencodes` to rationale/toelichting fields;
- translated override reasons away from raw internal labels;
- kept signed deltas in numeric table columns while moving prose toward client-facing wording.

---

## 2026-05-29 — Shadow and guarded model execution bridge

Added the first self-steering model-execution bridge:

- `runtime/model_execution_engine.py`
- `tools/validate_etf_model_execution.py`

The engine now supports:

- `shadow` mode: build proposed ledger rows and shadow post-trade positions without writing official state;
- `guarded_auto` mode: write official model trade-ledger rows and update `output/etf_portfolio_state.json` when all hard policy checks pass.

The execution is model-portfolio execution only. It does not place broker orders.

---

## 2026-05-29 — Post-execution report rebuild added

Issue found from the received PDF: the workflow could execute guarded model rotation after the report was already rendered, leaving the delivered PDF as a pre-execution report.

Added:

- `runtime/finalize_executed_etf_report.py`
- `runtime/build_etf_report_state.py --no-rotation-plan`
- guarded-auto validation now finalizes the report from the executed portfolio state.

New intended run order:

1. build rotation plan from current portfolio;
2. build pre-execution runtime state;
3. execute guarded model rotation if hard policy checks pass;
4. update `output/etf_trade_ledger.csv` and `output/etf_portfolio_state.json`;
5. rebuild runtime state from the executed portfolio state without the old rotation plan;
6. overwrite the current EN/NL report pair from executed holdings;
7. continue delivery validation/render/send from the executed report pair.

Expected visible result after the next successful run:

- Section 15 holdings should show the reduced GLD share count and a new GSG position if GLD→GSG still passes generic rules;
- Section 14 should show executed model changes rather than only proposed trade intents;
- Continuity input should start the next run from the executed holdings;
- trade ledger should contain official Sell/Buy model rows.

---

## 2026-05-30 — Execution-state authority validator added

Issue confirmed from `weekly_analysis_pro_260529_05.pdf`: Section 15 mixed stale pre-execution shares with post-execution market values. GLD showed 29 shares, while the displayed EUR market value implied the post-sale GLD share count. NAV-level validation alone was therefore insufficient.

Added:

- `tools/validate_etf_execution_state_authority.py`
- integration inside `tools/validate_etf_model_execution.py`

The new hard validation checks:

- row-level arithmetic: shares × local price = local market value;
- local market value / FX = EUR market value;
- EUR market value / NAV = displayed weight;
- guarded-auto shadow positions match official `output/etf_portfolio_state.json` after execution;
- executed final report runtime state matches official portfolio-state quantities after `finalize_executed_etf_report.py` runs.

This is intentionally validator-first. It blocks stale scorecard/report-state quantity leakage before PDF/email delivery instead of patching the report surface after the fact.
