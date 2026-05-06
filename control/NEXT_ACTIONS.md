# ETF Review OS — Next Actions

## Status legend
- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 1 — keep the working environment disciplined

### 1. Keep using the control-layer start sequence
- Owner: `[JOINT]`
- Action: every meaningful ETF architecture, debugging, prompt, state, workflow, delivery, discovery, or lab-optimization session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution file(s)
- Done when: sessions no longer rediscover the architecture.

### 2. Keep GitHub as source of truth
- Owner: `[JOINT]`
- Action: read changing repo files live from GitHub and do not rely on stale uploaded copies.
- Done when: prompt, state, workflow, and output changes are all traceable in GitHub.

---

## Phase 2 — validate lane discovery in the next live ETF report

### 3. Run and inspect the first discovery-driven report
- Owner: `[JOINT]`
- Action:
  - run `Send weekly ETF Pro report` manually
  - confirm `Discover and score ETF opportunity lanes` passes
  - confirm the matching lane artifact includes `discovery_engine_version`
  - confirm the report uses the newly written lane artifact
- Done when: workflow succeeds and both EN/NL reports are received.

### 4. Inspect whether radar freshness improved
- Owner: `[JOINT]`
- Action:
  - compare Structural Opportunity Radar with the prior report
  - check whether omitted-but-assessed lanes include useful rotating challengers
  - confirm the radar no longer looks like a static list of previously suggested themes
- Done when: the radar contains a believable mix of retained leaders, portfolio-gap challengers, and rotating discovery lanes.

### 5. Expand and curate the discovery universe
- Owner: `[ASSISTANT]`
- Source file:
  - `config/etf_discovery_universe.yml`
- Action:
  - add additional sectors, factor ETFs, region ETFs, commodity ETFs, and defensive exposures
  - keep each lane investable, differentiated, and scored
- Done when: the universe is broad enough to surface new candidates without becoming noisy.

---

## Phase 3 — improve discovery intelligence

### 6. Add historical relative-strength scoring
- Owner: `[ASSISTANT]`
- Action:
  - add 1-month and 3-month ETF return calculations
  - add trend quality
  - add volatility/drawdown filters
  - feed values into `runtime/score_etf_lanes.py`
- Done when: lane ranking is less dependent on configured priors and more market-data backed.

### 7. Expand challenger pricing coverage
- Owner: `[ASSISTANT]`
- Action:
  - adapt pricing to include top discovery challengers
  - or split the workflow into discovery pre-scan and pricing pass two-pass mode
- Done when: top challenger lanes have close-based pricing evidence before final scoring.

### 8. Add better macro/fundamental freshness inputs
- Owner: `[ASSISTANT]`
- Action:
  - add machine-readable macro/regime input file
  - add policy/geopolitical catalyst tags
  - add current official or market-based freshness notes where possible
- Done when: discovery is no longer only config-driven.

---

## Phase 4 — continue capital discipline

### 9. Apply the capital re-underwriting layer in every report
- Owner: `[ASSISTANT]`
- Source files:
  - `control/CAPITAL_REUNDERWRITING_RULES.md`
  - latest `output/etf_recommendation_scorecard.csv`
- Action:
  - run the fresh cash test for every current holding
  - split thesis validity from implementation quality
  - force alternative duels for replaceable or weak holdings
  - flag factor overlap and cash policy explicitly
  - test hedge validity for GLD or any hedge sleeve
- Done when: the report clearly explains why Hold is still justified or why action is required.

### 10. Force the specific current weak-point reviews
- Owner: `[ASSISTANT]`
- Action: in the next report explicitly review:
  - SPY overlap versus SMH
  - PPA versus ITA
  - PAVE versus GRID
  - GLD hedge validity and pricing confidence
  - cash reserve versus actionable SMH / URNM lanes
- Done when: no weak or replaceable holding remains vague.

---

## Phase 5 — keep send-path hardening

### 11. Confirm production workflow trigger behavior
- Owner: `[JOINT]`
- Action:
  - confirm GitHub Actions actually triggers on canonical report pushes and manual dispatch
  - confirm logs produce visible render/send/manifest evidence
  - avoid claiming delivery success without a real receipt
- Done when: delivery status can be verified reliably.

### 12. Keep workflow behavior operational only
- Owner: `[ASSISTANT]`
- Action:
  - production send workflow should be for production report-output pushes and manual dispatch only
  - code changes should not silently resend subscriber emails
- Done when: workflow logic remains operational, not editorial.

---

## Current checkpoint

**The next priority is to validate the new lane discovery engine in a live workflow run, then inspect whether the Structural Opportunity Radar has become genuinely broader and less static.**
