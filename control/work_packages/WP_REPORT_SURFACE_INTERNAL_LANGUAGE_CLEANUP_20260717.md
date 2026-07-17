# Work Package — WP_REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Layer: output contract + operational runbook
Status: active

## Current issue

The latest delivered English/Dutch report is analytically valid, but future client surfaces can still expose internal workflow language such as:

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

The same surface also contains repeated punctuation in position-review lines and process-heavy wording that obscures the actual client decision.

## Root cause

Client cleanup is distributed across multiple legacy sanitizers. Existing gates remove snake_case, stale holdings language and several localization defects, but they do not share one explicit bilingual internal-language contract.

## Recommended change

1. Add a shared deterministic bilingual client-language normalizer and finding scanner.
2. Apply it through the existing Markdown/HTML cleanup path used before delivery.
3. Rewrite the supplementary deterministic regime surface at source so it no longer says `shadow engine`, `legacy regime read` or `review-only`, while preserving all false-authority fields.
4. Extend the existing pre-send clean gate to fail on forbidden internal phrases.
5. Add a no-send evidence replay against the immutable `260716` English/Dutch reports in memory only.

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
```

## Required safeguards

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
deterministic_regime_false_authority_fields: unchanged
existing_client_surface_gate: enforces_new_contract
historical_report_files: byte_unchanged
email_sent: false
```
