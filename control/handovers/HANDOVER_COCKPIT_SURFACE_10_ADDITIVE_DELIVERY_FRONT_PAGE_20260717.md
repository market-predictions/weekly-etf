# Handover — WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-wp10-additive-delivery-front-page`
PR: #83
Status: implementation validated / production enablement pending

## Authority

```text
promotion decision PR: #81
promotion decision merge: 3200d2a39afa0027ff9fdc65f7490ed97e54ffc8
promotion closeout PR: #82
promotion closeout merge: 61f9a4b27d5e656d566c5679b237b5b31a8f0a47
selected_option: additive_delivery_front_page
promotion_status: not_promoted
```

## Implemented files

```text
runtime/additive_cockpit_front_page.py
send_report_runtime_html.py
tests/test_cockpit_wp10_additive_delivery_front_page.py
tools/validate_cockpit_wp10_delivery_integration.py
.github/workflows/validate-cockpit-wp10-additive-front-page.yml
control/work_packages/WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE_20260717.md
control/evidence/COCKPIT_WP10_ADDITIVE_DELIVERY_FRONT_PAGE_EVIDENCE_20260717.json
```

## Implemented behavior

- delivery-specific front page renders directly from current runtime inputs;
- feature values are restricted to `disabled|enabled`;
- missing feature value defaults to `disabled`;
- disabled mode preserves the existing classic HTML exactly;
- enabled mode injects exactly one client-facing EN/NL front page;
- enabled PDF adds exactly one page per language;
- the full classic report remains intact after the front page;
- the smaller decision cockpit is suppressed only after successful full-page injection;
- disabled and fallback modes retain the smaller decision cockpit;
- invalid values and planted render failures fail closed;
- diagnostic output uses the `COCKPIT_FRONT_PAGE` status line;
- equity, attachment, manifest, state, pricing and ledger contracts remain intact.

## Exact-current validation

```text
validated_code_head: b2ca4b032793f23f13b0d4557a919623366dc501
final_validation_run: 29541727393
final_validation_status: success
focused_and_existing_tests: 30 passed
visual_artifact_run: 29542004498
visual_artifact_id: 8392637794
visual_artifact_digest: sha256:c18cc4281efae34237aa90f2bcdb28bae4d85e1e73f32e3a76bed71e0b3917b8
feature_default: disabled
front_page_count_EN: 1
front_page_count_NL: 1
front_page_PDF_pages_EN: 1
front_page_PDF_pages_NL: 1
classic_report_body: preserved
small_decision_cockpit_duplicate: false
protected_authority_hashes_before_after: identical
WP08_blocking_findings: []
email_sent: false
promotion_status: not_promoted
```

Persistent evidence:

```text
control/evidence/COCKPIT_WP10_ADDITIVE_DELIVERY_FRONT_PAGE_EVIDENCE_20260717.json
```

## Visual review

English and Dutch page 1 were rendered at 180 DPI. Both passed for:

```text
one-page fit
no clipping
no overlap
no broken glyphs
readability
premium layout
clean transition to the classic report on page 2
```

## What was not changed

```text
production workflow feature enablement
email send
portfolio state
trade ledger
valuation history
pricing authority
model execution
report markdown
attachment count
manifest semantics
```

## Next package

```text
WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT
```

WP11 must decide whether to set `MRKT_RPRTS_COCKPIT_FRONT_PAGE=enabled` in the real production workflow. It must validate before any send and preserve rollback to `disabled`.
