# Weekly ETF Report Request

requested_at_utc: 2026-07-15T17:58:20Z
repository: market-predictions/weekly-etf
report_scope: standard U.S. Weekly ETF Pro report
explicit_exclusion: not ETF EU, not UCITS
trigger_reason: production proof after merge of PR #58 rotation current-run authority fix
merge_sha: b9e7ffb615ad4c7052e1d72f5bcc91b44b0fa3f0

## Required execution

Run the complete production workflow on `main` using the latest completed U.S. regular-session close permitted by the workflow cutoff.

Required steps:

1. Refresh holding and challenger pricing.
2. Refresh relative-strength discovery and lane scoring.
3. Derive current-run valuation authority before rotation.
4. Reconstruct any missing average entry from official model-execution history.
5. Refresh and persist the current-run recommendation scorecard.
6. Build the deterministic rotation plan with primary and alternative ETFs independently selectable.
7. Execute the guarded model mutation if all hard policy and validation gates pass.
8. Persist official portfolio state, trade ledger, scorecard, rotation plan, execution artifact and valuation history.
9. Rebuild the final post-execution English and Dutch reports.
10. Run all pricing, state, execution, report, delivery and manifest validators.
11. Render HTML/PDF and send both U.S. Weekly ETF editions.
12. Persist immutable run and delivery evidence.

## Required production proof

- current-run scorecard date equals the requested close date;
- current prices and P/L agree with current close and authoritative average entry;
- average-entry authority is complete for every holding;
- any mutation is reflected in official state and trade ledger;
- final reports describe executed state, not proposed or pending state;
- run manifest records workflow success and pricing-lineage pass;
- delivery manifest records both English and Dutch delivery attempts;
- end-recipient inbox receipt must be checked separately after delivery.

This request authorizes the normal guarded model-portfolio execution defined by the production workflow. It does not authorize broker execution.