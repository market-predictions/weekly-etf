# Macro Policy Pack Schema Status

## Date
2026-05-31

## Status
Started / compatibility gate added. Not yet production-promoted deterministic regime authority.

## Current issue

After pricing-lineage closure, the next approved roadmap step is to formalize the macro policy pack contract before replacing legacy regime and confidence logic.

## Root cause

`runtime/build_macro_policy_pack.py` already feeds `output/macro/latest.json` into lane discovery. Without a schema/compatibility validator, later macro/regime changes could accidentally change the decision path before fixture replay, compliance gates, and bilingual checks exist.

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

The production workflow now validates the macro policy pack immediately after building it and before lane discovery consumes `output/macro/latest.json`.

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

## Validation status

Not yet confirmed by a fresh production workflow run after this patch set.

Next validation run should confirm:

```text
ETF_MACRO_POLICY_PACK_OK
ETF_MACRO_POLICY_PACK_SCHEMA_OK
ETF_LANE_DISCOVERY_OK
ETF_PRICING_LINEAGE_CONTRACT_OK
```

Do not claim the macro pack schema gate is production-proven until a run produces those markers and a successful manifest.

## Next action

Implement deterministic regime/confidence in shadow mode:

- `config/regime_thresholds.yml`
- `macro_regime/classify.py`
- `macro_regime/confidence.py`

The new engine should write shadow comparison fields first and must not change client-facing fundable decisions until fixture replay and compliance gates pass.
