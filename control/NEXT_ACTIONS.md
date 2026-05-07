# ETF Review OS — Next Actions

## Status legend
- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 1 — protect the stable runtime baseline

### 1. Keep using the control-layer start sequence
- Owner: `[JOINT]`
- Action: every meaningful ETF architecture, debugging, prompt, state, workflow, delivery, discovery, or lab-optimization session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution file(s)
- Done when: sessions no longer rediscover the architecture.

### 2. Treat the current runtime path as the production baseline
- Owner: `[JOINT]`
- Current baseline:
  ```text
  pricing audit
  → lane discovery
  → runtime state
  → EN/NL report render
  → polish/linkify
  → validation
  → PDF/email delivery
  ```
- Action: do not keep changing the renderer unless there is a concrete output defect or validated improvement.
- Done when: future changes preserve the runtime architecture rather than reintroducing manual markdown patching.

### 3. Keep workflow behavior operational only
- Owner: `[ASSISTANT]`
- Action:
  - production send workflow should be for production report-output pushes and manual dispatch only
  - code changes should not silently resend subscriber emails
  - do not claim delivery success without a real receipt or manifest
- Done when: delivery status remains verifiable.

---

## Phase 2 — improve discovery intelligence

### 4. Add historical relative-strength scoring
- Owner: `[ASSISTANT]`
- Action:
  - add 1-month and 3-month ETF return calculations
  - add trend quality
  - add volatility/drawdown filters
  - add relative strength versus SPY
  - add relative strength versus current holdings where possible
  - feed values into `runtime/score_etf_lanes.py`
- Done when: lane ranking is less dependent on configured priors and more market-data backed.

### 5. Expand challenger pricing coverage with a two-pass flow
- Owner: `[ASSISTANT]`
- Action:
  - first pass: broad lane discovery
  - identify top challengers
  - second pricing pass for top challengers
  - final scoring
  - report render
- Done when: top challenger lanes have close-based pricing evidence before final scoring.

### 6. Expand and curate the discovery universe
- Owner: `[ASSISTANT]`
- Source file:
  - `config/etf_discovery_universe.yml`
- Action:
  - add additional sectors, factor ETFs, region ETFs, commodity ETFs, defensive exposures, and non-U.S. exposures
  - keep each lane investable, differentiated, and scored
- Done when: the universe is broad enough to surface new candidates without becoming noisy.

### 7. Add better macro/fundamental freshness inputs
- Owner: `[ASSISTANT]`
- Action:
  - add machine-readable macro/regime input file
  - add policy/geopolitical catalyst tags
  - add current official or market-based freshness notes where possible
- Done when: discovery is no longer only config-driven.

---

## Phase 3 — continue capital discipline

### 8. Apply the capital re-underwriting layer in every report
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

### 9. Force the specific current weak-point reviews
- Owner: `[ASSISTANT]`
- Action: in the next report explicitly review:
  - SPY overlap versus SMH
  - PPA versus ITA
  - PAVE versus GRID
  - GLD hedge validity and pricing confidence
  - cash reserve versus actionable SMH / URNM lanes
- Done when: no weak or replaceable holding remains vague.

---

## Current checkpoint

**The runtime-driven bilingual production baseline is stable. The next priority is historical relative-strength scoring, then two-pass challenger pricing.**
