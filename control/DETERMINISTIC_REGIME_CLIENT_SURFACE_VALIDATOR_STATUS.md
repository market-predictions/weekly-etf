# Deterministic Regime Client Surface Validator Status

## Work package

```text
WP22 — Deterministic regime client-safe surface validator
```

## Status

```text
implemented / pending workflow evidence
```

## Scope

WP22 adds a validator/helper-only layer for the WP21 safe-surface design.

It does not integrate deterministic regime output into production reports and does not change portfolio state, scoring, fundability, delivery, or historical output artifacts.

## Implemented files

```text
fixtures/deterministic_regime_client_surface/safe_surface_fixture.json
tools/validate_deterministic_regime_client_surface.py
tests/test_deterministic_regime_client_surface_validator.py
```

## Implemented checks

The validator checks:

```text
required DTO fields
all authority fields are present and false
safe English and Dutch text are present
review-only language is present
confidence is expressed as a band, not raw precision
raw macro axes and raw macro evidence do not appear in the text
workflow ids, fixture names and source paths do not appear in the text
macro compliance and leakage validators pass on the rendered text
```

## Manual validation commands

```bash
python tools/validate_deterministic_regime_client_surface.py --self-test
python -m pytest tests/test_deterministic_regime_client_surface_validator.py -q
python tools/validate_deterministic_regime_client_surface.py --surface fixtures/deterministic_regime_client_surface/safe_surface_fixture.json
```

Expected markers:

```text
DETERMINISTIC_REGIME_CLIENT_SURFACE_SELF_TEST_OK
DETERMINISTIC_REGIME_CLIENT_SURFACE_OK
```

## Workflow status

A dedicated GitHub Actions workflow was attempted but not committed because the tool safety layer blocked the workflow create call.

Therefore WP22 is not closed as workflow-proven.

## Authority boundary

```text
validator_or_helper_only=true
client_facing_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
historical_output_mutation=false
production_report_integration=false
```

## Next action

Run the manual validation commands or add the dedicated workflow in a separate environment where workflow writes are permitted.

After validation is green, update the control layer to close WP22 and proceed to WP23 only if desired.
