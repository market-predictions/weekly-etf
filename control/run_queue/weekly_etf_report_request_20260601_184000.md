# Weekly ETF report request — native Dutch label-normalization production validation

## Purpose

Trigger the production Weekly ETF report workflow from the repo-native run queue after the native Dutch label-normalization fix.

This rerun validates the full production path after adding a narrow native runtime-state label alias for:

```text
Non-U.S. developed market diversification → Ontwikkelde markten buiten de VS
```

## Validation focus

The run should prove:

- the full production report flow passes;
- the Dutch report remains native-rendered from runtime state;
- broad English-to-Dutch scrub/translation remains disabled for native Dutch reports;
- narrow runtime-state display-label normalization is sufficient for the previously failing `Non-U.S.` lane label;
- malformed `Neeg` wording remains absent;
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

Confirm the Dutch report contains:

```text
Ontwikkelde markten buiten de VS
Nog geen alternatief is sterk genoeg om direct te financieren.
```

Confirm these malformed/raw fragments are absent:

```text
Non-U.S. developed market diversification
Neeg geen alternatief
```

Do not claim email delivery success unless a delivery receipt/manifest exists or the user confirms receipt.
