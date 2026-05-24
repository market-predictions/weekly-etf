# ETF Pricing Lineage Contract V1

## Purpose

This contract is the authority for the next ETF pricing hardening cycle. It exists because the report can now display fresh close rows that reconcile internally, while the repository can still lack a deterministic end-to-end proof that the displayed closes, runtime NAV, Section 7 equity curve, Section 15 holdings table, persisted portfolio state, valuation history, and delivery manifest all derive from the same immutable pricing audit.

The contract uses the stronger parts of the Weekly Index workflow as the operating template, but tightens the areas where Weekly Index is still incomplete: immutable audit identity, exact close-date semantics, provider symbol lineage, independent verification, and challenger-tier separation.

## Four-layer placement

### 1. Decision framework

Pricing lineage does not decide which ETF to own. It decides whether a report is allowed to present a valuation, action table, or fundable challenger as current.

A report may only present a holding as priced on the requested close date when the pricing layer can prove:

- the correct instrument was requested
- the provider returned a close for the intended close date, or the report explicitly labels the row as prior valid close
- the selected close type is known
- the value used for NAV equals the audit value
- the same value flows through runtime state, report tables, valuation history, and delivery manifest

### 2. Input / state contract

Pricing authority must flow in this order:

```text
requested_close_date + report_token
→ immutable pricing audit
→ explicit run manifest
→ runtime report state
→ English/Dutch report render
→ delivery assets
→ persisted portfolio state
→ persisted valuation history
```

No production step may silently reselect `latest price_audit_*.json` once a run manifest exists.

### 3. Output contract

The client report must remain readable and must not expose internal resolver names. It should show:

- requested close date
- close date used
- close used
- currency
- client-facing source label
- status label

The client report does not need to show provider URLs, raw JSON, cache keys, or internal handler names. Those belong in the audit and manifest.

### 4. Operational runbook

The workflow must fail before delivery if the pricing-lineage validator cannot prove audit-to-report-to-state consistency.

## Required run identity

Every production pricing run must have a run id.

Recommended format:

```text
YYYYMMDD_HHMMSS
```

Every pricing artifact for a production run must carry:

```json
{
  "run_id": "20260524_213000",
  "requested_close_date": "2026-05-22",
  "report_token": "260522"
}
```

## Required artifact names

The pricing audit must be immutable. Do not overwrite by run date only.

Required pattern:

```text
output/pricing/price_audit_<requested_close_date>_<run_id>.json
```

Example:

```text
output/pricing/price_audit_2026-05-22_20260524_213000.json
```

The runtime state should likewise be run-scoped:

```text
output/runtime/etf_report_state_<requested_close_date>_<run_id>.json
```

The run manifest should be stored centrally under:

```text
output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json
```

## Required manifest fields

The manifest is the bridge between pricing, runtime, report, and delivery.

Minimum schema:

```json
{
  "run_id": "20260524_213000",
  "requested_close_date": "2026-05-22",
  "report_token": "260522",
  "pricing_audit_path": "output/pricing/price_audit_2026-05-22_20260524_213000.json",
  "runtime_state_path": "output/runtime/etf_report_state_2026-05-22_20260524_213000.json",
  "english_report_path": "output/weekly_analysis_pro_260522.md",
  "dutch_report_path": "output/weekly_analysis_pro_nl_260522.md",
  "portfolio_state_path": "output/etf_portfolio_state.json",
  "valuation_history_path": "output/etf_valuation_history.csv",
  "delivery_manifest_path": null,
  "pricing_lineage_status": "pending | passed | failed"
}
```

## Required price row schema

Each price result row in the audit must contain enough lineage to prove what was priced.

Minimum holding / valuation-grade row fields:

```json
{
  "symbol": "SPY",
  "asset_role": "holding | replacement_duel_challenger | promoted_discovery_challenger | research_only_candidate",
  "pricing_tier": "valuation_grade | research_grade",
  "provider_symbol": "SPY",
  "provider_exchange": "NYSE Arca or provider-specific equivalent when available",
  "requested_close_date": "2026-05-22",
  "returned_close_date": "2026-05-22",
  "raw_close": 745.64,
  "adjusted_close": null,
  "selected_close": 745.64,
  "selected_close_type": "raw_close | adjusted_close | provider_close | prior_valid_close",
  "currency": "USD",
  "source": "twelve_data",
  "source_detail": "time_series",
  "provider_timestamp": null,
  "provider_timezone": null,
  "is_final_eod_bar": true,
  "status": "fresh_exact_close",
  "confidence": "high",
  "verification": {
    "source": "yahoo_history",
    "selected_close": 745.64,
    "returned_close_date": "2026-05-22",
    "delta_abs": 0.0,
    "delta_pct": 0.0,
    "status": "passed"
  }
}
```

## Required status semantics

Use explicit status labels. Do not collapse prior valid data into a generic fresh label.

Allowed production status labels:

- `fresh_exact_close` — returned close date equals requested close date and the close passed validation rules.
- `fresh_exact_unverified` — returned close date equals requested close date, but independent verification was unavailable.
- `prior_valid_close` — source returned the latest valid close before the requested close date. This is acceptable only when the market/calendar makes that date valid or when the report labels it clearly.
- `carried_forward` — no fresh/prior provider row was obtained and prior stored close is reused.
- `unresolved` — no valid price may be used.
- `blocked` — the row or run must not be used for valuation.

Client-facing labels should be readable, for example:

- Fresh exact close
- Fresh exact close, unverified
- Prior valid market close
- Carried forward
- Unresolved
- Blocked

## Required provider-symbol contract

The source registry must stop relying only on plain ticker symbols where a provider-specific symbol or exchange qualifier is needed.

For every current holding and valuation-grade challenger, the symbol registry should be able to express:

```yaml
SPY:
  canonical_symbol: SPY
  currency: USD
  provider_symbols:
    twelve_data: SPY
    yahoo_history: SPY
    fmp: SPY
    alpha_vantage: SPY
  expected_exchange: NYSE Arca
```

Provider exchange availability may differ by source. Missing exchange data is acceptable only if recorded as unavailable, not silently ignored.

## Challenger pricing tiers

Challenger coverage must be explicit.

### Tier 1 — valuation-grade

Must receive full pricing lineage before it can be presented as fundable or replacement-ready.

Includes:

- current holdings
- direct replacement-duel challengers
- discovery candidates promoted to actionable/fundable status

### Tier 2 — research-grade

May use relative-strength and broad-history pricing for ranking, but cannot be presented as fundable without promotion to Tier 1.

Includes:

- broad discovery universe
- early watchlist lanes
- candidates shown as research-only or not-yet-fundable

## Required validator

Add a hard validator:

```text
tools/validate_etf_pricing_lineage_contract.py
```

It must fail unless all required conditions are true:

1. A manifest exists for the current run.
2. The manifest points to one exact pricing audit.
3. The runtime state `source_files.pricing_audit` equals that exact audit path.
4. Disclosure table values equal audit selected closes.
5. Runtime position prices equal audit selected closes for all holdings.
6. Section 15 position values equal runtime values.
7. Latest Section 7 NAV equals Section 15 total NAV.
8. Recalculated NAV from shares × selected close ÷ FX + cash equals reported NAV within tolerance.
9. `output/etf_portfolio_state.json` is updated after successful pricing and matches runtime NAV.
10. `output/etf_valuation_history.csv` contains the current requested close date after successful pricing.
11. No row is labeled fresh unless returned close date equals requested close date.
12. Any valuation-grade challenger surfaced as fundable has a valuation-grade price row.

## Implementation phases

### Phase A — control and design

- Add this contract.
- Add the dedicated pricing-lineage changelog.
- Register both files in `control/SYSTEM_INDEX.md`.
- Update `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md` so pricing lineage becomes the active engineering priority.

### Phase B — immutable run identity

- Add a run id resolver.
- Make pricing audit filenames immutable.
- Write a run manifest.
- Pass exact paths through the workflow.

### Phase C — audit schema upgrade

- Extend price rows with selected close, close type, provider symbol, provider exchange, finality, verification, and pricing tier.
- Split current statuses into exact/prior/carried/unresolved/blocked semantics.

### Phase D — state persistence

- Persist `output/etf_portfolio_state.json` from the successful pricing/runtime state.
- Append or replace the current requested close date in `output/etf_valuation_history.csv` deterministically.

### Phase E — challenger-tier enforcement

- Keep broad discovery as research-grade.
- Promote replacement-duel and actionable candidates to valuation-grade pricing.
- Block fundable challenger presentation when valuation-grade pricing is missing.

### Phase F — hard validation and delivery block

- Add `tools/validate_etf_pricing_lineage_contract.py`.
- Run it before render/send.
- Include pricing-lineage status in the delivery/run manifest.

## Authority rule

Until the validator exists and is wired into the workflow, reports can be internally consistent but not yet fully lineage-proven. Do not describe the pricing problem as solved merely because the closing-price table is visible or because Section 7 reconciles visually.
