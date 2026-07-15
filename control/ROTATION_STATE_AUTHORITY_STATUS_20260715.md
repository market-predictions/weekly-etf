# Rotation State Authority Status — 2026-07-15

Repository: `market-predictions/weekly-etf`
Work package: `WP_ROTATION_STATE_AUTHORITY_AND_ALT_CANDIDATES`
PR: #58

## Status

```text
implementation: complete
focused_validation: passed
production_artifact_replay: passed
merge: pending
fresh_production_run: pending
production_delivery_proof: pending
```

## Defect closed at PR level

The rotation engine no longer treats prior scorecard valuation fields as current authority. It now:

- derives current values and weights from the current pricing audit;
- reconstructs missing average entries from official model-execution history;
- recomputes P/L from current close and average entry;
- refreshes the canonical scorecard before release scoring;
- blocks date, price, average-entry and P/L inconsistencies;
- evaluates primary and alternative ETFs independently;
- uses quality evidence to resolve capped destination-score ties.

## Final clean validation

```text
head_sha: 68432f65e2c19e039956bc129d3a484d46ce9b78
workflow_run_id: 29438154551
job_id: 87429929415
conclusion: success
focused_tests: 10 passed
```

## Actual July replay proof

```text
report_date: 2026-07-14
validated_holding_count: 9
NAV_EUR: 110224.85
average_entry_authority_complete: true
scorecard_date_aligned: true
pnl_consistent_with_current_close_and_avg_entry: true
current_price_consistent: true
trade_intent_count: 1
source: URNM
destination: XBI
source_delta_weight_pct: -5.00
destination_delta_weight_pct: +5.00
estimated_notional_EUR: 5511.24
```

## Recomputed incumbent P/L used by the replay

```text
CIBR: +1.05%
DFEN: +3.28%
GSG: -2.52%
IEFA: -0.08%
PAVE: +9.10%
SMH: +42.89%
SPY: +11.16%
URNM: -23.57%
XLU: +4.08%
```

## Authority boundary

This status proves implementation and replay correctness only. It does not claim that official portfolio state, trade ledger, reports or email delivery have changed. Those changes require merge and a fresh production workflow run.