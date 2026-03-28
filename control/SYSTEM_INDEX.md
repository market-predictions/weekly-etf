# ETF Review OS — System Index

This file is the **first entry point** for any serious work on the `daily-etf` system.

## Purpose
This repository now has two different kinds of files:

1. **Execution files** — the files that produce and deliver the report.
2. **Control files** — the files that explain how the system is organized, what is authoritative, what is changing, and what to do next.

Use this index to avoid starting from the wrong file or mixing strategy logic, state logic, and delivery logic.

## Canonical execution files
Read these only as needed after reading the control files.

- `etf.txt` — current monolithic masterprompt for the Weekly IBKR ETF Portfolio Review.
- `send_report.py` — delivery/rendering script for HTML email, PDF generation, attachments, and manifest logic.
- `.github/workflows/send-weekly-report.yml` — GitHub Actions workflow that runs the report and delivery process.
- `output/` — archived report outputs and related artifacts.
- `daily_outputs/latest/` — latest generated supporting outputs.
- `mt5_output/latest/` — latest MT5-related supporting outputs when applicable.
- `prompts/` — prompt fragments and related prompt assets.
- `scripts/` — helper scripts and supporting tooling.

## Canonical control files
These files are the new control layer for architecture and operating discipline.

- `control/CURRENT_STATE.md` — current architecture snapshot, current risks, and immediate priorities.
- `control/NEXT_ACTIONS.md` — ordered implementation backlog split between user and assistant work.
- `control/DECISION_LOG.md` — stable record of key operating and architecture decisions.
- `control/CHATGPT_PROJECT_INSTRUCTIONS.md` — text to paste into the ChatGPT Project instructions for ETF work.
- `control/OPTIONAL_CUSTOM_GPT_SPEC.md` — optional spec for a helper GPT that acts as architect/reviewer, not as the production runner.

## Operating model
This repository should now be treated as having **four layers**:

### 1. Decision framework
What the ETF review is actually trying to decide:
- regime classification
- portfolio changes
- opportunity ranking
- structural opportunity monitoring
- portfolio evolution through time

Primary file today:
- `etf.txt`

### 2. Input/state contract
Where authoritative facts come from, in what order, and how conflicts are resolved.

Today the system still relies heavily on prior reports and report parsing. That is functional, but more fragile than explicit state files.

Target state:
- strategy intent from the latest report
- implementation facts from explicit state files
- current pricing from fresh market data where feasible

### 3. Output contract
How the final report must be structured and rendered.

Today this is still embedded mainly inside `etf.txt` and enforced partly by `send_report.py`.

### 4. Operational runbook
How a review session is actually executed from start to finish.

Today too much of this lives inside the prompt. Over time, more of it should move into scripts, manifests, and control docs.

## Session start rule
For architecture work, debugging, prompt changes, or flow redesign, start in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. the specific execution file relevant to the task

Recommended execution file priority by task:
- prompt logic → `etf.txt`
- delivery/rendering/email/PDF → `send_report.py`
- automation/scheduling/secrets/workflow → `.github/workflows/send-weekly-report.yml`
- historical continuity or latest live artifact → latest file in `output/`

## Session close rule
At the end of any meaningful architecture or implementation session:

1. record any stable decisions in `control/DECISION_LOG.md`
2. update `control/CURRENT_STATE.md` if the system materially changed
3. update `control/NEXT_ACTIONS.md` so the next session can restart cleanly

## Non-negotiable discipline
- Do not treat the latest report as the only source of truth for implementation state.
- Do not treat old report prices as current prices when fresh retrieval is feasible.
- Do not put all architecture, state, delivery, and workflow control back into one giant prompt.
- Do not claim delivery completion without a real manifest/receipt from the delivery layer.

## Current direction of travel
The target architecture for ETF is:

- **ChatGPT Project** as working memory and workbench
- **GitHub** as explicit state, audit trail, and operational source of truth
- **GitHub Actions + scripts** as the real execution and delivery layer
- **Optional Custom GPT** only as architect/reviewer, not as the main runtime container
