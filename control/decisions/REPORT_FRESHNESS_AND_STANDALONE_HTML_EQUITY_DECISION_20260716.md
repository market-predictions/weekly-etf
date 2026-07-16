# Decision — Report Freshness and Standalone HTML Equity

Date: 2026-07-16
Repository: `market-predictions/weekly-etf`
Status: accepted

## Decision

For Weekly ETF client reports:

```text
What changed / Wat veranderde is delta-only.
```

A current threshold condition is not a change. If no material regime transition or evidence delta exists, the report must say so explicitly before describing continuity.

## State authority

Current runtime positions, weights and dated event fields override static editorial memory.

Consequences:

- current IEFA funding overrides absent, limited, watchlist-only and zero-allocation wording;
- current DFEN state overrides PPA-as-incumbent wording;
- PPA may remain as an alternative or challenger;
- dated policy events may use `this week / deze week` only inside the report-week window.

## HTML image authority

The equity graph has two valid transport forms:

```text
MIME email body: cid:equitycurve
standalone HTML artifact: data:image/png;base64,...
```

The client sanitizer may continue to reject arbitrary CID/data-URI links. After normal sanitization, the delivery layer restores only the uniquely identified equity image source. It must reject ambiguous or missing image matches.

## Consequence

Future report validation must block:

- continuity-only wording under `What changed / Wat veranderde` unless explicitly framed as no material change;
- stale relative-date policy claims;
- contradictions between current holdings and editorial copy;
- standalone HTML with `cid:equitycurve`, `#harmful-link` or an equity placeholder;
- MIME email HTML that lacks the equity CID.

This decision changes report and delivery contracts only. It grants no portfolio-action, pricing, fundability, execution or state-mutation authority.
