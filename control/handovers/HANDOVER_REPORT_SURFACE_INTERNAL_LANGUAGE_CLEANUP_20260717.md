# Handover — Report-surface internal-language cleanup

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`
Package: `WP_REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP`
Status: closed and merged
PR: `#88`
Merge commit: `4571c4c045962908609b3a5e2f784199d4e3b142`

## Current issue closed

The delivery pipeline had several separate language scrubs but no shared bilingual contract for internal workflow terminology. The current `260716` reports demonstrated visible terms such as `shadow engine`, `runtime macro pack`, `rotation engine status`, `guarded model rotation`, `release score`, `override`, `guarded auto-execution`, process disclaimers and repeated punctuation.

## Implemented change

```text
runtime/report_surface_language_contract.py
runtime/wp16_followup3_cleanup.py
runtime/deterministic_regime_client_surface.py
tools/validate_deterministic_regime_client_surface.py
tools/validate_report_surface_internal_language_cleanup.py
fixtures/deterministic_regime_client_surface/safe_surface_fixture.json
tests/test_report_surface_internal_language_cleanup.py
tests/test_deterministic_regime_client_surface_helper.py
tests/test_deterministic_regime_client_surface_validator.py
tests/test_deterministic_regime_report_surface_integration.py
.github/workflows/validate-report-surface-internal-language-cleanup.yml
```

The shared contract is applied through the existing `runtime.wp16_followup3_cleanup.clean_text()` path. Because `tools/validate_etf_client_surface_clean.py` already uses that path and its failure scanner, the future pre-send gate now enforces the new contract for Markdown and delivery HTML.

## Supplementary deterministic regime wording

The client surface now uses:

```text
Supplementary regime cross-check
Aanvullende regimecontrole
```

It no longer displays `shadow engine`, `legacy regime read`, `review-only` or `alleen ter review`. All explicit false-authority fields remain false.

## Validation evidence

```text
workflow_run: 29590932038
workflow_job: 87919550815
result: success
focused_tests: 30 passed
artifact_id: 8411017345
artifact_digest: sha256:8a7acad3c573ae2eaa9a82fcd92f295ae5c6b33cc6090ca6936b5cd1a7997a74
```

Read-only replay against immutable `260716` reports:

```text
EN findings: 18 -> 0
NL findings: 6 -> 0
EN numeric tokens: 635 preserved
NL numeric tokens: 588 preserved
EN markdown links: 234 preserved
NL markdown links: 236 preserved
cleanup idempotent: true
historical source hashes: identical before/after
```

Persistent evidence:

```text
control/evidence/REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP_EVIDENCE_20260717.json
```

## Authority boundary

```text
portfolio_state_mutation: false
trade_ledger_mutation: false
pricing_authority_change: false
macro_thesis_authority_promotion: false
lane_scoring_change: false
fundability_change: false
portfolio_execution_change: false
historical_report_mutation: false
email_sent: false
```

## Next action

Do not resend the historical `260716` package.

The next operational step is a separate explicitly authorized fresh Weekly ETF production run. That run should prove in its real EN/NL HTML/PDF package that:

1. the enabled cockpit front page is present once per language;
2. official holdings and all trade deltas remain whole-share compliant;
3. the new internal-language clean gate passes;
4. the delivery manifest is written;
5. inbox delivery is confirmed before claiming success.
