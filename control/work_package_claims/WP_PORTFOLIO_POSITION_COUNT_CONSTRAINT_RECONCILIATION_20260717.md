# Work Package Claim

```text
package: WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION
repository: market-predictions/weekly-etf
claimed_by: ChatGPT
claimed_at_utc: 2026-07-17T16:40:00Z
implementation_branch: agent/position-count-constraint-reconciliation
implementation_pull_request: 91
implementation_merge: 0bcb6af7e243775d876b59719ce9898fa97c690f
closeout_branch: agent/position-count-constraint-closeout
closeout_pull_request: 92
status: closed / released
released_at_utc: 2026-07-17T22:45:00Z
scope: decision rule, input/state contract, guarded execution preflight, output contract, validation, governance closeout
```

Authority boundary confirmed at release:

- official portfolio state unchanged;
- trade ledger unchanged;
- valuation history unchanged;
- historical report files unchanged;
- no portfolio execution;
- no report generation;
- no email delivery;
- every non-zero whole-share position counts toward the maximum;
- the current nine-position state is handled as `close_first`, not by a silent residual exemption.

Validation:

```text
focused_tests: 13 passed
artifact_id: 8420903168
artifact_digest: sha256:cf98f8d4b4d172bc4f463598a557e8490fd2f188bbd5ae3f0c34347ee1688b5b
final_position_count_run: 29618185729 success
final_report_surface_run: 29618185736 success
final_current_runtime_cockpit_run: 29618185701 success
final_wp08_run: 29618185711 success
final_wp11_run: 29618185709 success
final_closed_recovery_run: 29618185751 success
final_fresh_send_diagnostic_run: 29618185706 success
protected_authority_hashes: identical
historical_report_hashes: identical
portfolio_execution: false
email_sent: false
```

The claim is released. A future `WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW` requires a new claim and separate explicit authorization before any real mutation.
