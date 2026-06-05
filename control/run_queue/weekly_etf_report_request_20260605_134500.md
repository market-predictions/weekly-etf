# Weekly ETF report request

Date: 2026-06-05

Purpose:

Trigger a fresh Weekly ETF Pro production run after fixing the upstream runtime-state score enrichment for active ETF positions.

Issue observed in the generated PDFs:

- English `Current Position Review` still showed `n/a` scores for CIBR, DFEN, GSG, IEFA and XLU.
- Dutch `Review huidige posities` still showed `n/a` scores for the same active holdings.
- This occurred because the PDF/HTML delivery surface uses the native runtime table renderer, while the earlier patch only improved a later output-contract path.

Patch under verification:

- `runtime/build_etf_report_state.py` now enriches active holdings with a score before rendering:
  - existing position scorecard score when available
  - live lane-assessment score when available
  - deterministic semantic fallback score only where no comparable lane score exists yet
- `tools/validate_etf_current_position_scores.py` was added to validate that active positions have numeric scores in runtime state and report surfaces.

Validation focus after completion:

- No active position in Current Position Review may show `n/a`, `n.v.t.`, blank, `None`, or `-` in the score column.
- CIBR, DFEN, GSG, IEFA, PAVE, SMH, SPY, URNM and XLU must all have numeric scores.
- English and Dutch PDF/HTML delivery surfaces must reflect the same score completeness.
- Section 7A must retain semantic thesis labels.
- GLD must not appear as a current active holding, current hedge review, current action item, or current replacement source when not active.
- Delivery evidence remains SMTP-send manifest evidence only, not inbox receipt.
