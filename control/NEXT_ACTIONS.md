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
- Action: every meaningful ETF architecture, debugging, prompt, state, workflow, delivery, or lab-optimization session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution file(s)
- Done when: sessions no longer need to rediscover how the system is organized.

---

## Phase 2 — validate the breadth-enforcement architecture in live ETF runs

### 3. Run the next live ETF review from the updated production prompt
- Owner: `[ASSISTANT]`
- Source files:
  - `etf.txt`
  - `etf-pro.txt`
- Action:
  - use the updated production files directly
  - confirm the report still feels compact, premium, and decision-useful
  - confirm omitted sectors now show up as promoted lanes or compact challengers
  - confirm a matching pricing audit is consumed correctly when available
  - confirm a matching lane artifact is written correctly
- Done when: a live production run shows the broader discovery model, omitted-lane visibility, and matching lane artifact working inside the existing executive format.

### 4. Confirm compact publication discipline
- Owner: `[ASSISTANT]`
- Action:
  - confirm the Structural Opportunity Radar remains compact
  - confirm the report still publishes only the best-ranked 5-8 lanes
  - confirm omitted-lane proof does not bloat the report
  - confirm “strong but not yet actionable” ideas remain selective rather than padded
- Done when: broader discovery does not degrade executive selectivity.

### 5. Check lane continuity and omitted-lane behavior in real output
- Owner: `[ASSISTANT]`
- Action:
  - confirm retained lanes, new entrants, dropped lanes, and near-miss challengers are handled cleanly
  - confirm omitted but relevant lanes are surfaced naturally in premium language
  - confirm the report explains changes without exposing internal process machinery
- Done when: the report feels fresher and broader without feeling unstable.

---

## Phase 3 — finish wiring breadth enforcement into the send path

### 6. Wire `validate_lane_breadth.py` into `send_report.py`
- Owner: `[ASSISTANT]`
- Action:
  - import or replicate the lane breadth validation logic inside `send_report.py`
  - fail before render/send if the report lacks omitted-lane proof or a matching lane artifact
  - confirm the check only applies where operationally appropriate
- Done when: the delivery script itself can block non-compliant production reports before email send.

### 7. Wire breadth validation into `.github/workflows/send-weekly-report.yml`
- Owner: `[ASSISTANT]`
- Action:
  - add a distinct pre-render breadth validation step
  - make the workflow fail before render/send if breadth proof is missing
  - surface a clear `BREADTH_OK` or equivalent log line when successful
- Done when: breadth is enforced operationally before subscriber delivery.

### 8. Keep workflow behavior operational only
- Owner: `[ASSISTANT]`
- Action:
  - keep `.github/workflows/send-weekly-report.yml` limited to actual production report send events
  - keep code, pricing, prompt, and render checks in non-email validation workflows
  - confirm no non-report code change can silently resend the latest subscriber email
- Done when: workflow logic remains operational, not thematic or editorial, and email sending is gated to real report publication only.

---

## Phase 4 — move ETF toward explicit implementation state

### 9. Validate the expanded pricing subsystem in real runs
- Owner: `[ASSISTANT]`
- Action:
  - validate issuer-page handlers in real runtime output
  - determine whether Yahoo fallback remains necessary after API coverage testing
  - confirm richer holding snapshots are written correctly
  - confirm shortlist pricing for alternatives and challengers behaves within free-tier limits
  - confirm prompt consumption of matching pricing audits is clean and non-stale
- Done when: the pricing subsystem can support real report pricing authority rather than just a dry-run audit.

### 10. Validate lane artifact quality in real runs
- Owner: `[ASSISTANT]`
- Action:
  - confirm all required breadth buckets appear in each matching lane artifact
  - confirm challengers are present in sufficient number
  - confirm report/artifact date and version match one-to-one
  - confirm omitted-lane explanations are concise and decision-useful
- Done when: lane breadth becomes auditable rather than impressionistic.

### 11. Design explicit ETF state files
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

### 12. Validate stale-data handling under the broader discovery model
- Owner: `[ASSISTANT]`
- Action: review handling of:
  - stale ETF quote data
  - stale EUR/USD conversion data
  - stale portfolio values
  - stale pricing audits
  - stale report artifacts
  - stale lane artifacts
  - stale watchlist / lane continuity memory
- Done when: stale inputs cannot silently flatten, distort, or misstate the portfolio or report.

---

## Phase 5 — run and judge the ETF optimization lab with auto-fetched history

### 13. Review the ETF optimizer fetch config
- Owner: `[USER]`
- Action:
  - inspect `lab_inputs/etf_optimizer_fetch_config.json`
  - adjust the ETF ticker universe, period, or date range if desired
- Done when: the fetch config reflects the ETF lab universe you want to test.

### 14. Run the manual PyPortfolioOpt optimization workflow
- Owner: `[JOINT]`
- Action:
  - use `.github/workflows/lab-pyportfolioopt-optimization.yml` manually
  - let the workflow auto-fetch ETF history with yfinance first
  - inspect the generated artifact bundle from `lab_outputs/optimization/`
  - compare max Sharpe, min volatility, HRP, and optional Black-Litterman outputs
- Done when: the ETF optimization lab run completes successfully on a real fetched daily history and produces interpretable artifacts.

### 15. Judge whether the optimizer adds decision value or just model noise
- Owner: `[ASSISTANT]`
- Action:
  - compare optimizer outputs against ETF breadth discipline and regime logic
  - check whether optimized allocations are sensible or merely concentrated
  - decide whether the optimizer is useful as an internal QA layer
  - decide whether the next extension should be a Riskfolio-Lib comparison layer
- Done when: the optimizer’s role is clear before any further extension.

---

## Phase 6 — reduce monolith risk later without weakening production

### 16. Keep the four-layer model explicit in future changes
- Owner: `[ASSISTANT]`
- Action: preserve the distinction between:
  1. decision framework
  2. input/state contract
  3. output contract
  4. operational runbook
- Done when: future changes do not collapse everything back into a single opaque blob.

### 17. Reduce monolith risk only where it is safe
- Owner: `[JOINT]`
- Action:
  - tighten boundaries gradually
  - keep production reliability intact
  - preserve the ETF executive look & feel while doing so
- Done when: clarity improves without destabilizing the live workflow.

---

## Suggested immediate next move

The best next move after this update is:
1. review the ETF fetch config in `lab_inputs/etf_optimizer_fetch_config.json`
2. run the manual PyPortfolioOpt optimization workflow once
3. inspect the fetched-price history and optimization artifact bundle for concentration, diversification, and plausibility
4. decide whether the optimizer is useful enough to keep extending
5. only after that, return to production-critical send-path hardening work or extend the optimizer with a Riskfolio-Lib comparison layer

---

## Current checkpoint

**The ETF repo still has a production-critical breadth-enforcement hardening task outstanding, and it now includes a first manual PyPortfolioOpt optimization lab that can auto-fetch longer ETF history with yfinance before optimization runs, while remaining intentionally separate from the production ETF review flow.**
