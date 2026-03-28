# ETF Review OS — Next Actions

## Status legend
- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

## Phase 1 — establish the working environment
### 1. Create the ChatGPT Project
- Owner: `[USER]`
- Action: create a new ChatGPT Project named **ETF Review OS**.
- Why: Projects are the right working-memory layer for recurring ETF work.
- Done when: the project exists in your sidebar.

### 2. Paste project instructions
- Owner: `[USER]`
- Source file: `control/CHATGPT_PROJECT_INSTRUCTIONS.md`
- Action: open Project settings and paste the instruction text.
- Done when: the ETF project has its own instructions separate from your global custom instructions.

### 3. Upload the minimum canonical files to the project
- Owner: `[USER]`
- Recommended first upload set:
  - `etf.txt`
  - `send_report.py`
  - `.github/workflows/send-weekly-report.yml`
  - one recent example report from `output/`
  - optionally this control folder exported or copied into a doc
- Done when: the project contains the smallest file set that gives strong context without creating clutter.

## Phase 2 — separate control from execution
### 4. Keep using the new control layer at the start of each ETF session
- Owner: `[JOINT]`
- Action: every ETF architecture/debugging session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
- Done when: sessions stop re-discovering the architecture from scratch.

### 5. Refactor the prompt conceptually into four layers
- Owner: `[ASSISTANT]`
- Action:
  - extract decision framework
  - extract input/state contract
  - extract output contract
  - extract operational runbook
- Done when: the ETF operating model is understandable without reading one giant masterprompt end to end.

## Phase 3 — strengthen explicit state
### 6. Add ETF state-file scaffolding
- Owner: `[ASSISTANT]`
- Planned files:
  - `output/etf_portfolio_state.json`
  - `output/etf_trade_ledger.csv`
  - `output/etf_valuation_history.csv`
  - `output/etf_recommendation_scorecard.csv`
- Goal: reduce dependence on parsing old reports as operational truth.
- Note: this should be done carefully so it does not break the current workflow.

### 7. Define the ETF state authority rules
- Owner: `[ASSISTANT]`
- Action: document exactly which files are authoritative for:
  - holdings
  - cash
  - valuation
  - recommendation intent
  - delivery status
- Done when: conflicts between report text and state files can be resolved deterministically.

## Phase 4 — improve delivery isolation
### 8. Review `send_report.py` against the new architecture
- Owner: `[ASSISTANT]`
- Action: identify which responsibilities should remain in the script and which should leave the prompt.
- Focus areas:
  - manifest/receipt logic
  - HTML/PDF rendering
  - report structure validation
  - stale/fresh pricing handling

### 9. Review the GitHub Actions workflow against the new control model
- Owner: `[ASSISTANT]`
- Action: confirm that workflow responsibilities are limited to orchestration, secrets, execution, and delivery.

## Phase 5 — optional GPT layer
### 10. Decide whether to build the optional helper GPT
- Owner: `[USER]`
- Source file: `control/OPTIONAL_CUSTOM_GPT_SPEC.md`
- Recommendation: build it only as an **architect/reviewer GPT**, not as the primary production runner.
- Done when: you either create it or explicitly decide to skip it.

## Suggested immediate next move
The best next move after this file exists is:

1. you create the ETF Project manually
2. I refactor the ETF prompt into layered docs and/or scaffold the ETF state files in GitHub

## Current checkpoint
**Phase 1 partially completed: GitHub control layer started. ChatGPT Project creation still pending manual action.**