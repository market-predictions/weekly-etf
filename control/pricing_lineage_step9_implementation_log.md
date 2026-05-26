# ETF Pricing Lineage Step 9 Implementation Log

## 2026-05-24 — Enforce valuation-grade challenger pricing discipline

### Current issue

The ETF workflow could price challengers and score lanes, but the system still allowed discovery/radar candidates and replacement-duel rows to look decision-relevant without a hard distinction between research-grade pricing and valuation-grade pricing.

### Root cause

The pricing audit now carries `pricing_tier`, but the lane scoring and replacement-duel layers did not yet enforce that a fundable challenger must have `pricing_tier == valuation_grade` plus a priced close status.

### What changed

- `runtime/score_etf_lanes.py`
  - Added valuation-grade and research-grade constants.
  - Added `price_tier_by_symbol` and `price_source_by_symbol` to `LaneContext`.
  - Added fundability classification for lanes.
  - Added `fundability_status`, `is_fundable_candidate`, primary/alternative pricing tier, and pricing source fields to lane artifacts.
  - Promoted challenger lanes that are not valuation-grade priced are marked as radar-only through `promotion_fundability_note`.

- `runtime/discover_etf_lanes.py`
  - Reads `pricing_tier` and source from the pricing audit.
  - Passes pricing tier/source into lane scoring.
  - Updates discovery engine version to `lane_discovery_v4_valuation_grade_fundability`.
  - Prints the count of promoted fundable lanes in workflow logs.

- `runtime/replacement_duel_v2.py`
  - Adds challenger pricing tier/status fields to replacement-duel rows.
  - Requires valuation-grade challenger pricing before actionable replacement language is allowed.
  - Non-valuation-grade challenger pricing now produces review-only language.

- `tools/validate_replacement_duel_pricing_contract.py`
  - Adds a hard failure if a duel row looks actionable without valuation-grade challenger pricing.
  - Converts missing valuation-grade challenger rows into warnings unless they are shown as actionable.

- `tools/validate_etf_challenger_fundability_contract.py`
  - New validator for lane-level fundability discipline.
  - Fails if `is_fundable_candidate` is true without a valuation-grade audit row.
  - Fails if a promoted challenger lacks valuation-grade pricing and lacks an explicit fundability note.

### Affected files

- `runtime/score_etf_lanes.py`
- `runtime/discover_etf_lanes.py`
- `runtime/replacement_duel_v2.py`
- `tools/validate_replacement_duel_pricing_contract.py`
- `tools/validate_etf_challenger_fundability_contract.py`
- `control/pricing_lineage_step9_implementation_log.md`

### Validation / evidence

No production workflow run has been executed yet after this implementation. Expected future evidence:

- Lane artifact contains `fundability_status`, `is_fundable_candidate`, pricing tier, and pricing source fields.
- Replacement-duel rows contain `challenger_pricing_tier` and `valuation_grade_pricing_complete`.
- `tools/validate_replacement_duel_pricing_contract.py` fails actionable duel rows without valuation-grade challenger pricing.
- `tools/validate_etf_challenger_fundability_contract.py` fails fundable challenger lanes without valuation-grade audit rows.

### Known follow-up

The new fundability validator exists but still needs to be wired into `.github/workflows/send-weekly-report.yml` in a later workflow-only patch. This log exists because the central changelog file is large; the next housekeeping patch should merge this entry into `control/ETF_PRICING_LINEAGE_CHANGELOG.md` and optionally the root `changelog.md`.
