# ETF Control Update Pack

This folder contains **exact replacement drafts** for the existing ETF control files.

## Why this exists
The GitHub connector in this session allowed creation of new files, but did not reliably allow in-place overwrite of the existing control files.

To avoid losing the completed refactor work, the replacement content is stored here in full.

## Intended target files
- `control/SYSTEM_INDEX.md`
- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `control/DECISION_LOG.md`
- `control/CHATGPT_PROJECT_INSTRUCTIONS.md`

## Status
The split scaffold is already live in:
- `control/PROJECT_BOOTSTRAP.md`
- `prompts/as_is_split/`
- `.github/workflows/send-weekly-report-split-test.yml`
- `output_split_test/README.md`

This folder exists only to hold the exact updated content for the older control files until they are overwritten directly.
