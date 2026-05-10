# ETF Macro & Policy Research Contract

## Purpose

This contract adds a compact macro / policy / regime layer to the Weekly ETF Review without turning the client report into a crowded macro note.

The macro layer is an input/state artifact first and a report section second.

## Layer distinction

### 1. Decision framework

No Add, Replace, or Fundable Challenger decision should be made unless the exposure is supported by at least one of:

- the current macro / policy regime
- cross-asset confirmation
- a clear policy catalyst
- a documented exception with explicit risk controls

### 2. Input/state contract

The workflow must build a machine-readable macro policy pack before lane discovery:

```text
output/macro/etf_macro_policy_pack_YYYYMMDD.json
output/macro/latest.json
```

The pack is the source of truth for macro regime inputs used by lane discovery, scoring, runtime state, and compact report rendering.

### 3. Output contract

The client report should only surface the highest-signal macro content:

- current regime
- what changed
- highest-impact central bank / policy signal
- 3 to 5 ETF implications
- only the macro points that change portfolio decisions

Do not publish long central-bank summaries, source dumps, or crowded macro tables in the PDF.

### 4. Operational runbook

The production workflow must run the macro policy pack builder before first-pass lane discovery.

Lane discovery must consume the pack through `output/macro/latest.json` or an explicit `--macro-policy-pack` argument.

## Required schema

```json
{
  "report_date": "YYYY-MM-DD",
  "regime": {
    "current": "Policy transition / mixed regime",
    "previous": "Policy transition / mixed regime",
    "confidence": 0.75,
    "what_changed": [],
    "portfolio_implication": ""
  },
  "central_banks": {
    "fed": {},
    "ecb": {},
    "boj": {},
    "boe": {},
    "pboc": {}
  },
  "macro_signals": {
    "growth": {},
    "inflation": {},
    "real_rates": {},
    "usd": {},
    "credit": {},
    "energy": {},
    "commodities": {},
    "equity_breadth": {}
  },
  "policy_catalysts": [],
  "cross_asset_confirmation": [],
  "portfolio_implications": [],
  "lane_adjustments": {},
  "report_digest": {}
}
```

## Report digest rule

`report_digest` is intentionally short. It is the only macro prose that should be inserted directly into the client report unless a specific macro event forces an exception.

Recommended digest shape:

```json
{
  "headline": "Policy transition regime; stay invested but require close-based evidence for new capital.",
  "top_changes": ["...", "...", "..."],
  "decision_implications": ["...", "...", "..."],
  "central_bank_focus": "...",
  "risk_watch": "..."
}
```

## Authority rules

- Prior reports are historical context, not current macro truth.
- Config files may provide curated context, but the generated pack is the runtime input for the report.
- If live macro research is later added, official and market-data sources should feed the pack, not the report directly.
- Missing macro freshness must reduce confidence or produce a warning; it must not fabricate certainty.

## Non-goals

- Do not turn the ETF review into a full macro newsletter.
- Do not publish every central-bank detail in the report.
- Do not let macro language override pricing, holdings, or recommendation state.
