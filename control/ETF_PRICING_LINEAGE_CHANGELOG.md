# ETF Pricing Lineage Changelog

This file is the central changelog for the ETF pricing-lineage repair track. It is separate from the root `changelog.md` so pricing regressions, design decisions, and validation changes can be reviewed without scanning unrelated rendering, localization, or delivery changes.

## Rules

- Record every meaningful pricing-lineage design, code, workflow, validation, and state-contract change.
- Keep entries implementation-facing and regression-friendly.
- Include why the change was made, what changed, affected files, and validation evidence.
- Do not use this file for ordinary report content changes unless they affect pricing lineage.
- Keep root `changelog.md` updated for repo-level visibility; keep this file as the detailed pricing-lineage log.

---

## 2026-05-31 — Add hard pricing-lineage validator and pre-send gate

### Current issue

The ETF workflow had immutable run ids, run-scoped pricing audits, run manifests, persisted valuation state, and visible close-price disclosure, but it still lacked the hard end-to-end validator required by `ETF_PRICING_LINEAGE_CONTRACT_V1`.

That meant a report could be internally useful while the workflow still did not prove, in one gate, that manifest → audit → runtime state → report tables → persisted portfolio state → valuation history all came from the same immutable pricing audit.

### Root cause

The existing validators covered important pieces separately:

- pricing-basis disclosure
- equity-curve history
- persisted valuation state
- challenger fundability
- delivery HTML/client-surface cleanliness

But no single validator enforced the complete pricing-lineage contract. In addition, the final always-run manifest write stored generic workflow lifecycle labels such as `workflow_success` in `pricing_lineage_status`, which blurred the difference between workflow completion and pricing-lineage proof.

### What changed

- Added `tools/validate_etf_pricing_lineage_contract.py`.
  - Validates the current run manifest.
  - Verifies the manifest points to one exact pricing audit and runtime state.
  - Verifies `runtime.source_files.pricing_audit` equals the exact audit path.
  - Verifies audit fresh/exact status semantics.
  - Verifies required priced-row lineage fields for priced rows.
  - Verifies runtime holding prices/statuses equal audit selected closes/statuses.
  - Verifies report close-disclosure values equal audit selected closes.
  - Verifies Section 7 NAV equals Section 15 NAV and runtime NAV.
  - Recalculates NAV from shares × selected close ÷ FX + cash.
  - Verifies `output/etf_portfolio_state.json` and `output/etf_valuation_history.csv` match the runtime valuation.
  - Verifies fundable challenger lanes have valuation-grade priced audit rows.
  - Writes `pricing_lineage_status=passed` into the run manifest when the contract passes.

- Updated `tools/write_weekly_etf_run_manifest.py`.
  - Preserves `pricing_lineage_status=passed` if the final always-run manifest update later writes a generic `workflow_*` status.
  - Adds a separate `workflow_status` field so workflow lifecycle and pricing-lineage proof are no longer conflated.

- Updated `tools/validate_etf_client_surface_clean.py`.
  - Calls the hard pricing-lineage validator as part of the existing pre-send validation path.
  - The production workflow already runs this tool before email delivery, so delivery now fails before send if the pricing-lineage contract does not pass.

### Affected files

- `tools/validate_etf_pricing_lineage_contract.py`
- `tools/write_weekly_etf_run_manifest.py`
- `tools/validate_etf_client_surface_clean.py`
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md`
- `changelog.md`

### Validation / evidence

No production workflow run has been executed yet after this patch.

Expected evidence in the next fresh workflow run:

```text
ETF_PRICING_LINEAGE_CONTRACT_OK
ETF_PRICING_LINEAGE_PRE_SEND_GATE_OK
```

The final run manifest should keep:

```text
pricing_lineage_status = passed
```

while separately recording the generic workflow status/conclusion.

### Status

This implements the missing Phase 1B hard validator and pre-send delivery block. The pricing-lineage baseline should not be called production-proven until the next fresh workflow run passes this gate and commits the resulting run manifest.

---

## 2026-05-27 — Preserve fundability notes after lane-quality repromotion

### Current issue

The fresh ETF workflow failed at `Validate ETF challenger fundability contract`. The log showed: `COPX: promoted challenger lacks valuation-grade pricing and lacks fundability note`.

### Root cause

The Step 9 lane-scoring layer correctly added `promotion_fundability_note` for promoted challengers that are radar-only rather than valuation-grade fundable. However, `runtime/augment_lane_artifact_with_quality_filters.py` runs after final lane discovery and repromotes lanes by score. That quality-filter repromotion cleared `rejection_reason` and set `promoted_to_live_radar=True`, but did not re-apply the Step 9 fundability note. As a result, a non-valuation-grade promoted challenger such as `COPX` could be valid as radar-only, yet fail the validator because the note had been dropped/never restored after repromotion.

### What changed

- Updated `runtime/augment_lane_artifact_with_quality_filters.py`.
  - Added `FUNDABLE_STATUS = "funding_candidate_valuation_grade"`.
  - Added `_needs_fundability_note()` and `ensure_fundability_note()`.
  - Added `clear_rejection_if_promoted()` so quality-filter promotion preserves or restores an explicit radar-only note.
  - `augment_lane()` and `repromote()` now ensure every promoted challenger without valuation-grade fundability carries: `Promoted to radar only; funding requires valuation-grade pricing.`

### Affected files

- `runtime/augment_lane_artifact_with_quality_filters.py`
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md`

### Validation / evidence

A production workflow run failed before this patch with:

```text
RuntimeError: ETF challenger fundability contract failed: COPX: promoted challenger lacks valuation-grade pricing and lacks fundability note
```

Expected evidence after rerun:

- `ETF_LANE_QUALITY_FILTERS_OK`
- `ETF_CHALLENGER_FUNDABILITY_CONTRACT_OK`
- any promoted challenger lacking valuation-grade pricing includes `promotion_fundability_note` in the lane artifact

---

## 2026-05-24 — Close Phase 1B Step 9 by wiring challenger fundability validation into workflow

### Current issue

The new challenger fundability validator existed, but it was not yet part of the production workflow. That meant valuation-grade challenger discipline could be implemented in code and artifacts, while production delivery could still proceed without the dedicated lane-level fundability gate.

### Root cause

`tools/validate_etf_challenger_fundability_contract.py` was added after the Step 9 model changes, but `.github/workflows/send-weekly-report.yml` still moved directly from final lane discovery into runtime state build. The workflow needed a hard validation step using the exact final lane artifact and exact immutable pricing audit for the current run.

### What changed

- Updated `.github/workflows/send-weekly-report.yml`.
  - Added `Validate ETF challenger fundability contract` immediately after final lane discovery and lane-quality augmentation.
  - The validator receives the exact current-run artifacts:
    - `--lane-artifact "$ETF_LANE_ARTIFACT_PATH"`
    - `--pricing-audit "$ETF_PRICING_AUDIT_PATH"`
  - Runtime state/report build now only proceeds after challenger fundability validation passes.

### Affected files

- `.github/workflows/send-weekly-report.yml`
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md`

### Validation / evidence

No production workflow run has been executed yet after this workflow-wiring change. Expected evidence in the next run:

- `ETF_CHALLENGER_FUNDABILITY_CONTRACT_OK`
- failure if a lane is marked `is_fundable_candidate=true` without a valuation-grade audit row
- failure if a promoted challenger lacks valuation-grade pricing and lacks an explicit radar-only/fundability note

### Status

This closes Phase 1B Step 9 at model + validator + workflow level. Remaining pricing-lineage work:

- add independent cross-provider verification so `fresh_exact_close` can be used instead of `fresh_exact_unverified`

---

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
- `control/ETF_PRICING_LINEAGE_CHANGELOG.md`

### Validation / evidence

No production workflow run has been executed yet after this implementation. Expected evidence:

- Lane artifact contains `fundability_status`, `is_fundable_candidate`, pricing tier, and pricing source fields.
- Replacement-duel rows contain `challenger_pricing_tier` and `valuation_grade_pricing_complete`.
- `tools/validate_replacement_duel_pricing_contract.py` fails actionable duel rows without valuation-grade challenger pricing.
- `tools/validate_etf_challenger_fundability_contract.py` fails fundable challenger lanes without valuation-grade audit rows.
