# Work Package Claim

```text
package: WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION
repository: market-predictions/weekly-etf
claimed_by: ChatGPT
claimed_at_utc: 2026-07-17T16:40:00Z
branch: agent/position-count-constraint-reconciliation
status: active
scope: decision rule, input/state contract, guarded execution preflight, output contract, validation, governance closeout
```

Authority boundary:

- current official portfolio state remains unchanged;
- no trade-ledger or valuation-history mutation;
- no report generation or email delivery;
- every non-zero whole-share position counts toward the maximum;
- the current nine-position state is handled as `close_first`, not by a silent residual exemption.
