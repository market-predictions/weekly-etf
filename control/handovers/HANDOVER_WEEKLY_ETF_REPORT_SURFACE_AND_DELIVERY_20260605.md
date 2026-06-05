# Handover — Weekly ETF Report Surface, Delivery Evidence, and Macro/Thesis Guardrails

Date: 2026-06-05
Repository: `market-predictions/weekly-etf`

## Purpose

This handover lets a fresh ChatGPT session continue the Weekly ETF Review OS work without relying on prior chat memory.

The current workstream focused on production report-surface cleanup, delivery evidence, Dutch/English parity, stale exited-holding cleanup, and preserving macro/thesis authority boundaries.

## Fresh-chat start prompt

Continue in `market-predictions/weekly-etf`.

Start by reading from GitHub, in this order:

```text
control/SYSTEM_INDEX.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/handovers/HANDOVER_WEEKLY_ETF_REPORT_SURFACE_AND_DELIVERY_20260605.md
```

Then read only the minimum relevant execution files for the specific task.

If continuing report-surface/debug work, likely relevant files are:

```text
.github/workflows/send-weekly-report.yml
send_report.py
send_report_runtime_html.py
runtime/render_etf_report_from_state.py
runtime/render_etf_report_nl_from_state.py
runtime/add_etf_position_performance_section.py
runtime/replacement_duel_v2.py
runtime/scrub_etf_client_surface.py
runtime/macro_report_pre_send_guard.py
tools/validate_etf_report_content_contract.py
tools/validate_etf_position_performance_section.py
tools/validate_etf_dutch_language_quality.py
tools/validate_etf_dutch_client_surface_clean.py
tools/validate_nl_terminology_contract.py
```

## Current production status

Latest repo-visible successful production run:

```text
workflow: Send weekly ETF Pro report
run_id: 20260605_000758
requested_close_date: 2026-06-04
report_token: 260604
workflow_status: workflow_success
workflow_conclusion: success
pricing_lineage_status: passed
pricing_lineage_validated_at_utc: 2026-06-05T00:15:33.912108+00:00
english_report_path: output/weekly_analysis_pro_260604_05.md
dutch_report_path: output/weekly_analysis_pro_nl_260604_05.md
runtime_state_path: output/runtime/etf_report_state_20260604_20260605_000758.json
pricing_audit_path: output/pricing/price_audit_2026-06-04_20260605_000758.json
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-04_20260605_000758.json
total_portfolio_value_eur: 111105.47
```

Pricing summary from latest run:

```text
holdings_count: 9
fresh_holdings_count: 9
carried_forward_holdings_count: 0
coverage_count_pct: 100.0
invested_weight_coverage_pct: 98.26
unresolved_tickers: []
```

Holdings validated in latest pricing-lineage evidence:

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

GLD is not an active holding in the latest manifest validation set.

Delivery evidence:

```text
artifact_type: weekly_etf_delivery_manifest_summary
delivery_status: smtp_sendmail_returned_no_exception
language_count: 2
recipient_data_policy: redacted_hash_only
english_pdf: weekly_analysis_pro_260604_05.pdf
dutch_pdf: weekly_analysis_pro_nl_260604_05.pdf
```

Important delivery boundary:

```text
This proves SMTP send returned without raising and that per-language delivery manifests were written.
It is not an end-recipient inbox receipt.
```

## What was done in this session/workstream

### 1. Delivery manifest evidence closed

Problem:

```text
The workflow could prove report generation and pricing-lineage success, but the final run manifest previously had delivery_manifest_path: null.
```

Implemented:

```text
tools/write_etf_delivery_manifest_summary.py
.github/workflows/send-weekly-report.yml
control/DELIVERY_MANIFEST_STATUS_20260604.md
```

Result:

```text
output/delivery/weekly_etf_delivery_manifest_<requested_close_date>_<run_id>.json
```

is now written after the send step and linked from the final run manifest.

Latest successful manifest proves this path is non-null:

```text
output/delivery/weekly_etf_delivery_manifest_2026-06-04_20260605_000758.json
```

### 2. Dutch terminology alias centralization completed

Problem:

```text
runtime/nl_localization.py duplicated terminology maps that already existed in runtime/nl_terminology.py.
```

Implemented:

```text
runtime/nl_localization.py
tools/validate_nl_terminology_contract.py
.github/workflows/send-weekly-report.yml
control/NL_TERMINOLOGY_CONTRACT_STATUS.md
```

Current rule:

```text
runtime/nl_terminology.py is the central source of truth for Dutch terms, labels, action wording, decision wording, trigger wording, allowed English terms, and forbidden client-surface tokens.
runtime/nl_localization.py keeps backward-compatible names but directly aliases central terminology objects.
```

Workflow evidence:

```text
Validate ETF Dutch terminology #16 passed
commit: 25aac7a823ddf9eaaca3362a33cf07c050b53b9f
```

The production send workflow now runs:

```bash
python tools/validate_nl_terminology_contract.py
```

inside the Dutch quality step.

### 3. Section 7A English/Dutch parity work

Problem:

```text
Section 7A differed between English and Dutch.
English rows could show ticker-only thesis fallback such as CIBR / CIBR, while Dutch could show generic Portefeuilleblootstelling.
```

First fix:

```text
runtime/add_etf_position_performance_section.py
```

made English and Dutch use the same fallback strategy.

Second fix:

```text
runtime/add_etf_position_performance_section.py
```

added semantic thesis fallbacks for holdings whose `original_thesis` is missing.

Examples:

```text
CIBR -> Cybersecurity resilience
DFEN -> Defense innovation / tactical defense beta
GSG -> Commodity-breadth hedge exposure
IEFA -> Non-U.S. developed-market diversification
XLU -> Defensive utilities / rate-sensitive ballast
```

Dutch equivalents were added in the same generator.

Current watch item:

```text
A stricter validator for generic/ticker-only 7A thesis labels was attempted but blocked twice by the GitHub connector safety layer.
The generator fix is committed, but a dedicated regression validator should still be added later if possible.
```

### 4. GLD stale-current-surface cleanup

Problem:

```text
GLD was no longer in the portfolio, but the report still mentioned GLD in active/current-state areas such as replacement duels, watchlist/radar memory, and regime/dashboard-style wording.
```

Implemented across:

```text
runtime/replacement_duel_v2.py
runtime/render_etf_report_from_state.py
runtime/scrub_etf_client_surface.py
tools/validate_etf_report_content_contract.py
```

Current rule:

```text
If GLD is not an active holding, it must not appear as a current active replacement-duel source, current watchlist holding, current action item, or misleading current hedge statement.
```

Allowed:

```text
Explicit historical context may mention a prior gold-sleeve exit only if clearly historical.
```

Not allowed:

```text
GLD -> GSG as current replacement duel
GLD → GSG as current replacement duel
Gold hedge review as current active sleeve
Added as commodity-breadth replacement for part of GLD as current-state wording
```

### 5. Macro pre-send guard false positive fixed

Problem:

A run failed at:

```text
Validate HTML/PDF render before send
```

because `runtime/macro_report_pre_send_guard.py` passed the full report into macro compliance. The orphan-macro-figure rule then flagged a normal Section 7A performance row, for example:

```text
XLU | 5.07% | -1.55% | -5.24% | -5.66%
```

This was not macro narrative. It was portfolio-performance table data.

Fix:

```text
runtime/macro_report_pre_send_guard.py
```

Now:

```text
macro compliance scans only macro-sensitive report sections
full-report leakage scan still scans full report/html
```

This preserves leakage protection while avoiding false positives from ordinary performance tables.

### 6. Macro/thesis status clarified

Current status:

```text
Client-safe macro narrative: embedded in report surface.
Full deterministic/rules-based macro engine: still shadow-only for authority.
Macro/thesis outputs do not drive lane scoring, fundability, portfolio actions, or report recommendations unless explicitly promoted later.
```

The system has green evidence for:

```text
macro-regime shadow validation
macro compliance validation
Stage-1 thesis candidate shadow evidence
Stage-2 thesis promotion discipline contract
```

But those are not production-authority promotions.

## Four-layer summary

### 1. Decision framework

Current production decisions remain driven by:

```text
pricing audit
runtime state
post-execution portfolio state
lane discovery
challenger pricing/fundability
rotation plan / guarded execution
pricing-lineage validator
```

Macro/thesis layers are still shadow/promotion-gated unless the current safe macro surface is already explicitly rendered as client-safe narrative.

### 2. Input/state contract

Authoritative current-state sources:

```text
output/pricing/price_audit_<requested_close_date>_<run_id>.json
output/runtime/etf_report_state_<report_token>_<run_id>.json
output/etf_portfolio_state.json
output/etf_valuation_history.csv
output/etf_trade_ledger.csv
output/lane_reviews/etf_lane_assessment_<report_token>.json
output/market_history/etf_relative_strength.json
output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json
output/delivery/weekly_etf_delivery_manifest_<requested_close_date>_<run_id>.json
```

Latest successful state:

```text
run_id: 20260605_000758
requested_close_date: 2026-06-04
portfolio value EUR: 111105.47
cash EUR: 1936.52
active holdings: CIBR, DFEN, GSG, IEFA, PAVE, SMH, SPY, URNM, XLU
```

### 3. Output contract

The reports must preserve:

```text
English canonical report
Dutch native companion report from the same runtime state
Section 7 equity curve equals Section 15 total NAV
Section 7A uses semantic thesis labels, not ticker-only/generic fallback labels
GLD is not presented as a current holding/current duel/current hedge sleeve when exited
pricing-basis disclosure derives active holdings dynamically
client surface must not leak internal snake-case/shadow labels
macro pre-send guard must protect macro sections and leakage without misclassifying normal performance rows
```

### 4. Operational runbook

Current production path:

```text
run-queue request
-> pricing pass
-> relative-strength fetch
-> macro policy pack build
-> lane discovery
-> challenger pricing
-> final lane discovery
-> challenger fundability validation
-> rotation plan
-> runtime report state
-> EN/NL markdown rendering
-> Section 7A position-performance insertion
-> pricing-basis disclosure
-> polish/localization/scrub/linkify
-> report content/Dutch/macro leakage validators
-> persisted valuation state
-> guarded model execution
-> delivery HTML/PDF validation
-> macro report pre-send guard
-> pricing-lineage pre-send gate
-> email/PDF delivery step
-> delivery manifest summary
-> final run manifest
-> commit output artifacts
```

## Open items / next actions

### Priority 1 — verify final visual report quality after latest successful run

The user confirmed the latest run was successful. Repo-visible manifest confirms success for:

```text
output/weekly_analysis_pro_260604_05.md
output/weekly_analysis_pro_nl_260604_05.md
output/weekly_analysis_pro_260604_05.pdf
output/weekly_analysis_pro_nl_260604_05.pdf
```

Next fresh chat should visually inspect or ask the user to inspect screenshots/PDFs for:

```text
Section 7A semantic thesis labels
EN/NL 7A parity
absence of stale current GLD wording
Regime Dashboard wording
replacement-duel table no longer showing GLD as current source
```

### Priority 2 — add stricter Section 7A validator

A desired validator should fail if Section 7A includes ticker-only or generic thesis rows for current holdings.

Target file:

```text
tools/validate_etf_position_performance_section.py
```

Desired checks:

```text
CIBR row contains Cybersecurity resilience
DFEN row contains Defense innovation / tactical defense beta
GSG row contains Commodity-breadth hedge exposure
IEFA row contains Non-U.S. developed-market diversification
XLU row contains Defensive utilities / rate-sensitive ballast
No `Rotation destination | Rotation destination` thesis cell
No `Rotation destination | CIBR | CIBR` style row
```

The previous attempt was blocked by connector safety twice. Try a smaller incremental edit or implement via a fixture-based validator if needed.

### Priority 3 — review macro surface source for gold wording

If future reports still show `Gold hedge behavior remains under review...`, inspect and patch:

```text
runtime/build_macro_policy_pack.py
runtime/macro_report_surface.py
runtime/polish_runtime_reports.py
```

Current known source in `runtime/build_macro_policy_pack.py` includes gold/GLD wording in `classify_regime`, `lane_adjustments`, and `portfolio_implications`.

Recommended approach:

```text
Use current portfolio state or active holdings to choose between:
- current commodity-breadth hedge wording when GSG is active and GLD is exited
- historical gold-sleeve wording only when explicitly framed as historical
- GLD-specific wording only when GLD is active
```

### Priority 4 — update main control files if the latest run should become canonical baseline

If the team accepts `20260605_000758` as the current canonical production baseline, update:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

to replace the previous baseline run `20260604_190001` / report `260603` with:

```text
run_id: 20260605_000758
requested_close_date: 2026-06-04
report_token: 260604
english_report_path: output/weekly_analysis_pro_260604_05.md
dutch_report_path: output/weekly_analysis_pro_nl_260604_05.md
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-04_20260605_000758.json
total_portfolio_value_eur: 111105.47
```

### Priority 5 — direct challenger-vs-current-holding scoring

Still a future model enhancement:

```text
map challenger lanes to the current holding they may replace
compute direct 1m and 3m relative strength versus that holding
feed direct replacement edge into lane scoring and replacement-duel notes
```

### Priority 6 — independent price verification

Still optional future enhancement:

```text
upgrade exact unverified rows only when independent provider agreement exists
preserve Yahoo/free-source connectivity evidence boundary
avoid pretending one-provider exact close is independent validation
```

## Authority boundaries to preserve

Do not change without explicit control-layer decision:

```text
macro axes -> no lane scoring authority
macro axis scores -> no fundability authority
deterministic_regime_shadow -> no client-facing decision authority
Stage-1 thesis candidates -> no report/lane/fundability/action authority
Stage-2 promotion chains -> contract-only, not promoted
workflow success -> not the same as inbox receipt
SMTP send evidence -> not the same as inbox receipt
old report text -> historical context, not current price/portfolio truth
```

## Known good latest artifacts

```text
output/run_manifests/latest_weekly_etf_run_manifest_path.txt
output/run_manifests/weekly_etf_run_manifest_2026-06-04_20260605_000758.json
output/delivery/weekly_etf_delivery_manifest_2026-06-04_20260605_000758.json
output/weekly_analysis_pro_260604_05.md
output/weekly_analysis_pro_nl_260604_05.md
output/weekly_analysis_pro_260604_05.pdf
output/weekly_analysis_pro_nl_260604_05.pdf
```

## Suggested first task in fresh chat

Verify the latest committed report content directly:

```text
Read output/weekly_analysis_pro_260604_05.md
Read output/weekly_analysis_pro_nl_260604_05.md
Search both for GLD, Gold hedge, Goud, Rotation destination, Portefeuilleblootstelling, and Section 7A rows.
Confirm whether the user-visible issues are fully resolved.
If resolved, update CURRENT_STATE.md and NEXT_ACTIONS.md to mark this run as canonical.
If not resolved, patch the exact source and rerun.
```
