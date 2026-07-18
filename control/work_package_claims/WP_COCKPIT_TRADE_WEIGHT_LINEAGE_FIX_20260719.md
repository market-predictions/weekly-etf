# Work Package Claim

```text
package: WP_COCKPIT_TRADE_WEIGHT_LINEAGE_FIX
repository: market-predictions/weekly-etf
claimed_by: ChatGPT
claimed_at_utc: 2026-07-18T23:39:00Z
branch: agent/fix-trade-weight-lineage
status: active
```

Scope is limited to preserving and validating pre-trade quantity/value/weight lineage for executed ETF report actions and correcting the resulting cockpit before/after presentation.

Protected authority surfaces are not to be mutated by this package:

- `output/etf_portfolio_state.json`;
- `output/etf_trade_ledger.csv`;
- `output/etf_valuation_history.csv`;
- pricing and runtime pointers;
- historical delivered HTML/PDF/Markdown;
- delivery manifests.

No report generation, portfolio execution, broker execution or email delivery is authorized.
