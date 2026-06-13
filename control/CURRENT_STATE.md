# ETF Review OS — Current State

## Snapshot date

2026-06-13

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 is closed, WP17 PDF visual QA / delivery-runbook hardening is closed, WP18 macro audit foundation is closed, WP19 deterministic regime engine fixture baseline is closed, and WP20 deterministic regime engine promotion review is closed as `not_promoted`. The latest manifest-linked production baseline remains `260612_08`. Deterministic macro remains not promoted. Historical generated outputs remain immutable by default. The next package is WP21 — Deterministic regime client-safe report surface design.**

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

## WP16 repair closeout status

WP16 and its follow-ups are closed for the latest verified client-surface baseline.

Resolved WP16 issues:

```text
ECB macro recency miss repaired.
ECB stance now surfaces as Tightening / inflation-sensitive / Verkrappend / inflatiegevoelig.
ECB rate-policy tightening appears as a policy catalyst.
Non-U.S. developed exposure wording is reconciled with active IEFA exposure.
English performance tables no longer use Dutch n.v.t. residue.
Dutch empty-comment residue is removed.
Soft-cap / soft-target duplicate wording is normalized.
Dutch equity curve renders visibly in PDF.
No-trade model execution artifacts are accepted in shadow and guarded-auto modes when no trade intents exist.
Dutch ETF/product names are protected from localization corruption.
GSG continuity product name renders as iShares S&P GSCI Commodity-Indexed Trust.
```

## WP17 closeout status

WP17 is closed on `260612_08`.

Implemented and verified:

```text
PDF visual contract validator added.
Poppler rendering tools installed in the production workflow.
EN/NL PDF equity-curve visual gate runs before send.
Dutch PDF product-name corruption gate runs before send.
Manifest evidence validator added.
Manifest evidence gate runs after final run-manifest write.
Latest run #247 succeeded after these gates were wired.
```

## WP18 macro audit foundation closeout status

WP18 is closed.

Closeout evidence:

```text
Validate ETF macro audit foundation: green
workflow_run_id: 27476145040
workflow_run_number: 6
latest_wp18_macro_audit_foundation_validation.json: committed

Validate ETF macro regime shadow: green
workflow_run_id: 27478580626
workflow_run_number: 40
latest_macro_regime_shadow_validation.json: committed
```

WP18 remains:

```text
shadow_only=true
client_facing_authority=false
decision_impact=none_phase2_audit_only
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
production_report_path_changed=false
```

## WP19 deterministic regime engine fixture baseline closeout status

WP19 is closed.

Implemented:

```text
Added explicit no-authority flags to deterministic shadow payloads.
Hardened tools/validate_macro_regime_shadow.py.
Hardened tools/replay_macro_regime_shadow_fixtures.py.
Added no-authority fields to fixtures/macro_regime_shadow/regime_shadow_fixtures.json.
Hardened tools/write_macro_regime_shadow_validation_evidence.py.
Added tests/test_macro_regime_shadow.py.
Updated .github/workflows/validate-macro-regime-shadow.yml to run the WP19 tests.
Updated control/MACRO_REGIME_SHADOW_STATUS.md.
```

Closeout evidence:

```text
Validate ETF macro regime shadow: green
workflow_run_id: 27480244857
workflow_run_number: 46
commit_sha: 1ba3f4e5a6126fd824a151525b0d9d91d42c3627
latest_macro_regime_shadow_validation.json: committed
```

WP19 remains:

```text
fixture-only=true
shadow_only=true
client_facing_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
historical_output_mutation=false
```

## WP20 deterministic regime engine promotion-review closeout status

WP20 is closed as review-only and not promoted.

Review artifact:

```text
output/macro/promotion/deterministic_regime_engine_promotion_review_20260613_000000.json
```

Review status:

```text
status=not_promoted
client_facing_narrative_authority=false
production_report_narrative_authority=false
control_layer_decision=not_promoted
explicit_control_layer_promotion_decision=false
```

Reviewed evidence:

```text
latest_shadow_evidence_path: output/macro/validation/latest_macro_regime_shadow_validation.json
latest_shadow_comparison_path: output/macro/validation/latest_macro_regime_shadow_comparison.json
latest_shadow_workflow_run_id: 27480244857
latest_shadow_workflow_run_number: 46
shadow_candidate_regime: Risk-on growth
legacy_regime: Risk-on growth
regime_label_differs: false
confidence_differs: true
```

Promotion gates assessed:

```text
methodology_approved=false
bilingual_parity_approved=false
compliance_validator_passed=false
old_vs_new_comparison_reviewed=true
explicit_control_layer_promotion_decision=false
```

Because not all gates are true, deterministic regime output remains shadow-only and not promoted.

WP20 does not authorize:

```text
client_facing_narrative_authority
production_report_narrative_authority
portfolio_action_authority
lane_scoring_authority
fundability_authority
funding_authority
portfolio_mutation
execution_authority
delivery_authority
production_report_mutation
historical_output_mutation
```

## Deterministic macro boundary

Current deterministic macro state remains:

```text
macro report surface: integrated as client-safe only
deterministic macro read as raw/shadow object: not client-facing
deterministic macro read as official decision/regime source: not promoted
deterministic regime engine: not promoted
```

Do not infer deterministic macro promotion from WP16, WP17, WP18, WP19, WP20, or their follow-ups.

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

WP16/WP17/WP18/WP19/WP20 did not manually rewrite historical report artifacts. Current production truth is tied to the latest manifest-linked report/runtime/pricing/delivery artifacts.

## Four-layer operating status

### 1. Decision framework

- WP16 repaired report-surface QA and macro-event recency handling.
- WP17 hardened visual PDF QA and delivery-runbook evidence.
- WP18 closed the shadow-only macro audit foundation validation path.
- WP19 closed the shadow-only deterministic regime engine fixture baseline.
- WP20 reviewed deterministic regime engine promotion readiness and kept it not promoted.
- WP16 through WP20 do not alter scoring, fundability, execution authority, or portfolio authority.
- WP16 through WP20 do not promote deterministic macro.

### 2. Input/state contract

- Current production truth remains tied to manifest-linked runtime/pricing/delivery artifacts.
- Uploaded PDFs are QA evidence, not source-of-truth state.
- Latest pricing lineage is passed for all 9 holdings.
- Macro audit values remain provenance input evidence only and are not production decision authority.
- WP18 proves the macro audit fixture/replay evidence path and compatibility with the shadow-regime validation stack.
- WP19 proves deterministic regime fixture coverage and explicit no-authority payload validation.
- WP20 records a not-promoted review artifact under the promotion contract.

### 3. Output contract

- Future reports must not expose empty-comment residue, duplicated soft-cap wording, English/Dutch language leakage, Dutch equity-curve clipping, invisible charts, or product-name localization corruption such as `iAantal aandelen`.
- PDF visual validation is now part of the pre-send gate.
- WP18 macro audit fixture validation writes evidence only under `output/macro/validation/` and does not change client reports.
- WP19 macro-regime shadow validation evidence is internal/shadow-only and must not leak to client reports.
- WP20 does not change English or Dutch report output.

### 4. Operational runbook

- Do not claim inbox delivery; the latest delivery evidence is `smtp_sendmail_returned_no_exception` plus delivery manifest.
- Manual GitHub Actions starts may still be required when run-queue pushes do not automatically trigger the workflow.
- Latest successful report baseline after WP17 is `260612_08`.
- WP18 is closed after green macro-audit foundation and macro-regime shadow validation evidence.
- WP19 is closed after green deterministic regime fixture baseline evidence.
- WP20 is closed after a valid not-promoted promotion-review artifact.
- The next package is WP21.

## Immediate next action

Start the next package only if desired:

```text
WP21 — Deterministic regime client-safe report surface design
```

WP21 must remain output-contract design work unless a separate implementation package is approved.

Required WP21 boundary:

```text
design_only=true
client_facing_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
historical_output_mutation=false
```
