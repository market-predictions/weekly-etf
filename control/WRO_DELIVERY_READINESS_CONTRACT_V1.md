# Weekly Review OS — Delivery Readiness Contract V1

Status: candidate contract for `WEEKLY_REVIEW_OS@2026-09-02-r3:WRO-GAP-40`.

## Purpose

This contract defines when one exact Weekly Review OS package may be called `delivery-ready` without confusing that state with `delivered` or granting send authority.

It extends the existing evidence and quality contract. It does not create a second delivery state plane, manifest store, scheduler, SMTP path, portfolio authority, broker authority or release workflow.

## State semantics

The terms are deliberately separate:

- `generated` — report artifacts exist, but quality/readiness gates are not yet proven;
- `delivery-ready` — one exact package satisfies the prerequisite gates below;
- `delivery-authorized` — separate governed authority exists to perform the delivery action for that exact package;
- `delivered` — an authorized delivery attempt has separate positive delivery/receipt evidence.

`delivery-ready` never implies `delivery-authorized`. `delivery-authorized` never implies `delivered`. Absence of delivery authority leaves a delivery-ready package safely non-sent.

## Exact package identity

A delivery-readiness decision must bind one exact package. The binding must identify, where applicable:

- repository candidate SHA;
- canonical review/run or input-manifest identity;
- exact Dutch artifact identity or content hash;
- exact English artifact identity or content hash;
- exact rendered HTML/PDF artifact identities or content hashes when those forms are in scope;
- exact QA result identity bound to those artifacts;
- exact evidence snapshot or equivalent governed input identity used by QA/assurance.

A material change to candidate code, governed inputs or any in-scope output bytes invalidates the previous package identity and therefore invalidates its delivery-readiness decision.

## Prerequisite gates

A package is delivery-ready only when all applicable gates are proven for the exact package identity:

1. evidence lineage and freshness satisfy `control/WRO_EVIDENCE_QUALITY_CONTRACT_V1.md`;
2. missing or conflicting material evidence has no unresolved quality blocker;
3. deterministic QA has passed against the exact in-scope artifacts;
4. Dutch and English outputs represent the same canonical review state;
5. recommendations are not represented as executed portfolio changes;
6. required exact-candidate review/assurance for the package has passed under the governing project lifecycle;
7. no unresolved blocker invalidates the package or its evidence binding.

A missing, stale, ambiguous or contradictory prerequisite fails closed: the package remains not delivery-ready rather than being promoted with a warning.

## Delivery authority remains separate

Readiness evaluation is read-only with respect to delivery. It must not:

- invoke SMTP or a report-send workflow;
- resend an earlier package;
- create or infer principal delivery authorization;
- mutate broker, portfolio, holdings, cash, share or ledger state;
- treat successful rendering, QA or review as delivery evidence.

If no current delivery authority exists, the only valid operational outcome is that the exact delivery-ready package remains unsent.

## Delivered evidence

`delivered` requires evidence from the separately authorized delivery path. SMTP invocation or workflow success alone is not sufficient if the governing delivery contract requires positive receipt/attachment evidence.

Delivery evidence must remain bound to the exact package identity that was authorized. A different package cannot inherit an earlier delivery authorization or delivery receipt.

## One source of truth

This contract defines semantics and gates only. Existing canonical project artifacts remain authoritative for holdings, pricing, reports, QA, delivery authority and delivery evidence. Implementations should reference those artifacts rather than copying them into a new readiness database or status service.

## Acceptance mapping

- **Delivery-ready is distinct from delivered:** the state semantics above separate generated, delivery-ready, delivery-authorized and delivered.
- **Exact package identity and prerequisite gates are explicit:** candidate/input/output/QA/evidence identities plus seven fail-closed gates define the bounded readiness decision.
- **Absent delivery authority leaves the package safely non-sent:** readiness grants no send authority and explicitly requires no delivery action when authority is absent.

## Explicit non-authority

This candidate adds no report-send, SMTP, broker, portfolio, ledger, release or deployment authority. `integration_policy=HOLD_AFTER_PASS` remains governing for this Mission gap.
