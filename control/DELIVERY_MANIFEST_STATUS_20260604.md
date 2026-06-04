# ETF Delivery Manifest Status

Snapshot date: 2026-06-04

## Current issue

Workflow success and pricing-lineage success previously did not prove durable delivery evidence because the run manifest had `delivery_manifest_path: null`.

## Implemented change

Added delivery summary writer:

```text
tools/write_etf_delivery_manifest_summary.py
```

Updated workflow:

```text
.github/workflows/send-weekly-report.yml
```

The workflow now writes a redaction-safe delivery summary after the `Send email` step succeeds and passes that summary path into the final Weekly ETF run manifest.

## Latest confirmed run

```text
workflow: Send weekly ETF Pro report
run_number: 205
trigger_commit: 3bd07f7ff31af77adbd23359d66a8c5ab7ab3343
status: passed
branch: main
observed_at: 2026-06-04
source: user-provided GitHub Actions UI screenshot and repo-visible manifest artifacts
```

## Run identity

```text
run_id: 20260604_190001
requested_close_date: 2026-06-03
report_token: 260603
```

## Delivery manifest evidence

Latest delivery manifest pointer:

```text
output/delivery/latest_weekly_etf_delivery_manifest_path.txt
```

points to:

```text
output/delivery/weekly_etf_delivery_manifest_2026-06-03_20260604_190001.json
```

The delivery summary records:

```text
artifact_type: weekly_etf_delivery_manifest_summary
delivery_status: smtp_sendmail_returned_no_exception
language_count: 2
recipient_data_policy: redacted_hash_only
english_pdf: weekly_analysis_pro_260603.pdf
dutch_pdf: weekly_analysis_pro_nl_260603.pdf
```

Important boundary:

```text
This is SMTP send evidence, not an end-recipient inbox receipt.
```

## Final run manifest linkage

Latest run manifest pointer:

```text
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
```

points to:

```text
output/run_manifests/weekly_etf_run_manifest_2026-06-03_20260604_190001.json
```

The final run manifest now records:

```text
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-03_20260604_190001.json
pricing_lineage_status: passed
workflow_status: workflow_success
workflow_conclusion: success
```

## Work-package status

Delivery manifest evidence: closed for this stage.

This closes the previous `delivery_manifest_path: null` production-evidence gap.

## Remaining boundary

Do not claim final inbox receipt. The current evidence proves that the send workflow reached SMTP send successfully and wrote per-language delivery manifests plus a durable redaction-safe delivery summary.
