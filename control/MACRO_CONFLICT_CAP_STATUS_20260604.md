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
```

## Verification status

The files are committed.

The GitHub connector currently shows no workflow run for commit:

```text
5c54f11edfe40f9735a86b3ded33f8678fda253c
```

So the workflow result still needs verification through Actions UI or a later connector-visible run.

## Next action

Verify the macro compliance workflow result for commit `5c54f11edfe40f9735a86b3ded33f8678fda253c`.

After that, continue only with macro compliance hardening if the workflow is green.
