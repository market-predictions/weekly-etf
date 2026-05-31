# Macro Policy Pack Schema Status

## Date
2026-05-31

## Status
Compatibility gate added and production-proven by fresh workflow run. Deterministic regime authority is still not promoted.

## Current issue

After pricing-lineage closure, the next approved roadmap step was to formalize the macro policy pack contract before replacing legacy regime and confidence logic.

## Root cause

`runtime/build_macro_policy_pack.py` already feeds `output/macro/latest.json` into lane discovery. Without a schema/compatibility validator, later macro/regime changes could accidentally change lane scoring before fixture replay, compliance gates, and bilingual checks exist.

## What changed

Added:

- `schemas/macro_policy_pack.schema.json`
- `tools/validate_macro_policy_pack.py`

Updated:

- `runtime/build_macro_policy_pack.py`
- `.github/workflows/send-weekly-report.yml`
- `control/SYSTEM_INDEX.md`

## Contract now enforced

The macro policy pack must include:

- `schema_version`
- `authority`
- `macro_data_audit_summary`
- `regime`
- `confidence_decomposition`
- `central_banks`
- `macro_signals`
- `policy_catalysts`
- `cross_asset_confirmation`
- `portfolio_implications`
- `lane_adjustments`
- `active_drivers`
- `regime_memory`
- `report_transfer`

## Authority rules

- `lane_adjustments` remains available for backward-compatible lane discovery.
- Phase 2 macro audit remains shadow-only and non-authoritative.
- `active_drivers` exists as an empty placeholder until WP-9 is implemented in shadow mode.
- `confidence_decomposition` is explanatory only for now.
- The deterministic regime/confidence engine is not yet production authority.

## Workflow integration

The production workflow validates the macro policy pack immediately after building it and before lane discovery consumes `output/macro/latest.json`.

Expected marker:

```text
ETF_MACRO_POLICY_PACK_SCHEMA_OK
```

## Commits

- `7dbaadaaa66ffa44a84b5cd9682619aac0a5828c` — add macro policy pack schema
- `296559dc4e84c12124a46ef9217106ed0c2602fb` — add macro policy pack validator
- `54e1f3d8b6408266bd98c72f585d693c24e3bbf4` — add schema compatibility fields to macro pack builder
- `cacfe1de2546b75303793158ffcaf42577ba5b63` — validate macro policy pack before lane discovery
- `1690c5f53c8f1200e5a710fc2e8d0be0411bb8c6` — register macro policy pack schema/validator in system index
- `133e475caa30f46c08b528a213a6bf5ce77390ed` — add this schema status note

## Validation evidence

Fresh workflow validation passed after the schema-gate patch set.

Evidence:

```text
run_id: 20260531_203900
requested_close_date: 2026-05-29
workflow_conclusion: success
pricing_lineage_status: passed
english_report_path: output/weekly_analysis_pro_260529_23.md
dutch_report_path: output/weekly_analysis_pro_nl_260529_23.md
macro_pack_path: output/macro/etf_macro_policy_pack_20260529_20260531_203900.json
runtime_state_path: output/runtime/etf_report_state_20260529_20260531_203900.json
pricing_audit_path: output/pricing/price_audit_2026-05-29_20260531_203900.json
total_portfolio_value_eur: 109964.97
```

The generated macro pack includes:

```text
schema_version: 1.0
authority.shadow_only: true
authority.client_facing_authority: false
authority.decision_impact: legacy_lane_adjustments_only
macro_data_audit_summary.decision_impact: none_phase2_audit_only
regime.confidence_source: legacy_proxy_static
confidence_decomposition.decision_impact: none_shadow_explanation_only
active_drivers: []
```

The schema gate is therefore production-proven as a compatibility/regression guard. It does not promote deterministic regime authority.

## Delivery caveat

The run manifest still has:

```text
delivery_manifest_path: null
```

So workflow success and pricing-lineage success are proven, but independent email delivery receipt is not proven by this manifest alone.

## Next action

Implement deterministic regime/confidence in shadow mode:

- `config/regime_thresholds.yml`
- `macro_regime/classify.py`
- `macro_regime/confidence.py`

The new engine should write shadow comparison fields first and must not change client-facing fundable decisions until fixture replay and compliance gates pass.
