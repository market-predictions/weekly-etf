# Handover — Cockpit Email HTML Inline-Style Fix

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Package: `WP_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX`
Status: implementation complete / validation green / merge pending
Pull request: #98

## Current issue

The uploaded screenshot demonstrated a real channel-specific production defect: the cockpit front page was correctly designed in the PDF, but appeared as largely unstyled text in the email HTML body. The classic report behind it retained its design.

The historical PDF on page 1 is the visual reference for the intended cockpit information hierarchy. The package does not rewrite or resend that historical delivery.

## Root cause

The cockpit front page used class-based markup and a separate `<style>` block injected into `<head>`. The PDF renderer and browsers retained that CSS. The receiving mail client did not reliably retain or apply it.

Because essential cockpit nodes had almost no inline presentation, stylesheet loss reduced the cockpit to a text stream. The existing gate did not test this failure mode.

## Decision framework

The output channel now controls presentation mechanics while current-state facts remain shared:

1. email HTML uses presentation tables and inline styles;
2. PDF/browser keeps the existing class-based premium cockpit;
3. English and Dutch use the same current-state values;
4. selectors required by current production validators remain intact;
5. the classic report body remains the evidence layer behind the cockpit.

## Input/state contract

No authority changed. Rendering continues to derive from:

```text
output/etf_portfolio_state.json
output/etf_valuation_history.csv
output/runtime/latest_etf_report_state_path.txt
output/macro/latest.json
output/pricing/latest_price_audit_path.txt
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
```

## Output contract

### Email

The email cockpit now has:

- fifteen required inline-styled components;
- eight `role="presentation"` tables;
- no required head stylesheet;
- no essential grid, flexbox, pseudo-element or SVG dependency;
- one cockpit front page;
- retained exact-current NAV selector compatibility;
- retained classic report body.

A degradation test removes every `<style>` element from the full generated HTML and then repeats the structural checks.

### PDF/browser

The existing renderer remains authoritative:

- class-based stylesheet preserved;
- `@media print` rules preserved;
- SVG sparkline preserved;
- PDF cockpit structure unchanged.

## Exact implementation files

```text
runtime/cockpit_email_safe_surface.py
runtime/additive_cockpit_front_page.py
tests/test_cockpit_email_html_inline_style.py
tools/validate_cockpit_email_html_inline_style.py
.github/workflows/validate-cockpit-email-html-inline-style.yml
control/evidence/COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX_EVIDENCE_20260718.json
control/decisions/COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX_DECISION_20260718.md
```

## Validation

```text
validated_head: 72841c3bbedfea19122269f2f7c78168676955cb
email_inline_run: 29640677887 success
email_inline_job: 88070568127
wp10_run: 29640677890 success
current_runtime_run: 29640677892 success
wp08_run: 29640677898 success
wp11_run: 29640677882 success
artifact_id: 8428508030
artifact_digest: sha256:df5c3daae4e82b386bdc868aaeb53d8be00cdeb4da1a6f87decd9b62037e8a34
```

Measured EN and NL results:

```text
front_page_count: 1
inline_selector_count: 15
presentation_table_count: 8
head_style_dependency: false
style_strip_degradation_test: passed
classic_body_preserved: true
PDF_class_based_stylesheet_preserved: true
PDF_print_rules_preserved: true
PDF_svg_sparkline_preserved: true
```

## Validation history

The first implementation attempt contained a Python f-string syntax error and stopped at compilation. It was corrected before functional validation or authority mutation.

The dedicated email gate subsequently passed. WP11 then exposed one compatibility selector gap: the email NAV caption contained the correct value but lacked `.etf-cockpit-chart-caption`. That class was restored without changing content or appearance. The final same-head suite passed all five gates.

## Authority boundary

```text
portfolio_state_changed: false
trade_ledger_changed: false
valuation_history_changed: false
pricing_pointer_changed: false
historical_report_changed: false
production_report_generated: false
email_sent: false
```

## Next action

After merge, future production-generated email HTML will use the inline/table cockpit. A real mail-client receipt can only be proven by a separately authorized fresh report delivery. Do not resend or rewrite the historical `260716_02` package as part of this fix.
