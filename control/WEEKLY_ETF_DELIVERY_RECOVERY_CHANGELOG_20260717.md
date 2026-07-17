# Weekly ETF Delivery Recovery Changelog — 2026-07-17

Repository: `market-predictions/weekly-etf`
Run: `20260717_154351`

## Initial production result

- fresh pricing and runtime state generated for close date `2026-07-16`;
- whole-share guarded execution persisted `XLU -> PAVE`;
- `XLU` reduced by 134 shares to 14 shares;
- `PAVE` added at 107 shares;
- report Markdown, HTML, PDF and chart assets generated;
- workflow stopped before SMTP delivery;
- no delivery manifest and no new inbox message existed at that point.

## Repair 1 — client-language residual

PR #89, merge `68e8587ff6032c8cf3fe1c30019fb513cf57058f`:

- normalized generic `discipline gates` to `decision conditions`;
- normalized `disciplinepoorten` to `beslisvoorwaarden`;
- added bilingual delivery-language regression coverage;
- proved state, ledger and valuation authority remained unchanged.

## Repair 2 — visible-text Dutch validation

PR #90, merge `de2464fc81cc1579437ffaad4a62f4add279d6f5`:

- identified `confidence` as a CSS/class identifier rather than visible English;
- added visible-text Dutch delivery validation;
- retained failure behavior for visible `confidence` text;
- added a fail-closed `prepare` / SMTP / `finalize` recovery workflow;
- blocked repeat delivery when prior sendreceipt artifacts exist;
- reused the persisted execution and did not rerun pricing, discovery or portfolio mutation.

Validation:

```text
run: 29596023922
job: 87936494610
result: success
whole_share_execution: passed
trade_ledger_idempotency: passed
pricing_lineage: passed
client_language: passed
macro_thesis_leakage: passed
pdf_visual: passed
EN cockpit front pages: 1
NL cockpit front pages: 1
protected authority hashes: unchanged
```

## Delivery result

```text
delivery evidence commit: ddc745fddf0e80a31c4309658743f6435a4d486b
delivery manifest: output/delivery/weekly_etf_delivery_manifest_2026-07-16_20260717_154351.json
run manifest: output/run_manifests/weekly_etf_run_manifest_2026-07-16_20260717_154351.json
workflow_status: workflow_success
workflow_conclusion: success
smtp_status: smtp_sendmail_returned_no_exception
```

Gmail receipt:

- English message present in Inbox at `2026-07-17T09:28:00-07:00` with four `_02` attachments;
- Dutch message present in Inbox at `2026-07-17T09:28:02-07:00` with four `_02` attachments.

## Final authority

```text
nav_eur: 107117.94
cash_eur: 2534.36
position_count: 9
whole_share_status: compliant
second_portfolio_mutation: false
```

## Follow-up

The official nine-position state conflicts with the report constraint `Max number of positions: 8`. This is assigned to `WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION`; no holding is changed by this changelog or closeout.
