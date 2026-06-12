# Weekly ETF fresh report request

## Request

Generate a fresh Weekly ETF Pro report from the current production workflow.

## Requested by

User request in ChatGPT Project session.

## Requested at

```text
2026-06-12
```

## Scope

```text
repository: market-predictions/weekly-etf
workflow: Send weekly ETF Pro report
mode: production workflow
```

## Requested close-date policy

Use the workflow's built-in requested-close resolver.

The workflow resolves `REQUESTED_CLOSE_DATE` from `pricing.run_pricing_pass.requested_close_from_now(datetime.now(timezone.utc))`, so the run should use the latest completed U.S. market close according to the production workflow logic.

## Required boundaries

```text
pricing_lineage_required=true
run_manifest_required=true
delivery_manifest_required=true
bilingual_report_required=true
no_deterministic_macro_promotion=true
replacement_edge_notes_diagnostic_only=true
historical_output_mutation=false
```

## Notes

This request is a workflow trigger only. Successful report generation, delivery, and artifact persistence must be verified from the resulting GitHub Actions run plus run/delivery manifests.
