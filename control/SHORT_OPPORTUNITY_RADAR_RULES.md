# Short Opportunity Radar Rules

## Purpose

The Weekly ETF Pro Review must include a compact **Short Opportunity Radar** when publishing a professional ETF review. This section is separate from the long-only Structural Opportunity Radar.

The goal is not to recommend aggressive shorting by default. The goal is to show a disciplined view of where downside asymmetry, weak relative strength, crowded positioning, or macro vulnerability may create hedge or short-watchlist candidates.

## Placement

Add the section after `## 4. Structural Opportunity Radar` and before `## 5. Key Risks / Invalidators`.

Use heading:

`## 4A. Short Opportunity Radar`

Do not renumber Sections 5 through 17. Keep downstream parsers stable.

## Published table

Use this compact table:

| Short theme | Candidate ETF | Short thesis | Trigger | Invalidation | Time horizon | Confidence |
|---|---|---|---|---|---|---|

Publish 3 to 5 candidates by default.

## Candidate principles

Short candidates may include:
- overextended momentum ETFs vulnerable to reversal
- weak cyclical or small-cap exposures under restrictive real rates
- region or country ETFs facing policy, FX, earnings, or liquidity pressure
- long-duration or rate-sensitive ETFs vulnerable to higher real yields
- commodity or thematic ETFs where the thesis is crowded, stale, or technically weak

Avoid using inverse or leveraged ETFs as default implementation vehicles unless the report explicitly allows them. Prefer naming the ETF whose long exposure is vulnerable, with the understanding that the idea is a short or hedge candidate, not a long recommendation.

## Required caveat

The section must include a short caveat that short ideas are tactical hedge/watchlist ideas, not automatic executed trades. They must not change long portfolio holdings unless Section 13 and Section 14 explicitly execute that change.

## Lane artifact extension

The matching `output/lane_reviews/etf_lane_assessment_YYMMDD[_NN].json` should include a top-level `short_opportunity_radar` array. Each item should include:
- short_theme
- candidate_etf
- short_thesis
- trigger
- invalidation
- time_horizon
- confidence
- status

## Continuity

Section 16 should include compact short-radar continuity notes when relevant:
- retained short watchlist themes
- new short watchlist themes
- dropped short watchlist themes
- what would activate a hedge or short idea next run

## Authority rule

The Short Opportunity Radar is an output-contract requirement. It does not override the implemented long portfolio unless the Final Action Table and Position Changes Executed This Run explicitly show an executed change.
