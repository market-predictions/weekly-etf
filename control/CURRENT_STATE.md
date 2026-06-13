# ETF Review OS — Current State

## Snapshot date

2026-06-13

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16, WP17, WP18, WP19, WP20, and WP21 are closed. WP22 deterministic regime client-safe surface validator is implemented but pending validation evidence. The latest manifest-linked production baseline remains `260612_08`. Deterministic macro remains not promoted. Historical generated outputs remain immutable by default.**

## Latest verified production baseline

```text
requested_close_date: 2026-06-12
run_id: 20260613_113054
report_token: 260612
english_report_path: output/weekly_analysis_pro_260612_08.md
dutch_report_path: output/weekly_analysis_pro_nl_260612_08.md
pricing_lineage_status: passed
workflow_status: workflow_success
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-12_20260613_113054.json
delivery_status: smtp_sendmail_returned_no_exception
total_portfolio_value_eur: 108243.33
cash_eur: 1936.52
fresh_holdings_count: 9
carried_forward_holdings_count: 0
```

Delivery evidence remains delivery-layer evidence only. It is not an end-recipient inbox receipt.

## Closed package status

```text
WP16: closed — report repair closeout
WP17: closed — PDF visual QA and delivery-runbook hardening
WP18: closed — macro audit foundation, shadow-only
WP19: closed — deterministic regime engine fixture baseline, shadow-only
WP20: closed — deterministic regime engine promotion review, not_promoted
WP21: closed — deterministic regime client-safe surface design, design-only
```

WP20 review status remains:

```text
status=not_promoted
client_facing_narrative_authority=false
production_report_narrative_authority=false
control_layer_decision=not_promoted
explicit_control_layer_promotion_decision=false
```

WP21 design artifact:

```text
control/DETERMINISTIC_REGIME_CLIENT_SAFE_SURFACE_DESIGN.md
```

WP21 blocked direct report concepts:

```text
raw macro axes
raw macro axis scores
raw macro evidence
raw confidence decomposition
raw conflict scores
workflow run ids
fixture names
source file paths in client report
production action wording
scoring or fundability wording
predictive certainty
```

## WP22 deterministic regime client-safe surface validator status

WP22 is implemented but not yet closed.

Status:

```text
implemented / pending validation evidence
```

Implemented files:

```text
fixtures/deterministic_regime_client_surface/safe_surface_fixture.json
tools/validate_deterministic_regime_client_surface.py
tests/test_deterministic_regime_client_surface_validator.py
control/DETERMINISTIC_REGIME_CLIENT_SURFACE_VALIDATOR_STATUS.md
```

Implemented checks:

```text
required DTO fields
false authority fields
safe English and Dutch text
review-only wording
confidence band rather than raw numeric confidence
blocked raw macro fields and source paths absent from surface text
macro compliance scan
macro/thesis leakage scan
```

Manual validation commands:

```bash
python tools/validate_deterministic_regime_client_surface.py --self-test
python -m pytest tests/test_deterministic_regime_client_surface_validator.py -q
python tools/validate_deterministic_regime_client_surface.py --surface fixtures/deterministic_regime_client_surface/safe_surface_fixture.json
```

Expected markers:

```text
DETERMINISTIC_REGIME_CLIENT_SURFACE_SELF_TEST_OK
DETERMINISTIC_REGIME_CLIENT_SURFACE_OK
```

Workflow note:

```text
A dedicated workflow create attempt was blocked by the tool safety layer in this chat run. WP22 is therefore not workflow-proven yet.
```

## Deterministic macro boundary

Current deterministic macro state remains:

```text
macro report surface: integrated as client-safe only
deterministic macro read as raw/shadow object: not client-facing
deterministic macro read as official decision/regime source: not promoted
deterministic regime engine: not promoted
deterministic regime client-safe surface: design-only, not production-integrated
WP22 validator: implemented, pending validation evidence
```

Do not infer deterministic macro promotion from WP16 through WP22.

Standing authority boundary:

```text
client_facing_narrative_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
delivery_authority=false
execution_authority=false
production_report_mutation=false
```

## Historical artifact policy

WP15 remains active:

```text
historical_output_artifacts_are_immutable_by_default=true
current_baseline_scope=manifest_linked_latest_report_set
historical_output_mutation=false
```

WP16 through WP22 did not manually rewrite historical report artifacts. Current production truth is tied to the latest manifest-linked report/runtime/pricing/delivery artifacts.

## Four-layer operating status

### 1. Decision framework

- WP20 reviewed deterministic regime engine promotion readiness and kept it not promoted.
- WP21 defined a future client-safe deterministic regime surface shape without implementation.
- WP22 adds a validator/helper-only layer for that design, pending validation evidence.
- WP16 through WP22 do not promote deterministic macro.

### 2. Input/state contract

- Current production truth remains tied to manifest-linked runtime/pricing/delivery artifacts.
- Macro audit values remain provenance input evidence only and are not production decision authority.
- WP22 validates only a fixture DTO, not a production report path.

### 3. Output contract

- WP21 defines the future safe output surface.
- WP22 implements validation checks for fixture-rendered safe-surface text.
- WP22 does not integrate deterministic regime output into English/Dutch reports.

### 4. Operational runbook

- Do not claim inbox delivery; delivery evidence remains `smtp_sendmail_returned_no_exception` plus delivery manifest.
- Do not start WP23 until WP22 validation evidence is green and recorded.

## Immediate next action

Validate WP22 with the manual commands above or add a dedicated workflow outside this blocked tool path.

After green validation evidence, close WP22 and only then consider:

```text
WP23 — Deterministic regime safe-surface helper
```
