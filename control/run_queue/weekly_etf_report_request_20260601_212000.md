# Weekly ETF report request — dynamic pricing-basis disclosure rerun

## Purpose

Trigger the production Weekly ETF report workflow from the repo-native run queue after fixing the pricing-basis disclosure validator.

The previous run failed at:

```text
Validate ETF pricing basis disclosure
missing pricing row for GLD
```

Root cause:

```text
The validator used a stale hardcoded required ticker set that still included GLD.
GLD was no longer a current active holding after guarded execution.
Section 15 correctly listed active holdings only, and the pricing disclosure correctly covered those active ETF holdings.
```

## Validation focus

This run should prove:

- pricing-basis disclosure required tickers are derived dynamically from Section 15 current holdings;
- fully exited historical tickers are not required in the current active-holdings pricing table;
- all active holdings still require visible pricing rows;
- guarded model execution validation still passes;
- Dutch HTML/PDF render still passes;
- Dutch localized chart labels remain in place;
- pricing-lineage validation still passes.

## Follow-up verification targets

After completion, verify:

```text
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json
output/weekly_analysis_pro_<token>.md
output/weekly_analysis_pro_nl_<token>.md
output/weekly_analysis_pro_nl_<token>.pdf
```

Do not claim email delivery success unless a delivery receipt/manifest exists or the user confirms receipt.
