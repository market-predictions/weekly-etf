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
WP34: closed as Stage-2 promotion review decision artifact design verified, design-only
WP35: closed as Stage-2 promotion review decision artifact schema verified, schema-only

## Active package

WP36: implemented; pending external verification

## Latest WP36 files

fixtures/stage2_promotion_review_decision/README.md
fixtures/stage2_promotion_review_decision/manifest.json
tools/validate_stage2_promotion_review_decision_fixtures.py
tests/test_stage2_promotion_review_decision_fixtures.py
.github/workflows/validate-stage2-promotion-review-decision-fixtures.yml

## Verification commands

```bash
pytest tests/test_stage2_promotion_review_decision_fixtures.py
python tools/validate_stage2_promotion_review_decision_fixtures.py
python tools/validate_stage2_promotion_review_decision_schema.py
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

Verify WP36 in Codespaces or CI. If verification passes, close WP36.

Next candidate after clean closeout:

WP37 — Stage-2 promotion review decision artifact validator hardening
