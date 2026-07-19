# Work Package — WP_WEEKLY_ETF_FIX_VERIFICATION_DELIVERY

Date: 2026-07-19
Repository: `market-predictions/weekly-etf`
Status: claimed / validation in progress

## Objective

Deliver the already persisted bilingual Weekly ETF package for run `20260719_002755` so the corrected cockpit trade-weight lineage can be judged in the actual received email and PDF.

## Source package

```text
requested_close_date: 2026-07-17
run_id: 20260719_002755
English report: output/weekly_analysis_pro_260717_04.md
Dutch report: output/weekly_analysis_pro_nl_260717_04.md
runtime state: output/runtime/etf_report_state_20260717_20260719_002755.json
pricing audit: output/pricing/price_audit_2026-07-17_20260719_002755.json
```

## Required cockpit contract

```text
PAVE 0.0% → 4.9%
XLU 5.5% → 0.5%
```

## Fail-closed controls

1. Delivery must stop if any prior delivery receipt exists for the source run.
2. Portfolio and broker execution remain unauthorized.
3. The guarded wrapper must return `no_trade_intents` with authorization status `not_authorized`.
4. Official portfolio state, trade ledger and valuation history must remain byte-identical through prepare, send and finalize.
5. Both English and Dutch delivery HTML must contain exactly one cockpit front page and the corrected weight line.
6. Pricing lineage, whole-share, client-surface, macro-leakage, delivery-HTML and PDF visual gates must pass before SMTP.
7. Delivery success requires bilingual send manifests, a delivery summary and an updated run manifest.

## Implementation

```text
tools/recover_weekly_etf_fix_verification_20260719.py
.github/workflows/validate-weekly-etf-fix-verification-delivery.yml
.github/workflows/deliver-weekly-etf-fix-verification-20260719.yml
```

## Authority boundary

```text
repeat_portfolio_execution: false
broker_execution_authorized: false
portfolio_state_mutation: forbidden
trade_ledger_mutation: forbidden
valuation_history_mutation: forbidden
email_delivery: separately authorized by the user's current request
```
