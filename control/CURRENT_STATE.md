# ETF Review OS — Current State

## Snapshot date
2026-06-12

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 macro event recency and report-surface QA repair has been implemented as pipeline/source changes and a rerun request has been created. The 2026-06-11 generated reports exposed client-surface defects: stale ECB stance, missing ECB policy catalyst, stale non-U.S. exposure wording, English `n.v.t.` residue, empty comment residue, and constraint wording that needed soft-cap/override clarity. WP16 fixed source logic and added regression tests, but successful clean delivery is not yet proven until the rerun produces valid GitHub Actions, run-manifest and delivery-manifest evidence. Deterministic macro remains not promoted. Historical generated outputs remain immutable by default.**

## Latest fully verified clean baseline before WP16 rerun

```text
workflow: Send weekly ETF Pro report
requested_close_date: 2026-06-10
run_id: 20260610_211606
report_token: 260610
english_report_path: output/weekly_analysis_pro_260610_02.md
dutch_report_path: output/weekly_analysis_pro_nl_260610_02.md
pricing_lineage_status: passed
delivery_status: smtp_sendmail_returned_no_exception
```

Delivery evidence remains delivery-layer evidence only. It is not an end-recipient inbox receipt.

## 2026-06-11 report QA finding

The 2026-06-11 reports were generated and uploaded for review, but should not be treated as clean premium final output without repair/rerun verification.

Confirmed defects:

```text
ECB stance remained Neutral / transition after a same-day ECB rate hike.
ECB rate-policy event was absent from the policy catalyst surface.
Non-U.S. exposure wording still implied zero/non-existent exposure although IEFA was a material position.
English position-performance output contained Dutch n.v.t. residue.
Dutch replacement-analysis surface exposed an empty comment residue.
Position constraint wording needed soft-cap / inherited-overweight / no-fresh-cash clarification.
Dutch equity-curve PDF clipping was observed in the uploaded PDF and requires rerun/render verification.
```

## WP16 repair status

```text
WP16 — Macro event recency and report-surface QA repair: implemented / rerun requested / delivery not yet verified
```

Files changed by WP16:

```text
runtime/build_macro_policy_pack.py
runtime/macro_report_surface.py
runtime/add_etf_position_performance_section.py
runtime/scrub_etf_client_surface.py
tests/test_wp16_report_surface_qa_contract.py
control/run_queue/weekly_etf_report_request_20260612_wp16_rerun.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

WP16 source changes:

```text
ECB same-week hike is surfaced as Tightening / inflation-sensitive for report dates >= 2026-06-11.
ECB rate-policy tightening is added as a report-transfer policy catalyst.
Macro surface can render up to three policy catalysts when the pack allows it.
English performance tables use n/a while Dutch keeps n.v.t.
Client-surface scrub removes empty comment residue.
Client-surface scrub replaces stale zero/non-U.S. exposure wording when IEFA/EFA/VEA is active.
Constraint copy is reframed as soft-cap / soft-target with inherited-state discipline.
```

WP16 regression tests:

```text
tests/test_wp16_report_surface_qa_contract.py
```

Rerun request:

```text
control/run_queue/weekly_etf_report_request_20260612_wp16_rerun.md
```

## Deterministic macro boundary

Current deterministic macro state remains:

```text
macro report surface: integrated as client-safe only
deterministic macro read as raw/shadow object: not client-facing
deterministic macro read as official decision/regime source: not promoted
```

Do not infer deterministic macro promotion from WP16. The ECB repair is a client-safe legacy macro policy-pack/report-surface repair, not deterministic macro promotion.

Standing deterministic macro authority boundary:

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

WP16 did not manually rewrite historical report artifacts. A clean report must be produced by rerunning the workflow.

## Four-layer operating status

### 1. Decision framework

- WP16 repairs report-surface QA only.
- It does not alter scoring, fundability, execution, delivery authority, or portfolio authority.
- It does not promote deterministic macro.

### 2. Input/state contract

- ECB same-week hike is represented inside the macro policy-pack path as client-safe descriptive policy context.
- Current production truth remains tied to manifest-linked runtime/pricing/delivery artifacts.

### 3. Output contract

- Future reports should not show stale ECB Neutral / transition wording when the 2026-06-11 ECB event applies.
- Future reports should not imply zero non-U.S. developed exposure when IEFA/EFA/VEA is active.
- English output should not contain Dutch `n.v.t.`.
- Empty comment residue should not surface in client reports.

### 4. Operational runbook

- The rerun request has been created.
- Do not claim successful report delivery until GitHub Actions, run manifest, delivery manifest, pricing lineage and persisted EN/NL artifacts are verified.

## Immediate next action

Verify the WP16 rerun:

```text
control/run_queue/weekly_etf_report_request_20260612_wp16_rerun.md
```

Required verification:

```text
GitHub Actions run success
run manifest exists
delivery manifest exists
English/Dutch reports exist
pricing lineage passes
ECB policy catalyst appears
ECB stance no longer says Neutral / transition
non-U.S. exposure wording reconciles with IEFA
English n.v.t. residue absent
empty comment residue absent
Dutch equity-curve render checked
```
