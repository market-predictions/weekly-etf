# Work Package — WP_REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Layer: output contract + operational runbook
Status: closed

## Current issue

The latest delivered English/Dutch report was analytically valid, but future client surfaces could expose internal workflow language such as:

```text
shadow engine
runtime macro pack
rotation engine status
guarded model rotation
release score
override
guarded auto-execution
diagnostic-only authority narration
run(s)
```

The same surface contained repeated punctuation and process-heavy wording that obscured the client decision.

## Root cause

Client cleanup was distributed across multiple legacy sanitizers. Existing gates removed snake_case, stale holdings language and several localization defects, but they did not share one explicit bilingual internal-language contract.

## Implemented change

1. Added a shared deterministic bilingual client-language normalizer and forbidden-term scanner.
2. Applied it through the existing Markdown/HTML cleanup path used before delivery.
3. Rewrote the supplementary deterministic regime surface at source so it no longer says `shadow engine`, `legacy regime read`, `review-only` or `alleen ter review`.
4. Preserved all deterministic-regime false-authority fields.
5. Extended the existing pre-send clean gate through the shared scanner.
6. Added a no-send evidence replay against immutable `260716` English/Dutch reports in memory only.

## Exact files

```text
runtime/report_surface_language_contract.py
runtime/wp16_followup3_cleanup.py
runtime/deterministic_regime_client_surface.py
tools/validate_deterministic_regime_client_surface.py
tools/validate_etf_client_surface_clean.py
tools/validate_report_surface_internal_language_cleanup.py
fixtures/deterministic_regime_client_surface/safe_surface_fixture.json
tests/test_report_surface_internal_language_cleanup.py
tests/test_deterministic_regime_client_surface_helper.py
tests/test_deterministic_regime_client_surface_validator.py
tests/test_deterministic_regime_report_surface_integration.py
.github/workflows/validate-report-surface-internal-language-cleanup.yml
control/evidence/REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP_EVIDENCE_20260717.json
```

## Validation

```text
workflow_run: 29590932038
workflow_job: 87919550815
result: success
focused_tests: 30 passed
artifact_id: 8411017345
artifact_digest: sha256:8a7acad3c573ae2eaa9a82fcd92f295ae5c6b33cc6090ca6936b5cd1a7997a74
EN findings: 18 -> 0
NL findings: 6 -> 0
EN numeric tokens: 635 preserved
NL numeric tokens: 588 preserved
EN markdown links: 234 preserved
NL markdown links: 236 preserved
cleanup_idempotent: true
historical_report_files: byte_unchanged
email_sent: false
```

## Safeguards confirmed

```text
portfolio_state_mutation: false
trade_ledger_mutation: false
pricing_authority_change: false
macro_thesis_authority_promotion: false
lane_scoring_change: false
fundability_change: false
portfolio_execution_change: false
historical_report_mutation: false
email_send: false
numeric_parity: preserved
markdown_links: preserved
cockpit_front_page: preserved
```

## Acceptance criteria

```text
forbidden_internal_terms_after_cleanup: 0
double_punctuation_after_cleanup: 0
numeric_multiset_before_after: identical
markdown_link_multiset_before_after: identical
cleanup_idempotent: true
deterministic_regime_false_authority_fields: unchanged_false
existing_client_surface_gate: enforces_new_contract
historical_report_files: byte_unchanged
email_sent: false
status: closed
```
