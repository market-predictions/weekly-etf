# ETF Review OS — Current State

## Snapshot date

2026-07-15

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**The July 14 production review is the latest verified production baseline. A guarded URNM-to-XBI rotation was executed and persisted. The first post-execution report surface was corrected through `WP_POST_EXECUTION_REPORT_CONSISTENCY`; corrected English and Dutch `260714_03` reports were rendered, delivered, persisted and confirmed in the inbox. The package is closed.**

## Latest verified production baseline

```text
requested_close_date: 2026-07-14
run_id: 20260715_175910
report_token: 260714
pricing_lineage_status: passed
portfolio_execution_status: executed
portfolio_mutation: URNM -> XBI
```

Authoritative mutation:

```text
URNM: Sell -122.008961 shares; model weight 7.01% -> 2.01%
XBI: Buy +40.491749 shares; model weight 0.00% -> 5.00%
```

Authority sources:

```text
output/runtime/etf_model_execution_20260714_20260715_175910.json
output/runtime/etf_report_state_20260714_20260715_175910_executed.json
output/etf_portfolio_state.json
output/etf_trade_ledger.csv
```

## Latest verified client-delivery baseline

```text
english_report: output/weekly_analysis_pro_260714_03.md
english_pdf: output/weekly_analysis_pro_260714_03.pdf
dutch_report: output/weekly_analysis_pro_nl_260714_03.md
dutch_pdf: output/weekly_analysis_pro_nl_260714_03.pdf
corrected_delivery_run: 29455717158
delivery_layer_status: smtp_sendmail_returned_no_exception
inbox_receipt_status: verified_bilingual
```

The corrected reports consistently show:

```text
URNM: Reduce — executed / Verlagen — uitgevoerd
XBI: Add — executed / Toevoegen — uitgevoerd
```

No stale `no portfolio action` / `geen portefeuilleactie` wording remains.

## Delivery and persistence evidence

```text
implementation_validation_run: 29442287444
implementation_validation_conclusion: success
corrected_delivery_run: 29455717158
recovery_and_persistence_run: 29455966433
recovery_and_persistence_conclusion: success
persistence_commit: d829e89329656b29be4c1d9b3b4aca75ba46f3b4
```

Evidence artifacts:

```text
output/delivery/weekly_etf_correction_delivery_receipt_2026-07-14_29455717158.txt
output/delivery/weekly_etf_correction_manifest_2026-07-14_20260715_223718.json
```

The final correction manifest proves:

```text
model_execution_replayed: false
official_state_mutated: false
official_trade_ledger_mutated: false
state_sha256_before == state_sha256_after
trade_ledger_sha256_before == trade_ledger_sha256_after
```

## Package status

```text
WP_POST_EXECUTION_REPORT_CONSISTENCY: closed
PR #59: merged
corrected EN/NL delivery: complete
corrected EN/NL inbox receipts: verified
```

Previously closed WP16-WP42, report-quality, localization and PDF-surface packages remain closed. Their historical evidence is unchanged.

## Cockpit-first surface roadmap

The cockpit-first roadmap remains a separate preview lane. It has no production pricing, portfolio-action, state-mutation or delivery authority.

```text
roadmap: docs/roadmaps/WEEKLY_ETF_COCKPIT_SURFACE_ROADMAP_20260618.md
preview_output: output/cockpit_preview/
production_promotion: not_granted
```

## Operational debt created during correction closeout

A one-shot dispatch bridge and evidence-recovery runner were introduced to recover a successful delivery after the original correction runbook used obsolete SMTP secret names and expected the wrong manifest format.

These files are useful evidence but should not silently become permanent production architecture without review:

```text
.github/workflows/dispatch-corrected-etf-report-bridge.yml
runtime/run_post_execution_correction_delivery.py
runtime/recover_post_execution_correction_evidence.py
```

## Immediate next action

Create a narrow cleanup work package to consolidate the correction runbook onto the established production SMTP contract, replace the wrong JSON-manifest assumption, retire the one-shot dispatch bridge, and preserve the delivery receipt/recovery evidence. Do not resend `260714_03`.

After that cleanup, return to the explicitly selected ETF roadmap package.
