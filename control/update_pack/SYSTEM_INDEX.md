# ETF Review OS — System Index

This file is the **first entry point** for any serious work on the `daily-etf` system.

## Purpose
This repository now contains both:
1. **Execution files** — the files that produce and deliver the report.
2. **Control files** — the files that explain how the system is organized, what is authoritative, and what should happen next.

Use this file first so you do not start in the wrong place or collapse strategy, state, output, and delivery back into one monolith.

## Canonical execution files
Read these only after the control files and only when relevant to the task.

- `etf.txt` — current production masterprompt for the Weekly ETF Review.
- `etf-pro.txt` — premium editorial delivery-layer prompt used to convert the internal ETF output into the subscriber-facing pro version.
- `prompts/as_is_split/ETF_RUNTIME_SPLIT.txt` — split-test runtime entrypoint for the as-is ETF architecture comparison.
- `prompts/as_is_split/` — the four-layer split scaffold plus section map.
- `send_report.py` — delivery/rendering script for HTML email, PDF generation, attachments, and manifest logic.
- `.github/workflows/send-weekly-report.yml` — production GitHub Actions workflow.
- `.github/workflows/send-weekly-report-split-test.yml` — split-test workflow for evaluation runs from `output_split_test/`.
- `output/` — archived production ETF report outputs and related artifacts.
- `output_split_test/` — archived split-test ETF outputs used for comparison, not as production truth.
- `daily_outputs/latest/` — latest generated supporting outputs.
- `mt5_output/latest/` — latest supporting outputs when applicable.

## Canonical control files
These are the control-layer files for future sessions.

- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `control/DECISION_LOG.md`
- `control/CHATGPT_PROJECT_INSTRUCTIONS.md`
- `control/OPTIONAL_CUSTOM_GPT_SPEC.md`
- `control/PROJECT_BOOTSTRAP.md`

## Operating model
This repository should now be treated as having **four layers**.

### 1. Decision framework
What the ETF review is trying to decide:
- regime classification
- portfolio changes
- opportunity ranking
- structural opportunity monitoring
- portfolio evolution through time

Primary files today:
- `etf.txt`
- `prompts/as_is_split/01_DECISION_FRAMEWORK.md` for split evaluation

### 2. Input/state contract
Where authoritative facts come from, in what order, and how conflicts are resolved.

Today production still leans heavily on prior reports and the pricing-pass logic inside `etf.txt`. Over time ETF should move toward more explicit implementation state files, but those should not be invented silently ahead of the authority rules.

Primary files today:
- `etf.txt`
- `prompts/as_is_split/02_INPUT_STATE_CONTRACT.md` for split evaluation

### 3. Output contract
How the final report must be structured and rendered.

Today this still lives mainly inside `etf.txt` and is enforced partly by `send_report.py`. The ETF review remains the visual reference point for the reporting family and its executive look & feel must be preserved.

Primary files today:
- `etf.txt`
- `etf-pro.txt`
- `prompts/as_is_split/03_OUTPUT_CONTRACT.md` for split evaluation
- `send_report.py`

### 4. Operational runbook
How a review session is actually executed from start to finish.

Today too much of this still lives inside the prompt. The split scaffold exists so the runbook can be evaluated separately from the decision logic without changing production behavior.

Primary files today:
- `etf.txt`
- `prompts/as_is_split/04_OPERATIONAL_RUNBOOK.md` for split evaluation
- `.github/workflows/send-weekly-report.yml`
- `.github/workflows/send-weekly-report-split-test.yml`

## Session start rule
For architecture work, debugging, prompt changes, or flow redesign, start in this order:

1. `control/SYSTEM_INDEX.md`
2. `control/CURRENT_STATE.md`
3. `control/NEXT_ACTIONS.md`
4. only then open the specific execution file(s) needed for the task

Recommended execution file priority by task:
- prompt logic / methodology / structure → `etf.txt`
- premium editorial delivery layer → `etf-pro.txt`
- split-architecture evaluation → `prompts/as_is_split/ETF_RUNTIME_SPLIT.txt`
- delivery / rendering / email / PDF → `send_report.py`
- workflow / secrets / scheduling → `.github/workflows/send-weekly-report.yml`
- split-test delivery comparison → `.github/workflows/send-weekly-report-split-test.yml`
- historical continuity or latest live artifact → latest file in `output/`
- split-output comparison → latest file in `output_split_test/`

## Session close rule
At the end of any meaningful architecture or implementation session:

1. write stable decisions into `control/DECISION_LOG.md`
2. update `control/CURRENT_STATE.md` if the architecture changed
3. update `control/NEXT_ACTIONS.md` so the next session can restart without rediscovery

## Non-negotiable discipline
- Do not collapse decision logic, state logic, output rules, and delivery rules back into one giant opaque prompt.
- Do not weaken the ETF executive look & feel while splitting files.
- Do not treat split-test outputs as production truth.
- Do not claim delivery succeeded without a real receipt or manifest.
- Do not treat prior report prices as current prices when a fresh pricing pass is feasible.

## Current direction of travel
The target architecture for ETF is:

- **ChatGPT Project** as working memory and recurring workspace
- **GitHub** as explicit state, audit trail, and operational source of truth
- **GitHub Actions + scripts** as the real execution and delivery layer
- **Split prompt scaffold** as a safe evaluation layer while production remains protected
- **Optional Custom GPT** only as architect/reviewer, not as the main runtime container
