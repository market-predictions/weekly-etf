# MISSION_WRO_GAP_01 — Mission-aware current-state review

## Mission binding

- Mission: `WEEKLY_REVIEW_OS`
- Mission revision: `2026-08-15-r1`
- Mission criterion: `WRO-SC-01`
- Mission gap: `WRO-GAP-01`
- Derivation key: `WEEKLY_REVIEW_OS@2026-08-15-r1:WRO-GAP-01`
- Project governance: `control/PROJECT_GOVERNANCE_BOOTSTRAP.md`
- Authoritative repository baseline inspected: `main` at `3ffff5e6104fcc2b72ce6553718a59be2905d3af`

## Current-state reconstruction

The Weekly ETF repository is operationally mature and already has strong separation between decision framework, state authority, output contract and execution runbook. It also has hard implementation-versus-release-assurance governance and exact-main validation. Recent authoritative `main` history materially advanced that control surface beyond the dates recorded in the human-maintained current-state files.

Authoritative repository evidence includes, among other things:

1. the shared ETF strategy/portfolio-target contract released in PR #113;
2. project-local two-role governance adopted and then hardened through PRs #114–#116;
3. the LEVEL 4 bilingual delivery-confirmation mechanism added in PR #117;
4. production-boundary cleanup removing inherited FX workflow/output contamination in PR #119;
5. release-assurance parity repairs in PRs #118 and #120;
6. exact-main release-assurance validation enabled in PR #122, which is the current `main` head.

At the same time, `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md` still present July 2026 operational baselines and immediate-next-action language. Those files remain useful historical operational records, but they no longer by themselves reconstruct the current governed Review OS as of the authoritative August `main` head.

This creates a mission-level control problem: a fresh autonomous worker following the required session read order can read correct but temporally stale operational guidance before it sees the later governance and release-assurance changes that now define the repository.

## Highest-value unsatisfied governed review gap

**Close canonical current-state drift so a fresh worker can deterministically reconstruct the present Weekly Review OS from repository state without relying on chat memory or manually inferring chronology from many later PRs.**

This is the highest-value current gap for `WRO-SC-01` because the mission criterion is specifically about deterministic reconstruction of current project state and autonomous selection of the next governed gap. The repository already contains strong execution and assurance mechanisms; the weak point is that the canonical session-start state summary lags the actual governed `main` state.

The gap is not authority to execute the separately governed portfolio package mentioned in July `NEXT_ACTIONS.md`, and it is not authority to generate or deliver a report. Before any future mission evaluator can safely choose portfolio, report, pricing, methodology or product-surface work, it needs an unambiguous current-state control surface.

## Narrowest governed follow-up

Create a separate governance-only successor workpackage that reconciles the canonical session-start control surface against current `main` while preserving historical evidence. That successor should:

1. update or supersede stale current-state assertions only after reconstructing exact authoritative state from `main`, recent merged PRs, current output/state artifacts and current governance contracts;
2. explicitly distinguish historical delivered-run state from current architecture/governance maturity;
3. record the current release-assurance and LEVEL 4 delivery-confirmation mechanisms as installed capabilities without manufacturing a new delivery event;
4. reconcile stale immediate-next-action language with any later governed work and current authority requirements;
5. retain product identity: this US Weekly ETF repository remains the donor/US product and does not absorb EU investability, FX or Index product semantics;
6. return to Mission Contract evaluation after the canonical state surface is current, so the next workpackage is selected from authoritative state rather than this document.

This artifact identifies and bounds that successor. It does not itself rewrite `CURRENT_STATE.md` or `NEXT_ACTIONS.md`, because those files contain operational assertions that should be reconciled in one dedicated governance change with exact evidence rather than partially edited during the pilot assessment.

## Existing strengths that must be preserved

Any successor must preserve:

- `control/SYSTEM_INDEX.md` as the serious-work entry point and its four-layer operating model;
- `control/PROJECT_GOVERNANCE_BOOTSTRAP.md` and the implementation/assurance role separation;
- exact-head and exact-main release-assurance behavior;
- the distinction between official portfolio state, trade ledger, pricing audit, run manifest, delivery manifest and receiving-system confirmation;
- the shared ETF contract as a shared strategy interface rather than permission to collapse product-specific implementation boundaries;
- the US/EU product-boundary separation and the removal of inherited FX runtime contamination;
- explicit promotion boundaries for shadow macro/thesis and cockpit-preview work.

## Authority boundaries

This workpackage grants no authority to:

- generate, resend or deliver a Weekly ETF report;
- invoke SMTP;
- execute broker actions;
- change allocation decisions;
- mutate `output/etf_portfolio_state.json`;
- write or amend `output/etf_trade_ledger.csv`;
- treat historical portfolio-review evidence as current execution authority;
- release or deploy anything;
- merge this candidate without fresh independent exact-head assurance.

## Acceptance evidence for WRO-GAP-01

`WRO-GAP-01` is satisfied as the first mission-derived current-state review workpackage when independent assurance confirms that this artifact:

1. is reconstructed from authoritative repository `main`, canonical session-start governance files and merged project history rather than conversational memory;
2. explicitly links the selected gap to mission criterion `WRO-SC-01`;
3. correctly identifies canonical current-state drift as the highest-value prerequisite to reliable autonomous next-gap selection;
4. does not mistake July operational state for the complete August governed architecture;
5. proposes only a governance/state-reconciliation successor and does not execute a report, portfolio, ledger, broker or delivery action;
6. preserves product identity and existing authority boundaries;
7. returns control to mission re-evaluation after the successor state reconciliation instead of hard-coding a long downstream roadmap.

This is a mission-aware current-state review decision artifact. It is not a production report, portfolio recommendation, execution authorization or delivery authorization.
