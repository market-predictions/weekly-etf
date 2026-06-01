# Weekly ETF report request — Dutch HTML newline validator rerun

## Purpose

Trigger the production Weekly ETF report workflow from the repo-native run queue after fixing the Dutch HTML validation rule that incorrectly rejected normal HTML line breaks.

The previous run failed at:

```text
Validate HTML/PDF render before send
RuntimeError: Dutch HTML body still contains raw markdown / escaped formatting token:
```

The blank token was a normal newline, not a raw markdown artifact.

## Validation focus

This run should prove:

- HTML/PDF render now passes with normal HTML newlines allowed;
- Dutch chart labels still render as:
  - Portefeuillecurve (EUR)
  - Portefeuillewaarde (EUR)
  - Datum
- Dutch markdown remains native-rendered and guard-only;
- runtime-state labels/comments remain narrowly normalized;
- Dutch language quality validation still passes;
- delivery HTML validation still passes;
- pricing-lineage validation still passes.

## Follow-up verification targets

After completion, verify:

```text
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json
output/weekly_analysis_pro_nl_<token>.pdf
output/weekly_analysis_pro_nl_<token>_equity_curve.png
```

Do not claim email delivery success unless a delivery receipt/manifest exists or the user confirms receipt.
