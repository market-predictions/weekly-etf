# Handover — Weekly ETF delivery recovery

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Package: `WP_FRESH_WEEKLY_ETF_SEND_RECOVERY`
Status: closed_delivered

## Delivered production package

```text
run_id: 20260717_154351
requested_close_date: 2026-07-16
report_token: 260716
English report: output/weekly_analysis_pro_260716_02.md
Dutch report: output/weekly_analysis_pro_nl_260716_02.md
workflow_status: workflow_success
pricing_lineage_status: passed
```

## Official portfolio authority

```text
nav_eur: 107117.94
cash_eur: 2534.36
whole_share_status: compliant
position_count: 9
rotation: XLU -> PAVE
XLU shares: 14
PAVE shares: 107
```

The initial production attempt persisted the rotation before failing in the post-render/pre-send layer. Recovery did not run the portfolio model again.

## Root causes and fixes

### Residual internal terminology

Generic `discipline gates` / `disciplinepoorten` language survived phrase-specific cleanup.

Fixed in PR #89:

```text
merge: 68e8587ff6032c8cf3fe1c30019fb513cf57058f
```

### Dutch validator false positive

The Dutch validator found `confidence` in CSS/class identifiers even though the visible client label was `vertrouwen`.

Fixed in PR #90 by validating Dutch forbidden tokens on visible rendered text:

```text
merge: de2464fc81cc1579437ffaad4a62f4add279d6f5
validation run: 29596023922
validation job: 87936494610
```

Visible English still fails the contract.

## Delivery evidence

```text
delivery manifest: output/delivery/weekly_etf_delivery_manifest_2026-07-16_20260717_154351.json
run manifest: output/run_manifests/weekly_etf_run_manifest_2026-07-16_20260717_154351.json
delivery evidence commit: ddc745fddf0e80a31c4309658743f6435a4d486b
persistent evidence: control/evidence/WEEKLY_ETF_DELIVERY_RECOVERY_EVIDENCE_20260717.json
```

Transport result:

```text
smtp_sendmail_returned_no_exception
English attachments: 4
Dutch attachments: 4
```

Inbox confirmation:

```text
English subject: Weekly ETF Pro Review 2026-07-16
English received: 2026-07-17T09:28:00-07:00
Dutch subject: Weekly ETF Pro Review | Nederlands 2026-07-16
Dutch received: 2026-07-17T09:28:02-07:00
```

Both messages were present in Gmail Inbox with the expected `_02` attachment set.

## Stable operating rule

For future late-stage failures after execution persistence:

1. preserve official execution authority;
2. hash protected state and ledger files;
3. rebuild and validate the exact package;
4. do not repeat pricing, discovery or execution;
5. fail closed if a prior receipt exists;
6. finalize manifests only after SMTP success;
7. confirm inbox receipt independently.

## Open issue / next package

The official state has nine positions while the report constraint states a maximum of eight. The 14-share `XLU` residual caused the count to remain nine after adding `PAVE`.

Next package:

```text
WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION
```

Do not silently close `XLU` or change the maximum in documentation. First define whether all non-zero positions count or whether sub-threshold residual positions receive an explicit temporary exception.
