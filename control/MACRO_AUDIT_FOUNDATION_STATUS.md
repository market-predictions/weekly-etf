# Macro Audit Foundation Status

## Status date

2026-06-13

## Phase

```text
WP18 — Macro/thesis roadmap Phase 2: macro audit foundation
```

## Status

```text
implemented / shadow-only / validation workflow added / pending fresh workflow evidence
```

WP18 extends the already implemented macro audit foundation with a hardened validator, deterministic fixture replay evidence path, isolated validation workflow, and explicit no-authority boundaries.

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

The fixture replay path intentionally writes under `output/macro/validation/` so it does not overwrite `output/macro/latest.json` or production report artifacts.

### 4. Operational runbook

New isolated validation workflow:

```text
.github/workflows/validate-macro-audit-foundation.yml
```

Expected markers:

```text
ETF_MACRO_DATA_AUDIT_VALID_OK
ETF_MACRO_AUDIT_FOUNDATION_FIXTURE_OK
```

The production weekly report workflow still builds the macro policy pack and may build a live macro audit in shadow mode. The WP18 validation workflow proves the fixture path deterministically and commits only validation evidence.

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
```

## Not yet done

```text
fresh WP18 validation workflow evidence not yet observed in this chat
production macro audit latest pointer still needs observation after the next successful weekly report run
Deterministic regime engine remains not promoted
Derived confidence remains not promoted
Macro policy pack schema modernization remains incomplete
Macro/thesis compliance and Dutch client-surface gates remain future work
Client-facing macro output remains governed by the existing validated report path
```

## Next action

Run/observe the new workflow:

```text
Validate ETF macro audit foundation
```

Accept WP18 only after the workflow is green and validation evidence is committed under:

```text
output/macro/validation/latest_wp18_macro_audit_foundation_validation.json
```

After WP18 closes, proceed to Phase 3 only as a separate shadow-only package:

```text
WP19 — Deterministic regime engine fixture baseline
```
