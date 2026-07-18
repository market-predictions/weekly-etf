# Work Package Claim

```text
package: WP_FRESH_REPORT_DELIVERY_REQUEST_AUTHORITY
repository: market-predictions/weekly-etf
claimed_by: ChatGPT
claimed_at_utc: 2026-07-18T12:53:24Z
branch: agent/fresh-report-delivery-authority-pr
pull_request: 101
status: implementation_validated / merge_pending / production_delivery_pending
scope: fail-closed report-request execution authority, fresh 2026-07-17 production report and delivery proof
```

Boundaries:

- fresh report generation and bilingual delivery are authorized;
- portfolio execution is not authorized;
- official share quantities and trade ledger may not change;
- valuation refresh and immutable run/delivery evidence are allowed;
- delivery success requires a manifest and independent inbox receipt.

Validation:

```text
validated_head: 6e85cef34a5ee8ca5aa6054c9bcac6e4e550d1f3
request_authority_run: 29646313346 success
whole_share_run: 29646313337 success
portfolio_execution_authorized: false
delivery_authorized: true
```

The claim remains active until the production workflow, delivery manifest and both inbox receipts are complete.