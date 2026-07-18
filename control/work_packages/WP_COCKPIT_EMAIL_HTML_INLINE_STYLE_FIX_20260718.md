# Work Package — WP_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Status: active / claimed

## Current issue

The cockpit front page renders correctly in the PDF, but the HTML body received by the mail client shows the cockpit as largely unstyled text while the classic report body remains designed.

The delivered HTML currently adds cockpit styling through a separate `<style>` block in `<head>`. The cockpit markup itself contains almost no inline presentation. Email clients may remove or ignore that second or complex stylesheet even though browsers and the PDF renderer honor it.

## Decision framework

Preserve the existing cockpit information hierarchy and PDF appearance while making the email body resilient to removal of all cockpit head CSS.

The fix must:

1. use an email-specific, table-based layout with inline styles;
2. keep the existing class names and front-page marker for auditability;
3. avoid reliance on CSS grid, flexbox, pseudo-elements or head-only styling for essential structure;
4. keep the current browser/PDF cockpit implementation unchanged;
5. preserve English and Dutch content, numbers and source/control disclosures;
6. preserve the complete classic report body behind the cockpit.

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

This package may read current state for deterministic rendering but must not modify portfolio, ledger, valuation, pricing, runtime pointers, historical reports or delivery manifests.

## Output contract

For `render_mode=email`:

- one cockpit front page appears before the classic report;
- essential layout and typography are encoded inline;
- the layout remains readable after all `<style>` elements are removed;
- two-column and three-column structures use presentation tables with mobile-safe fallbacks;
- the front page remains bilingual and client-safe;
- the classic report body remains byte/text equivalent apart from the additive cockpit.

For PDF/browser rendering:

- retain the current class-based premium cockpit and print stylesheet;
- preserve the current one-page cockpit PDF result.

## Operational runbook

Implement and validate:

1. an email-safe inline cockpit renderer in `runtime/additive_cockpit_front_page.py`;
2. focused tests for email/PDF render-mode separation;
3. a stylesheet-removal degradation test;
4. extensions to the WP11 production validator requiring inline email resilience;
5. EN/NL read-only render evidence;
6. compatibility regressions for position-count, report language and cockpit production gates;
7. governance closeout with evidence, decision, claim release and handover.

## Authority boundary

This package must not:

- execute or propose a portfolio transaction;
- change official state, ledger, valuation history or pricing authority;
- rewrite historical delivered reports;
- send or resend email;
- claim that the existing historical email has been corrected retroactively.

## Acceptance criteria

- work package and claim recorded before implementation;
- root cause documented;
- email cockpit remains designed after all head styles are removed;
- PDF cockpit output remains unchanged in structure and page count;
- English and Dutch tests pass;
- classic report body remains preserved;
- no protected authority file changes;
- PR merged;
- claim released;
- handover and control files updated;
- email sent: false.
