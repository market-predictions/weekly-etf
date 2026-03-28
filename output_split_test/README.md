# ETF Split-Test Output Folder

Use this folder for reports generated with the split runtime entrypoint.

## Naming
- `weekly_analysis_pro_YYMMDD.md`
- `weekly_analysis_pro_YYMMDD_NN.md`

## Rule
Keep the report content in the same report family as production.
The purpose is to compare outputs, not to introduce new logic.

## Workflow
A dedicated split-test GitHub Actions workflow listens to this folder and can render/send the latest split-test report for comparison.
