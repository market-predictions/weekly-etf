# ETF Review OS — Current State

## Snapshot date
2026-06-12

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**ETF has a latest successful runtime-driven bilingual production baseline for run `20260610_211606` / report set `260610_02`, with pricing-lineage proof, 100.0% fresh holdings coverage, run-manifest evidence, delivery-manifest evidence, and marker-free replacement-edge diagnostic notes. The prior workflow run #216 / run `20260605_081216` remains historical evidence only and is no longer the current production baseline. The client-safe macro report surface is integrated through the macro policy pack, but the raw deterministic macro read remains non-client-facing and is not promoted as the official production regime source. WP13, WP14, and WP15 are review/policy packages only; they did not promote deterministic macro, mutate report behavior, or rewrite historical outputs. Historical output artifacts are immutable by default under WP15. Replacement-edge notes remain diagnostic-only and do not grant lane-scoring, fundability, recommendation, execution, or portfolio-mutation authority.**

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

## Current output and historical-artifact status

The current report set is:

```text
260610_02
```

The visible marker `ETF_REPLACEMENT_EDGE_DIAGNOSTIC_NOTES_EMBEDDED` is absent from the current `260610_02` Markdown / clean Markdown / HTML / PDF surfaces.

Older historical artifacts such as `260609_06`, `260609_07`, and early `260610` outputs may still contain prior client-surface issues. They are historical artifacts and should not be treated as current delivery output.

WP15 policy artifact:

```text
control/HISTORICAL_ARTIFACT_CLEANUP_POLICY.md
```

WP15 policy status:

```text
policy_status=cleanup_policy_defined_no_artifact_mutation
historical_output_artifacts_are_immutable_by_default=true
current_baseline_scope=manifest_linked_latest_report_set
historical_output_mutation=false
production_report_behavior_changed=false
scoring_changed=false
fundability_changed=false
execution_changed=false
delivery_changed=false
portfolio_state_changed=false
macro_authority_changed=false
```

Operational rule:

```text
Repo-wide grep can identify historical residue, but current production truth must be determined from CURRENT_STATE plus the latest manifest-linked report/runtime/pricing/delivery artifacts.
```

## Macro roadmap implementation status

The production report is integrated with the macro policy pack through a client-safe report surface:

```text
runtime.build_macro_policy_pack
  -> output/macro/latest.json
  -> runtime.macro_report_surface
  -> runtime.polish_runtime_reports / native report rendering
  -> English/Dutch report sections
```

Current deterministic macro state:

```text
macro report surface: integrated as client-safe only
deterministic macro read as raw/shadow object: not client-facing
deterministic macro read as official decision/regime source: not promoted
```

Do not infer deterministic macro promotion from green validators, old-vs-new review readiness, client-safe macro surface presence, macro policy pack existence, prior pilot output, prior review artifacts, WP13 review checklist, WP14 replay evidence, or WP15 historical-artifact policy.

Completed or established deterministic macro packages:

```text
WP1 — deterministic macro narrative shadow candidate: completed / not promoted
WP2 — macro narrative compliance and bilingual parity gate: completed / not promoted
WP3 — macro promotion decision contract: completed / merged
WP7 — deterministic macro regime client-surface pilot: completed / non-authoritative / not promoted
WP8 — old-vs-new macro review evidence: completed / ready_for_narrative_promotion_review / not promoted
WP9 — controlled promotion artifact: completed / status=not_promoted
WP10 — explicit promotion decision artifact: completed / status=not_promoted
WP13 — deterministic macro read promotion review: completed / review-only / not promoted
WP14 — deterministic macro read shadow replay evidence: completed / replay-only / not promoted
WP15 — historical artifact cleanup policy: completed / policy-only / no artifact mutation
```

Review and policy artifacts:

```text
control/DETERMINISTIC_MACRO_READ_PROMOTION_REVIEW.md
output/macro/replay/deterministic_macro_shadow_replay_20260612_000000.json
control/HISTORICAL_ARTIFACT_CLEANUP_POLICY.md
```

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

Replacement-edge diagnostics must not be promoted into ranking, lane scoring, fundability, recommendation, target weights, trade intents, execution, or portfolio mutation.

## Four-layer operating status

### 1. Decision framework

- Deterministic macro remains review/control evidence only and is not promoted.
- WP10 explicitly records `status=not_promoted`.
- WP13 records promotion-review criteria only.
- WP14 records shadow replay evidence only.
- WP15 records historical-artifact cleanup policy only.
- Historical output artifacts are immutable by default unless a future explicit cleanup/archive work package authorizes a scoped change.

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

Review, replay, policy, and promotion artifacts remain control/review artifacts only unless explicitly promoted through a later contract.

### 3. Output contract

The report pipeline must continue to protect pricing lineage, runtime-state authority, bilingual output, Dutch terminology, ticker linkification, client-surface scrub, macro/thesis leakage guard, replacement-edge diagnostic-only boundary, delivery HTML contract, delivery manifest summary, and run manifest summary.

The current `260610_02` client output is the latest report set. Old historical outputs are not current production truth.

### 4. Operational runbook

Current production delivery evidence is the `20260610_211606` run-manifest and delivery-manifest pair. Delivery evidence remains delivery-layer evidence only unless a real end-recipient inbox receipt exists.

WP15 created a policy artifact only. It did not rewrite historical outputs, change report generation logic, scoring, portfolio state, macro authority, replacement-edge authority, delivery behavior, or execution behavior.

## Immediate priorities

### Priority A — preserve pricing-lineage and delivery-evidence discipline

Do not weaken pricing lineage, manifest, official portfolio-state, or delivery-evidence boundaries.

### Priority B — preserve deterministic macro `not_promoted` boundary

Any future production deterministic macro integration requires a future explicit control-layer promotion decision and a separate report-integration work package.

### Priority C — preserve historical-output immutability by default

Do not rewrite or delete historical generated outputs unless a future explicit cleanup/archive work package defines exact scope, traceability, rollback, and current-baseline verification.

### Priority D — next action

There is no automatic cleanup or promotion task after WP15. The next step is a coordinator/user decision:

```text
Option 1 — stop and observe the clean current production baseline
Option 2 — prepare an explicit deterministic macro promotion decision package
Option 3 — define a scoped historical archive execution package, if grep noise becomes operationally blocking
```
