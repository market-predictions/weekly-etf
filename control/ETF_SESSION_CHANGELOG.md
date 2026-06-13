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

## 2026-06-13 — WP18 macro audit foundation closed and WP19 queued

### Current issue

WP18 had been implemented but still needed conclusive workflow evidence before it could be closed. The dedicated macro-audit foundation workflow passed, but the related macro-regime shadow workflow initially failed in its evidence commit step because GitHub Actions runs rewrote the same `latest_*.json` files and collided during push/rebase.

### Root cause / architectural tension

The macro audit foundation is an input/provenance layer and must remain shadow-only. At the same time, the validation stack needs committed evidence under `output/macro/validation/`. Repeated workflow runs update stable pointer files such as `latest_macro_regime_shadow_validation.json`, so the evidence commit runbook must be robust to remote-ahead races and `latest_*.json` conflicts.

### What changed

Updated:

```text
control/MACRO_AUDIT_FOUNDATION_STATUS.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_SESSION_CHANGELOG.md
.github/workflows/validate-macro-regime-shadow.yml
```

Implementation / closeout details:

```text
- WP18 status moved from implemented/pending evidence to closed/verified/shadow-only.
- Macro audit foundation validation evidence is committed and passed.
- Macro-regime shadow validation evidence is committed and passed after run #40.
- The macro-regime shadow evidence commit step now commits from a freshly synced origin/main working tree and retries pushes.
- WP19 is now the active next package.
```

### Validation evidence

Dedicated WP18 macro-audit foundation evidence:

```text
artifact: output/macro/validation/latest_wp18_macro_audit_foundation_validation.json
workflow: Validate ETF macro audit foundation
workflow_run_id: 27476145040
workflow_run_number: 6
status: passed
```

Related macro-regime shadow compatibility evidence:

```text
artifact: output/macro/validation/latest_macro_regime_shadow_validation.json
workflow: Validate ETF macro regime shadow
workflow_run_id: 27478580626
workflow_run_number: 40
status: passed
validated_markers:
  ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
  ETF_MACRO_DATA_AUDIT_VALID_OK
  ETF_MACRO_AUDIT_AXIS_SHADOW_OK
  ETF_MACRO_REGIME_SHADOW_OK
```

### Authority boundary preserved

```text
shadow_only=true
client_facing_authority=false
decision_impact=none_phase2_audit_only
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
historical_output_mutation=false
```

### Remaining work

Proceed to:

```text
WP19 — Deterministic regime engine fixture baseline
```

WP19 must remain fixture-only and shadow-only. It may validate deterministic regime classification fixtures, but it must not promote deterministic macro, change report wording, alter scoring/fundability, mutate portfolio state, or rewrite historical outputs.

---

## 2026-06-13 — WP18 macro audit foundation implemented, pending workflow evidence

### Current issue

The roadmap’s Phase 2 macro audit foundation existed in partial form, but the status still said fresh workflow validation was missing. The macro audit validator was also too permissive for a production-grade provenance contract, and the fixture replay path was mixed with broader macro-regime shadow validation rather than having a clean WP18-only evidence path.

### Root cause / architectural tension

Macro audit values are intended to become the future authoritative macro input layer, but they are not yet decision authority. This requires two things at the same time:

```text
- stronger provenance/audit validation
- strict isolation from client-facing reports, lane scoring, fundability, and portfolio action
```

The production macro policy pack may build a live macro audit in shadow mode, but WP18 needed a deterministic fixture replay path that writes only validation evidence and does not overwrite `output/macro/latest.json` or production report artifacts.

### What changed

Added:

```text
tools/replay_macro_audit_foundation_fixture.py
tests/test_wp18_macro_data_audit_validator.py
tests/test_wp18_macro_audit_foundation_fixture.py
.github/workflows/validate-macro-audit-foundation.yml
```

Updated:

```text
tools/validate_macro_data_audit.py
control/MACRO_AUDIT_FOUNDATION_STATUS.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_SESSION_CHANGELOG.md
```

Implementation details:

```text
- hardened macro audit validation for required_source_groups, source_group_status, report_token, run_id, summary counts, staleness summary, authority fields, and live source_url provenance
- added a WP18 fixture replay tool that builds a macro audit from tests/fixtures/macro_data_audit_fixture.json
- fixture replay writes shadow-only evidence under output/macro/validation/
- added an isolated GitHub Actions workflow: Validate ETF macro audit foundation
- workflow runs unit tests and fixture replay, then commits only output/macro/validation/*.json evidence
- fixture replay does not change production reports, portfolio state, lane scoring, fundability, or output/macro/latest.json
```

Expected workflow markers:

```text
ETF_MACRO_DATA_AUDIT_VALID_OK
ETF_MACRO_AUDIT_FOUNDATION_FIXTURE_OK
```

Expected latest evidence path after a green workflow run:

```text
output/macro/validation/latest_wp18_macro_audit_foundation_validation.json
```

### Authority boundary preserved

```text
shadow_only=true
client_facing_authority=false
decision_impact=none_phase2_audit_only
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
deterministic_macro_promotion=false
historical_output_mutation=false
```

### Remaining work

Superseded by the closeout entry above. WP18 is now closed and WP19 is the next active package.

---

## 2026-06-13 — WP17 PDF visual QA and delivery-runbook hardening closed

### Current issue

WP16 showed that text validators and HTML/Markdown checks could pass while rendered PDFs still had client-visible defects, especially Dutch equity-curve rendering and Dutch ETF/product-name corruption.

### Root cause / architectural tension

The workflow had strong state, pricing, report-content, and delivery-HTML validation, but did not render committed PDFs into images before send. That meant a defect could exist only in the PDF visual layer and still pass text-level gates.

### What changed

Added:

```text
tools/validate_etf_pdf_visual_contract.py
tools/validate_etf_manifest_evidence.py
tests/test_wp17_pdf_visual_contract.py
```

Updated:

```text
.github/workflows/send-weekly-report.yml
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/ETF_SESSION_CHANGELOG.md
```

Implementation details:

```text
- installed poppler-utils in the production workflow
- added PDF visual validation after HTML/PDF render and before send
- PDF visual validation renders EN/NL PDFs to images and checks visible equity-curve pixels
- Dutch PDF validation also fails on product-name corruption such as iAantal aandelen
- added manifest evidence validation after final run-manifest write
- manifest evidence validation checks workflow success, pricing lineage, EN/NL report paths, EN/NL PDF attachments, delivery status, and the inbox-receipt caveat
```

### Validation / production evidence

Latest verified manifest-linked baseline after WP17:

```text
requested_close_date: 2026-06-12
run_id: 20260613_113054
report_token: 260612
english_report_path: output/weekly_analysis_pro_260612_08.md
dutch_report_path: output/weekly_analysis_pro_nl_260612_08.md
pricing_lineage_status: passed
workflow_status: workflow_success
delivery_status: smtp_sendmail_returned_no_exception
total_portfolio_value_eur: 108243.33
cash_eur: 1936.52
```

Green workflow evidence:

```text
#246 Request WP17 visual manifest gate rerun — green
#247 Send weekly ETF Pro report — green
```

Because the workflow now runs the PDF visual contract before send and the manifest evidence validator after final manifest write, the green #247 run verifies the WP17 gates on the latest manifest-linked baseline.

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

Return to roadmap proper through WP18. WP18 must remain shadow/audit-only unless separately promoted.

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

WP17 closed the immediate PDF visual QA gap. Return to the macro/thesis roadmap proper via WP18.

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
