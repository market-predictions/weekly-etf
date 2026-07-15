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

---

## 2026-05-30 — Execution validator follow-up after first blocked run

The first run after adding the validator was correctly blocked before delivery. It exposed two follow-up problems:

- model-execution inputs still inherited stale per-run fields such as `shares_delta_this_run`, `weight_change_pct`, `action_executed_this_run`, and `funding_source_note` from previously persisted portfolio state;
- the validator used truthy fallbacks, so a legitimate current weight of `0.00` could fall through to stale legacy `weight_pct`.

Changed:

- `runtime/model_execution_engine.py` now clears stale this-run execution fields before building shadow and guarded positions;
- `tools/validate_etf_execution_state_authority.py` now treats zero values as valid present values and only applies shadow share-delta bridge checks to tickers with a current-run non-zero share delta.

This preserves the useful hard block while removing false positives from prior-run metadata.

---

## 2026-05-30 — Executed report finalization authority overlay

The next guarded-auto run reached `ETF_MODEL_EXECUTION_OK` and wrote the official model portfolio/trade state, but failed after `ETF_EXECUTED_REPORT_FINALIZED`. The failure showed that the final report rebuild had reintroduced stale scorecard quantities into the executed report runtime state, including stale GLD shares and stale market values for several holdings.

Changed:

- `runtime/finalize_executed_etf_report.py` now overlays official `output/etf_portfolio_state.json` fields onto the rebuilt executed runtime state after `build_runtime_state(..., disable_rotation_plan=True)`.

The overlay keeps report commentary enrichment, but makes these execution-critical fields authoritative from official portfolio state:

- shares;
- current/previous prices;
- local and EUR market values;
- current/previous/inherited weights;
- target weight;
- current-run execution fields;
- pricing audit fields.

The finalization step then recalculates cash, invested market value, NAV and row weights from the official positions before rendering EN/NL reports.

---

## 2026-05-30 — Executed report wording and before/after table contract

The received `weekly_analysis_pro_260529_09.pdf` showed that Section 15 holdings were now arithmetically correct, but the delivered report still mixed proposed and executed language. Section 14 also showed non-zero share deltas with equal previous/new weights, which is not client-facing acceptable.

Added:

- `runtime/fix_executed_report_contract.py`

Changed:

- `runtime/finalize_executed_etf_report.py` now stores `executed_model_changes` from the guarded-auto artifact and runs the executed-report contract patcher after all normal post-processors.

The new patcher:

- rewrites post-execution wording away from proposed/pending rotation language;
- rebuilds Section 14 / Dutch Section 14 from `executed_model_changes` using real previous weight, new weight, weight change and share delta values;
- validates that any row with a non-zero share delta cannot show unchanged previous/new weights;
- patches both English and Dutch report markdown before delivery render.

---

## 2026-05-30 — Post-execution delivery HTML copy contract

The received `weekly_analysis_pro_260529_15.pdf` showed that state, valuation history, holdings arithmetic, duplicate-execution prevention and the already-executed table were fixed, but the delivery/PDF layer still surfaced proposed/pending language in the Portfolio Action Snapshot and replacement-funding copy.

Changed:

- `runtime/delivery_html_overrides.py` now treats post-execution and already-executed runtime states as delivery-layer post-execution states;
- `runtime/delivery_html_overrides.py` now prefers the latest finalized post-execution runtime pointer over the earlier pre-execution runtime-state environment variables;
- `runtime/render_etf_report_from_state.py` now avoids active/proposed rotation wording when `execution_context.report_phase == post_execution` or `validation_flags.already_executed_noop == true`;
- `tools/validate_etf_delivery_html_contract.py` now validates the rendered delivery HTML, not only markdown, and blocks post-execution reports if visible HTML still contains proposed/pending execution wording.

Forbidden post-execution delivery phrases now include:

- `Rotation plan artifact is active`;
- `proposed until`;
- `pending execution`;
- `pending portfolio-state persistence`;
- `Proposed rotation`;
- `trade intents are proposed`;
- `not executed trades until`.

Required behavior:

- `executed`: show the model rotation as executed and persisted;
- `already_executed`: show the model rotation as already reflected, with no new state or ledger mutation;
- delivery HTML/PDF must not describe the GLD→GSG rotation as proposed or pending once the official portfolio state already reflects it.

---

## 2026-05-30 — Max-position action cap delivery guard

The received `weekly_analysis_pro_260529_17.pdf` showed that state, valuation history, post-execution wording and GLD/GSG arithmetic were fixed, but SMH was still surfaced as `Add / destination` while its current weight was above the 25% maximum-position constraint.

Added:

- `runtime/max_position_action_contract.py`

Changed:

- `send_report_runtime_html.py` now applies the max-position action sanitizer during delivery HTML/PDF generation;
- `tools/validate_etf_delivery_html_contract.py` now applies and validates the same max-position action contract on rendered delivery HTML;
- `runtime/scrub_etf_client_surface.py` now scrubs over-cap `Add` wording from current markdown/report surfaces before client-surface validation.

Required behavior:

- if a ticker is above the max-position cap, it must not appear in `Add` or `Add / destination` in client-facing report surfaces;
- over-cap leaders such as SMH should be described as `best earned exposure, but no fresh capital is added while above the 25% cap`;
- delivery HTML/PDF validation must fail if an over-cap ticker is still rendered as Add.

---

## 2026-07-15 — Current-run state authority and alternative-candidate correction

The 2026-07-14 production report used fresh pricing and relative-strength discovery, but its rotation plan still consumed stale recommendation-memory valuation fields. It also treated lane alternatives as descriptive metadata rather than independently selectable destinations.

Added:

- `runtime/rotation_state_authority.py`;
- `runtime/portfolio_rotation_engine_v2.py`;
- `tools/validate_etf_rotation_state_authority.py`;
- `tests/test_etf_rotation_state_authority.py`;
- `.github/workflows/validate-etf-rotation-state-authority.yml`.

Changed:

- current-run pricing now determines market value, NAV and weights before rotation;
- P/L is recomputed from current close versus average entry;
- missing average entry is reconstructed from official trade-ledger references and model-execution artifacts or blocks rotation;
- the recommendation scorecard is refreshed before capital-release scoring;
- primary and alternative ETFs are scored independently;
- replacement-only alternatives require a direct 3-month edge of at least 10%;
- capped destination-score ties use direct-duel evidence, live-radar status, primary implementation, structural score, relative strength and liquidity rather than alphabetical order.

Validation:

```text
PR: #58
workflow_run_id: 29438154551
job_id: 87429929415
focused_tests: 10 passed
actual_2026-07-14_replay: passed
validated_holdings: 9
replay_mutation: URNM -> XBI, -5.00% / +5.00%, EUR 5511.24
```

This entry records implementation and replay proof. Official state mutation and client delivery remain dependent on merge and a fresh production report run.

