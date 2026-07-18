# Work Package Claim

```text
package: WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW
repository: market-predictions/weekly-etf
claimed_by: ChatGPT
claimed_at_utc: 2026-07-17T23:38:20Z
implementation_branch: agent/portfolio-close-first-execution-review
implementation_pull_request: 95
implementation_merge: 2895bbb5940ead8526ab4c10d0ce3687f8aca423
closeout_branch: agent/portfolio-close-first-execution-review-closeout
closeout_pull_request: 96
closeout_merge: pending
status: closeout_ready / release_effective_on_merge
scope: read-only evidence review, deterministic source comparison, transition validation, governance closeout
```

Confirmed boundaries:

- official portfolio state unchanged;
- trade ledger unchanged;
- valuation history unchanged;
- pricing pointers unchanged;
- historical reports unchanged;
- production report not generated;
- email not sent;
- any later portfolio change requires separate approval.

Review result:

```text
selected_source_for_review: URNM
reviewed_quantity: 48 whole shares
destination: cash
estimated_proceeds_eur: 2022.23
projected_cash_eur: 4556.59
projected_active_count: 8
portfolio_change_applied: false
```

Final same-head validation:

```text
validated_head: bbf03f8966c93d714ff750c9d177917bcc0eef9d
review_run: 29622792895 success
position_count_run: 29622792864 success
report_language_run: 29622792867 success
current_runtime_cockpit_run: 29622792888 success
wp08_run: 29622792861 success
wp11_run: 29622792862 success
focused_tests: 7 passed
artifact_id: 8422761924
artifact_digest: sha256:1526642d997b2c9055554a3bab969ba84d1bafdf103285af00056fb7f96eae29
protected_authority_hashes: identical
historical_report_hashes: identical
```

The claim is released when PR #96 merges. The exact closeout merge will then be recorded in a metadata-only closeout correction.
