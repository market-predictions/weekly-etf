# Weekly ETF post-execution correction request

request_type: post_execution_report_surface_correction
source_artifact: output/runtime/etf_model_execution_20260714_20260715_175910.json
report_token: 260714
correction_suffix: 03
original_run_id: 20260715_175910
report_date: 2026-07-14
send_confirmation: confirm_correction_resend

## Authority boundary

- Rebuild the corrected English and Dutch reports from the existing execution artifact.
- Do not rerun portfolio selection or execute another portfolio mutation.
- Preserve official portfolio state and trade ledger byte-for-byte.
- Send distinctly labeled corrected English and Dutch reports.
- Persist delivery manifests and the correction manifest.
