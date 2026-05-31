# Macro Audit Foundation Status

## Status date
2026-05-31

## Phase
Phase 2 — Macro audit foundation / WP-1

## Status
Implemented in shadow mode. Needs fresh workflow validation.

## Authority rule
The macro audit foundation is an input/provenance layer only. It may fetch and validate FRED, ECB, Treasury, and volatility observations, but it must not set regime, confidence, lane scoring, fundability, portfolio actions, or client-facing report wording until later deterministic regime, methodology, compliance, and bilingual gates explicitly promote it.

## Four-layer placement

### 1. Decision framework
The macro audit does not decide allocation or portfolio action. It only proves that official/public macro observations were fetched, timestamped, attributed, and checked for freshness.

### 2. Input/state contract
Every observation must carry:

- `key`
- `value`
- `units`
- `source`
- `series_id`
- `label`
- `category`
- `as_of_date`
- `fetched_at_utc`
- `staleness_days`
- `max_staleness_days`
- `status`

Required source groups:

- FRED
- ECB
- Treasury Fiscal Data
- volatility

### 3. Output contract
The output is an internal JSON audit artifact:

```text
output/macro/macro_data_audit_<reference_date>_<run_id>.json
```

The latest pointer is:

```text
output/macro/latest_macro_data_audit_path.txt
```

The macro policy pack records the audit path and summary, but marks it:

```text
shadow_only = true
client_facing_authority = false
decision_impact = none_phase2_audit_only
```

### 4. Operational runbook
`runtime/build_macro_policy_pack.py` now builds and validates the macro audit before writing `output/macro/latest.json`.

Expected workflow markers after a fresh run:

```text
ETF_MACRO_DATA_AUDIT_OK
ETF_MACRO_DATA_AUDIT_VALID_OK
ETF_MACRO_POLICY_PACK_OK ... macro_audit_present=True
```

Fixture replay is available with:

```text
MRKT_RPRTS_MACRO_DATA_AUDIT_FIXTURE=tests/fixtures/macro_data_audit_fixture.json
```

## Implemented files

- `config/macro_data_sources.yml`
- `config/cb_calendar.yml`
- `macro_sources/__init__.py`
- `macro_sources/common.py`
- `macro_sources/fred_client.py`
- `macro_sources/ecb_client.py`
- `macro_sources/treasury_client.py`
- `macro_sources/vol_client.py`
- `macro_sources/cb_calendar.py`
- `macro_sources/build_macro_data_audit.py`
- `schemas/macro_data_audit.schema.json`
- `tools/validate_macro_data_audit.py`
- `tests/fixtures/macro_data_audit_fixture.json`
- `runtime/build_macro_policy_pack.py`

## Not yet done

- Fresh workflow validation has not yet been observed.
- The deterministic regime engine is not implemented yet.
- Derived confidence is not implemented yet.
- Macro policy pack schema modernization is not complete.
- Macro/thesis compliance and Dutch client-surface gates are not implemented yet.
- Client-facing macro output remains governed by the existing validated report path.

## Next action
Run a fresh ETF workflow and verify the macro audit markers plus existing pricing-lineage and delivery markers before starting Phase 3.
