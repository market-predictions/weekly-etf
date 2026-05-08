# ETF Review OS — Decision Log

Use this file to capture stable architecture decisions so future sessions do not need to rediscover them.

---

## 2026-03-28 — Adopt Project + GitHub + Actions architecture
### Decision
The ETF flow will no longer be treated conceptually as one giant prompt-centered system.

### Chosen architecture
- **ChatGPT Project** = working memory and recurring workspace
- **GitHub repo** = explicit source of truth for prompts, scripts, outputs, and control docs
- **GitHub Actions + scripts** = real execution and delivery layer
- **Optional Custom GPT** = architect/reviewer only, not the primary runtime container

### Reason
This separates thinking/work context, system state/audit trail, and production execution.

---

## 2026-04-17 — Replace fixed structural-lane gating with open discovery and compact executive publication
### Decision
The production ETF prompt should no longer use a small fixed structural lane list as the front-end discovery gate.

### Chosen architecture
- open internal discovery across broad investable domains each run
- dynamic candidate-lane construction before publication
- persistent taxonomy as a back-end memory layer, not a front-end gate
- compact executive publication of only the best-ranked lanes
- continuity memory for retained lanes, new entrants, dropped lanes, and near-miss challengers

### Reason
This reduces omission risk while preserving premium executive selectivity.

---

## 2026-04-18 — Add starter pricing subsystem on main
### Decision
ETF has a starter explicit pricing subsystem rather than leaving pricing entirely as ad hoc retrieval inside the prompt.

### Chosen architecture
- `pricing/`
- `output/pricing/`
- pricing clients and audit writer
- pricing pass CLI

### Reason
This creates a machine-readable input/state layer for fresh ETF closes.

---

## 2026-04-21 — Make breadth assessment explicit through lane artifacts
### Decision
Broader discovery should be auditable through a matching machine-readable lane artifact and a compact visible omitted-lane block.

### Chosen architecture
- mandatory breadth assessment universe
- matching lane artifact in `output/lane_reviews/`
- compact omitted-lane proof in the published report
- helper validator in `validate_lane_breadth.py`

### Reason
Open discovery should not remain only a prompt intention.

---

## 2026-04-23 — Adopt English-canonical plus Dutch-companion bilingual delivery pattern
### Decision
ETF bilingual publication should use one canonical English pro report and one Dutch companion report derived from the completed English report.

### Chosen architecture
- English pro report remains canonical
- Dutch companion is a faithful language render
- one lane artifact remains tied to the English report
- paired filenames share date/version
- workflow can validate, render, and send both language versions

### Reason
This preserves analytical determinism while enabling bilingual delivery.

---

## 2026-04-27 — Introduce and enrich minimum explicit ETF state
### Decision
ETF should have explicit implementation state files instead of relying only on prior-report parsing and prompt continuity.

### Chosen architecture
- `tools/write_etf_minimum_state.py`
- `tools/write_etf_trade_ledger.py`
- `output/etf_portfolio_state.json`
- `output/etf_valuation_history.csv`
- `output/etf_trade_ledger.csv`
- dedicated state refresh workflow
- pre-send state derivation checks

### Reason
This moves ETF toward the FX-style state model while staying honest that ETF state is still report-derived.

---

## 2026-04-27 — Add lab-only ETF optimization layer
### Decision
ETF includes a lab-only optimization workbench using PyPortfolioOpt and yfinance-fetched history.

### Chosen architecture
- `tools/generate_pyportfolioopt_optimization_lab.py`
- `tools/fetch_etf_optimizer_prices_yfinance.py`
- `.github/workflows/lab-pyportfolioopt-optimization.yml`
- `lab_inputs/`
- `lab_outputs/`

### Reason
Optimization may be useful as QA/research, but must not become production authority without explicit review.

---

## 2026-05-05 — Add capital re-underwriting discipline and recommendation scorecard
### Decision
ETF now has an explicit capital re-underwriting discipline layer and a machine-readable recommendation scorecard.

### Chosen architecture
- `control/CAPITAL_REUNDERWRITING_RULES.md`
- `tools/write_etf_recommendation_scorecard.py`
- `output/etf_recommendation_scorecard.csv`
- pre-send scorecard derivation validation in `.github/workflows/send-weekly-report.yml`
- state-refresh support in `.github/workflows/refresh-etf-state-from-report.yml`

### Reason
The first-principles review identified a real process weakness: a holding can be described as replaceable, weakening, or difficult to reprice while still remaining unchanged for repeated runs.

The new discipline layer forces the model to ask whether each holding would be bought today with fresh cash, separates thesis validity from implementation quality, requires alternative duels for weak or replaceable holdings, flags factor overlap, tests hedge validity, classifies cash, and prevents indefinite `Hold but replaceable` inertia.

### Consequence
- Weak or replaceable holdings now need a named next action, alternative comparison, or explicit override.
- The next live ETF report should force clear review of SPY, PPA, PAVE, GLD, and cash policy.
- ETF state now includes portfolio state, valuation history, trade ledger, lane artifacts, pricing audits, and recommendation discipline memory.

---

## 2026-05-07 — Lock runtime-driven bilingual production baseline
### Decision
ETF now treats the runtime-driven pipeline as the stable production baseline.

### Chosen architecture
```text
pricing audit
→ lane discovery
→ runtime state
→ EN/NL report render
→ polish/linkify
→ validation
→ PDF/email delivery
```

### Reason
This path has produced received bilingual reports and resolves the prior architecture problem where markdown reports acted as hidden state, pricing source, continuity memory, and delivery artifact all at once.

### Consequence
- Markdown reports are presentation output, not primary state authority.
- Future changes should preserve the runtime flow and avoid manual markdown patching.
- Renderer changes should be limited to concrete output defects or validated improvements.
- The next discovery-maturity phase is historical relative-strength scoring.
- The next pricing-maturity phase is two-pass challenger pricing.

---

## 2026-05-07 — Validate historical relative-strength and two-pass challenger pricing baseline
### Decision
ETF now treats historical relative-strength scoring and two-pass challenger pricing as part of the validated production baseline.

### Chosen architecture
```text
pricing audit
→ historical relative strength
→ first-pass lane discovery
→ targeted challenger pricing
→ final lane discovery
→ runtime state
→ EN/NL report render
→ polish/linkify
→ validation
→ PDF/email delivery
```

### Reason
The workflow successfully passed after adding:

- `runtime/fetch_etf_relative_strength.py`
- historical 1m/3m return, trend, drawdown, volatility and relative-strength inputs
- `pricing/augment_challenger_pricing.py`
- targeted challenger pricing between first-pass and final discovery

### Consequence
- The Structural Opportunity Radar is now less dependent on configured priors.
- Top discovery challengers can receive targeted pricing before final scoring.
- Priced challengers are not automatically fundable; they only enable a fairer comparison.
- The next maturity steps are liquidity/tradability filtering, relative strength versus current holdings, and macro/fundamental freshness inputs.

---

## 2026-05-08 — Move strict branded sections to delivery HTML and validate rendered contract
### Decision
Sections with strict layout or clickable behavior are delivery-HTML responsibilities, not markdown-polish responsibilities.

### Chosen architecture
```text
runtime state
→ EN/NL markdown render
→ polish/linkify
→ delivery HTML overrides for strict sections
→ dynamic delivery HTML contract validator
→ PDF/email delivery
```

### Scope
This applies specifically to:

- Portfolio Action Snapshot
- Current Position Review

### Reason
Repeated markdown-level fixes could not reliably guarantee clickable ticker formatting or a stable Current Position Review table because the branded PDF renderer uses special panel logic. The stable solution is to render these strict sections directly from runtime state at the delivery HTML layer.

### Consequence
- `runtime/delivery_html_overrides.py` owns the final HTML for strict branded sections.
- `send_report_runtime_html.py` is the workflow delivery entrypoint.
- `tools/validate_etf_delivery_html_contract.py` dynamically reads holdings from runtime state and validates rendered delivery HTML before email send.
- The validator checks for real TradingView anchors, prevents raw markdown links, and ensures Current Position Review is a real HTML table.
- Future PDF layout defects in these sections should be fixed in the delivery HTML layer, not by more markdown post-processing.
