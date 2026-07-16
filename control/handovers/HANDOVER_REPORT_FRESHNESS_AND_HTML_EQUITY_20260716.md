# Handover — Report Freshness and Standalone HTML Equity

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Work package: `WP_REPORT_FRESHNESS_AND_HTML_EQUITY_GRAPH`
PR: #70
Status: closed

## Session outcome

The report was audited beyond the original `Wat veranderde` complaint. The package repaired stale macro-change wording, dated-event leakage, current-holding contradictions, Dutch hybrid language and the missing standalone HTML equity graph.

## Stable authority rules

1. `What changed / Wat veranderde` is a delta surface.
2. An unchanged regime is labelled explicitly as no material change before continuity context.
3. Current runtime positions and weights override static editorial memory.
4. Dated policy events may use relative-week wording only inside the report-week window.
5. A non-held ETF may be a challenger, but not the current holding.
6. MIME email HTML uses `cid:equitycurve`.
7. Standalone delivery HTML embeds the PNG as a data URI.
8. Only the uniquely identified equity image is restored after sanitization.

## Implemented corrections

- AI/semiconductor continuity no longer masquerades as a new change.
- The gold continuity sentence is removed from `What changed`.
- The 11 June ECB event is not described as occurring in the 14 July report week.
- IEFA's 24.05% allocation replaces stale absent/limited/watchlist/zero wording.
- DFEN is current; PPA remains an alternative candidate.
- specified Dutch mixed-language fragments are removed.
- standalone EN/NL HTML displays the equity graph.

## Evidence

```text
output/weekly_analysis_pro_260714_04.md
output/weekly_analysis_pro_260714_04_delivery.html
output/weekly_analysis_pro_260714_04.pdf
output/weekly_analysis_pro_nl_260714_04.md
output/weekly_analysis_pro_nl_260714_04_delivery.html
output/weekly_analysis_pro_nl_260714_04.pdf
output/validation/etf_report_freshness_260714_04.json
```

```text
validated_head: 2864050289b2bf4259e5c2f0375b6b9c42078fed
freshness_validation_run: 29461019794
post_execution_validation_run: 29461019772
PR: #70
merge_commit: 61f6a6a5ab2dd1dfe60f28f1b86a5517a0813dd5
```

The validation artifact records `email_sent=false`, no model replay, no state mutation and no trade-ledger mutation.

## Next action

Do not email `_04` unless separately authorized. Continue with the already recommended correction-runbook cleanup package before returning to cockpit-preview work.
