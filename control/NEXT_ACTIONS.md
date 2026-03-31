# ETF Review OS — Next Actions

## Status legend
- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 1 — establish the working environment

### 1. Use the lean bootstrap upload model
- Owner: `[USER]`
- Primary upload:
  - `control/PROJECT_BOOTSTRAP.md`
- Action:
  - upload only the bootstrap file as the default stable project context
  - do **not** upload changing repo files as standard project context unless there is a specific task-driven need
- Why:
  - the ChatGPT Project should stay lean
  - GitHub should remain the live source of truth for prompts, scripts, workflows, outputs, and control docs
  - this reduces drift between project memory and repo reality
- Done when:
  - the project contains the bootstrap file
  - future sessions read the live repo files from GitHub instead of relying on stale uploaded copies

### 2. Keep using the control layer at the start of each ETF session
- Owner: `[JOINT]`
- Action: every meaningful ETF architecture, debugging, prompt, state, workflow, split-test, or delivery session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution file(s)
- Done when: sessions no longer need to rediscover how the system is organized.

---

## Phase 2 — complete the control-layer refresh

### 3. Overwrite the older control files with the prepared update pack
- Owner: `[ASSISTANT]`
- Source folder: `control/update_pack/`
- Target files:
  - `control/SYSTEM_INDEX.md`
  - `control/CURRENT_STATE.md`
  - `control/NEXT_ACTIONS.md`
  - `control/DECISION_LOG.md`
  - `control/CHATGPT_PROJECT_INSTRUCTIONS.md`
- Why: the split scaffold is now live, so the older control files should reflect the current architecture instead of the pre-split state.
- Done when: the live control files match the prepared update-pack versions.

### 4. Keep the four-layer model explicit
- Owner: `[ASSISTANT]`
- Action: preserve and reinforce the separation between:
  1. decision framework
  2. input/state contract
  3. output contract
  4. operational runbook
- Why: this is the core architectural improvement and must not collapse back into a monolith.
- Done when: future changes and reviews are consistently framed against these four layers.

---

## Phase 3 — validate the as-is ETF split architecture safely

### 5. Keep the split test strictly non-destructive
- Owner: `[JOINT]`
- Action:
  - keep `etf.txt` unchanged as the production prompt
  - use `prompts/as_is_split/` only for comparison runs
  - keep split outputs in `output_split_test/`
- Done when: the split architecture can be evaluated without changing production behavior.

### 6. Use the split runtime as the comparison entrypoint
- Owner: `[ASSISTANT]`
- Source file: `prompts/as_is_split/ETF_RUNTIME_SPLIT.txt`
- Action:
  - use the split runtime as the entrypoint for split tests
  - preserve the exact read order defined there
  - treat `05_SECTION_MAP.md` as reference only, not as runtime authority
- Done when: split runs are reproducible and faithful to production logic.

### 7. Compare split outputs against production outputs
- Owner: `[ASSISTANT]`
- Action:
  - compare methodology preservation
  - compare pricing-pass behavior
  - compare scoring integrity
  - compare portfolio treatment
  - compare executive presentation quality
  - compare delivery-readiness
- Done when: the split architecture is validated as truly “as-is” in practical output quality, not just in wording.

### 8. Confirm ETF executive look & feel preservation explicitly
- Owner: `[ASSISTANT]`
- Action:
  - review split outputs against recent production ETF outputs
  - confirm hierarchy, spacing, compact-table behavior, appendix separation, and premium feel remain intact
- Done when: the split architecture is shown not to degrade the ETF design standard.

---

## Phase 4 — tighten boundaries without changing behavior

### 9. Review `send_report.py` against the new architecture
- Owner: `[ASSISTANT]`
- Action: identify which responsibilities belong in the script and which should stop living in the prompt.
- Focus areas:
  - manifest/receipt logic
  - HTML/PDF rendering
  - equity-curve handling
  - stale-report detection
  - portfolio-valuation refresh logic
  - split-test output handling

### 10. Review the GitHub Actions workflows
- Owner: `[ASSISTANT]`
- Action:
  - confirm production workflow responsibilities stay limited to orchestration, secrets, execution, and delivery
  - confirm split-test workflow remains comparison-only and does not silently replace production
- Done when: workflow logic is clearly operational, not decision-making.

---

## Phase 5 — move ETF toward explicit implementation state

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
- Done when: ETF can rely less on prior report parsing for implementation facts.

### 12. Validate stale-data handling
- Owner: `[ASSISTANT]`
- Action: review handling of:
  - stale ETF quote data
  - stale EUR/USD conversion data
  - stale portfolio values
  - stale report artifacts
  - stale split-test artifacts
- Done when: stale inputs cannot silently flatten, distort, or misstate the portfolio or report.

---

## Suggested immediate next move

The best next move after this update is:
1. overwrite the older control files from `control/update_pack/`
2. run one ETF split comparison through `prompts/as_is_split/ETF_RUNTIME_SPLIT.txt`
3. compare the result against a current production `etf.txt` + `etf-pro.txt` run
4. only after output validation, continue boundary tightening in production-adjacent files

---

## Current checkpoint

**Architecture transition in progress — split runtime exists, production prompt remains protected, split-test workflow exists, and the remaining task is to merge the prepared control update pack into the live control files and validate output parity.**
