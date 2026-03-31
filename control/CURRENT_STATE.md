# ETF Review OS — Current State

## Snapshot date
2026-03-31

## What this repository currently is

This repository is now a production-style weekly ETF review system with:
- a production masterprompt in `etf.txt`
- a premium editorial layer in `etf-pro.txt`
- a delivery/rendering script in `send_report.py`
- a production GitHub Actions workflow for execution and email delivery
- archived outputs in `output/`
- a newly added control layer in `control/`
- a newly added as-is split scaffold in `prompts/as_is_split/`
- a split-test workflow in `.github/workflows/send-weekly-report-split-test.yml`
- a split-test output folder in `output_split_test/`

## Current strengths

- Strong executive look & feel in the ETF report family.
- Clear client-grade delivery standard.
- Production report, pro-editing layer, and delivery script already exist.
- The control layer exists and now has a proper bootstrap file.
- The split scaffold now exists as a non-destructive architecture layer.
- Split-test outputs are separated from production outputs.

## Current weaknesses

### 1. Production prompt monolith still exists
Even though the split scaffold now exists, the production system still relies on `etf.txt` as a large combined prompt mixing:
- strategy logic
- state/input rules
- valuation protocol
- output rules
- delivery expectations
- workflow orchestration
- completion logic

### 2. Existing control files still need in-place overwrite
The replacement content for several older control files has been prepared, but the connector in this session did not reliably allow direct overwrite of existing files.
The completed replacement drafts are therefore stored in:
- `control/update_pack/`

### 3. Explicit ETF state files still do not yet exist
ETF still relies mainly on prior report parsing and the pricing-pass logic inside `etf.txt`.
Planned future state files remain:
- `output/etf_portfolio_state.json`
- `output/etf_trade_ledger.csv`
- `output/etf_valuation_history.csv`
- `output/etf_recommendation_scorecard.csv`

### 4. Production and split still need practical comparison runs
The split architecture has been scaffolded, but it still needs output comparison against production before further boundary tightening should be trusted.

## Target architecture

### ChatGPT side
- One dedicated ChatGPT Project called **ETF Review OS**.
- Project instructions that reinforce the operating model.
- A lean bootstrap model using `control/PROJECT_BOOTSTRAP.md` as the default standing upload.
- Live GitHub reads for changing repo files.

### GitHub side
- GitHub remains the source of truth for prompts, scripts, workflows, outputs, and control docs.
- The split scaffold exists for safe architectural evaluation.
- Production files remain protected while split comparisons happen separately.

### Delivery side
- Delivery remains in `send_report.py` plus GitHub Actions.
- The prompt still carries too much runbook logic, but the split scaffold now makes the four-layer separation explicit.
- The ETF executive look & feel remains the non-negotiable presentation reference for the report family.

## Immediate priorities

### Priority A — stabilize the operating layer
Completed in this step:
- add `control/PROJECT_BOOTSTRAP.md`
- add `prompts/as_is_split/`
- add `ETF_RUNTIME_SPLIT.txt`
- add split-test workflow
- add split-test output folder documentation
- create replacement drafts for older control files in `control/update_pack/`

### Priority B — update existing control files in place
Still required:
- overwrite `control/SYSTEM_INDEX.md`
- overwrite `control/CURRENT_STATE.md`
- overwrite `control/NEXT_ACTIONS.md`
- overwrite `control/DECISION_LOG.md`
- overwrite `control/CHATGPT_PROJECT_INSTRUCTIONS.md`
using the content stored in `control/update_pack/`

### Priority C — validate the split architecture as truly as-is
Still required:
- run split output comparisons against production
- confirm methodology preservation
- confirm portfolio treatment preservation
- confirm delivery-readiness preservation
- confirm executive look & feel preservation

### Priority D — move ETF toward explicit implementation state
Planned after split validation:
- add explicit ETF state files
- make valuation authority less dependent on report parsing
- tighten deterministic conflict resolution between report intent and implementation facts

## Recommended session start sequence

For any future ETF architecture session:
1. read `control/SYSTEM_INDEX.md`
2. read this file
3. read `control/NEXT_ACTIONS.md`
4. only then open the specific execution file relevant to the task

## Current role split

### Manual by user
- create or maintain the ChatGPT Project
- paste project instructions if needed
- upload `control/PROJECT_BOOTSTRAP.md` as the default stable project context
- optionally approve or apply overwrite steps if a future connector session supports them more cleanly

### Can be done by assistant
- design the project instructions
- design the GPT spec
- create and update GitHub control files
- refactor prompts
- propose or write repo files
- review and improve scripts/workflows
- strengthen pricing/state authority rules
- run split comparisons

## Current status label

**Architecture transition in progress — split scaffold now initialized in GitHub, production prompt remains protected, lean bootstrap model added, existing control files still need final in-place overwrite from the prepared update pack.**
