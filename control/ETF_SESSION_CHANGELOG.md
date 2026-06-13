# ETF Review OS — Session Changelog

This is the broad operating changelog for `market-predictions/weekly-etf` development sessions.

It is intentionally separate from specialized logs:

- `control/ETF_PRICING_LINEAGE_CHANGELOG.md` — pricing-lineage specific implementation/regression history
- `control/DECISION_LOG.md` — stable architecture decisions only
- `control/CURRENT_STATE.md` — current state snapshot
- `control/NEXT_ACTIONS.md` — roadmap / active backlog

## Rules

- Record every meaningful architecture, workflow, control-file, validator, runtime, delivery, roadmap, and handover-relevant change.
- Include the current issue, root cause, what changed, affected files, validation evidence, and remaining work.
- Keep entries specific enough that a fresh chat can continue without relying on hidden memory.
- Do not use this file for ordinary report-content edits unless they affect workflow, state, validation, delivery, or roadmap direction.
- Specialized changes may be summarized here and tracked in more detail in their dedicated changelog.

---

## 2026-06-13 — WP16 closeout after macro recency, client-surface, render, no-trade, and product-name repairs

### Current issue

The `260611` and early `260612` report series exposed multiple premium-client-surface defects after the macro-event recency repair: stale/missing ECB policy context, English/Dutch language leakage, visible comment residue, Dutch equity-curve PDF rendering failures, no-trade execution validation mismatches, and Dutch product-name localization corruption.

### Root cause / architectural tension

The report workflow had strong text/state/pricing contracts, but several output-layer defects sat between render, localization, PDF embedding, and delivery validation:

```text
- macro event recency was not fully reflected in the client-safe macro surface
- Dutch localization could apply broad token replacement inside protected ETF/product names
- PDF visual defects were not caught by text validators
- no-trade execution artifacts were valid runtime states but not accepted by validators in both shadow and guarded-auto modes
```

### What changed

Implemented and verified the WP16 repair cycle and follow-ups. Key files changed during the cycle included:

```text
runtime/wp16_followup3_cleanup.py
runtime/client_facing_sanitizer.py
runtime/equity_curve_png_contract.py
runtime/equity_curve_svg_contract.py
send_report.py
send_report_runtime_html.py
tools/validate_etf_client_surface_clean.py
tools/validate_etf_model_execution.py
tools/validate_etf_execution_state_authority.py
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_SESSION_CHANGELOG.md
control/DECISION_LOG.md
```

Key resolved defects:

```text
ECB tightening event surfaced in EN/NL macro narrative.
ECB stance now reads Tightening / inflation-sensitive and Verkrappend / inflatiegevoelig.
Non-U.S. / IEFA wording reconciled with live IEFA exposure.
English n.v.t. residue removed.
Dutch empty-comment residue removed.
Soft-cap / soft-target duplicated wording normalized.
Dutch equity curve now renders visibly in PDF.
Shadow and guarded-auto no-trade execution artifacts are valid when no trade intents exist and no state/ledger writes are claimed.
Dutch product-name corruption repaired; iShares is protected against Shares -> Aantal aandelen localization.
```

### Validation / production evidence

Latest verified manifest-linked baseline:

```text
requested_close_date: 2026-06-12
run_id: 20260613_094305
report_token: 260612
english_report_path: output/weekly_analysis_pro_260612_06.md
dutch_report_path: output/weekly_analysis_pro_nl_260612_06.md
pricing_lineage_status: passed
workflow_status: workflow_success
delivery_status: smtp_sendmail_returned_no_exception
total_portfolio_value_eur: 108243.33
cash_eur: 1936.52
```

Uploaded `260612_06` PDF QA confirmed:

```text
English equity curve visible.
Dutch equity curve visible.
Dutch continuity table shows GSG product name as iShares S&P GSCI Commodity-Indexed Trust.
No iAantal aandelen corruption observed.
```

### Authority boundary preserved

```text
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
deterministic_macro_promotion=false
historical_output_mutation=false
```

### Remaining work

Recommended next package:

```text
WP17 — PDF visual QA and delivery-runbook hardening
```

Reason: WP16 showed that text validators alone are not enough for premium report delivery. Add deterministic visual/render checks and clearer manifest evidence before resuming larger macro/thesis roadmap work.

---

## 2026-06-10 — WP11A-FIX replacement-edge diagnostic notes wired into report surface

### Current issue

WP11A had created a safe helper and tests for replacement-edge diagnostic notes, but the helper was not yet wired into the English/Dutch report output path.

### Root cause / architectural tension

WP5 replacement-edge scoring is useful diagnostic evidence, but it must not become implicit allocation, lane-scoring, fundability, recommendation, execution, or portfolio-mutation authority. The safest integration point was the report polish layer after the main runtime renderer has already produced the report text.

### What changed

Updated:

```text
runtime/replacement_edge_report_notes.py
runtime/polish_runtime_reports.py
tests/test_replacement_edge_report_notes.py
tools/validate_etf_report_content_contract.py
control/REPLACEMENT_EDGE_REPORT_NOTES_STATUS.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_SESSION_CHANGELOG.md
handover/workpackages/20260610_0000_wp11a_fix_replacement_edge_render_integration.md
```

Implementation details:

- Expanded the replacement-edge note disclaimer to explicitly deny:
  - allocation authority
  - fundability authority
  - lane-scoring authority
  - production recommendation authority
  - execution authority
  - portfolio mutation authority
- Injected the diagnostic notes into English and Dutch polished report text below the final Replacement Duel / Vervangingsanalyse section.
- Added focused tests for English helper output, Dutch helper output, empty fallback output, English polish insertion, Dutch polish insertion, and non-promoted authority fields.
- Extended the English report content validator to require the replacement-edge diagnostic marker and authority disclaimer.

### Marker

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
```

### Authority boundary preserved

```text
diagnostic_only=true
portfolio_action_authority=false
fundability_authority=false
lane_scoring_authority=false
funding_authority=false
production_recommendation_authority=false
execution_authority=false
portfolio_mutation=false
```

No pricing, lane scoring, fundability, target-weight, trade-intent, execution, or portfolio-state mutation logic was changed.

### Commits

```text
11c9a00a57204fb226f077b52c18377d6f7fa04a — Clarify replacement-edge diagnostic authority boundary
4ee42122aca1ceaccf7ba9a5eda3506ef637f3c4 — Wire replacement-edge diagnostic notes into runtime polish
3ca18c9adee77c148291a2b1cfbaa6513c0735c1 — Test replacement-edge notes render integration
d6b8cee7a5b4eb99d536a0bae199bd639edd3459 — Validate replacement-edge diagnostic report notes
1c2a0763d37c6d6f947789567e79569260f973ca — Close WP11A-FIX replacement-edge report notes status
cda383a13e3a0395e46a87bad564250ed44422b6 — Record WP11A-FIX replacement-edge render status
78e32202e1d01ae0340b4f3c1e54d804fce5a131 — Update next actions after WP11A-FIX wiring
```

### Validation status

Not executed in this chat environment.

Required focused validation:

```bash
python -m pytest tests/test_replacement_edge_report_notes.py -q
```

A fresh report/content-validation pass should also confirm that `tools/validate_etf_report_content_contract.py` passes against a newly polished English report containing the marker and diagnostic disclaimer.

### Remaining work

- Run focused pytest.
- Run or trigger a fresh report/content-validation pass.
- Record CI/fresh-run evidence after validation.

---

## Open watch items

### Delivery evidence

Workflow success is not the same as email delivery proof. The current manifest has delivery-manifest evidence for the latest recorded baseline, but inbox receipt remains not proven unless separately confirmed.

### Price verification

Rows may still show `fresh_exact_unverified`. Cross-provider verification could later upgrade rows to `fresh_exact_close` where independent sources agree.

### Dutch alias consolidation

Dutch labels and validator aliases are working but still distributed across several files. Consolidation remains a useful cleanup.

### Replacement-edge diagnostic notes validation

WP11A-FIX is wired into the report surface, but focused pytest and fresh report/content validation evidence still need to be recorded.
