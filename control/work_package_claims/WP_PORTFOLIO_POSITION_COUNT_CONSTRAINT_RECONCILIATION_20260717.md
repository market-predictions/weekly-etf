# Work Package Claim

```text
package: WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION
repository: market-predictions/weekly-etf
claimed_by: ChatGPT
claimed_at_utc: 2026-07-17T16:40:00Z
branch: agent/position-count-constraint-reconciliation
pull_request: 91
status: implementation_complete / validation_green / merge_pending
scope: decision rule, input/state contract, guarded execution preflight, output contract, validation, governance closeout
```

Authority boundary:

- current official portfolio state remains unchanged;
- no trade-ledger or valuation-history mutation;
- no report generation or email delivery;
- every non-zero whole-share position counts toward the maximum;
- the current nine-position state is handled as `close_first`, not by a silent residual exemption.

Validation:

```text
primary_run: 29617207278
primary_job: 88004737784
focused_tests: 13 passed
artifact_id: 8420903168
report_surface_regression: 29617207295 success
closed_recovery_regression: 29617207264 success
fresh_send_diagnostic_regression: 29617207249 success
protected_authority_hashes: identical
historical_report_hashes: identical
portfolio_execution: false
email_sent: false
```

The claim remains held only through merge and exact post-merge handover recording. It must then be marked closed/released.
