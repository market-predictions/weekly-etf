# Weekly ETF report request — Dutch PDF chart-label validation

## Purpose

Trigger the production Weekly ETF report workflow from the repo-native run queue after the runtime delivery patch that localizes Dutch equity-curve PNG labels.

This validates the Dutch PDF/chart output after:

```text
send_report_runtime_html.py
```

was updated so Dutch reports use:

```text
Portefeuillecurve (EUR)
Portefeuillewaarde (EUR)
Datum
```

instead of:

```text
Equity Curve (EUR)
Portfolio value (EUR)
Date
```

## Validation focus

The run should prove:

- the full production report flow passes;
- English report chart labels remain English;
- Dutch report chart labels render in Dutch;
- native Dutch markdown remains guard-only and is not broad-translated;
- remaining runtime-state labels/comments are normalized narrowly;
- macro/thesis leakage guards still pass;
- Dutch language quality and delivery HTML validations still pass;
- pricing-lineage validation still passes.

## Follow-up verification targets

After the workflow completes, verify:

```text
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json
output/weekly_analysis_pro_<token>.pdf
output/weekly_analysis_pro_nl_<token>.pdf
output/weekly_analysis_pro_nl_<token>_equity_curve.png
```

Inspect the Dutch PDF/chart output for these Dutch chart labels:

```text
Portefeuillecurve (EUR)
Portefeuillewaarde (EUR)
Datum
```

And confirm these English chart labels are not present in the Dutch chart image/PDF surface:

```text
Equity Curve (EUR)
Portfolio value (EUR)
Date
```

Do not claim email delivery success unless a delivery receipt/manifest exists or the user confirms receipt.
