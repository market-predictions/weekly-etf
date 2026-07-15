# ETF Post-Execution Report Consistency — Changelog

Repository: `market-predictions/weekly-etf`
Work package: `WP_POST_EXECUTION_REPORT_CONSISTENCY`

## 2026-07-15 — Production surface contradiction identified

Production run `20260715_175910` executed and persisted one guarded model rotation:

```text
URNM: Sell -122.008961 shares; model weight 7.01% -> 2.01%
XBI: Buy +40.491749 shares; model weight 0.00% -> 5.00%
```

Authority sources:

```text
output/runtime/etf_model_execution_20260714_20260715_175910.json
output/etf_portfolio_state.json
output/etf_trade_ledger.csv
```

The first delivered English and Dutch reports mixed correct execution evidence with stale no-action wording. Earlier intermediate share quantities were superseded by the official execution artifact and ledger values above.

## 2026-07-15 — Output-authority decision

Stable rule introduced:

```text
executed_model_changes is authoritative for all post-execution action wording and classification.
```

Official portfolio state remains authoritative for post-execution holdings and values. Official trade ledger remains authoritative for executed share deltas. `suggested_action` is research memory only after execution.

## 2026-07-15 — Implementation completed

Added deterministic post-execution action classification and bilingual report surfaces, including:

- dynamic main takeaways;
- dynamic English and Dutch decision cockpits;
- executed Add, Reduce and Close buckets;
- executed-action labels in final action tables;
- aligned Sections 1, 2, 12, 13, 14 and 15;
- a blocking cross-section consistency validator;
- delivery HTML cockpit generation from corrected Markdown;
- a dedicated correction-resend workflow that does not rerun the model mutation.

The validator rejects:

- no-action wording when executed changes exist;
- a changed ticker in the wrong Section 2 action bucket;
- a changed ticker in the wrong Section 12 action column;
- a Section 13 row without the correct executed-action label;
- delivery HTML cockpit wording that contradicts corrected Markdown.

## 2026-07-15 — Validation completed

Final read-only validation:

```text
workflow: Validate ETF post-execution report consistency
run_id: 29442287444
conclusion: success
```

Verified:

- affected modules compile;
- focused Markdown and HTML tests pass;
- exact execution artifact replays without model re-execution;
- portfolio-state hash remains unchanged;
- trade-ledger hash remains unchanged;
- English and Dutch action surfaces agree with URNM reduction and XBI addition;
- English and Dutch delivery cockpits contain no stale no-action wording.

## 2026-07-15 — Merge-ready status

PR #59 is governance-complete and may be promoted from draft and merged.

Merge is not the delivery closeout. After merge, one explicitly confirmed correction resend must create corrected EN/NL reports and positive delivery evidence. Inbox receipt confirmation remains required before the package is fully closed.