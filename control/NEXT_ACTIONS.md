# ETF Review OS — Next Actions

## Status legend
- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 1 — protect the validated runtime and delivery baseline

### 1. Keep using the control-layer start sequence
- Owner: `[JOINT]`
- Status: active standing rule
- Action: every meaningful ETF architecture, debugging, prompt, state, workflow, delivery, discovery, or lab-optimization session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution file(s)
- Done when: sessions no longer rediscover the architecture.

### 2. Treat the current runtime + delivery HTML path as the production baseline
- Owner: `[JOINT]`
- Status: active baseline
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
  → Dutch localization contract pass
  → Dutch language quality validation
  → bilingual numeric parity validation
  → delivery HTML overrides
  → bilingual delivery HTML contract validation
  → PDF/email delivery
  ```
- Action: do not repair strict branded sections through markdown post-processing.
- Done when: Section 2, Current Position Review, Portfolio Rotation Plan, and Vervangingsanalyse stay governed by delivery HTML overrides and validator checks.

### 3. Keep workflow behavior operational only
- Owner: `[ASSISTANT]`
- Status: active standing rule
- Action:
  - production send workflow should be for production report-output pushes, manual dispatch, or safe run-queue requests only
  - code changes should not silently resend subscriber emails
  - do not claim delivery success without a real receipt, manifest, or explicit user confirmation of received delivery
- Done when: delivery status remains verifiable.

---

## Phase 2 — ChatGPT-triggerable report generation

### 4. Use safe report request queue for ChatGPT-initiated fresh reports
- Owner: `[ASSISTANT]`
- Status: active baseline
- Action: when the user asks ChatGPT to generate a fresh Weekly ETF Review, create a request file under:
  ```text
  control/run_queue/weekly_etf_report_request_YYYYMMDD_HHMMSS.md
  ```
- Do not create trigger files under `output/`.
- Done when: the send workflow is triggered by the run-queue request path and no placeholder report files are introduced.

### 5. Run one fresh production confirmation workflow
- Owner: `[USER]` or `[ASSISTANT]` if GitHub write permission is approved
- Status: done on 2026-05-10
- Result:
  - English and Dutch reports were generated and received.
  - Dutch localization contract passed after validator drift was corrected.
  - Bilingual numeric parity passed.
  - Delivery HTML render and final email delivery succeeded.
- Follow-up: no additional confirmation run is needed unless the delivery/render path changes.

---

## Phase 3 — bilingual quality and validator consolidation

### 6. Consolidate bilingual alias handling
- Owner: `[ASSISTANT]`
- Priority: high engineering cleanup before adding more NL output features
- Current issue:
  - Dutch labels and aliases currently exist across several files:
    - `runtime/nl_localization.py`
    - `runtime/apply_nl_localization.py`
    - `send_report.py`
    - `tools/validate_etf_dutch_language_quality.py`
    - `tools/validate_etf_delivery_html_contract.py`
  - This caused validator drift and repeated one-failure-at-a-time fixes.
- Action:
  - define one canonical bilingual terminology/alias source
  - reuse it from markdown localization, Dutch markdown validation, send-time numeric parity, NL HTML body validation, and delivery HTML contract validation
  - keep allowed English financial terms explicit
  - preserve English canonical report as analytical source of truth
- Done when: adding or changing one Dutch section/table label requires one edit, not patches across several validators.

### 7. Keep the Dutch companion premium but selective
- Owner: `[ASSISTANT]`
- Action:
  - continue improving Dutch client-facing language through the language-contract layer
  - avoid low-grade literal translations
  - keep accepted financial terms such as ETF, ticker, cash, hedge, drawdown, beta, capex, outperformance, watchlist where they read better
  - keep numeric parity and report structure identical to English
- Done when: Dutch reports read as professional Dutch companion reports, not translated English with system artifacts.

---

## Phase 4 — improve portfolio decision quality

### 8. Continue direct challenger-vs-current-holding scoring
- Owner: `[ASSISTANT]`
- Action:
  - map challenger lanes to likely funded holdings they could replace
  - compare challenger 1m and 3m returns directly versus the target holding
  - add direct replacement edge to lane scoring
  - add direct duel fields to lane artifacts
  - surface the direct edge in replacement-duel notes
- Done when: replacement candidates are compared against the actual holding they would replace, not only versus SPY.

### 9. Expand and curate the discovery universe
- Owner: `[ASSISTANT]`
- Source file:
  - `config/etf_discovery_universe.yml`
- Action:
  - add additional sectors, factor ETFs, region ETFs, commodity ETFs, defensive exposures, and non-U.S. exposures
  - keep each lane investable, differentiated, and scored
- Done when: the universe is broad enough to surface new candidates without becoming noisy.

### 10. Add better macro/fundamental freshness inputs
- Owner: `[ASSISTANT]`
- Action:
  - add machine-readable macro/regime input file
  - add policy/geopolitical catalyst tags
  - add current official or market-based freshness notes where possible
- Done when: discovery is no longer only config-driven.

---

## Phase 5 — continue capital discipline

### 11. Apply the capital re-underwriting layer in every report
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

### 12. Force the specific current weak-point reviews
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

**The runtime-driven bilingual production baseline now includes delivery HTML overrides, a dynamic bilingual delivery HTML validator, Dutch localization contract validation, bilingual numeric parity, direct replacement-duel logic, and a safe ChatGPT-triggerable report request queue under `control/run_queue/`. The latest confirmation run delivered English and Dutch reports successfully.**
