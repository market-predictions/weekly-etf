# WRO read-only operator status

The operator view is a stdout-only projection of one explicitly selected existing
release-assurance record and its source files. It creates no state store and does
not select a latest report, persist assurance, alter Control queues, send mail,
or mutate portfolio/trade state.

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

Add `--format text` for a compact operator summary of the exact package,
including the recorded SHA-256 hash of each artifact, delivery authorization,
delivery evidence and every blocker. The default
`--format json` remains the default. Both formats use the same read-only
projection and exit code; the text view does not add readiness or delivery
authority.

## Current evidence limits

Legacy ETF assurance proves its scoped identity/format/numeric checks. It does
not prove all seven gates in WRO_DELIVERY_READINESS_CONTRACT_V1: complete material
claim lineage/freshness, conflict resolution, full deterministic QA, canonical
bilingual state, recommendations versus executions, exact-candidate independent
lifecycle assurance, and absence of unresolved WRO blockers. Those gates remain
UNPROVEN unless existing exact-package checks demonstrate a failure, in which
case the affected gates report FAIL. `wro_gate_evidence` shows each reused check,
its result and the remaining proof limitation. The operator recomputes legacy
QA without writing a new assurance record, validates bound report freshness,
pricing/runtime consistency where available and explicit runtime trade lineage.
A legitimate legacy FAIL record can be inspected; send/release validation still
requires PASS by default. Contradictions between stored and recomputed checks
remain blockers. Passing partial checks never certifies a complete WRO gate.

Existing report requests also provide no governed exact-package
principal delivery authority binding. Authorization therefore remains BLOCKED;
no broader or older request is inherited. Delivery is UNPROVEN, never inferred
from workflow or assurance success. Thus current legacy evidence cannot produce
a ready/authorized status. This is an evidence limitation, not send authority.

No new QA/authorization record contract is invented here. Later governed evidence
can extend this projection once its canonical source contract exists. Tests cover
valid legacy evidence remaining blocked, identity mismatch, malformed/missing
assurance, tampering, missing artifacts, inventory gaps and absence of writes.
The existing release-assurance CI also runs these regressions, including stale
claims, bilingual divergence and executions without supporting trade lineage.

## Selected existing package

The latest assurance package committed at the start of WRO-GAP-70 is historical:
close 2026-08-07, run 20260809_004402, source
`cec1b330b3c26773d0dcd8c54ed299e7a25fd01a`. It is not current October market evidence.
Inspect it explicitly from the repository root:

```bash
python -m tools.wro_operator_status \
  --assurance output/run_manifests/weekly_etf_release_assurance_2026-08-07_20260809_004402.json \
  --source-sha cec1b330b3c26773d0dcd8c54ed299e7a25fd01a \
  --run-id 20260809_004402 --close-date 2026-08-07 --report-token 260807
```

Its 13 recorded artifacts are the pricing audit, runtime state, run manifest,
portfolio, trade ledger and the Markdown/HTML/PDF/PNG bundle in each language.
Legacy assurance already records a bilingual numeric mismatch (268 English table
numbers versus 264 Dutch). The current manifest bytes also differ from the stored
assurance hash. The operator reports this binding failure and does not trust that
record for further semantic evaluation. This package remains BLOCKED; independent exact-package
assurance and delivery authority cannot be inferred from those artifacts.
