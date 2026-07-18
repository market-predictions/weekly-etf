# Work Package — WP_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Status: implementation_complete / validation_green / merge_pending

## Current issue

The cockpit front page rendered correctly in the PDF, but the HTML body received by the mail client showed the cockpit as largely unstyled text while the classic report body remained designed.

## Root cause

The cockpit was injected with a separate class-based `<style>` block in `<head>`, while the cockpit markup itself contained almost no inline presentation. Browsers and the PDF renderer honored that stylesheet; a mail client could remove or ignore it.

The earlier production gate checked cockpit count, current-state metrics, classic-body preservation and PDF page count, but did not remove all head styles to test email degradation.

## Decision framework

The implementation preserves the same current-state information hierarchy while separating delivery mechanics:

1. email uses inline styles and presentation tables;
2. PDF/browser retains the existing class-based premium renderer;
3. existing class names and markers remain available for validators;
4. essential email structure does not rely on grid, flexbox, pseudo-elements, SVG or head CSS;
5. English and Dutch values and source/control disclosures remain aligned;
6. the complete classic report remains behind the cockpit.

## Input/state contract

Authoritative inputs remain unchanged:

```text
output/etf_portfolio_state.json
output/etf_valuation_history.csv
output/runtime/latest_etf_report_state_path.txt
output/macro/latest.json
output/pricing/latest_price_audit_path.txt
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
```

The package reads current state for deterministic rendering and does not modify portfolio, ledger, valuation, pricing, runtime pointers, historical reports or delivery manifests.

## Output contract

For `render_mode=email`:

- exactly one cockpit front page precedes the classic report;
- fifteen essential cockpit components carry inline styling;
- cards, metrics, confidence and evidence sections use eight presentation tables;
- all `<style>` elements can be removed without collapsing the cockpit into plain text;
- no essential CSS grid, flexbox or SVG dependency remains;
- English and Dutch client wording remains present;
- the existing exact-current metric selectors remain compatible;
- the classic report body remains present.

For PDF/browser rendering:

- the existing class-based cockpit remains active;
- the existing print stylesheet remains active;
- the SVG sparkline remains active;
- the current PDF front-page structure remains unchanged.

## Operational implementation

```text
runtime/cockpit_email_safe_surface.py
runtime/additive_cockpit_front_page.py
tests/test_cockpit_email_html_inline_style.py
tools/validate_cockpit_email_html_inline_style.py
.github/workflows/validate-cockpit-email-html-inline-style.yml
```

The new validator explicitly removes every `<style>` element from generated EN/NL email HTML and then verifies inline presentation, table structure, front-page count and classic-body preservation.

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
EN_style_strip_test: passed
NL_style_strip_test: passed
protected_authority_hashes: identical
```

## Authority boundary

```text
portfolio_state_changed: false
trade_ledger_changed: false
valuation_history_changed: false
pricing_authority_changed: false
historical_report_changed: false
production_report_generated: false
email_sent: false
```

The historical `260716_02` email and files remain immutable. The correction applies to future generated email HTML after merge.

## Acceptance status

- work package and claim recorded before implementation: complete;
- root cause documented: complete;
- email cockpit survives removal of all head styles: complete;
- PDF cockpit route preserved: complete;
- English and Dutch focused tests: complete;
- classic report body preserved: complete;
- exact-current WP11 compatibility: complete;
- protected authority hashes unchanged: complete;
- PR merge: pending;
- claim release and final handover closeout: pending merge;
- email sent: false.
