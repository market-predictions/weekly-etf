# ETF Review OS — Current State

## Snapshot date
2026-05-05

## What this repository currently is

This repository is a production-style weekly ETF review system with:

- `etf.txt` as the production masterprompt
- `control/CAPITAL_REUNDERWRITING_RULES.md` as the decision-framework addendum for model discipline
- `etf-pro.txt` and `etf-pro-nl.txt` as premium English/Dutch delivery layers
- `send_report.py` as the delivery/rendering script
- `.github/workflows/send-weekly-report.yml` as the production send workflow
- `.github/workflows/refresh-etf-state-from-report.yml` as the explicit state refresh workflow
- a pricing subsystem in `pricing/`
- archived reports in `output/`
- pricing audits in `output/pricing/`
- lane artifacts in `output/lane_reviews/`
- explicit ETF state files:
  - `output/etf_portfolio_state.json`
  - `output/etf_valuation_history.csv`
  - `output/etf_trade_ledger.csv`
  - `output/etf_recommendation_scorecard.csv`
- state derivation scripts:
  - `tools/write_etf_minimum_state.py`
  - `tools/write_etf_trade_ledger.py`
  - `tools/write_etf_recommendation_scorecard.py`
- a lab-only optimization layer using PyPortfolioOpt and yfinance history fetches

## What changed in this step

This update implements the **capital discipline / re-underwriting upgrade** requested after the first-principles review of the portfolio.

The key additions are:

- a new authoritative control addendum: `control/CAPITAL_REUNDERWRITING_RULES.md`
- a new machine-readable recommendation memory file: `output/etf_recommendation_scorecard.csv`
- a new writer: `tools/write_etf_recommendation_scorecard.py`
- send-path validation that the latest report can derive the recommendation scorecard before email delivery
- state-refresh workflow support so the scorecard is refreshed and committed with the other ETF state files
- updated control docs that make the capital re-underwriting layer explicit

The model-discipline upgrade adds these concepts to the ETF Review OS:

- fresh cash test
- thesis versus implementation split
- direct alternative duel for replaceable or weak holdings
- factor-overlap test
- hedge validity test
- cash policy test
- action-clock / inertia test
- deterministic re-underwriting triggers

## Why this matters

The latest portfolio critique identified a real process risk: a position could be called `Hold but replaceable`, weakening, or difficult to reprice, while still remaining unchanged for repeated runs.

That is not enough for a premium allocation model.

This upgrade makes `Hold` harder to hide behind:

- weak holdings must be re-underwritten
- replaceable holdings must carry a timer and best alternative
- hedges must prove hedge usefulness
- factor overlap must be visible
- cash must be explained as a deliberate choice
- the recommendation scorecard preserves this discipline across runs

## Current strengths

- Strong executive look and feel in the ETF report family.
- English canonical + Dutch companion delivery model exists.
- Pricing audit layer exists and is used operationally.
- Lane breadth artifact layer exists.
- Explicit ETF state files now cover portfolio state, valuation history, trade ledger, and recommendation discipline.
- Send workflow validates pricing, lane breadth, bilingual pairing, renderability, ETF state derivation, trade ledger derivation, and recommendation scorecard derivation before delivery.
- State refresh workflow can now commit the recommendation scorecard alongside the other state files.

## Current weaknesses

### 1. `etf.txt` remains a production monolith
The production masterprompt still mixes decision framework, state rules, output rules, and runbook rules.

The capital discipline logic is now represented in a separate control addendum instead of fully decomposing the monolith.

### 2. Recommendation scorecard is still report-derived
The scorecard currently derives from the canonical English report. It is a major improvement for state memory, but it is not yet an independent implementation engine.

### 3. Alternative duel scoring is not yet fully data-backed
The scorecard stores best alternative and required next action, but true 1-month / 3-month relative strength comparison still needs better machine-readable market history.

### 4. Factor exposure is rule-derived, not holdings-lookthrough-derived
The factor overlap flags are useful and deterministic, but still approximate. A future layer could add underlying ETF holdings/factor lookthrough if needed.

### 5. Delivery trigger behavior still needs validation
Recent delivery attempts showed that GitHub Actions visibility and triggering may not always be obvious through the connector. Production email success must still be verified from real workflow logs or manifests.

## Immediate priorities

### Priority A — validate scorecard derivation on the next live report
Confirm that:
- `tools/write_etf_recommendation_scorecard.py --check-only` passes before send
- `output/etf_recommendation_scorecard.csv` refreshes after report publication
- flagged holdings are sensible and not noisy

### Priority B — use the next ETF report to force decisions on weak/replaceable holdings
The next report should explicitly apply the new discipline to:
- SPY factor overlap versus SMH
- PPA re-underwriting versus ITA
- PAVE replaceability versus GRID
- GLD hedge validity and pricing confidence
- cash policy versus actionable SMH / URNM lanes

### Priority C — improve scorecard quality over time
Future enhancements:
- add real relative-strength alternative duel values
- add better cash classification extraction
- add more robust factor exposure model
- add explicit history of consecutive replaceable weeks across reports

### Priority D — keep the four-layer architecture explicit
Do not collapse the new rules back into a prompt-only narrative. The addendum is decision framework; the scorecard is input/state contract; the report remains output contract; workflows remain runbook.

## Current status label

**ETF now has a capital re-underwriting discipline layer and a recommendation scorecard state file. The next live run should validate that weak or replaceable positions can no longer hide behind vague Hold language without a named next action, alternative comparison, or override reason.**
