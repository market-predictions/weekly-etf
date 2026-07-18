# Work Package Claim

```text
package: WP_COCKPIT_TRADE_WEIGHT_LINEAGE_FIX
repository: market-predictions/weekly-etf
claimed_by: ChatGPT
claimed_at_utc: 2026-07-18T23:39:00Z
branch: agent/fix-trade-weight-lineage
implementation_pull_request: 109
implementation_merge: 85d82930e40d37c145727d14468dc8914e041e00
merged_at_utc: 2026-07-18T23:56:26Z
status: closed / released
```

Scope was limited to preserving and validating pre-trade quantity/value/weight lineage for executed ETF report actions and correcting the cockpit before/after presentation.

Validation completed before release:

```text
trade_lineage_and_whole_share_run: 29666054365 success
trade_lineage_and_whole_share_job: 88136546831 success
report_request_authority_run: 29666054332 success
report_request_authority_job: 88136546755 success
```

Confirmed at release:

- implementation PR #109 merged to `main`;
- PAVE-like purchases preserve zero pre-trade shares and weight;
- XLU-like reductions preserve full pre-trade shares and weight;
- material identical before/after client weights fail validation;
- current NAV remains based on current market value;
- protected execution authority remained unchanged;
- no production report was generated or sent;
- no historical delivered package was changed.
