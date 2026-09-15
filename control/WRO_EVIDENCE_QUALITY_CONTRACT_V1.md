# Weekly Review OS — Evidence & Quality Contract V1

Status: candidate contract for `WEEKLY_REVIEW_OS@2026-08-16-r2:WRO-GAP-30`.

## Purpose

This contract defines the minimum mission-visible evidence lineage and review-quality rules for Weekly Review OS. It does not create a second state plane, pricing authority, delivery authority, portfolio authority or broker authority. Existing canonical project artifacts remain authoritative for their own facts.

## Evidence identity and lineage

Every material review claim must be reconstructable from an explicit evidence record or canonical repository artifact. At minimum the review assembly must preserve:

- source identity: canonical repository path or external source identifier;
- observation/reference time where freshness matters;
- retrieval or generation time when available;
- exact artifact identity when immutable identity exists (commit SHA, content hash, run id, manifest id or equivalent);
- transformation lineage from source evidence to normalized runtime state and then to rendered review output;
- authority class: canonical state, governed methodology, external evidence, derived analysis, or non-authoritative shadow/lab evidence.

A rendered review is derived output. It never becomes a new authority for holdings, prices, executions, delivery receipts or portfolio state merely because it contains those values.

## Freshness

Freshness is evidence-specific and must be evaluated against the governing source contract rather than one universal age threshold.

- Market/pricing evidence uses the canonical pricing/runtime contracts and their exact reference-date semantics.
- Portfolio and ledger facts come from their canonical machine-readable state artifacts.
- Methodology and governance use the exact repository revision being evaluated.
- External research must retain its observation/reference date and source identity.
- Shadow, lab and preview artifacts remain non-authoritative unless an explicit governed promotion says otherwise.

When a required freshness rule cannot be proven, the affected claim or section is not silently carried forward as current fact.

## Missing and conflicting evidence

Missing or conflicting material evidence fails closed.

The assembly/QA path must not invent, interpolate, silently substitute or relabel evidence to make a review appear complete. It must instead produce an explicit unavailable/conflict state that identifies the affected field or section and the competing/missing sources. Existing source-specific fallback rules may be used only where already governed by that source contract and must preserve truthful provenance.

Conflicts are resolved only by an existing authority rule. If no authority rule deterministically resolves the conflict, the review remains blocked for that material claim rather than choosing a convenient value.

## Internal consistency checks

Before a review can be treated as quality-gated, deterministic checks must establish at least:

1. every material value/claim that requires evidence has a resolvable lineage;
2. portfolio, ledger and pricing references do not contradict their canonical machine state;
3. report reference dates, pricing dates and evidence freshness states are internally coherent;
4. English and Dutch outputs represent the same canonical review state rather than independent research passes;
5. missing/conflicting evidence is surfaced rather than manufactured away;
6. shadow/lab/preview evidence is not presented as promoted production truth;
7. recommendations are not represented as executed portfolio changes;
8. delivery-ready/delivered state is not inferred by review generation or QA.

A failed material check is a failed quality gate, not a warning that can be silently ignored.

## Exact-output identity

The exact review candidate presented for independent assurance must be identifiable without ambiguity. The assurance package must bind:

- the exact repository candidate SHA;
- the exact canonical input/run manifest or equivalent governed input identity when one exists;
- the exact English and Dutch output artifact identities (content hash or immutable artifact identity);
- the QA result bound to those exact identities.

Any material change to candidate code, governed inputs or assured output bytes invalidates the prior exact-output assurance for the changed artifact and requires fresh assurance where the project lifecycle requires it.

## Independent assurance boundary

Independent assurance is read-only with respect to the candidate it judges. It verifies the exact candidate/output identity, evidence lineage, freshness handling, missing/conflict behavior and deterministic QA results. It does not repair the candidate during review and does not create delivery, SMTP, broker, portfolio, ledger, release or deployment authority.

A PASS proves only the scoped quality/assurance contract for the exact candidate. A FAIL routes back through governed repair. An indeterminate or unverifiable exact identity cannot be promoted as PASS.

## Non-delivery authority boundary

This contract may support a later deterministic delivery-readiness gate, but it cannot send or resend a report, invoke SMTP, mutate portfolio or trade-ledger state, execute broker actions, release or deploy. `delivery-ready` and `delivered` remain distinct states under separate authority.

## Acceptance mapping

- Evidence source, freshness and lineage requirements are explicit: defined above by evidence identity, authority class and source-specific freshness semantics.
- Missing/conflicting evidence fails closed: unresolved material gaps/conflicts block the affected quality gate and may not be manufactured away.
- Review QA and independent assurance boundaries are testable: deterministic consistency checks plus exact candidate/input/output identities define the test surface.
- No report-send, broker, portfolio or ledger authority is added: all such actions remain explicitly outside this contract.
