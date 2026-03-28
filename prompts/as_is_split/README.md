# ETF Prompt As-Is Split

This folder contains a non-destructive architectural split of `etf.txt`.

## Purpose
The goal is to separate concerns **without changing**:
- research logic
- decision methodology
- scoring rules
- presentation contract
- delivery expectations
- executive look and feel

## Current authority
`etf.txt` remains the current production source.

These split files are parallel reference files only.

## Files
- `01_DECISION_FRAMEWORK.md`
- `02_INPUT_STATE_CONTRACT.md`
- `03_OUTPUT_CONTRACT.md`
- `04_OPERATIONAL_RUNBOOK.md`
- `05_SECTION_MAP.md`

## Use
Use `05_SECTION_MAP.md` to see how the original prompt sections were redistributed.
