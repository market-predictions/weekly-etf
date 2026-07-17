# ETF Whole-Share State Contract Decision

Date: 2026-07-17
Status: accepted for implementation

## Decision

The official U.S. Weekly ETF model portfolio will use whole shares only.

Legacy fractional holdings will be reconciled once using current persisted pricing and FX authority. Fractional remainders are floored and transferred to cash. Tickers explicitly prohibited by current portfolio constraints may be closed in full during that reconciliation. For the current migration, `DFEN` is designated for full policy close because leveraged ETFs are not allowed.

Future guarded execution must:

1. begin from a whole-share-compliant official state;
2. sell and buy whole units only;
3. never round a long-only quantity upward beyond available source units or funded destination capacity;
4. transfer unspent proceeds to EUR cash;
5. preserve NAV within EUR 0.05;
6. fail closed when the official state or the resulting artifact violates the contract.

## Authority hierarchy

```text
decision framework: whole shares only
input/state authority: output/etf_portfolio_state.json
execution evidence: guarded execution artifact + output/etf_trade_ledger.csv
migration evidence: etf_whole_share_reconciliation artifact
cash authority: explicit residual EUR cash after whole-unit execution
```

## Rollback boundary

This decision does not rewrite historical reports or historical ledger rows. It changes current official state through a separately authorized reconciliation and applies prospectively to guarded model execution.

## Roadmap relationship

This state-contract repair blocks `WP_COCKPIT_SURFACE_11_PRODUCTION_ENABLEMENT_CLOSEOUT`. Product-surface promotion resumes only after whole-share reconciliation evidence is persisted and validated.
