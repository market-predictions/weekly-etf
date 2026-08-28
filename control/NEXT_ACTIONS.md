# ETF Review OS — Next Actions

## Current control objective

The current Control-managed objective is to complete the governed current-state reconciliation for:

`WEEKLY_REVIEW_OS@2026-08-16-r2:WRO-GAP-10`

This is governance/state work only. It grants no report-send, SMTP, broker, portfolio, trade-ledger, release or deployment authority.

## Required sequence

1. Freeze the exact WRO-GAP-10 candidate.
2. Obtain fresh independent exact-head assurance through the canonical Control B1 lifecycle.
3. On PASS only, integrate the unchanged candidate through the authorized A1 exact-head integration path.
4. Reconstruct authoritative project state again.
5. Return to the active Mission Contract and derive the next eligible unsatisfied gap from current evidence.

Do not hard-code later mission work before this sequence completes.

## Historical portfolio execution package

`WP_PORTFOLIO_CLOSE_FIRST_EXECUTION` was previously described as an immediate next portfolio package. It remains historical/separately governed work and is **not** automatically authorized or reactivated by this file, by WRO-GAP-10, or by mission scheduling.

Any future portfolio mutation still requires current explicit project authority and fresh evidence, including the applicable pricing, selection, whole-share, position-count and NAV gates. Review evidence is not execution authority.

## Delivery boundary

No report generation, resend or delivery recovery is authorized by this governance reconciliation.

A future delivery action must remain separately governed and must preserve the existing distinction between:

- report/package readiness;
- transport invocation;
- SMTP success;
- receiving-system confirmation.

No delivery may be claimed without the required exact package identity and positive receipt evidence.

## Product boundary

Continue to preserve the US Weekly ETF product identity. Do not introduce EU UCITS/investability, broker-availability, PRIIPs/KID or FX-product semantics into this repository merely because shared strategy contracts or donor patterns exist.

## Source-of-truth rule

For the next cycle:

- use `control/SYSTEM_INDEX.md` for architecture/navigation;
- use `control/CURRENT_STATE.md` for stable integrated governance state;
- use canonical machine artifacts for volatile portfolio/pricing/run/delivery facts;
- use current GitHub PR/commit/workflow state for exact candidate and assurance evidence;
- use the active Mission Contract for gap selection;
- do not use old narrative next-action text or chat memory as execution authority.

## Stop conditions

Fail closed rather than infer authority when:

- evidence is stale, missing or contradictory;
- exact candidate identity moved;
- independent assurance is absent or not bound to the exact head;
- a required project authority is absent;
- an action would mutate portfolio, ledger, broker, delivery or deployment state outside its separately governed contract.
