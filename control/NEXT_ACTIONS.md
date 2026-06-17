# ETF Review OS — Next Actions

## Current production baseline

baseline: 260616
run_id: 20260616_211726
requested_close_date: 2026-06-16
workflow_status: workflow_success
workflow_conclusion: success

Delivery evidence remains delivery-layer evidence only and is not an inbox receipt.

## Closed packages

WP16: closed
WP17: closed
WP18: closed
WP19: closed
WP20: closed
WP21: closed
WP22: closed
WP23: closed
WP24: closed
WP25: closed
WP26: closed
WP27: closed
WP28: closed as macro/thesis leakage firewall verified
WP29: closed as bilingual macro/thesis alias source verified, preparation-only
WP30: closed as Stage-2 bridge design verified, design-only
WP31: closed as Stage-2 review schema verified, schema-only
WP32: closed as Stage-2 review checklist verified, checklist-only
WP33: closed as Stage-2 review fixture set verified, fixture-only

## Active package

WP34: implemented; pending external verification

## Latest WP34 files

control/STAGE2_PROMOTION_REVIEW_DECISION_ARTIFACT_DESIGN.md
tools/validate_stage2_promotion_review_decision_artifact_design.py
tests/test_stage2_promotion_review_decision_artifact_design.py
.github/workflows/validate-stage2-promotion-review-decision-artifact-design.yml

## Verification commands

```bash
pytest tests/test_stage2_promotion_review_decision_artifact_design.py
python tools/validate_stage2_promotion_review_decision_artifact_design.py
python tools/validate_stage2_promotion_review_fixtures.py
python tools/validate_stage2_promotion_review_checklist.py
python tools/validate_stage2_promotion_review_schema.py
python tools/validate_stage2_promotion_bridge_design.py
python tools/validate_etf_macro_thesis_surface_leakage.py --output-dir output
python tools/validate_macro_thesis_bilingual_aliases.py
python tools/validate_macro_report_surface.py
git diff --check
```

## Recommended next action

Verify WP34 in Codespaces or CI. If verification passes, close WP34.

Next candidate after clean closeout:

WP35 — Stage-2 promotion review decision artifact schema
