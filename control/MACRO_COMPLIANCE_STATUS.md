# Macro Compliance Status

## Date
2026-06-01

## Status
Phase 4 methodology/compliance gate has been implemented as an isolated pre-promotion guard. It is not wired into the production report path yet.

## Current purpose

This gate protects the macro/regime/thesis roadmap before any expanded macro content is allowed onto the client surface.

It blocks:

- predictive market or central-bank phrasing
- uncited institutional/consensus overlay claims
- orphan macro figures without nearby provenance/source/as-of context
- Stage-1 thesis candidate leakage
- shadow/internal label leakage

## Files added

```text
MACRO_METHODOLOGY.md
tools/validate_macro_compliance.py
fixtures/macro_compliance/safe_macro_note.md
fixtures/macro_compliance/bad_predictive_macro_note.md
.github/workflows/validate-macro-compliance.yml
```

## Methodology rule

The macro/regime engine is descriptive, not predictive.

Allowed content describes current observable conditions, evidence alignment, confidence decomposition, and confirmation requirements.

Blocked content forecasts exact market outcomes, presents central-bank actions as certain, exposes Stage-1 thesis candidates, or surfaces shadow/internal labels.

## Validator behavior

The validator supports:

```text
python tools/validate_macro_compliance.py --self-test
python tools/validate_macro_compliance.py --text <report.md>
python tools/validate_macro_compliance.py --macro-pack <pack.json>
python tools/validate_macro_compliance.py --text <bad_fixture.md> --expect-fail
```

Expected markers:

```text
ETF_MACRO_COMPLIANCE_SELF_TEST_OK
ETF_MACRO_COMPLIANCE_OK
ETF_MACRO_COMPLIANCE_EXPECTED_FAILURE_OK
```

## Isolated workflow

The isolated workflow is:

```text
.github/workflows/validate-macro-compliance.yml
```

It runs:

```text
python tools/validate_macro_compliance.py --self-test
python tools/validate_macro_compliance.py --text fixtures/macro_compliance/safe_macro_note.md
python tools/validate_macro_compliance.py --text fixtures/macro_compliance/bad_predictive_macro_note.md --expect-fail
```

## Validation status

Implementation is committed. Workflow proof is pending GitHub Actions confirmation because connector-visible workflow lookup did not expose the push-triggered run.

The next check should confirm the isolated `Validate ETF macro compliance` workflow passes and logs the expected markers.

## Authority boundary

This validator does not promote deterministic regime output into production authority.

Do not wire expanded macro/thesis content into English or Dutch client-facing reports until:

1. this compliance workflow is confirmed green;
2. Dutch macro/thesis wording rules are added if Dutch output is affected;
3. production report validators are extended;
4. a control-layer promotion decision is made.

## Next action

Confirm the isolated compliance workflow pass. Then extend report validators only when client-facing macro/thesis content is actually introduced.
