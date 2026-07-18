# Decision — Cockpit trade-weight lineage

Date: 2026-07-19
Repository: `market-predictions/weekly-etf`
Decision status: accepted
Work package: `WP_COCKPIT_TRADE_WEIGHT_LINEAGE_FIX`
Implementation PR: #109

## Decision

Executed ETF positions must carry two independent valuation surfaces:

- the current/post-trade quantity, value and portfolio weight used for NAV and current reporting;
- an immutable pre-trade quantity, value and portfolio weight used to explain the executed action.

The official trade ledger is the preferred source for pre-trade and post-trade weights. Where historical state has already overwritten its pre-trade fields, the report-state builder may reconstruct them from current shares plus `shares_delta_this_run`, and from current weight minus `weight_change_pct`.

A material executed trade is invalid for client reporting when its one-decimal before-and-after weights are identical. Validation must fail before persistence or rendering rather than allowing an intuitive but false action line.

## Consequences

- current NAV remains based on current market value;
- new purchases can show an explicit zero starting weight;
- partial reductions retain the original quantity and weight context;
- no-trade rows use the current snapshot as both previous and current;
- the cockpit renderer remains simple and receives already-normalized state;
- future state writers cannot silently erase trade lineage without failing focused tests or the runtime validation gate.

## Rejected alternatives

- hiding the supporting line: rejected because it removes useful allocation context;
- displaying only share deltas: rejected because portfolio-weight impact remains important;
- cosmetically changing the arrow or labels: rejected because the underlying data would remain false;
- patching only the historical HTML: rejected because it would not correct future report generation.
