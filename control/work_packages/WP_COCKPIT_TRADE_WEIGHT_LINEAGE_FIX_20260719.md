# Work Package — WP_COCKPIT_TRADE_WEIGHT_LINEAGE_FIX

Date: 2026-07-19
Repository: `market-predictions/weekly-etf`
Status: implementation complete / validated / ready for merge

## Current issue

The client cockpit correctly identifies the executed PAVE/XLU rotation, but its supporting before-and-after line can show identical weights, for example `PAVE 4.9% → 4.9%; XLU 0.5% → 0.5%`.

## Root cause

The guarded whole-share execution path calculated correct pre-trade and post-trade weights for the official ledger, but the subsequent cash reconciliation overwrote `previous_weight_pct`, `previous_market_value_*` and inherited weight fields with post-trade values. The report-state revaluation path then propagated that loss while retaining a material `shares_delta_this_run` and `weight_change_pct`.

The state contract did not preserve explicit pre-trade shares, and no validation gate rejected a material trade whose formatted before-and-after weights were identical.

## Implemented contract

1. Preserve an immutable pre-trade snapshot for each executed position: shares, local/EUR market value and portfolio weight.
2. Prefer the official trade-ledger snapshot when it is present.
3. Reconstruct legacy overwritten rows deterministically from current quantity plus recorded run deltas.
4. Reject material executed trades when the one-decimal client display has identical before-and-after weights.
5. Validate share and weight deltas before state persistence or report rendering.
6. Keep current market value as the NAV authority after previous-value lineage is restored.
7. Preserve no-trade position behavior and protected authority surfaces.

## Implementation

```text
runtime/trade_lineage.py
runtime/model_execution_guarded_auto.py
runtime/build_etf_report_state.py
tests/test_etf_trade_lineage.py
.github/workflows/validate-etf-whole-share-contract.yml
```

The shared helper eliminated the need to modify the renderer or execution engine. The existing cockpit renderer continues to consume `previous_weight_pct → current_weight_pct`; those fields are now normalized and validated upstream.

## Resulting client contract

```text
PAVE 0.0% → 4.9%
XLU 5.5% → 0.5%
```

The headline remains:

```text
PAVE added · XLU reduced
```

## Validation

```text
implementation_pull_request: 109
validated_head: 81e61a5039d28a60a9056156054dec84a8691d29
trade_lineage_and_whole_share_run: 29665973984 success
trade_lineage_and_whole_share_job: 88136341408 success
report_request_authority_run: 29665973971 success
report_request_authority_job: 88136341429 success
compile_gate: passed
focused_whole_share_and_trade_lineage_tests: passed
protected_execution_authority: unchanged
```

Focused regression coverage includes:

- legacy PAVE/XLU overwrite reconstruction;
- official ledger precedence;
- immutable pre-trade shares and value derivation;
- material identical-display rejection;
- no-trade snapshot behavior;
- report-state builder integration;
- cockpit English output contract.

## Acceptance status

- PAVE-like new purchases preserve a zero pre-trade quantity and weight: passed;
- XLU-like reductions preserve the full pre-trade quantity and weight: passed;
- guarded execution persists validated trade lineage: passed;
- legacy overwritten rows are repaired in report state: passed;
- a material trade cannot render identical one-decimal weights: passed;
- no-trade positions retain current snapshot defaults: passed;
- current NAV uses current market value after lineage restoration: passed;
- EN/NL renderer compatibility preserved: passed by shared numeric input contract;
- protected authority gate: passed;
- report generation or delivery performed: false.

## Authority boundary

```text
portfolio_state_mutated_by_this_package: false
trade_ledger_mutated_by_this_package: false
valuation_history_mutated: false
pricing_authority_changed: false
historical_report_mutated: false
production_report_generated: false
email_sent: false
```
