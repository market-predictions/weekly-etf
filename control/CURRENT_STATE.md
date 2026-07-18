# ETF Review OS — Current State

Date: 2026-07-18
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

The latest official rotation reduced `XLU` by 134 shares and added 107 shares of `PAVE`. A 14-share XLU residual remains. No later review package changed the official portfolio.

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
closeout_pull_request: #93
closeout_merge: 9cfca787620c73e65a4302d2e4dc403a921f5ffb
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
3. A no-change review may preserve the current nine-position state while reporting `close_first`.
4. Any proposed change while above eight must reduce the active count and may not introduce a new ticker.
5. At exactly eight positions, a new ticker requires another ticker to reach zero shares in the same projected whole-share transition.
6. A partial source reduction that leaves positive shares does not free a slot.
7. Transition validation uses projected whole-share quantities before official writes.
8. Current matching EN/NL report surfaces disclose the actual count; non-current historical reports remain unchanged.

## Portfolio close-first execution review

```text
package: WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW
pull_request: #95
implementation_merge: 2895bbb5940ead8526ab4c10d0ce3687f8aca423
closeout_pull_request: #96
closeout_merge: b2d32e327023ea515c1c78ccbc66f69b69afab45
metadata_pull_request: #97
status: closed_merged_validated_no_change
review_evidence_date: 2026-07-17
review_freshness: complete
selected_review_source: URNM
reviewed_quantity: 48 whole shares
selected_destination: cash
estimated_proceeds_eur: 2022.23
projected_cash_eur: 4556.59
projected_active_positions: 8
portfolio_change_applied: false
email_sent: false
```

The review compared all nine holdings under one deterministic rubric. URNM ranked first even after removing position-size and practicality points. Its holding score was 3.70, current lane score 2.96, one-month relative strength versus SPY -15.64 percentage points, three-month relative strength -33.97 percentage points and trend score 0.0.

XLU ranked second. The smallest position was therefore not selected automatically.

Validation:

```text
workflow_run: 29622365939 success
workflow_job: 88019775095
focused_tests: 7 passed
artifact_id: 8422627986
artifact_digest: sha256:9f0b833f6d9dd5bb7b7558afe598c20246e67707fc5cff974e1bfc661479851a
protected_authority_hashes: identical
historical_report_hashes: identical
```

Persistent records:

```text
control/evidence/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EVIDENCE_20260718.json
control/decisions/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_DECISION_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EN_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_NL_20260718.md
control/handovers/HANDOVER_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_20260718.md
```

The official portfolio remains unchanged at nine active positions and retains `close_first` status until a separately approved implementation succeeds.

## Cockpit email HTML rendering status

```text
package: WP_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX
pull_request: #98
cockpit_email_fix_implementation_merge: 467726f2449b3a409008075812c761c4dc48c3f3
cockpit_email_fix_closeout_pull_request: #99
status: closed_on_governance_closeout_merge
root_cause: cockpit presentation depended on a head stylesheet not reliably applied by the mail client
email_layout: inline_styles_and_presentation_tables
email_head_css_required: false
EN_style_strip_test: passed
NL_style_strip_test: passed
PDF_renderer: existing_class_based_surface_preserved
classic_report_body: preserved
protected_authority_hashes: identical
historical_report_mutation: false
email_sent: false
```

Future generated email HTML uses a dedicated table-based cockpit with essential styling inline. The PDF/browser route retains the existing premium class-based cockpit, print rules and SVG sparkline. The historical `260716_02` package remains immutable and was not resent.

Validation:

```text
validated_head: 72841c3bbedfea19122269f2f7c78168676955cb
email_inline_run: 29640677887 success
wp10_run: 29640677890 success
current_runtime_run: 29640677892 success
wp08_run: 29640677898 success
wp11_run: 29640677882 success
artifact_id: 8428508030
artifact_digest: sha256:df5c3daae4e82b386bdc868aaeb53d8be00cdeb4da1a6f87decd9b62037e8a34
```

## Immediate next action

No official portfolio change is authorized by this review package.

A separate explicit approval may create and claim:

```text
WP_PORTFOLIO_CLOSE_FIRST_EXECUTION
```

That package must refresh URNM and EUR/USD pricing, rerun the source-selection rubric, use whole shares, open no new ticker, and complete position-count and NAV reconciliation before official writes. If the current evidence no longer supports URNM, it must stop without changes.

Report generation and delivery require separate approval and the normal manifest and inbox-receipt controls.
