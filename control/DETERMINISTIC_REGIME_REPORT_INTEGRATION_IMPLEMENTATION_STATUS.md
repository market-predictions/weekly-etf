# Deterministic Regime Report Integration Implementation Status

## Work package

```text
WP26 — Deterministic regime report integration implementation
```

## Status

```text
implemented / pending validation evidence
```

## Scope

WP26 implements the WP25 proposal with minimal report-surface changes.

The implementation adds the deterministic regime safe-surface text to the existing macro dashboard area as a visibly review-only additive line.

It does not change portfolio state, lane scoring, fundability, funding, execution, delivery, or historical generated outputs.

## Implemented files

```text
runtime/macro_report_surface.py
tools/validate_macro_report_surface.py
tests/test_deterministic_regime_report_surface_integration.py
```

## Integration behavior

The implementation:

```text
loads committed deterministic regime validation/comparison evidence
builds the narrow safe DTO through runtime/deterministic_regime_client_surface.py
renders safe EN/NL review-only text
adds the safe line into dashboard_en/dashboard_nl after the legacy macro confidence line
keeps the legacy macro policy pack as the governing production macro source
validates the deterministic DTO through the WP22 validator inside tools/validate_macro_report_surface.py
```

## Explicitly unchanged layers

```text
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
historical_output_mutation=false
delivery_authority=false
execution_authority=false
```

## Manual validation commands

Run in GitHub Codespace from repo root:

```bash
PYTHONPATH=. python -m pytest tests/test_deterministic_regime_report_surface_integration.py -q
PYTHONPATH=. python -m pytest tests/test_deterministic_regime_client_surface_validator.py tests/test_deterministic_regime_client_surface_helper.py tests/test_deterministic_regime_report_surface_integration.py -q
PYTHONPATH=. python tools/validate_macro_report_surface.py --self-test
PYTHONPATH=. python tools/validate_macro_report_surface.py --macro-pack output/macro/latest.json
```

Expected result:

```text
all tests pass
ETF_MACRO_REPORT_SURFACE_OK
```

## Closeout condition

WP26 is not closed until the manual validation output is recorded.

Next package after validation:

```text
WP27 — Deterministic regime report integration closeout / visual report QA
```
