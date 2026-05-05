# ETF Review OS — Next Actions

## Status legend
- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 1 — keep the working environment disciplined

### 1. Keep using the control-layer start sequence
- Owner: `[JOINT]`
- Action: every meaningful ETF architecture, debugging, prompt, state, workflow, delivery, or lab-optimization session starts with:
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

## Phase 2 — validate capital discipline in the next live ETF report

### 3. Apply the capital re-underwriting layer in the next report
- Owner: `[ASSISTANT]`
- Source files:
  - `etf.txt`
  - `control/CAPITAL_REUNDERWRITING_RULES.md`
  - latest `output/etf_recommendation_scorecard.csv`
- Action:
  - run the fresh cash test for every current holding
  - split thesis validity from implementation quality
  - force alternative duels for replaceable or weak holdings
  - flag factor overlap and cash policy explicitly
  - test hedge validity for GLD or any hedge sleeve
- Done when: the next report clearly explains why Hold is still justified or why action is required.

### 4. Force the specific current weak-point reviews
- Owner: `[ASSISTANT]`
- Action: in the next report explicitly review:
  - SPY overlap versus SMH
  - PPA versus ITA
  - PAVE versus GRID
  - GLD hedge validity and pricing confidence
  - cash reserve versus actionable SMH / URNM lanes
- Done when: no weak or replaceable holding remains vague.

### 5. Validate scorecard derivation over a live report
- Owner: `[ASSISTANT]`
- Action:
  - confirm `tools/write_etf_recommendation_scorecard.py --check-only` passes before send
  - confirm `output/etf_recommendation_scorecard.csv` refreshes after canonical English report push
  - inspect whether discipline flags are useful and not noisy
- Done when: the recommendation scorecard is stable across a live run.

---

## Phase 3 — continue send-path hardening

### 6. Confirm production workflow trigger behavior
- Owner: `[JOINT]`
- Action:
  - confirm GitHub Actions actually triggers on canonical report pushes
  - confirm logs produce visible render/send/manifest evidence
  - avoid claiming delivery success without a real receipt
- Done when: delivery status can be verified reliably.

### 7. Wire breadth validation deeper into `send_report.py`
- Owner: `[ASSISTANT]`
- Action:
  - import or replicate lane breadth validation inside `send_report.py`
  - fail before render/send if matching lane artifact or omitted-lane proof is missing
- Done when: delivery script itself blocks non-compliant reports.

### 8. Keep workflow behavior operational only
- Owner: `[ASSISTANT]`
- Action:
  - production send workflow should be for production report-output pushes and manual dispatch only
  - code changes should not silently resend subscriber emails
- Done when: workflow logic remains operational, not editorial.

---

## Phase 4 — improve explicit ETF state quality

### 9. Improve recommendation scorecard quality
- Owner: `[ASSISTANT]`
- Action:
  - add real 1-month and 3-month relative-strength values when reliable price history is available
  - improve best-alternative scoring
  - improve cash classification extraction
  - improve consecutive-week replaceable history
- Done when: scorecard becomes less heuristic and more data-backed.

### 10. Move ETF state beyond report-derived state over time
- Owner: `[ASSISTANT]`
- Action:
  - validate the pricing subsystem in real runs
  - add more valuation authority from machine-readable pricing outputs
  - reduce dependence on report-derived state where safe
- Done when: ETF explicit state is less dependent on rendered report parsing.

### 11. Validate stale-data handling under the broader discovery model
- Owner: `[ASSISTANT]`
- Action: review handling of stale:
  - ETF quotes
  - EUR/USD conversion
  - portfolio values
  - pricing audits
  - report artifacts
  - lane artifacts
  - recommendation scorecard rows
  - trade-ledger rows
- Done when: stale inputs cannot silently flatten, distort, or misstate the report.

---

## Phase 5 — keep optimization lab separate

### 12. Review ETF optimizer fetch config
- Owner: `[USER]`
- Action: inspect `lab_inputs/etf_optimizer_fetch_config.json` if optimization testing is desired.
- Done when: the lab universe reflects the intended ETF test set.

### 13. Run and judge the PyPortfolioOpt lab only after production state is stable
- Owner: `[JOINT]`
- Action:
  - run `.github/workflows/lab-pyportfolioopt-optimization.yml` manually
  - compare outputs against the ETF decision framework
  - keep optimizer results as QA/research, not production authority
- Done when: optimizer usefulness is clear.

---

## Current checkpoint

**The next state step is no longer to add `output/etf_recommendation_scorecard.csv`; it now exists. The next priority is to validate it during the next live report and use it to force clear decisions on SPY, PPA, PAVE, GLD, and cash policy.**
