# Weekly ETF report request — native Dutch guard-only production validation

## Purpose

Trigger the production Weekly ETF report workflow from the repo-native run queue to validate the full report flow after correcting the Dutch architecture:

```text
runtime state / key figures
→ English native render
→ Dutch native render from the same runtime state
→ guard-only Dutch validation for native reports
```

This rerun specifically validates that the Dutch report is not mutated by broad English-to-Dutch translation/scrub rules.

## Validation focus

The run should prove:

- the full production report flow still passes;
- the Dutch report is generated from `render_nl_native(state)` / runtime state;
- native Dutch localization is guard-only;
- native Dutch scrub is guard-only;
- the Dutch report does not contain the previous malformed `Neeg` wording;
- macro/thesis leakage guards still pass;
- delivery HTML validation and pricing-lineage validation still pass.

## Authority boundary

This request does not promote Stage-1, Stage-2, deterministic regime, or macro/thesis artifacts into client-facing authority.

It is a production pipeline validation run only.

## Follow-up verification targets

After the workflow completes, verify:

```text
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json
output/weekly_analysis_pro_<token>*.md
output/weekly_analysis_pro_nl_<token>*.md
output/weekly_analysis_pro_*_delivery.html
```

Confirm in the Dutch output:

```text
Nog geen alternatief is sterk genoeg om direct te financieren.
```

and confirm this malformed phrase is absent:

```text
Neeg geen alternatief
```

Do not claim email delivery success unless a delivery receipt/manifest exists or the user confirms receipt.
