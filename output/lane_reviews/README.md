# ETF lane assessment artifacts

This folder stores the machine-readable breadth-assessment artifact that must match each production ETF pro report.

## Naming
- `etf_lane_assessment_YYMMDD.json`
- `etf_lane_assessment_YYMMDD_NN.json`

## Purpose
Each artifact records which breadth buckets were assessed, which lanes were promoted into the live radar, which lanes remained challengers, and why omitted but relevant lanes were not promoted.

## Matching rule
A production ETF pro report and its lane assessment artifact must match one-to-one by date and version.

Examples:
- `output/weekly_analysis_pro_260420.md` ↔ `output/lane_reviews/etf_lane_assessment_260420.json`
- `output/weekly_analysis_pro_260420_02.md` ↔ `output/lane_reviews/etf_lane_assessment_260420_02.json`
