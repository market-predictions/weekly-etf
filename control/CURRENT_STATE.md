# ETF Review OS — Current State

## Snapshot date

2026-06-13

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**WP16 macro event recency and report-surface QA repair is closed on the latest verified report set `260612_06`. The latest manifest-linked production run succeeded with pricing lineage passed, EN/NL artifacts generated, delivery-manifest evidence written, Dutch equity-curve rendering fixed, and Dutch ETF/product-name corruption fixed. Deterministic macro remains not promoted. Historical generated outputs remain immutable by default.**

## Latest verified production baseline

```text
requested_close_date: 2026-06-12
run_id: 20260613_094305
report_token: 260612
english_report_path: output/weekly_analysis_pro_260612_06.md
dutch_report_path: output/weekly_analysis_pro_nl_260612_06.md
pricing_lineage_status: passed
workflow_status: workflow_success
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-12_20260613_094305.json
delivery_status: smtp_sendmail_returned_no_exception
total_portfolio_value_eur: 108243.33
cash_eur: 1936.52
fresh_holdings_count: 9
carried_forward_holdings_count: 0
```

Delivery evidence remains delivery-layer evidence only. It is not an end-recipient inbox receipt.

## WP16 repair closeout status

WP16 and its follow-ups are closed for the latest verified client-surface baseline.

Resolved issues:

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
GSG continuity product name now renders as iShares S&P GSCI Commodity-Indexed Trust.
```

Latest `260612_06` uploaded PDF QA evidence confirms:

```text
English equity curve visible.
Dutch equity curve visible.
Dutch GSG product name correct.
No iAantal aandelen corruption observed in the Dutch continuity table.
```

## Deterministic macro boundary

Current deterministic macro state remains:

```text
macro report surface: integrated as client-safe only
deterministic macro read as raw/shadow object: not client-facing
deterministic macro read as official decision/regime source: not promoted
```

Do not infer deterministic macro promotion from WP16 or its follow-ups.

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

WP16 follow-ups did not manually rewrite historical report artifacts. Current production truth is tied to the latest manifest-linked report/runtime/pricing/delivery artifacts.

## Four-layer operating status

### 1. Decision framework

- WP16 repaired report-surface QA and macro-event recency handling.
- It did not alter scoring, fundability, execution authority, or portfolio authority.
- It did not promote deterministic macro.
- ETF/product names are now treated as protected product terms and must not be translated by Dutch localization.

### 2. Input/state contract

- Current production truth remains tied to manifest-linked runtime/pricing/delivery artifacts.
- Uploaded PDFs are QA evidence, not source-of-truth state.
- Latest pricing lineage is passed for all 9 holdings.

### 3. Output contract

- Future reports must not expose empty-comment residue, duplicated soft-cap wording, English/Dutch language leakage, Dutch equity-curve clipping, or product-name localization corruption such as `iAantal aandelen`.

### 4. Operational runbook

- Do not claim inbox delivery; the latest delivery evidence is `smtp_sendmail_returned_no_exception` plus delivery manifest.
- Manual GitHub Actions starts may still be required when run-queue pushes do not automatically trigger the workflow.

## Immediate next action

Return to the roadmap proper. Recommended next choice:

```text
Option A — resume macro/thesis roadmap Phase 2: macro audit foundation
Option B — strengthen delivery/runbook verification and PDF visual gates
```

Recommended default: Option B for one small package first, because WP16 showed that visual PDF defects can pass text validators unless explicitly checked. Then resume macro/thesis roadmap Phase 2.
