# Work Package — WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Layer: decision framework + output contract + operational runbook
Status: active

## Current issue

WP10 implemented and validated an additive English/Dutch cockpit front page, but the real production workflow still leaves `MRKT_RPRTS_COCKPIT_FRONT_PAGE` unset and therefore defaults to `disabled`.

The official portfolio state was subsequently reconciled to whole shares. WP11 must therefore validate enablement against the current whole-share-compliant authority rather than against stale pre-reconciliation holdings.

## Decision

Select option B:

```text
enable the cockpit front page in the real production workflow
```

The only intended production behavior change is:

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE: enabled
```

Rollback remains:

```text
MRKT_RPRTS_COCKPIT_FRONT_PAGE: disabled
```

## Required validation

1. Build a temporary exact-current runtime overlay from:
   - latest persisted runtime context;
   - current `output/etf_portfolio_state.json` positions, cash and NAV.
2. Render fresh EN/NL report markdown in a temporary worktree only.
3. Generate disabled and enabled HTML/PDF bundles without email.
4. Prove exactly one enabled front page per language.
5. Prove one added PDF page per language.
6. Prove the classic body remains present and the smaller decision cockpit is not duplicated.
7. Prove front-page NAV, cash, position count and largest position match current official state.
8. Prove all official positions remain whole shares.
9. Prove protected portfolio, ledger, pricing, valuation and pointer files are byte-identical before and after validation.
10. Persist machine-readable validation evidence.

## Safety boundary

```text
production_send: false
portfolio_model_execution: false
official_state_mutation: false
official_trade_ledger_mutation: false
pricing_authority_change: false
report_history_rewrite: false
attachment_count_change: false
manifest_contract_change: false
```

## Exact files

```text
.github/workflows/send-weekly-report.yml
tools/validate_cockpit_wp11_production_enablement.py
.github/workflows/validate-cockpit-wp11-production-enablement.yml
tests/test_cockpit_wp11_production_enablement.py
control/evidence/COCKPIT_WP11_PRODUCTION_ENABLEMENT_EVIDENCE_20260717.json
```

## Acceptance criteria

```text
production_workflow_feature_value: enabled
exact_current_whole_share_overlay: passed
front_page_count_EN: 1
front_page_count_NL: 1
PDF_page_delta_EN: +1
PDF_page_delta_NL: +1
classic_report_body: preserved
small_decision_cockpit_duplicate: false
protected_authority_hashes: identical
email_sent: false
rollback_value: disabled
status: production_enabled_no_send
```
