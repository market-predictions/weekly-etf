# Macro Conflict Cap Status

Snapshot date: 2026-06-04

## Decision

The macro-conflict cap is now documented as a stable shadow methodology rule.

File:

```text
control/MACRO_CONFLICT_CAP_METHODOLOGY.md
```

## Scope

The cap is internal to the deterministic macro regime shadow layer.

It does not change report wording, lane scoring, fundability, portfolio actions, or recommendations.

## Current rule

The cap applies only to a risk-on shadow candidate when audited macro axes materially disagree.

Current settings:

```text
macro_conflict_cap_threshold: 0.75
risk_on_macro_conflict_cap: 0.72
```

Non-risk-on disagreements are diagnostic only at this stage.

## Validator hook

Updated:

```text
tools/validate_macro_compliance.py
.github/workflows/validate-macro-compliance.yml
```

The validator now supports:

```text
--cap-methodology control/MACRO_CONFLICT_CAP_METHODOLOGY.md
```

The workflow now runs that check.

## Commits

```text
be38f0e976e648c23647f8a19886b62ccc11185a  document macro conflict cap methodology
cdb09fa7868193839789ec11b6c2d48714d594a4  validate macro conflict cap methodology note
5c54f11edfe40f9735a86b3ded33f8678fda253c  validate macro conflict cap methodology in compliance workflow
f53eac45473c5863bdad8214a75f3fcf090d4661  trigger macro compliance validation rerun
```

## Verification status

The macro compliance workflow was rerun by a harmless watched fixture commit:

```text
workflow: Validate ETF macro compliance
run_number: 9
trigger_commit: f53eac45473c5863bdad8214a75f3fcf090d4661
status: passed
observed_at: 2026-06-04
source: user-provided GitHub Actions UI screenshot
```

The screenshot shows the green checkmark for:

```text
trigger macro compliance validation rerun
Validate ETF macro compliance #9
commit f53eac4
branch main
duration 11s
```

## Work-package status

Macro-conflict cap methodology decision: closed for this stage.

Macro-conflict cap methodology workflow validation: confirmed green by user-provided Actions UI evidence.

## Next action

Continue with macro compliance hardening only if needed:

```text
fixtures/macro_compliance/**
tools/validate_macro_compliance.py
.github/workflows/validate-macro-compliance.yml
```

Recommended next step: add targeted planted-failure fixtures for shadow-label leakage and orphan macro figures if not already sufficiently covered.
