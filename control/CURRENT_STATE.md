# ETF Review OS — Current State

Date: 2026-07-17
Repository: `market-predictions/weekly-etf`

## Official portfolio authority

```text
portfolio_state: output/etf_portfolio_state.json
trade_ledger: output/etf_trade_ledger.csv
whole_share_status: compliant
cash_eur: 2534.36
invested_market_value_eur: 104583.58
nav_eur: 107117.94
active_position_count: 9
maximum_active_positions: 8
position_count_status: close_first
```

Current whole-share positions:

```text
CIBR 253
GSG 374
IEFA 312
PAVE 107
SMH 59
URNM 48
XBI 40
XLU 14
XLV 37
```

The latest official rotation reduced `XLU` by 134 shares and added 107 shares of `PAVE`. A 14-share XLU residual remains. No second execution occurred during delivery recovery or position-count reconciliation.

## Latest successful production run

```text
requested_close_date: 2026-07-16
run_id: 20260717_154351
report_token: 260716
pricing_lineage_status: passed
workflow_status: workflow_success
workflow_conclusion: success
report_authority_source: portfolio_state_post_execution
production_rotation: XLU -> PAVE
```

Authority and evidence files:

```text
output/pricing/price_audit_2026-07-16_20260717_154351.json
output/runtime/etf_report_state_20260716_20260717_154351_executed.json
output/runtime/etf_model_execution_20260716_20260717_154351.json
output/run_manifests/weekly_etf_run_manifest_2026-07-16_20260717_154351.json
output/delivery/weekly_etf_delivery_manifest_2026-07-16_20260717_154351.json
control/evidence/WEEKLY_ETF_DELIVERY_RECOVERY_EVIDENCE_20260717.json
```

## Latest delivered client package

```text
English Markdown: output/weekly_analysis_pro_260716_02.md
English PDF: output/weekly_analysis_pro_260716_02.pdf
English HTML: output/weekly_analysis_pro_260716_02_delivery.html
Dutch Markdown: output/weekly_analysis_pro_nl_260716_02.md
Dutch PDF: output/weekly_analysis_pro_nl_260716_02.pdf
Dutch HTML: output/weekly_analysis_pro_nl_260716_02_delivery.html
delivery_status: smtp_sendmail_returned_no_exception
inbox_receipt: confirmed_both_languages
```

Each message contains the `_02` PDF, clean Markdown, full delivery HTML and equity-curve PNG.

## Production surface status

```text
cockpit_feature: MRKT_RPRTS_COCKPIT_FRONT_PAGE=enabled
English cockpit front pages: 1
Dutch cockpit front pages: 1
classic report body: preserved
client_language_gate: passed
macro_thesis_leakage_gate: passed
pdf_visual_gate: passed
```

Stable production rules:

1. Future production runs add one cockpit front page per language.
2. The full classic report remains the evidence layer behind that page.
3. Invalid feature values or front-page render failure fail closed to the classic output.
4. Internal implementation terms remain blocked from client surfaces.
5. Historical reports remain immutable by default.
6. Delivery success requires a real manifest and independent inbox receipt.

## Position-count constraint status

```text
package: WP_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION
implementation_pull_request: #91
implementation_merge: 0bcb6af7e243775d876b59719ce9898fa97c690f
closeout_pull_request: #92
status: closed_merged_validated_no_send
claim_status: closed_released
decision: every unique ticker with shares > 0 counts
zero_share_positions_count: false
generic_residual_exception: false
current_active_positions: 9
maximum_active_positions: 8
current_status: close_first
```

Stable position-count rules:

1. Every unique ticker with positive whole-share quantity counts as one active position.
2. Duplicate active ticker rows are invalid.
3. A no-trade run may preserve the current nine-position state while reporting `close_first`.
4. Any proposed trade while above eight must reduce the active count and may not introduce a new ticker.
5. At exactly eight positions, a new ticker requires another ticker to reach zero shares in the same projected whole-share execution.
6. A partial source reduction that leaves positive shares does not free a slot.
7. Transition validation uses projected whole-share quantities and runs before guarded mutation.
8. Current matching EN/NL report surfaces disclose the actual count; non-current historical reports remain unchanged.

Implementation:

```text
runtime/position_count_contract.py
runtime/position_count_report_surface.py
tools/validate_etf_persisted_valuation_state.py
tools/validate_etf_client_surface_clean.py
tools/validate_etf_position_count_contract.py
tests/test_etf_position_count_contract.py
.github/workflows/validate-etf-position-count-contract.yml
```

Final validation:

```text
focused_tests: 13 passed
artifact_id: 8420903168
artifact_digest: sha256:cf98f8d4b4d172bc4f463598a557e8490fd2f188bbd5ae3f0c34347ee1688b5b
position_count_run: 29618185729 success
report_surface_run: 29618185736 success
current_runtime_cockpit_run: 29618185701 success
wp08_exact_current_run: 29618185711 success
wp11_exact_current_run: 29618185709 success
closed_recovery_run: 29618185751 success
fresh_send_diagnostic_run: 29618185706 success
governance_append_run: 29618612112 success
protected_authority_hashes: identical
historical_report_hashes: identical
portfolio_execution: false
email_sent: false
```

Persistent records:

```text
control/evidence/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_EVIDENCE_20260717.json
control/decisions/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_DECISION_20260717.md
control/handovers/HANDOVER_PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_20260717.md
control/DECISION_LOG.md
control/ETF_SESSION_CHANGELOG.md
```

This package does not choose which holding should be closed and does not authorize a position change.

## Immediate next action

```text
WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW
```

The next package should be separately claimed and should first produce a no-mutation review using fresh pricing, current scores, relative strength, portfolio-role evidence, liquidity and funding logic. It must identify a justified count-reducing path from nine positions to no more than eight and must not assume that the smallest holding is automatically the correct source.

Any future portfolio change or report delivery requires separate explicit authorization and the normal whole-share, position-count, NAV, manifest and inbox-receipt controls.
