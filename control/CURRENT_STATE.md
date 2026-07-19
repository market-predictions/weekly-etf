# ETF Review OS — Current State

Date: 2026-07-19
Repository: `market-predictions/weekly-etf`

## Official portfolio authority

```text
portfolio_state: output/etf_portfolio_state.json
trade_ledger: output/etf_trade_ledger.csv
whole_share_status: compliant
pricing_close_date: 2026-07-17
cash_eur: 2534.36
invested_market_value_eur: 104109.85
nav_eur: 106644.21
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

The latest official rotation reduced `XLU` by 134 shares and added 107 shares of `PAVE`. A 14-share XLU residual remains. The fresh 2026-07-17 report and its fix-verification delivery did not repeat portfolio execution or change official share quantities or the trade ledger.

## Latest successful production run

```text
requested_close_date: 2026-07-17
run_id: 20260719_002755
report_token: 260717
pricing_lineage_status: passed
workflow_status: workflow_success
workflow_conclusion: success
report_authority_source: runtime_state
portfolio_execution_authorized: false
broker_execution_authorized: false
```

Authority and evidence files:

```text
output/pricing/price_audit_2026-07-17_20260719_002755.json
output/runtime/etf_report_state_20260717_20260719_002755.json
output/run_manifests/weekly_etf_run_manifest_2026-07-17_20260719_002755.json
output/delivery/weekly_etf_delivery_manifest_2026-07-17_20260719_002755.json
control/evidence/WEEKLY_ETF_FIX_VERIFICATION_DELIVERY_EVIDENCE_20260719.json
```

## Latest delivered client package

```text
English Markdown: output/weekly_analysis_pro_260717_04.md
English PDF: output/weekly_analysis_pro_260717_04.pdf
English HTML: output/weekly_analysis_pro_260717_04_delivery.html
Dutch Markdown: output/weekly_analysis_pro_nl_260717_04.md
Dutch PDF: output/weekly_analysis_pro_nl_260717_04.pdf
Dutch HTML: output/weekly_analysis_pro_nl_260717_04_delivery.html
delivery_status: smtp_sendmail_returned_no_exception
inbox_receipt: confirmed_both_languages
received_at_europe_amsterdam: 2026-07-19 02:55
attachments_per_language: 4
```

Each message contains the PDF, clean Markdown, full delivery HTML and equity-curve PNG.

## Fresh delivery recovery closeout

```text
package: WP_FRESH_ETF_DELIVERY_RECOVERY
status: closed_delivered_inbox_confirmed
claim_status: closed_released
source_run_id: 20260718_140601
client_language_fix_pr: 105
client_language_fix_merge: bfba7c2e038eaba9a071008fc33fe09832dd4f5c
retrigger_pr: 106
retrigger_merge: ba558abf9c79ecd2066ebe8fc57db41a9c9c44ee
delivery_evidence_commit: a1e5dad7a5a1957ddbe9f1bc750a9c33c45384ea
language_validation_run: 29659315302 success
exact_current_diagnostic_run: 29659315297 success
```

Root cause:

- GitHub Actions credits were not exhausted or blocking the run;
- the hosted runner was allocated and executed the workflow;
- the recovery stopped at `validate_etf_client_surface_clean.py`;
- uncovered `release score` and minimum-trade-size override labels remained in the English report and delivery HTML;
- the shared language normalizer and regression tests were expanded before the transport-only recovery was retriggered.

Stable delivery rules:

1. Diagnose red Actions runs from the first failing step; do not infer a credit problem from missing email.
2. A transport-only recovery may proceed only when no delivery manifest and no inbox receipt exist.
3. Recovery may not change official shares or the trade ledger.
4. Delivery success requires a completed run manifest, bilingual delivery manifest and independent inbox receipts.
5. A delivered source run is closed against further automatic resends.

## Production surface status

```text
cockpit_feature: MRKT_RPRTS_COCKPIT_FRONT_PAGE=enabled
email_layout: inline_styles_and_presentation_tables
English cockpit front pages: 1
Dutch cockpit front pages: 1
classic report body: preserved
client_language_gate: passed
macro_thesis_leakage_gate: passed
pdf_visual_gate: passed
```

The email HTML no longer depends on head-only CSS for essential cockpit presentation. The PDF/browser route retains the class-based premium cockpit, print rules and SVG/equity-curve rendering.

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
current_active_positions: 9
maximum_active_positions: 8
current_status: close_first
```

Stable position-count rules:

1. Every unique ticker with positive whole-share quantity counts as one active position.
2. Duplicate active ticker rows are invalid.
3. A no-change report may preserve the current nine-position state while disclosing `close_first`.
4. Any proposed change while above eight must reduce the active count and cannot introduce a new ticker.
5. A partial reduction that leaves positive shares does not free a slot.

## Portfolio close-first execution review

```text
package: WP_PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW
implementation_pull_request: #95
implementation_merge: 2895bbb5940ead8526ab4c10d0ce3687f8aca423
status: closed_merged_validated_no_change
selected_review_source: URNM
reviewed_quantity: 48 whole shares
selected_destination: cash
projected_active_positions: 8
portfolio_change_applied: false
```

The review ranked URNM first under the common rubric and XLU second. This is review evidence only. The official portfolio remains unchanged until a separately authorized execution package refreshes the evidence and passes all transition gates.

## Cockpit email HTML correction

```text
package: WP_COCKPIT_EMAIL_HTML_INLINE_STYLE_FIX
implementation_pull_request: #98
implementation_merge: 467726f2449b3a409008075812c761c4dc48c3f3
closeout_pull_request: #99
closeout_merge: 720c2e47e51ec59329fdb1eac4d5d69edd22e176
status: closed_merged_validated
email_layout: inline_styles_and_presentation_tables
style_strip_degradation_test: passed_both_languages
PDF_surface: preserved
```

The receiving-mail-client body continues to show the styled cockpit structure in both languages.

## Cockpit trade-weight lineage correction

```text
package: WP_COCKPIT_TRADE_WEIGHT_LINEAGE_FIX
implementation_pull_request: #109
implementation_merge: 85d82930e40d37c145727d14468dc8914e041e00
compatibility_closeout_pull_request: #110
compatibility_closeout_merge: 612ddea1cf43df4f717dff2b20d4fc509632f58a
status: closed_merged_validated
claim_status: closed_released
material_identical_display_gate: passed
```

The state contract preserves or reconstructs pre-trade shares, values and weights, prefers the official ledger when available, and rejects material trades whose one-decimal before/after weights are identical. Current NAV remains based on current market values.

## Fix-verification delivery closeout

```text
package: WP_WEEKLY_ETF_FIX_VERIFICATION_DELIVERY
implementation_pull_request: #111
implementation_merge: d3d4960b3611fe54f5db6d5ef2d3608fc2f6ac34
delivery_authorization_commit: 58f16df50309e30b5d5f3c3b5e2f4b37200c50ce
delivery_evidence_commit: 8ae50d7ccfe931dd9be5a9008b41570d32f4fdff
no_send_recovery_validation_run: 29667585209 success
full_render_boundary_run: 29667585181 success
status: closed_delivered_inbox_confirmed
claim_status: closed_released
```

The actual received email bodies show:

```text
English: PAVE 0.0% → 4.9%; XLU 5.5% → 0.5%.
Dutch:   PAVE 0,0% → 4,9%; XLU 5,5% → 0,5%.
```

The fix is therefore verified in the receiving mail client and the attached package, not only in unit tests or preview rendering. The source run is closed against automatic resend.

## Immediate next action

No report generation, resend or delivery recovery is pending.

The next portfolio package remains separately authorized only:

```text
WP_PORTFOLIO_CLOSE_FIRST_EXECUTION
```

It must refresh URNM and EUR/USD pricing, rerun the full nine-holding source-selection rubric, stop if URNM is no longer selected, use whole shares, open no new ticker and reconcile NAV and position count before official writes.
