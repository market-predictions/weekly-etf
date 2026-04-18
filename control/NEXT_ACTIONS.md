# ETF Review OS — Next Actions

## Status legend
- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 1 — keep the working environment disciplined

### 1. Keep using the lean bootstrap upload model
- Owner: `[USER]`
- Primary upload:
  - `control/PROJECT_BOOTSTRAP.md`
- Action:
  - keep the project context lean
  - continue reading changing repo files live from GitHub
- Done when:
  - future sessions do not depend on stale uploaded repo files

### 2. Keep using the control-layer start sequence
- Owner: `[JOINT]`
- Action: every meaningful ETF architecture, debugging, prompt, state, workflow, or delivery session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution file(s)
- Done when: sessions no longer need to rediscover how the system is organized.

---

## Phase 2 — validate the direct production architecture change

### 3. Run the next live ETF review from the updated production prompt
- Owner: `[ASSISTANT]`
- Source files:
  - `etf.txt`
  - `etf-pro.txt`
- Action:
  - use the updated production files directly
  - confirm the report still feels compact, premium, and decision-useful
  - confirm newly surfaced categories can appear without bloating the report
  - confirm a matching pricing audit is consumed correctly when available
- Done when: a live production run shows the new discovery model and pricing-audit consumption working inside the existing executive format.

### 4. Confirm compact publication discipline
- Owner: `[ASSISTANT]`
- Action:
  - confirm the Structural Opportunity Radar remains compact
  - confirm the report still publishes only the best-ranked 5-8 lanes
  - confirm “strong but not yet actionable” ideas remain selective rather than padded
- Done when: broader discovery does not degrade executive selectivity.

### 5. Check lane continuity behavior in real output
- Owner: `[ASSISTANT]`
- Action:
  - confirm retained lanes, new entrants, dropped lanes, and near-miss challengers are handled cleanly
  - confirm radar change language reads naturally in the premium layer
  - confirm the report explains changes without exposing internal process machinery
- Done when: the report feels fresher and broader without feeling unstable.

---

## Phase 3 — review rendering and delivery against the new prompt behavior

### 6. Review `send_report.py` against the updated architecture
- Owner: `[ASSISTANT]`
- Action: identify whether any rendering or delivery assumptions need tightening after the prompt changes.
- Focus areas:
  - radar table width and row-count behavior
  - HTML/PDF compactness with variable lane composition
  - placement and treatment of continuity language
  - appendix cleanliness
  - manifest/receipt behavior

### 7. Keep workflow behavior operational only
- Owner: `[ASSISTANT]`
- Action:
  - keep `.github/workflows/send-weekly-report.yml` limited to actual production report send events
  - keep code, pricing, prompt, and render checks in non-email validation workflows
  - confirm no non-report code change can silently resend the latest subscriber email
- Done when: workflow logic remains operational, not thematic or editorial, and email sending is gated to real report publication only.

---

## Phase 4 — move ETF toward explicit implementation state

### 8. Validate the expanded pricing subsystem in real runs
- Owner: `[ASSISTANT]`
- Action:
  - validate issuer-page handlers in real runtime output
  - determine whether Yahoo fallback remains necessary after API coverage testing
  - confirm richer holding snapshots are written correctly
  - confirm shortlist pricing for alternatives and challengers behaves within free-tier limits
  - confirm prompt consumption of matching pricing audits is clean and non-stale
- Done when: the pricing subsystem can support real report pricing authority rather than just a dry-run audit.

### 9. Design explicit ETF state files
- Owner: `[ASSISTANT]`
- Planned files:
  - `output/etf_portfolio_state.json`
  - `output/etf_trade_ledger.csv`
  - `output/etf_valuation_history.csv`
  - `output/etf_recommendation_scorecard.csv`
- Action:
  - define authority boundaries for each file
  - define how they interact with the report text
  - define deterministic conflict resolution when report intent and implementation facts differ
- Done when: ETF can rely less on prior report parsing and prompt-layer logic for implementation facts.

### 10. Validate stale-data handling under the broader discovery model
- Owner: `[ASSISTANT]`
- Action: review handling of:
  - stale ETF quote data
  - stale EUR/USD conversion data
  - stale portfolio values
  - stale pricing audits
  - stale report artifacts
  - stale watchlist / lane continuity memory
- Done when: stale inputs cannot silently flatten, distort, or misstate the portfolio or report.

---

## Phase 5 — reduce monolith risk later without weakening production

### 11. Keep the four-layer model explicit in future changes
- Owner: `[ASSISTANT]`
- Action: preserve the distinction between:
  1. decision framework
  2. input/state contract
  3. output contract
  4. operational runbook
- Done when: future changes do not collapse everything back into a single opaque blob.

### 12. Reduce monolith risk only where it is safe
- Owner: `[JOINT]`
- Action:
  - tighten boundaries gradually
  - keep production reliability intact
  - preserve the ETF executive look & feel while doing so
- Done when: clarity improves without destabilizing the live workflow.

---

## Suggested immediate next move

The best next move after this update is:
1. validate the matching pricing-audit consumption path in a real ETF production run
2. review render/delivery behavior against the updated prompt
3. continue with explicit state-file design after that
4. keep extending the pricing subsystem only where real runtime gaps still remain

---

## Current checkpoint

**Direct production architecture update is live in GitHub, the pricing subsystem now supports audits, richer holding snapshots, and quota-aware shortlist pricing on `main`, workflow safety has been tightened so code changes do not send subscriber email, and the next task is to validate live pricing-audit consumption before moving deeper into explicit ETF state authority.**
