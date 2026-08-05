# ETF Review OS — Project Bootstrap

## Purpose
This is the **one file** you should upload into the ChatGPT Project `ETF Review OS` as the stable project bootstrap.

Do **not** treat this file as the operational source of truth.
Its job is to point each session to the correct live files in GitHub.

## Core rule
- **ChatGPT Project** = working memory and workbench
- **GitHub** = live source of truth

That means:
- use this bootstrap file as the fixed starting context inside the ChatGPT Project
- use GitHub to read the current control files and execution files live
- avoid uploading changing repo files unless there is a specific reason

## First read sequence for meaningful ETF work
At the start of any serious ETF architecture, debugging, prompt, production, portfolio, or delivery session:

1. read `control/SYSTEM_INDEX.md` from GitHub
2. read `control/CURRENT_STATE.md` from GitHub
3. read `control/NEXT_ACTIONS.md` from GitHub
4. read `control/PROJECT_GOVERNANCE_BOOTSTRAP.md` for consequential work
5. only then read the minimum relevant execution file(s)

## Separation of duties

The project uses one user-facing coordinator and two internally separated roles:

```text
implementation_operations
governance_release_assurance
```

The user gives one instruction and receives one consolidated status. The user does not separately coordinate the two roles.

Implementation prepares the candidate. Governance independently reconstructs and certifies or rejects it. Implementation may not certify its own completion. Governance may not silently modify the candidate it reviews. A repaired candidate receives a new assurance pass.

The shared standard and current project maturity are linked from `control/PROJECT_GOVERNANCE_BOOTSTRAP.md`.

## Which execution files to read by task
### Prompt architecture / report logic
- `etf.txt`

### Rendering / PDF / email / manifest / delivery
- `send_report.py`

### Workflow / secrets / orchestration
- `.github/workflows/send-weekly-report.yml`

### Historical continuity / prior artifact review
- latest relevant file in `output/`

## Important architecture rule
The old ETF monolith should **not** silently become the dominant project context again.

So:
- do **not** upload `etf.txt` as default project context for now
- treat `etf.txt` as a **legacy reference document on GitHub** until it has been split into cleaner layers

## Required distinctions
Always keep these five layers separate in reasoning and recommendations:
1. decision framework
2. input/state contract
3. output contract
4. operational runbook
5. governance and release assurance

## Quality rules
- Prefer minimal, precise, non-destructive changes.
- Treat GitHub as the current truth when project context and repo content differ.
- Do not treat old report text as current pricing truth.
- Do not claim delivery succeeded without a real receipt or manifest from the delivery layer.
- Treat generated output as a release candidate until the required assurance pass exists.
- Report action execution separately from independently confirmed outcome.
- When proposing repo changes, identify the exact file(s) to edit.

## Minimal upload strategy for the ChatGPT Project
Recommended default upload set:
- this file only: `control/PROJECT_BOOTSTRAP.md`

Optional later additions only if there is a real need:
- a compact glossary
- a short naming-conventions file
- a future split-out ETF contract file after refactoring

## Session close rule
At the end of a meaningful ETF session, check whether GitHub should be updated in:
- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `control/DECISION_LOG.md`
- the project governance adoption or assurance files

## One-line reminder
**Upload this file to the ChatGPT Project; read the rest live from GitHub.**