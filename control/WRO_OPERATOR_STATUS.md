# WRO-GAP-50 — read-only operator status

The operator view is a stdout-only projection of one explicitly selected existing
release-assurance record and its source files. It creates no state store and does
not select a latest report, generate assurance, alter Control queues, send mail,
or invoke portfolio/trade code.

Run from the repository root:

```bash
python -m tools.wro_operator_status --assurance PATH_TO_ASSURANCE \
  --source-sha EXACT_REPORT_SOURCE_SHA --run-id EXACT_RUN_ID \
  --close-date YYYY-MM-DD --report-token YYMMDD
```

The JSON includes requested identity, existing quality checks and artifact
identities, seven WRO prerequisite gates, authorization, delivery evidence status,
and explicit blockers. Exit code 1 means BLOCKED. Missing/malformed assurance,
identity mismatch, incomplete inventory, changed or missing bytes fail closed.
The existing assurance validator is reused; hashes are additionally checked
against the actual files and manifest paths must match the selected package.
Relative source paths retain the existing repository-root interpretation.

## Current evidence limits

Legacy ETF assurance proves its scoped identity/format/numeric checks. It does
not prove all seven gates in WRO_DELIVERY_READINESS_CONTRACT_V1: complete material
claim lineage/freshness, conflict resolution, full deterministic QA, canonical
bilingual state, recommendations versus executions, exact-candidate independent
lifecycle assurance, and absence of unresolved WRO blockers. Those gates remain
UNPROVEN. Existing report requests also provide no governed exact-package
principal delivery authority binding. Authorization therefore remains BLOCKED;
no broader or older request is inherited. Delivery is UNPROVEN, never inferred
from workflow or assurance success. Thus current legacy evidence cannot produce
a ready/authorized status. This is an evidence limitation, not send authority.

No new QA/authorization record contract is invented here. Later governed evidence
can extend this projection once its canonical source contract exists. Tests cover
valid legacy evidence remaining blocked, identity mismatch, malformed/missing
assurance, tampering, missing artifacts, inventory gaps and absence of writes.
The existing release-assurance CI also runs these regressions.
