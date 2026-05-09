# ETF Review OS — Next Actions

## Status legend
- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 1 — protect the validated runtime and delivery baseline

### 1. Keep using the control-layer start sequence
- Owner: `[JOINT]`
- Action: every meaningful ETF architecture, debugging, prompt, state, workflow, delivery, discovery, or lab-optimization session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution file(s)
- Done when: sessions no longer rediscover the architecture.

### 2. Treat the current runtime + delivery HTML path as the production baseline
- Owner: `[JOINT]`
- Current baseline:
  ```text
  pricing audit
  → historical relative strength
  → first-pass lane discovery
  → targeted challenger pricing
  → final lane discovery
  → runtime state
  → EN/NL markdown render
  → polish/linkify
  → delivery HTML overrides
  → delivery HTML contract validation
  → PDF/email delivery
  ```
- Action: do not repair strict branded sections through markdown post-processing.
- Done when: Section 2 and Current Position Review stay governed by delivery HTML overrides and validator checks.

### 3. Keep workflow behavior operational only
- Owner: `[ASSISTANT]`
- Action:
  - production send workflow should be for production report-output pushes, manual dispatch, or safe run-queue requests only
  - code changes should not silently resend subscriber emails
  - do not claim delivery success without a real receipt or manifest
- Done when: delivery status remains verifiable.

---

## Phase 2 — ChatGPT-triggerable report generation

### 4. Use safe report request queue for ChatGPT-initiated fresh reports
- Owner: `[ASSISTANT]`
- Action: when the user asks ChatGPT to generate a fresh Weekly ETF Review, create a request file under:
  ```text
  control/run_queue/weekly_etf_report_request_YYYYMMDD_HHMMSS.md
  ```
- Do not create trigger files under `output/`.
- Done when: the send workflow is triggered by the run-queue request path and no placeholder report files are introduced.

### 5. Run one fresh production confirmation workflow
- Owner: `[USER]` or `[ASSISTANT]` if GitHub write permission is approved
- Action:
  - create a run-queue request file or use manual workflow dispatch
  - confirm `Validate ETF delivery HTML contract` passes
  - confirm email/PDF delivery succeeds
  - inspect received PDF for Section 2 links, Current Position Review table, Portfolio Rotation Plan, radar pagination, and Replacement Duel Table v2
- Done when: the report is received and all validation steps pass.

---

## Phase 3 — improve portfolio decision quality

### 6. Continue direct challenger-vs-current-holding scoring
- Owner: `[ASSISTANT]`
- Action:
  - map challenger lanes to likely funded holdings they could replace
  - compare challenger 1m and 3m returns directly versus the target holding
  - add direct replacement edge to lane scoring
  - add direct duel fields to lane artifacts
  - surface the direct edge in replacement-duel notes
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

**The runtime-driven bilingual production baseline now includes delivery HTML overrides, a dynamic delivery HTML validator, direct replacement-duel logic, and a safe ChatGPT-triggerable report request queue under `control/run_queue/`.**
