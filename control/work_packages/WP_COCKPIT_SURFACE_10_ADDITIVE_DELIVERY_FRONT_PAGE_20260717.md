# Work Package — WP_COCKPIT_SURFACE_10_ADDITIVE_DELIVERY_FRONT_PAGE

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Branch: `feature/cockpit-wp10-additive-delivery-front-page`
PR: #83

## Layer

```text
output contract
operational runbook
```

## Status

```text
status: validated_ready_for_enablement_decision
validated_code_head: b2ca4b032793f23f13b0d4557a919623366dc501
final_validation_run: 29541727393
visual_artifact_run: 29542004498
production_enablement: false
promotion_status: not_promoted
email_send: false
next_package: WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT
```

## Purpose

Implement the selected additive cockpit front page inside the existing English and Dutch delivery HTML/PDF while preserving the complete classic report body and all current delivery semantics.

WP10 implements and validates the path. It does not enable the feature in the production workflow and does not send email.

## Decision framework

```text
client entry surface: one additive cockpit front page
classic report evidence body: preserved intact
small Decision cockpit / Besliscockpit: suppressed only after successful full-front-page injection
production enablement: separate WP11 decision
```

## Input/state contract

The front page renders directly from current runtime authority, never from a committed preview artifact.

```text
runtime state pointer: output/runtime/latest_etf_report_state_path.txt
valuation history: output/etf_valuation_history.csv
macro pack: current runtime-linked macro policy pack
pricing audit pointer: output/pricing/latest_price_audit_path.txt
run manifest pointer: output/run_manifests/latest_weekly_etf_run_manifest_path.txt
```

Authority precedence remains:

```text
current_weight_pct > target_weight_pct > previous_weight_pct > weight_inherited_pct
market_value_eur > previous_market_value_eur
```

## Feature gate

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE=disabled|enabled
```

Rules:

```text
missing value -> disabled
implementation default -> disabled
validation enablement -> explicit enabled
invalid value -> fail closed to unchanged classic output
render/injection failure -> fail closed to unchanged classic output
rollback -> disabled
production enablement -> separate closeout required
```

No implicit truthy or falsey aliases are accepted.

## Output contract

### Disabled

- EN and NL delivery HTML remain byte-identical to the current classic output.
- The existing smaller decision cockpit remains available.
- No front page is added.

### Enabled

- exactly one EN cockpit front page;
- exactly one NL cockpit front page;
- exactly one added PDF page per language;
- complete classic report follows unchanged;
- smaller decision cockpit is not duplicated;
- one HTML body and one PDF remain per language;
- attachment and manifest semantics remain unchanged;
- standalone HTML equity uses the embedded data URI;
- email HTML retains the equity CID contract.

The delivery surface contains no preview-only or promotion-status labels.

## Implementation files

```text
runtime/additive_cockpit_front_page.py
send_report_runtime_html.py
tests/test_cockpit_wp10_additive_delivery_front_page.py
tools/validate_cockpit_wp10_delivery_integration.py
.github/workflows/validate-cockpit-wp10-additive-front-page.yml
control/evidence/COCKPIT_WP10_ADDITIVE_DELIVERY_FRONT_PAGE_EVIDENCE_20260717.json
```

## Acceptance evidence

```text
focused_and_existing_tests: 30 passed
production_delivery_html_contract: passed
macro_thesis_surface_leakage: passed
WP08_review_conclusion: ready_for_promotion_decision
WP08_blocking_findings: []
all_eleven_WP08_dimensions: pass
protected_authority_hashes_before_after: identical
disabled_EN_HTML_byte_identical: true
disabled_NL_HTML_byte_identical: true
enabled_front_page_count_EN: 1
enabled_front_page_count_NL: 1
enabled_front_page_PDF_pages_EN: 1
enabled_front_page_PDF_pages_NL: 1
classic_report_body: preserved
small_decision_cockpit_duplicate: false
standalone_equity_embed: passed
email_equity_CID: passed
email_count_change: false
pdf_count_change: false
attachment_contract_change: false
manifest_contract_change: false
email_sent: false
promotion_status: not_promoted
```

Persistent evidence:

```text
control/evidence/COCKPIT_WP10_ADDITIVE_DELIVERY_FRONT_PAGE_EVIDENCE_20260717.json
```

Visual review of English and Dutch page 1 and the transition to the classic report on page 2 passed without clipping, overlap, broken glyphs or readability defects.

## Safety boundary

```text
production_send: false
production_enablement: false
portfolio_model_execution: false
pricing_authority_change: false
official_state_mutation: false
official_trade_ledger_mutation: false
report_markdown_rewrite: false
```

## Next package

```text
WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT
```

WP11 must decide whether the explicit feature flag is enabled in the real production workflow. No send is authorized by WP10.
