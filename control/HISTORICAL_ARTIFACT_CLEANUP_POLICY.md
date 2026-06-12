# Historical Artifact Cleanup Policy

## Work package

```text
WP15 — Historical artifact cleanup policy
```

## Repository

```text
market-predictions/weekly-etf
```

## Snapshot date

```text
2026-06-12
```

## Layer

```text
input/state contract + operational runbook
```

## Purpose

This policy decides how the Weekly ETF repo should treat older generated report artifacts that may no longer match the current client-surface contract.

It prevents stale historical output files from being mistaken for the current production baseline while also preventing destructive cleanup of audit evidence.

## Current issue

Older generated report artifacts may still contain stale client-surface wording or old markers that were later fixed in the current report set.

Known example:

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
```

The current production baseline is clean:

```text
run_id: 20260610_211606
report set: 260610_02
```

The visible marker `ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED` is absent from the current `260610_02` Markdown / clean Markdown / HTML / PDF surfaces.

## Root cause

Generated report outputs under `output/` are historical artifacts. They reflect the report pipeline and client-surface contract at the time they were generated.

When the output contract later improves, old artifacts are not automatically rewritten. Repo-wide grep may therefore find stale wording in old outputs even when the current report set is clean.

## Policy decision

```text
historical_output_artifacts_are_immutable_by_default=true
```

Old generated outputs must be preserved as historical evidence by default.

Do not bulk-edit, rewrite, delete, squash, or silently regenerate historical output files merely to remove stale wording, old markers, or old formatting.

Historical cleanup or archiving may happen only through a future explicit cleanup/archive work package with defined scope, acceptance criteria, and rollback/traceability rules.

## Current baseline authority

Current production truth must be determined from current-state and manifest evidence, not by repo-wide historical grep.

Current production baseline:

```text
run_id=20260610_211606
github_actions_run=27306857013
artifact_commit=e2891ca
latest_report_set=260610_02
run_manifest=output/run_manifests/weekly_etf_run_manifest_2026-06-10_20260610_211606.json
delivery_manifest=output/delivery/weekly_etf_delivery_manifest_2026-06-10_20260610_211606.json
pricing_lineage_status=passed
delivery_status=smtp_sendmail_returned_no_exception
```

Delivery status remains delivery-layer evidence only. It is not an end-recipient inbox receipt.

## Artifact classes

### 1. Current production artifacts

Current production artifacts are the latest manifest-linked report/runtime/pricing/delivery artifacts recorded in `control/CURRENT_STATE.md`.

These are the artifacts to use for current client-surface verification.

### 2. Historical generated outputs

Historical generated outputs include older files such as previous `weekly_analysis_pro_*` Markdown, HTML, PDF, runtime, pricing, and delivery files.

They may contain older wording or markers. That does not imply the current production report is regressed.

### 3. Control and policy artifacts

Control files define current authority and operating rules.

When historical generated outputs conflict with current control docs, the control docs and latest manifests govern current operating status.

### 4. Review-only artifacts

Review-only artifacts include deterministic macro review, replay, pilot, promotion-decision, and shadow evidence files.

They are not production report authority unless explicitly promoted through the required control-layer process.

## Search and validation rules

Use scoped checks for current client-surface validation.

Preferred current-output checks should target:

```text
output/weekly_analysis_pro_260610_02*
output/weekly_analysis_pro_nl_260610_02*
```

or the latest explicit manifest-linked report paths.

Repo-wide grep is useful for finding historical residue, but it is not sufficient to prove current output regression.

If repo-wide grep finds stale text in old outputs, classify it as:

```text
historical_residue
```

unless the same text appears in the latest manifest-linked current report set.

## Cleanup/archive decision model

Allowed statuses for future cleanup/archive work:

```text
no_cleanup_required
cleanup_policy_defined_no_artifact_mutation
archive_plan_required
archive_approved_not_executed
archive_executed_with_manifest
cleanup_blocked_missing_traceability
```

Default current status:

```text
cleanup_policy_defined_no_artifact_mutation
```

## Future archive requirements

A future archive or cleanup work package must define:

```text
exact file scope
reason for archive or cleanup
whether files are moved, compressed, indexed, or deleted
manifest of affected files
rollback path
current-baseline verification before and after
confirmation that no current production report artifact is rewritten
confirmation that no pricing, portfolio, scoring, execution, delivery, or macro authority changes occur
```

A future archive operation should prefer moving old artifacts into a clearly named archive path or recording an archive manifest rather than deleting evidence.

## Forbidden actions

Do not:

```text
rewrite historical report Markdown/PDF/HTML just to remove stale wording
bulk-delete generated output files without explicit approval
silently regenerate old report sets
change current portfolio state as part of cleanup
change pricing lineage as part of cleanup
change scoring, fundability, delivery, execution, or macro authority as part of cleanup
treat historical grep hits as current production regressions without checking the latest manifest-linked report set
```

## Authority boundaries preserved

This policy does not grant:

```text
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
delivery_authority=false
execution_authority=false
production_report_mutation=false
macro_promotion_authority=false
```

## Operational runbook

When stale text is reported:

1. Identify whether it appears in the latest manifest-linked current report set.
2. If yes, treat it as a current output-contract regression.
3. If no, classify it as historical residue.
4. Do not modify historical outputs unless a future cleanup/archive work package explicitly authorizes it.
5. Record any stable cleanup/archive decision in `control/CURRENT_STATE.md`, `control/NEXT_ACTIONS.md`, and, if architectural, `control/DECISION_LOG.md`.

## WP15 conclusion

```text
policy_status=cleanup_policy_defined_no_artifact_mutation
historical_output_artifacts_are_immutable_by_default=true
current_baseline_scope=manifest_linked_latest_report_set
historical_output_mutation=false
production_report_behavior_changed=false
scoring_changed=false
fundability_changed=false
execution_changed=false
delivery_changed=false
portfolio_state_changed=false
macro_authority_changed=false
```

Recommended next action:

```text
No historical artifact cleanup is needed now. Future cleanup/archive requires an explicit follow-up work package.
```
