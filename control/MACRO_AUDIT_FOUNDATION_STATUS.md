# Macro Audit Foundation Status

## Status date

2026-06-13

## Phase

```text
WP18 — Macro/thesis roadmap Phase 2: macro audit foundation
```

## Status

```text
closed / verified / shadow-only
```

WP18 extends the already implemented macro audit foundation with a hardened validator, deterministic fixture replay evidence path, isolated validation workflow, and explicit no-authority boundaries.

WP18 is closed because both required evidence paths are now green and committed:

```text
Validate ETF macro audit foundation: green
Validate ETF macro regime shadow: green
latest_wp18_macro_audit_foundation_validation.json: committed
latest_macro_regime_shadow_validation.json: committed after run #40
```

## Validation evidence

WP18 dedicated audit-foundation evidence:

```text
artifact: output/macro/validation/latest_wp18_macro_audit_foundation_validation.json
workflow: Validate ETF macro audit foundation
workflow_run_id: 27476145040
workflow_run_number: 6
status: passed
```

Related macro-regime shadow evidence after the validator and workflow push hardening:

```text
artifact: output/macro/validation/latest_macro_regime_shadow_validation.json
workflow: Validate ETF macro regime shadow
workflow_run_id: 27478580626
workflow_run_number: 40
status: passed
```

## Authority rule

The macro audit foundation is an input/provenance layer only. It may fetch and validate FRED, ECB, Treasury, and volatility observations, but it must not set regime, confidence, lane scoring, fundability, portfolio actions, or client-facing report wording until later deterministic regime, methodology, compliance, and bilingual gates explicitly promote it.

Authority flags remain:

```text
shadow_only=true
client_facing_authority=false
decision_impact=none_phase2_audit_only
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
production_report_path_changed=false
```

## Four-layer placement

### 1. Decision framework

The macro audit does not decide allocation or portfolio action. It only proves that official/public macro observations were fetched, timestamped, attributed, and checked for freshness.

### 2. Input/state contract

Every observation must carry:

```text
key
value
units
source
series_id
label
category
as_of_date
fetched_at_utc
staleness_days
max_staleness_days
status
```

Required source groups:

```text
fred
ecb
treasury_fiscaldata
volatility
```

The hardened validator also checks:

```text
required_source_groups
source_group_status
report_token
run_id
summary.observation_count
summary.max_staleness_days
authority fields
live source_url provenance
zero-valued summary.max_staleness_days compatibility
```

### 3. Output contract

Production macro audit path when built by the production macro policy pack:

```text
output/macro/macro_data_audit_<reference_date>_<run_id>.json
output/macro/latest_macro_data_audit_path.txt
```

WP18 fixture validation evidence path:

```text
output/macro/validation/wp18_macro_data_audit_fixture_<run_token>.json
output/macro/validation/wp18_macro_audit_foundation_validation_<run_token>.json
output/macro/validation/latest_wp18_macro_audit_foundation_validation.json
```

Macro-regime shadow evidence path used to prove compatibility with the existing shadow-regime replay stack:

```text
output/macro/validation/latest_macro_regime_shadow_validation.json
output/macro/validation/latest_macro_regime_shadow_comparison.json
output/macro/validation/latest_macro_audit_axis_shadow_validation.json
```

The fixture replay path intentionally writes under `output/macro/validation/` so it does not overwrite `output/macro/latest.json` or production report artifacts.

### 4. Operational runbook

Isolated validation workflow:

```text
.github/workflows/validate-macro-audit-foundation.yml
```

Related compatibility workflow:

```text
.github/workflows/validate-macro-regime-shadow.yml
```

Expected markers:

```text
ETF_MACRO_DATA_AUDIT_VALID_OK
ETF_MACRO_AUDIT_FOUNDATION_FIXTURE_OK
ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
ETF_MACRO_AUDIT_AXIS_SHADOW_OK
ETF_MACRO_REGIME_SHADOW_OK
```

The macro-regime shadow workflow evidence push path was hardened after repeated GitHub Actions races by committing generated evidence from a freshly synced `origin/main` working tree and retrying pushes.

The production weekly report workflow still builds the macro policy pack and may build a live macro audit in shadow mode. WP18 does not change production reports, portfolio state, scoring, fundability, or client-facing wording.

## Implemented files

Existing foundation files:

```text
config/macro_data_sources.yml
config/cb_calendar.yml
macro_sources/__init__.py
macro_sources/common.py
macro_sources/fred_client.py
macro_sources/ecb_client.py
macro_sources/treasury_client.py
macro_sources/vol_client.py
macro_sources/cb_calendar.py
macro_sources/build_macro_data_audit.py
schemas/macro_data_audit.schema.json
tools/validate_macro_data_audit.py
tests/fixtures/macro_data_audit_fixture.json
runtime/build_macro_policy_pack.py
```

WP18 additions / hardening:

```text
tools/replay_macro_audit_foundation_fixture.py
tests/test_wp18_macro_data_audit_validator.py
tests/test_wp18_macro_audit_foundation_fixture.py
.github/workflows/validate-macro-audit-foundation.yml
.github/workflows/validate-macro-regime-shadow.yml
```

## Remaining work

```text
production macro audit latest pointer still needs observation after the next successful weekly report run
Deterministic regime engine remains not promoted
Derived confidence remains not promoted
Macro policy pack schema modernization remains incomplete
Macro/thesis compliance and Dutch client-surface gates remain future work
Client-facing macro output remains governed by the existing validated report path
```

## Next action

Proceed to the next separate shadow-only package:

```text
WP19 — Deterministic regime engine fixture baseline
```

WP19 must remain:

```text
fixture-only
shadow-only
client_facing_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
historical_output_mutation=false
```
