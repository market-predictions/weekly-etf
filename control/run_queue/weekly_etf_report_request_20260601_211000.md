# Weekly ETF report request — exited-position validation rerun

## Purpose

Trigger the production Weekly ETF report workflow from the repo-native run queue after fixing the guarded execution-state validator.

The previous run passed the Dutch HTML/PDF newline validation issue and failed later at guarded model execution validation:

```text
artifact_guarded_auto:position_missing_from_official_state:GLD
```

Root cause:

```text
GLD was sold down to zero and therefore removed from the active official portfolio state.
The execution artifact retained a zero-share GLD row for auditability.
The validator incorrectly treated that as a missing active position.
```

## Validation focus

This run should prove:

- fully exited zero-share positions are allowed to be absent from active official portfolio state;
- non-zero missing artifact positions are still blocked;
- guarded model execution validation passes after a full sell-down;
- Dutch HTML/PDF render still passes;
- Dutch chart labels remain localized:
  - Portefeuillecurve (EUR)
  - Portefeuillewaarde (EUR)
  - Datum
- pricing-lineage validation still passes;
- delivery manifest/receipt remains separate from workflow success.

## Follow-up verification targets

After completion, verify:

```text
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json
output/runtime/latest_etf_model_execution_path.txt
output/etf_portfolio_state.json
output/weekly_analysis_pro_nl_<token>.pdf
```

Do not claim email delivery success unless a delivery receipt/manifest exists or the user confirms receipt.
