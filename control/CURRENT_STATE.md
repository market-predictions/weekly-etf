# ETF Review OS — Current State

## Snapshot date
2026-06-12

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**ETF has a latest successful runtime-driven bilingual production baseline for run `20260610_211606` / report set `260610_02`, with pricing-lineage proof, 100.0% fresh holdings coverage, run-manifest evidence, delivery-manifest evidence, and marker-free replacement-edge diagnostic notes. The prior workflow run #216 / run `20260605_081216` remains historical evidence only and is no longer the current production baseline. The client-safe macro report surface is integrated through the macro policy pack, but the raw deterministic macro read remains non-client-facing and is not promoted as the official production regime source. WP13 added a deterministic macro promotion-review checklist only; it did not promote deterministic macro and did not mutate report behavior. Replacement-edge notes remain diagnostic-only and do not grant lane-scoring, fundability, recommendation, execution, or portfolio-mutation authority.**

## Latest production and report-surface evidence

```text
workflow: Send weekly ETF Pro report
github_actions_run: 27306857013
workflow_title: Retry ETF delivery after hiding replacement-edge marker
workflow_status: completed
workflow_conclusion: success
artifact_commit: e2891ca
requested_close_date: 2026-06-10
run_id: 20260610_211606
report_token: 260610
english_report_path: output/weekly_analysis_pro_260610_02.md
dutch_report_path: output/weekly_analysis_pro_nl_260610_02.md
english_pdf_path: output/weekly_analysis_pro_260610_02.pdf
dutch_pdf_path: output/weekly_analysis_pro_nl_260610_02.pdf
english_delivery_html: output/weekly_analysis_pro_260610_02_delivery.html
dutch_delivery_html: output/weekly_analysis_pro_nl_260610_02_delivery.html
runtime_state_path: output/runtime/etf_report_state_20260610_20260610_211606.json
executed_runtime_state_path: output/runtime/etf_report_state_20260610_20260610_211606_already_executed.json
pricing_audit_path: output/pricing/price_audit_2026-06-10_20260610_211606.json
run_manifest_path: output/run_manifests/weekly_etf_run_manifest_2026-06-10_20260610_211606.json
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-10_20260610_211606.json
pricing_lineage_status: passed
pricing_coverage_count_pct: 100.0
fresh_holdings_count: 9
carried_forward_holdings_count: 0
total_portfolio_value_eur: 103994.26
cash_eur: 1936.52
delivery_status: smtp_sendmail_returned_no_exception
```

Delivery manifest recorded `smtp_sendmail_returned_no_exception` after `send_report.py` returned from `smtplib.sendmail` without raising. This is delivery-layer evidence, not an end-recipient inbox receipt.

Current holdings validated in the run manifest:

```text
CIBR
DFEN
GSG
IEFA
PAVE
SMH
SPY
URNM
XLU
```

## Recent completed fixes in the current baseline

### GLD stale surface cleanup

```text
status: completed / current output clean
relevant files:
- runtime/render_etf_report_nl_from_state.py
- runtime/fix_report_output_contract.py
- tests/test_post_execution_replacement_note.py
```

Native Dutch and post-execution surfaces now derive hedge/replacement wording from active state instead of hardcoded GLD wording. GLD is not treated as a current holding in the latest production baseline.

### Valuation-history stale comment cleanup

```text
status: completed / current output clean
relevant files:
- runtime/fix_report_output_contract.py
- tests/test_valuation_history_comment_scrub.py
```

Section 7 valuation comments are sanitized before final English/Dutch output so stale comments such as GLD/PPA carried-forward wording do not surface in the current client reports.

### Replacement-edge diagnostic notes marker cleanup

```text
status: completed / verified successful in current 260610_02 baseline
```

The visible marker `ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED` is absent from the current `260610_02` Markdown / clean Markdown / HTML / PDF surfaces.

The diagnostic-only authority disclaimer remains present.

Older historical artifacts such as `260609_06`, `260609_07`, and early `260610` outputs may still contain prior client-surface issues. They are historical artifacts and should not be treated as current delivery output. Do not bulk-edit or rewrite them unless explicitly authorized.

## Macro roadmap implementation status

### Integrated macro surface

The production report is integrated with the macro policy pack through a client-safe report surface:

```text
runtime.build_macro_policy_pack
  -> output/macro/latest.json
  -> runtime.macro_report_surface
  -> runtime.polish_runtime_reports / native report rendering
  -> English/Dutch report sections
```

Current report content may include client-safe macro-derived content such as:

```text
Primary regime
Secondary cross-current
Regime Dashboard
Fed/ECB stance
policy/geopolitical status
policy catalysts
macro filters in the Structural Opportunity Radar
```

Relevant validation evidence from the latest marker-cleanup baseline:

```text
ETF_MACRO_REPORT_SURFACE_OK
ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
```

### Deterministic macro read boundary

The raw deterministic macro read is not the official production regime source.

Current state:

```text
macro report surface: integrated as client-safe only
deterministic macro read as raw/shadow object: not client-facing
deterministic macro read as official decision/regime source: not promoted
```

Raw deterministic fields such as the following must not appear in client reports:

```text
deterministic_regime_shadow
macro_axes
macro_axis_scores
macro_evidence
```

Do not infer deterministic macro promotion from green validators, old-vs-new review readiness, client-safe macro surface presence, macro policy pack existence, prior pilot output, or prior review artifacts.

### Completed or established deterministic macro packages

```text
WP1 — deterministic macro narrative shadow candidate: completed / not promoted
WP2 — macro narrative compliance and bilingual parity gate: completed / not promoted
WP3 — macro promotion decision contract: completed / merged
WP7 — deterministic macro regime client-surface pilot: completed / non-authoritative / not promoted
WP8 — old-vs-new macro review evidence: completed / ready_for_narrative_promotion_review / not promoted
WP9 — controlled promotion artifact: completed / status=not_promoted
WP10 — explicit promotion decision artifact: completed / status=not_promoted
WP13 — deterministic macro read promotion review: completed / review-only / not promoted
```

WP13 artifact:

```text
control/DETERMINISTIC_MACRO_READ_PROMOTION_REVIEW.md
```

WP13 answers the required six promotion-review questions but does not grant narrative authority and does not mutate production report behavior.

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

Future deterministic macro work must be framed as one of:

```text
1. Shadow-quality improvement only
2. Promotion-decision preparation only
3. Explicit control-layer promotion decision
4. Separate production report integration after promotion
```

Do not combine those into one implicit change.

## Replacement-edge authority boundary

Replacement-edge notes are visible as diagnostics only.

They do not grant:

```text
portfolio_action_authority=false
fundability_authority=false
lane_scoring_authority=false
funding_authority=false
production_recommendation_authority=false
execution_authority=false
portfolio_mutation=false
```

Replacement-edge diagnostics must not be promoted into:

```text
ranking
lane scoring
fundability
recommendation
target weights
trade intents
execution
portfolio mutation
```

## Four-layer operating status

### 1. Decision framework

- Deterministic macro remains review/control evidence only and is not promoted.
- WP10 explicitly records `status=not_promoted`.
- WP13 records promotion-review criteria only.
- Green compliance, review readiness, macro policy pack existence, client-safe macro surface presence, prior pilot output, or prior review artifact does not equal production deterministic macro promotion.
- WP5 replacement-edge scoring remains diagnostic-only.
- Replacement-edge notes are client-visible diagnostics only and do not create allocation, scoring, fundability, recommendation, execution, or mutation authority.

### 2. Input/state contract

Authoritative production inputs remain runtime/pricing/manifest/state artifacts:

```text
output/etf_portfolio_state.json
output/etf_valuation_history.csv
output/etf_trade_ledger.csv
output/runtime/etf_report_state_20260610_20260610_211606.json
output/runtime/etf_report_state_20260610_20260610_211606_already_executed.json
output/pricing/price_audit_2026-06-10_20260610_211606.json
output/run_manifests/weekly_etf_run_manifest_2026-06-10_20260610_211606.json
output/delivery/weekly_etf_delivery_manifest_2026-06-10_20260610_211606.json
output/macro/latest.json
```

Macro promotion-preparation, review, and decision artifacts remain control/review artifacts only:

```text
output/macro/shadow_narrative/macro_regime_shadow_narrative_<run_id>.json
output/macro/pilot/macro_regime_client_surface_pilot_<run_id>.json
output/macro/review/macro_old_vs_new_review_<run_id>.json
output/macro/promotion/macro_regime_promotion_decision_<run_id>.json
control/DETERMINISTIC_MACRO_READ_PROMOTION_REVIEW.md
control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
```

### 3. Output contract

The report pipeline must continue to protect:

```text
pricing lineage
runtime-state authority
bilingual English/Dutch output
Dutch terminology contract
ticker linkification
client-surface scrub
macro/thesis leakage guard
replacement-edge diagnostic-only boundary
delivery HTML contract
delivery manifest summary
run manifest summary
```

The current `260610_02` client output is the latest report set. Old historical outputs are not current production truth.

### 4. Operational runbook

Current production delivery evidence is the `20260610_211606` run-manifest and delivery-manifest pair. Delivery evidence remains delivery-layer evidence only unless a real end-recipient inbox receipt exists.

WP13 created a control-layer review artifact only. It did not change report generation logic, scoring, portfolio state, macro authority, replacement-edge authority, historical output artifacts, delivery behavior, or execution behavior.

## Immediate priorities

### Priority A — preserve pricing-lineage and delivery-evidence discipline

Do not weaken pricing lineage, manifest, official portfolio-state, or delivery-evidence boundaries. Delivery evidence remains SMTP-send/report-generation evidence unless a real receipt exists.

### Priority B — preserve deterministic macro `not_promoted` boundary

The client-safe macro report surface is integrated, but deterministic macro read remains outside official production regime authority. Any future production deterministic macro integration requires a future explicit control-layer promotion decision and a separate report-integration work package.

### Priority C — proceed to the next roadmap package

Next roadmap work should proceed as:

```text
WP14 — Deterministic macro read shadow replay evidence
```

After WP14, the likely next package remains:

```text
WP15 — Historical artifact cleanup policy
```
