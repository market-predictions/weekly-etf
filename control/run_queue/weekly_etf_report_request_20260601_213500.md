# Weekly ETF report request — post-execution pricing-lineage authority rerun

## Purpose

Trigger the production Weekly ETF report workflow from the repo-native run queue after fixing the pricing-lineage validator authority split.

The previous run failed at the pre-send pricing-lineage/client-surface gate:

```text
Section 15 PPA Market value (EUR)=10898.88, runtime previous_market_value_eur=16413.24
```

Root cause:

```text
runtime state = pre-execution pricing/report-state provenance
official portfolio state = post-execution active holdings after guarded execution
client report Section 15 = post-execution active official state
```

The validator was comparing the post-execution report table against the pre-execution runtime position value.

## Validation focus

This run should prove:

- pricing-lineage validation still keeps runtime state as audit/provenance input;
- report Section 7 / Section 15 validate against post-execution official portfolio state when `last_model_execution.run_id` matches the manifest run id;
- active holdings after execution reconcile to `output/etf_portfolio_state.json`;
- pricing audit rows still prove price provenance for all active holdings;
- guarded model execution validation still passes;
- Dutch HTML/PDF render still passes;
- Dutch chart labels remain localized;
- final run manifest records the true workflow result.

## Follow-up verification targets

After completion, verify:

```text
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json
output/etf_portfolio_state.json
output/weekly_analysis_pro_<token>.md
output/weekly_analysis_pro_nl_<token>.md
output/weekly_analysis_pro_nl_<token>.pdf
```

Do not claim email delivery success unless a delivery receipt/manifest exists or the user confirms receipt.
