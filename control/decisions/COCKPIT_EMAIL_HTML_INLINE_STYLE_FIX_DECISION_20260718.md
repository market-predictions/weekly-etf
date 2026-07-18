# Decision — Cockpit Email HTML Inline-Style Fix

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Package: `WP_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX`

## Current issue

The production cockpit front page rendered correctly in browsers and the PDF, but appeared as largely unformatted text in the HTML body received by the mail client. The classic report body remained designed.

## Root cause

The cockpit depended on a separate class-based `<style>` block injected into the HTML `<head>`. Its markup contained almost no inline presentation. The PDF renderer honored the stylesheet, but an email client could remove or ignore the second or complex stylesheet.

The prior production gate proved HTML presence, exact-current metrics, classic-body preservation and PDF page count. It did not simulate removal of all head styles.

## Decision

Use two explicit output implementations derived from the same current state:

1. **Email output** — a table-based cockpit with all essential presentation inline.
2. **PDF/browser output** — the existing class-based premium cockpit with print stylesheet and SVG sparkline.

The email surface may keep class names and audit markers, but essential structure must not depend on CSS grid, flexbox, pseudo-elements, external styles or a `<style>` block.

## Output contract

For English and Dutch email HTML:

- exactly one cockpit front page precedes the classic report;
- essential cockpit nodes contain inline styling;
- cards and metric groups use presentation tables;
- removal of every `<style>` element does not collapse the cockpit into plain text;
- the full classic report body remains present;
- the existing exact-current metric selectors remain available.

For PDF output:

- preserve the existing class-based cockpit;
- preserve print rules;
- preserve the SVG sparkline;
- preserve current one-page front-page behavior.

## Validation decision

A production gate is insufficient unless it deliberately removes all `<style>` elements from the generated email HTML and then verifies:

- the cockpit marker still occurs exactly once;
- fifteen required cockpit components retain inline styling;
- the table-based layout remains present;
- the classic report body remains present;
- English and Dutch client wording remains intact.

## Authority boundary

This decision changes only future email rendering behavior. It does not:

- rewrite the historical `260716_02` delivery package;
- modify portfolio state, ledger, valuation or pricing authority;
- generate a report for delivery;
- send or resend email.
