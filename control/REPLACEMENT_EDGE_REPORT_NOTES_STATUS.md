# Replacement-edge report notes status

## Workpackage

```text
WP11A-VERIFY / WP11A-VERIFY-OBSERVE / WP11A-POLICY-CAP — Validate replacement-edge diagnostic notes and keep model execution inside policy caps
```

## Repository

```text
market-predictions/weekly-etf
```

## Status

```text
status: policy-cap-fix-committed / retry-request-prepared / awaiting-workflow-evidence
```

## Purpose

WP5 added direct challenger-vs-current-holding replacement-edge diagnostics. WP11A created the safe helper and tests. WP11A-FIX wired those diagnostics into the report-output path as clearly non-authoritative notes. WP11A-VERIFY requests and tracks validation evidence for that report-output contract.

WP11A-VERIFY reached the report-build step and passed the Dutch client-language scrub, date localization, ticker linkification, and macro-thesis surface leakage validation. WP11A-VERIFY-OBSERVE made hidden model-execution policy/input failures visible in CI logs.

## Authority boundary

Replacement-edge report notes remain diagnostic-only.

They do not grant:

```text
portfolio_action_authority=false
fundability_authority=false
lane_scoring_authority=false
funding_authority=false
portfolio_mutation=false
production_recommendation_authority=false
execution_authority=false
```

The notes must not influence ranking, fundability, recommendation, target weights, trade intents, execution, or portfolio mutation.

## Files changed by WP11A-FIX

```text
runtime/replacement_edge_report_notes.py
runtime/polish_runtime_reports.py
tests/test_replacement_edge_report_notes.py
tools/validate_etf_report_content_contract.py
control/REPLACEMENT_EDGE_REPORT_NOTES_STATUS.md
```

## WP11A-FIX implementation summary

The helper:

```text
runtime/replacement_edge_report_notes.py
```

- builds a notes payload from the existing WP5 replacement-edge artifact builder
- renders English and Dutch markdown tables
- embeds a stable marker:

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
```

- explicitly states that the notes do not create allocation authority, fundability authority, lane-scoring authority, production recommendation authority, execution authority, or portfolio mutation authority
- preserves the existing WP5 diagnostic-only boundary

The runtime polish layer:

```text
runtime/polish_runtime_reports.py
```

- injects the replacement-edge notes after the final Replacement Duel / Vervangingsanalyse section
- applies the insertion to both English and Dutch report text
- uses a safe empty-state fallback when a lane-assessment source cannot be resolved
- does not alter pricing, lane scoring, rotation, trade-intent, execution, or portfolio-state logic

The content validator:

```text
tools/validate_etf_report_content_contract.py
```

requires the English rendered report to contain:

```text
ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
```

and the English diagnostic-only authority disclaimer.

## WP11A-VERIFY action taken

Created validation run-queue request:

```text
control/run_queue/weekly_etf_report_request_20260610_0015_wp11a_verify.md
```

Commit:

```text
31328c2e5d2a2c16c642914f1538808fe56f77ac — Request WP11A-VERIFY fresh report validation run
```

A later retry after a Dutch GLD surface fix reached further into the report-build step and showed:

```text
ETF_NL_CLIENT_LANGUAGE_SCRUB_OK
ETF_NL_DATE_LOCALIZATION_OK
ETF_LINKIFY_OK
ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
```

## WP11A-VERIFY-OBSERVE action taken

Committed observability-only stderr output in:

```text
runtime/model_execution_engine.py
```

Commit:

```text
887722cc638778ee44809b6556aa54c7ca72f569 — Expose model execution policy failures on stderr
```

The observe retry exposed the real blocker:

```text
ETF_MODEL_EXECUTION_BLOCKED | artifact=output/runtime/etf_model_execution_20260609_20260610_181023.json | errors=source_reduction_exceeds_policy:SPY:5.23>5.00
```

## WP11A-POLICY-CAP action taken

After explicit user approval, committed a bounded execution-engine fix:

```text
951a72c4492cfc72ab46289def755606d35a309c — Cap model execution source reductions to policy
```

Change summary:

- `_execution_notional` now caps executable notional to the existing `max_single_source_reduction_pct_nav` value.
- The policy remains unchanged at 5% unless the runtime policy says otherwise.
- The previous SPY intent can now be reduced from 5.23% requested to 5.00% executable.
- Policy-cap events are recorded as warnings, for example:

```text
source_notional_capped_to_policy:SPY:5555.27->5312.32
```

Local reproduction before committing showed:

```text
ETF_MODEL_EXECUTION_OK | artifact=/tmp/weekly-etf-model-exec-test-2/etf_model_execution_20260609_20260610_181023.json | mode=shadow | trades=1 | status=shadow_ready
policy_checks.passed=true
policy_checks.errors=[]
source_delta_weight_pct=-5.0
destination_delta_weight_pct=5.0
notional_cap_reason=policy
```

This is an execution behavior change, but it is a policy-enforcement change, not a policy relaxation.

## Prepared retry request

A new retry request is prepared as the final trigger commit for this sequence:

```text
control/run_queue/weekly_etf_report_request_20260610_190101_wp11a_policy_cap_retry.md
```

Purpose:

```text
Retry WP11A-VERIFY after capping model execution source reductions to the existing policy limit.
```

## Required validation evidence still needed

Fresh report/content validation should prove:

```text
English report contains ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
Dutch report contains ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED
python tools/validate_etf_report_content_contract.py --output-dir output passes
shadow model execution passes or clearly reports the next policy/input blocker
```

## Remaining work

```text
inspect GitHub Actions workflow result for the policy-cap retry
confirm latest fresh English report path
confirm latest fresh Dutch report path
confirm marker in both reports
confirm content validator result
record completed verification status in CURRENT_STATE, NEXT_ACTIONS, ETF_SESSION_CHANGELOG and a follow-up closeout handover
```

## WP11A-CONTENT-FIX action taken

The policy-cap retry moved past model execution and failed later in the English report content contract:

```text
ETF content contract failed for weekly_analysis_pro_260609_04.md: replacement-edge diagnostic notes missing/incomplete: ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED, Diagnostic-only: these notes grant no allocation authority, fundability authority, lane-scoring authority, production recommendation authority, execution authority or portfolio mutation authority., allocation authority, fundability authority, lane-scoring authority, production recommendation authority, execution authority, portfolio mutation authority
```

Root cause:

```text
runtime.polish_runtime_reports inserted replacement-edge diagnostic notes early, but runtime.fix_report_output_contract rebuilt the English replacement pricing/duel surface afterward and did not re-emit the diagnostic notes.
```

Fix commits:

```text
eb312232d86e2f9ffac5133695b2cf69f71ea64f — Preserve replacement-edge notes in output contract fix
0229ede09541aa9b61b6ff8136d7610a426853b1 — Test output contract replacement-edge notes
```

Change summary:

- `runtime.fix_report_output_contract` now appends English replacement-edge diagnostic notes to the replacement pricing/duel block it renders.
- The content validator remains strict.
- No policy, scoring, fundability, recommendation, execution, target-weight or portfolio-mutation authority changed.

Local validation on the failed fresh output after applying the fix showed:

```text
ETF_OUTPUT_CONTRACT_FIX_PATCHED | report=weekly_analysis_pro_260609_04.md | rotation_plan=True
ETF_OUTPUT_CONTRACT_FIX_SKIPPED | report=weekly_analysis_pro_nl_260609_04.md | reason=native_dutch_renderer
ETF_OUTPUT_CONTRACT_FIX_OK
ETF_REPORT_CONTENT_CONTRACT_OK | report=weekly_analysis_pro_260609_04.md
```

The local validation environment lacked optional render/test packages, so the focused smoke path used temporary import stubs for unused PDF/render imports. The CI environment already has the normal workflow dependencies.

## Prepared content-fix retry request

```text
control/run_queue/weekly_etf_report_request_20260610_191044_wp11a_content_fix_retry.md
```

Purpose:

```text
Retry WP11A-VERIFY after preserving English replacement-edge diagnostic notes through runtime.fix_report_output_contract.
```

## WP11A-NL-TERMINOLOGY-FIX action taken

The content-fix retry passed the English report content contract:

```text
ETF_REPORT_CONTENT_CONTRACT_OK | report=weekly_analysis_pro_260609_05.md
```

It then failed in the Dutch terminology contract:

```text
ContractError: ACTION_REPLACEMENTS is not sourced from runtime.nl_terminology
```

Fix commit:

```text
51998e242bb573bb6be55145fe355558b8e9f75b — Source NL localization aliases from central terminology
```

Change summary:

- `runtime.nl_localization` now sources identity-checked aliases directly from `runtime.nl_terminology`.
- `localize_text` still uses the shared contract overlay through `runtime.nl_terminology_contract.combined_text_replacements()`.
- No report scoring, policy, trading, execution or portfolio-state behavior changed.

Local validation:

```text
ETF_NL_TERMINOLOGY_CONTRACT_OK | source=runtime.nl_terminology
```
