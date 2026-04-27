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

## Phase 4 — stabilize and extend the ETF minimum state model

### 9. Validate the new ETF minimum state refresh over live runs
- Owner: `[JOINT]`
- Action:
  - let `.github/workflows/refresh-etf-state-from-report.yml` run on the next canonical English pro report push
  - confirm `output/etf_portfolio_state.json` and `output/etf_valuation_history.csv` refresh and commit correctly
  - confirm the pre-send derivation check passes in `.github/workflows/send-weekly-report.yml`
- Done when: ETF minimum state refresh is stable and repeatable.

### 10. Confirm ETF state/report alignment
- Owner: `[ASSISTANT]`
- Action:
  - compare the latest canonical English pro report with `output/etf_portfolio_state.json`
  - compare the latest Section 7 table with `output/etf_valuation_history.csv`
  - confirm the statefiles reflect the latest pro report deterministically
- Done when: state authority is explicit and visibly aligned with the canonical report.

### 11. Add the next ETF state files
- Owner: `[ASSISTANT]`
- Planned files:
  - `output/etf_trade_ledger.csv`
  - `output/etf_recommendation_scorecard.csv`
- Action:
  - define their minimum schemas
  - add repo-native writers for them
  - keep them aligned with the minimum ETF state model already introduced
- Done when: ETF has the next layer of explicit implementation memory beyond portfolio snapshot and valuation history.

### 12. Move ETF state beyond report-derived explicit state over time
- Owner: `[ASSISTANT]`
- Action:
  - validate the pricing subsystem in real runs
  - add more valuation authority from machine-readable pricing outputs
  - reduce dependence on report-derived state where it is safe to do so
  - tighten deterministic conflict resolution between report intent and implementation facts
- Done when: ETF explicit state is less dependent on the rendered report itself.

### 13. Validate stale-data handling under the broader discovery model
- Owner: `[ASSISTANT]`
- Action: review handling of:
  - stale ETF quote data
  - stale EUR/USD conversion data
  - stale portfolio values
  - stale pricing audits
  - stale report artifacts
  - stale lane artifacts
  - stale watchlist / lane continuity memory
  - stale ETF state files
- Done when: stale inputs cannot silently flatten, distort, or misstate the portfolio or report.

---

## Phase 5 — run and judge the ETF optimization lab with auto-fetched history

### 14. Review the ETF optimizer fetch config
- Owner: `[USER]`
- Action:
  - inspect `lab_inputs/etf_optimizer_fetch_config.json`
  - adjust the ETF ticker universe, period, or date range if desired
- Done when: the fetch config reflects the ETF lab universe you want to test.

### 15. Run the manual PyPortfolioOpt optimization workflow
- Owner: `[JOINT]`
- Action:
  - use `.github/workflows/lab-pyportfolioopt-optimization.yml` manually
  - let the workflow auto-fetch ETF history with yfinance first
  - inspect the generated artifact bundle from `lab_outputs/optimization/`
  - compare max Sharpe, min volatility, HRP, and optional Black-Litterman outputs
- Done when: the ETF optimization lab run completes successfully on a real fetched daily history and produces interpretable artifacts.

### 16. Judge whether the optimizer adds decision value or just model noise
- Owner: `[ASSISTANT]`
- Action:
  - compare optimizer outputs against ETF breadth discipline and regime logic
  - check whether optimized allocations are sensible or merely concentrated
  - decide whether the optimizer is useful as an internal QA layer
  - decide whether the next extension should be a Riskfolio-Lib comparison layer
- Done when: the optimizer’s role is clear before any further extension.

---

## Phase 6 — reduce monolith risk later without weakening production

### 17. Keep the four-layer model explicit in future changes
- Owner: `[ASSISTANT]`
- Action: preserve the distinction between:
  1. decision framework
  2. input/state contract
  3. output contract
  4. operational runbook
- Done when: future changes do not collapse everything back into a single opaque blob.

### 18. Reduce monolith risk only where it is safe
- Owner: `[JOINT]`
- Action:
  - tighten boundaries gradually
  - keep production reliability intact
  - preserve the ETF executive look & feel while doing so
- Done when: clarity improves without destabilizing the live workflow.

---

## Suggested immediate next move

The best next move after this update is:
1. let the next canonical English ETF pro report push run both the send workflow and the ETF state-refresh workflow
2. confirm `output/etf_portfolio_state.json` and `output/etf_valuation_history.csv` refresh cleanly on `main`
3. only after that, add `output/etf_trade_ledger.csv` and `output/etf_recommendation_scorecard.csv`
4. then return to optimizer-comparison or deeper send-path hardening work

---

## Current checkpoint

**The ETF repo now has a first explicit minimum state layer, a repo-native state refresh workflow, and a pre-send derivation check; the next ETF state step is to stabilize that new minimum model across live runs and then extend it with trade-ledger and recommendation-scorecard files.**
