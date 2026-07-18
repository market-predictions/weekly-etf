# Decision — Fresh ETF Delivery Recovery

Date: 2026-07-18
Repository: `market-predictions/weekly-etf`
Status: stable

## Decision

A failed GitHub Actions delivery run must be classified from the actual failing step rather than inferred from the absence of an email.

For the 2026-07-17 Weekly ETF delivery:

- GitHub Actions credits were not the cause;
- a hosted runner was allocated and executed the render chain;
- the blocking condition was the client-surface clean gate;
- the uncovered internal labels were repaired in the shared language contract;
- the already-generated reports were delivered through a transport-only recovery;
- no portfolio or broker execution was authorized.

## Stable rules

1. A normal Actions-minute credit block occurs before a job executes its workflow steps. When a runner performs pricing, rendering or validation, inspect the first failing step instead of attributing the failure to credits.
2. Client-surface cleanup must cover headings, plural labels and table values, not only sentence patterns with numeric values.
3. A transport-only recovery may reuse persisted reports only when no prior delivery manifest or inbox receipt exists.
4. Recovery must preserve official share quantities and the trade ledger.
5. Delivery success requires both a successful delivery manifest and independent English and Dutch inbox receipts.
6. Once those receipts exist, the source run is closed against further automatic resends.

## Implementation evidence

```text
client-language fix PR: #105
client-language fix merge: bfba7c2e038eaba9a071008fc33fe09832dd4f5c
recovery retrigger PR: #106
recovery retrigger merge: ba558abf9c79ecd2066ebe8fc57db41a9c9c44ee
delivery evidence commit: a1e5dad7a5a1957ddbe9f1bc750a9c33c45384ea
```
