# Handover — Report Freshness and Standalone HTML Equity

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Work package: `WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH`
PR: #70

## Session outcome

The post-execution `_03` report was audited beyond the original `Wat veranderde` complaint. The package repairs stale macro-change wording, dated-event leakage, current-holding contradictions and the missing standalone HTML equity graph.

## Stable authority rules

1. `What changed / Wat veranderde` is a delta surface.
2. An unchanged regime must be labelled explicitly as no material change before continuity context is shown.
3. Current runtime positions and weights override static editorial memory.
4. Dated policy events may use relative-week wording only when the event falls inside the report-week window.
5. A non-held ETF may appear as a challenger, but not as the current holding.
6. The MIME email body uses `cid:equitycurve`.
7. The standalone delivery HTML embeds the equity PNG as a data URI.
8. The equity image source is restored only after client sanitization; other links are not bypassed.

## Implemented surface corrections

- AI/semiconductor continuity no longer masquerades as a new change.
- The gold continuity sentence was removed from `What changed`.
- The 11 June ECB event is not described as occurring in the 14 July report week.
- IEFA's 24.05% current allocation replaces stale absent/limited/watchlist/zero wording.
- DFEN is the current defense implementation; PPA remains an alternative candidate.
- specified Dutch mixed-language fragments are removed.
- standalone EN/NL HTML displays the equity graph.

## Preview evidence

```text
output/weekly_analysis_pro_260714_04.md
output/weekly_analysis_pro_260714_04_delivery.html
output/weekly_analysis_pro_260714_04.pdf
output/weekly_analysis_pro_nl_260714_04.md
output/weekly_analysis_pro_nl_260714_04_delivery.html
output/weekly_analysis_pro_nl_260714_04.pdf
output/validation/etf_report_freshness_260714_04.json
```

## Validation

```text
workflow: Validate ETF report freshness and HTML equity
run_id: 29460852590
conclusion: success
```

The validation artifact proves:

```text
email_sent=false
model_execution_replayed=false
official_state_mutated=false
official_trade_ledger_mutated=false
standalone_html_uses_embedded_data_uri=true
mime_email_html_keeps_cid_reference=true
```

## Immediate next action

1. Confirm the final governance-head validation is green.
2. Promote PR #70 from draft.
3. Merge using the exact validated head.
4. Update `control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md` to record the package as closed.
5. Do not email `_04` unless separately authorized.

## Safety boundary

The `_04` package is validated preview/review evidence. It is not a delivery receipt, did not rerun the portfolio model and did not mutate official state or the trade ledger.
