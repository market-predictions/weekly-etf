# ETF Review OS — Next Actions

## Status legend
- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 1 — protect the validated runtime baseline

### 1. Keep using the control-layer start sequence
- Owner: `[JOINT]`
- Action: every meaningful ETF architecture, debugging, prompt, state, workflow, delivery, discovery, or lab-optimization session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution file(s)
- Done when: sessions no longer rediscover the architecture.

### 2. Treat the current two-pass runtime path as the production baseline
- Owner: `[JOINT]`
- Current baseline:
  ```text
  pricing audit
  → historical relative strength
  → first-pass lane discovery
  → targeted challenger pricing
  → final lane discovery
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

## Phase 2 — inspect latest report quality

### 4. Inspect latest received two-pass report
- Owner: `[JOINT]`
- Action:
  - check whether replacement challenger pricing is visible and sensible
  - check whether final radar ranking changed logically after challenger pricing
  - check whether omitted lanes have useful rejection reasons
  - check whether Section 2, 4A, 9, 10, 12, 13 and 15 still render cleanly
- Done when: no visible report regression remains.

---

## Phase 3 — improve discovery intelligence further

### 5. Add liquidity and tradability filters
- Owner: `[ASSISTANT]`
- Action:
  - add average dollar volume where available
  - add ETF liquidity/tradability score
  - penalize or block illiquid ETFs from live radar promotion
- Done when: technically attractive but illiquid ETFs are not promoted without an explicit override.

### 6. Add relative strength versus current holdings
- Owner: `[ASSISTANT]`
- Action:
  - compare SPY challengers versus SPY
  - compare PPA challengers versus PPA
  - compare PAVE challengers versus PAVE
  - compare GLD challengers versus GLD
  - use the result in replacement-duel scoring
- Done when: replacement candidates are compared against the actual holding they would replace, not only versus SPY.

### 7. Expand and curate the discovery universe
- Owner: `[ASSISTANT]`
- Source file:
  - `config/etf_discovery_universe.yml`
- Action:
  - add additional sectors, factor ETFs, region ETFs, commodity ETFs, defensive exposures, and non-U.S. exposures
  - keep each lane investable, differentiated, and scored
- Done when: the universe is broad enough to surface new candidates without becoming noisy.

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

## Current checkpoint

**The runtime-driven bilingual production baseline with historical relative-strength scoring and two-pass challenger pricing is validated. The next priority is report inspection, then liquidity/tradability filtering and direct replacement-duel relative strength.**
