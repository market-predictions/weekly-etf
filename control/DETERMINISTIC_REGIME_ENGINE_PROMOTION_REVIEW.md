# Deterministic Regime Engine Promotion Review

## Work package

```text
WP20 — Deterministic regime engine promotion-review contract
```

## Repository

```text
market-predictions/weekly-etf
```

## Snapshot date

```text
2026-06-13
```

## Layer

```text
decision framework + input/state contract
```

## Status

```text
reviewed / not_promoted / no production mutation
```

## Decision

The deterministic regime engine is **not promoted** to client-facing or production report narrative authority in WP20.

The valid promotion-review artifact is:

```text
output/macro/promotion/deterministic_regime_engine_promotion_review_20260613_000000.json
```

WP20 recognizes that the deterministic regime engine has a green fixture baseline and green shadow-validation evidence, but this is not enough to grant production report authority.

## Evidence reviewed

```text
WP18 macro audit foundation: closed / verified / shadow-only
WP19 deterministic regime fixture baseline: closed / verified / shadow-only
latest macro-regime shadow workflow: green
workflow_run_id: 27480244857
workflow_run_number: 46
workflow_commit_sha: 1ba3f4e5a6126fd824a151525b0d9d91d42c3627
latest_shadow_evidence_path: output/macro/validation/latest_macro_regime_shadow_validation.json
latest_shadow_comparison_path: output/macro/validation/latest_macro_regime_shadow_comparison.json
```

Latest reviewed comparison state:

```text
legacy_regime: Risk-on growth
shadow_candidate_regime: Risk-on growth
regime_label_differs: false
confidence_differs: true
promotion_status: not_promoted
```

## Promotion gates

The promotion contract requires all of the following before deterministic macro can become report narrative authority:

```text
methodology_approved=true
bilingual_parity_approved=true
compliance_validator_passed=true
old_vs_new_comparison_reviewed=true
explicit_control_layer_promotion_decision=true
```

WP20 assessment:

```text
methodology_approved=false
bilingual_parity_approved=false
compliance_validator_passed=false
old_vs_new_comparison_reviewed=true
explicit_control_layer_promotion_decision=false
```

Because not all gates are true, the only valid status is:

```text
not_promoted
```

## Authority boundary

WP20 does not grant any of these authorities:

```text
client_facing_narrative_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
execution_authority=false
delivery_authority=false
production_report_mutation=false
historical_output_mutation=false
```

## Four-layer distinction

### 1. Decision framework

WP20 decides whether the deterministic regime engine is ready to be promoted from shadow evidence to production report narrative authority.

Decision:

```text
not_promoted
```

The deterministic regime engine remains evidence for future review only.

### 2. Input/state contract

The reviewed inputs are:

```text
control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
control/DETERMINISTIC_MACRO_READ_PROMOTION_REVIEW.md
control/MACRO_REPORT_SURFACE_STATUS.md
control/MACRO_AUDIT_FOUNDATION_STATUS.md
control/MACRO_REGIME_SHADOW_STATUS.md
output/macro/validation/latest_macro_regime_shadow_validation.json
output/macro/validation/latest_macro_regime_shadow_comparison.json
```

The current production macro input remains:

```text
output/macro/latest.json
```

Raw deterministic fields remain blocked from production report surfaces:

```text
deterministic_regime_shadow
macro_axes
macro_axis_scores
macro_evidence
confidence_decomposition
```

### 3. Output contract

WP20 does not change English or Dutch report output.

A future output-contract package may design a client-safe deterministic regime surface, but it must not copy raw macro axes or raw shadow payload fields into the report.

Allowed future direction, only if separately approved:

```text
safe renderer -> concise English/Dutch deterministic regime summary -> compliance and bilingual gates -> separate integration package
```

Blocked in WP20:

```text
raw deterministic_regime_shadow in report
raw macro_axes in report
raw macro_axis_scores in report
raw confidence_decomposition in report
production report wording mutation
portfolio or scoring mutation
```

### 4. Operational runbook

WP20 creates a promotion-review artifact only. It does not run the production report workflow, does not send email, does not mutate portfolio state, and does not change delivery artifacts.

Validation command for the WP20 artifact:

```bash
python tools/validate_macro_regime_promotion_contract.py output/macro/promotion/deterministic_regime_engine_promotion_review_20260613_000000.json
```

Expected result:

```text
MACRO_REGIME_PROMOTION_CONTRACT_OK
```

## Next action

Proceed only to a separate output-contract design package if desired:

```text
WP21 — Deterministic regime client-safe report surface design
```

WP21 must remain design/output-contract work unless separately authorized. It must not promote or integrate deterministic regime output into production reports by implication.
