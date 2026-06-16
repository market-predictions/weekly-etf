# Handover — Weekly ETF fresh send run blocked by delivery HTML guard

## Repository

```text
market-predictions/weekly-etf
```

## Fresh chat start sequence

Read in order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/DETERMINISTIC_REGIME_REPORT_INTEGRATION_VISUAL_QA_STATUS.md
control/PRODUCTION_DELIVERY_VALIDATION_STATUS_20260614.md
```

Then inspect the minimum relevant files:

```text
.github/workflows/send-weekly-report.yml
tools/validate_etf_delivery_html_contract.py
tools/validate_etf_client_surface_clean.py
tools/validate_etf_pdf_polish_contract.py
runtime/client_facing_sanitizer.py
runtime/fix_executed_report_contract.py
send_report_runtime_html.py
```

## Current status at handover

The user requested:

```text
Send fresh weekly ETF reports
```

A run-queue trigger was created:

```text
control/run_queue/weekly_etf_report_request_20260616_222200.md
commit: 0832bb8394b916c89af736280d567ed84282821e
```

The production send workflow started but failed before the email step. This is correct fail-closed behavior.

No fresh delivery success should be claimed for this latest requested send.

## Baseline before this latest send attempt

The last confirmed successful production delivery validation remains:

```text
baseline: 260612_11
run_id: 20260614_185627
workflow_status: workflow_success
delivery_status: smtp_sendmail_returned_no_exception
```

Evidence:

```text
control/PRODUCTION_DELIVERY_VALIDATION_STATUS_20260614.md
output/run_manifests/weekly_etf_run_manifest_2026-06-12_20260614_185627.json
output/delivery/weekly_etf_delivery_manifest_2026-06-12_20260614_185627.json
```

Boundary:

```text
smtp_sendmail_returned_no_exception is delivery-layer evidence only, not an end-recipient inbox receipt.
```

## Completed roadmap before latest send attempt

```text
WP16-WP27 closed
Deterministic regime safe-surface report integration implemented, visually QA'd, and closed
No active deterministic-regime package
```

The deterministic regime line is review-only. It does not promote deterministic regime engine authority and does not authorize portfolio changes.

## Latest failed workflow symptoms

### Failed run #251

Workflow:

```text
Send weekly ETF Pro report #251
```

Failure step:

```text
Validate ETF delivery HTML contract
```

Observed failure:

```text
ETF PDF polish contract failed
weekly_analysis_pro_260615_delivery.html: idempotent execution heading still says executed this run
weekly_analysis_pro_260615_delivery.html: missing reflected-position-change heading
weekly_analysis_pro_nl_260615_delivery.html: idempotent execution heading still says in deze run
weekly_analysis_pro_nl_260615_delivery.html: missing reflected-position-change heading
```

Patch applied after run #251:

```text
runtime/client_facing_sanitizer.py
commit: 33139c7b3cf3ec048e727854ae5e3f8c4b355adf
```

Added test:

```text
tests/test_delivery_html_position_change_heading_sanitizer.py
commit: d8c44d60b984d036c9ac556bbd4ff648ef032cf8
```

Purpose: normalize delivery HTML headings:

```text
Position Changes Executed This Run -> Position Changes Reflected in Official State
Positiewijzigingen in deze run -> Positiewijzigingen verwerkt in de officiële portefeuillestaat
```

### Failed run #252

Workflow:

```text
Send weekly ETF Pro report #252
```

Failure step:

```text
Validate ETF delivery HTML contract
```

Observed failure still referenced stale base delivery HTML:

```text
weekly_analysis_pro_260615_delivery.html
weekly_analysis_pro_nl_260615_delivery.html
```

while the current run report pair was:

```text
weekly_analysis_pro_260615_02.md
weekly_analysis_pro_nl_260615_02.md
```

Root cause: the PDF-polish validator selected delivery HTML by lexicographic latest filename, not by the explicit current report paths from the workflow environment.

Patch applied after run #252:

```text
tools/validate_etf_pdf_polish_contract.py
commit: 4b82c7396ac9eeacfdd75c0d9c1b983515d1ab30
```

Added test:

```text
tests/test_pdf_polish_contract_explicit_delivery_selection.py
commit: d4d121e74549def3b6ec7f3ad4c79fe690261da5
```

Purpose: make `latest_delivery_html(output_dir, language=...)` prefer the matching delivery HTML for:

```text
MRKT_RPRTS_EXPLICIT_REPORT_PATH
MRKT_RPRTS_EXPLICIT_REPORT_PATH_NL
```

This should force the validator to check:

```text
weekly_analysis_pro_260615_02_delivery.html
weekly_analysis_pro_nl_260615_02_delivery.html
```

instead of stale base files.

## Next action for fresh chat

Start a new workflow run, not a rerun of old failed jobs:

```text
Actions -> Send weekly ETF Pro report -> Run workflow -> main
```

Expected next behavior:

```text
Validate ETF delivery HTML contract should validate the current explicit delivery HTML pair.
If that step passes, workflow should continue to Send email.
```

After the run finishes, inspect:

```text
Send email
Write ETF delivery manifest summary
Write final ETF run manifest
Validate ETF manifest evidence
Commit ETF run artifacts back to main
```

Only claim latest delivery success if the workflow is green and the delivery/final manifests exist.

## If it still fails

Treat the new failure as a narrow delivery-contract issue.

Do not add new deterministic-regime logic.

Likely files to inspect:

```text
tools/validate_etf_pdf_polish_contract.py
tools/validate_etf_client_surface_clean.py
tools/validate_etf_delivery_html_contract.py
runtime/client_facing_sanitizer.py
send_report_runtime_html.py
```

## Authority boundaries

Keep these unchanged:

```text
deterministic_regime_engine_promoted=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false unless guarded workflow executes and persists it
historical_output_mutation=false
```

## Session close notes

Stable decisions to preserve:

```text
- Deterministic regime report surface is review-only and additive.
- Production delivery success requires workflow and manifest evidence.
- SMTP sendmail success is not inbox receipt.
- Delivery HTML/PDF validators must bind to current explicit report paths, not stale lexicographic latest artifacts.
```
