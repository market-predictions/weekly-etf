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
--latest-report-macro-sections
```

The workflow now runs both checks.

## Targeted planted-failure fixtures

Added targeted expected-failure fixtures:

```text
fixtures/macro_compliance/bad_shadow_label_leakage.md
fixtures/macro_compliance/bad_orphan_macro_figure.md
```

The workflow validates them separately:

```text
Validate shadow label leakage fixture fails
Validate orphan macro figure fixture fails
```

## Latest report macro-section validation

Added focused report-artifact validation:

```text
tools/validate_macro_compliance.py --latest-report-macro-sections
```

This dynamically finds the latest committed English and Dutch markdown report artifacts and validates only the macro-sensitive early report surface, ending before Section 5.

This avoids treating the full portfolio report as a macro-only compliance target while still checking the actual committed client-facing macro/regime surface.

## Commits

```text
be38f0e976e648c23647f8a19886b62ccc11185a  document macro conflict cap methodology
cdb09fa7868193839789ec11b6c2d48714d594a4  validate macro conflict cap methodology note
5c54f11edfe40f9735a86b3ded33f8678fda253c  validate macro conflict cap methodology in compliance workflow
f53eac45473c5863bdad8214a75f3fcf090d4661  trigger macro compliance validation rerun
021f87e2fe08c1f5d62cc18b23a22285b4afd994  add macro compliance shadow label leakage fixture
57ab7d32f96ab6e9a56b8a7359c8b61404f8ff1f  add macro compliance orphan figure fixture
ce5097f672be98054730762a85350f7e5dc89651  validate targeted macro compliance failure fixtures
ef12aa4167be1fe97732c1cadadb102cd4d47d27  fix orphan macro figure planted failure fixture
d1566788361ba65ef97cf61259d7d83cf2bdbfde  validate latest report macro sections
28b6ddda28bd7f287bef7e0622ef8e9c70e726eb  validate latest report macro sections
```

## Verification status

Macro-conflict cap methodology workflow validation:

```text
workflow: Validate ETF macro compliance
run_number: 9
trigger_commit: f53eac45473c5863bdad8214a75f3fcf090d4661
status: passed
observed_at: 2026-06-04
source: user-provided GitHub Actions UI screenshot
```

Targeted macro compliance fixture validation:

```text
workflow: Validate ETF macro compliance
run_number: 13
trigger_commit: ef12aa4167be1fe97732c1cadadb102cd4d47d27
status: passed
branch: main
duration: 14s
observed_at: 2026-06-04
source: user-provided GitHub Actions UI screenshot
```

Latest committed EN/NL report macro-section validation:

```text
workflow: Validate ETF macro compliance
run_number: 15
trigger_commit: 28b6ddda28bd7f287bef7e0622ef8e9c70e726eb
status: passed
branch: main
duration: 18s
observed_at: 2026-06-04
source: user-provided GitHub Actions UI screenshot
```

The macro compliance workflow now validates:

```text
macro compliance self-test
macro conflict cap methodology
macro report surface self-test
current macro report surface if pack exists
latest committed English/Dutch report macro sections
safe macro fixture passes
combined blocked macro fixture fails as expected
shadow label leakage fixture fails as expected
orphan macro figure fixture fails as expected
```

## Work-package status

Macro-conflict cap methodology decision: closed for this stage.

Macro-conflict cap methodology workflow validation: confirmed green by user-provided Actions UI evidence.

Targeted macro compliance planted-failure fixtures: closed for this stage and confirmed green by user-provided Actions UI evidence.

Latest committed EN/NL report macro-section validation: closed for this stage and confirmed green by user-provided Actions UI evidence.

## Next action

Continue with macro compliance hardening only if needed:

```text
fixtures/macro_compliance/**
tools/validate_macro_compliance.py
.github/workflows/validate-macro-compliance.yml
```

Recommended next step: update `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md` to reflect that macro compliance now covers methodology, planted failures, macro pack surface, and latest committed report macro sections.