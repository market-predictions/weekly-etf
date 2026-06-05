# ETF Review OS — Decision Log

Use this file to capture stable architecture decisions so future sessions do not need to rediscover them.

---

## 2026-03-28 — Adopt Project + GitHub + Actions architecture

### Decision

The ETF flow uses the ChatGPT Project as working memory, GitHub as source of truth, and GitHub Actions/scripts as the real execution and delivery layer.

### Consequence

Do not treat chat memory as authoritative repo state. For meaningful repo work, read the control files first and then inspect the minimum relevant execution files.

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

---

## 2026-04-18 — Add starter pricing subsystem on main

### Decision

ETF has a starter explicit pricing subsystem rather than leaving pricing entirely as ad hoc retrieval inside the prompt.

### Consequence

Pricing lives as a machine-readable input/state layer under `pricing/` and `output/pricing/`.

---

## 2026-04-21 — Make breadth assessment explicit through lane artifacts

### Decision

Broader discovery should be auditable through a matching machine-readable lane artifact and a compact visible omitted-lane block.

---

## 2026-04-23 — Adopt English-canonical plus Dutch-companion bilingual delivery pattern

### Decision

ETF bilingual publication uses one canonical English pro report and one Dutch companion report derived from the same runtime/report state.

---

## 2026-04-27 — Introduce and enrich minimum explicit ETF state

### Decision

ETF should have explicit implementation state files instead of relying only on prior-report parsing and prompt continuity.

### Consequence

ETF state includes:

```text
output/etf_portfolio_state.json
output/etf_valuation_history.csv
output/etf_trade_ledger.csv
```

---

## 2026-04-27 — Add lab-only ETF optimization layer

### Decision

ETF includes a lab-only optimization workbench using PyPortfolioOpt and yfinance-fetched history.

### Consequence

Optimization may support QA/research but must not become production authority without explicit review.

---

## 2026-05-05 — Add capital re-underwriting discipline and recommendation scorecard

### Decision

ETF has an explicit capital re-underwriting discipline layer and a machine-readable recommendation scorecard.

### Consequence

Weak or replaceable holdings need a named next action, alternative comparison, or explicit override. This prevents indefinite `Hold but replaceable` inertia.

---

## 2026-05-07 — Lock runtime-driven bilingual production baseline

### Decision

ETF treats the runtime-driven pipeline as the stable production baseline.

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

### Consequence

Markdown reports are presentation output, not primary state authority.

---

## 2026-05-07 — Validate historical relative-strength and two-pass challenger pricing baseline

### Decision

ETF treats historical relative-strength scoring and two-pass challenger pricing as part of the validated production baseline.

### Consequence

Priced challengers are not automatically fundable; they only enable fairer comparison.

---

## 2026-05-08 — Move strict branded sections to delivery HTML and validate rendered contract

### Decision

Sections with strict layout or clickable behavior are delivery-HTML responsibilities, not markdown-polish responsibilities.

### Scope

- Portfolio Action Snapshot
- Current Position Review

### Consequence

Future PDF layout defects in these sections should be fixed in the delivery HTML layer, not by markdown post-processing.

---

## 2026-05-10 — Treat Dutch localization as a language-contract layer

### Decision

The Dutch ETF companion report is governed by a language-contract layer, not by ad-hoc markdown replacements or a separate research pass.

### Consequence

English remains canonical analytical report. Dutch remains native companion from the same runtime state/key figures. Strict bilingual numeric parity remains required.

---

## 2026-05-11 — Render Section 7 equity curve from full valuation history

### Decision

Section 7 equity curve rendering must use the full machine-readable valuation history, not a hardcoded start/latest pair.

---

## 2026-05-31 — Approve macro/thesis roadmap with phased shadow-first sequencing

### Decision

The Weekly ETF Macro & Thesis Engine roadmap is approved as the next major model-quality track, but only under strict phased sequencing and shadow-first controls.

### Chosen architecture

```text
pricing lineage first
→ macro audit foundation
→ deterministic regime and confidence engine
→ macro policy pack schema
→ compliance and methodology gates
→ thesis candidates in shadow mode
→ Stage-2 confirmation and valuation flags
→ client-surface integration only after validation
```

### Authority rule

Macro/regime modernization may produce internal artifacts while shadow-only. It must not change client-facing fundable decisions until explicit promotion gates pass.

---

## 2026-05-31 — Keep Phase 2 macro audit foundation shadow-only

### Decision

The Phase 2 macro audit foundation is an input/provenance layer only.

### Consequence

It may fetch and validate macro observations but must not yet set regime, confidence, lane scoring, fundability, portfolio actions, or client-facing report wording.

---

## 2026-06-03 — Validate macro-audit-derived regime axes in shadow CI only

### Decision

Macro-audit-derived axes are validated in isolated macro-regime shadow CI only.

### Authority rule

The following remain internal shadow evidence only:

```text
deterministic_regime_shadow
macro_axes
macro_axis_scores
macro_evidence
confidence_decomposition
```

They must not be used for client-facing regime labels, lane scoring, fundability decisions, portfolio trades, or report recommendations until future methodology, compliance, bilingual, and production-output gates pass.

---

## 2026-06-05 — Enforce Dutch delivery-surface localization at delivery runtime

### Decision

Dutch delivery-surface localization for strict branded PDF/HTML panels must be enforced in the layer that generates final delivery HTML, not only in native markdown renderers or markdown scrubbers.

### Reason

The June 5 cleanup showed that `Current Position Review` / `Review huidige posities` is rebuilt from runtime state by the delivery HTML override layer. Markdown-level scrub fixes were insufficient for the final PDF.

### Consequence

Strict branded panel defects must be fixed in `runtime/delivery_html_overrides.py`, `runtime/client_facing_sanitizer.py`, shared localization maps, or the delivery startup/runtime layer as appropriate.

---

## 2026-06-05 — Add deterministic macro narrative shadow candidate comparison path

### Decision

Work Package 1 — Deterministic macro narrative shadow candidate is completed as a shadow-only comparison path in `market-predictions/weekly-etf`.

### Chosen architecture

```text
current English report markdown
+ current Dutch report markdown
+ output/macro/validation/latest_macro_regime_shadow_validation.json
→ runtime/render_macro_regime_shadow_narrative.py
→ output/macro/shadow_narrative/macro_regime_shadow_narrative_<run_id>.json
→ tools/validate_macro_regime_shadow_narrative.py
```

### Authority rules

```text
client_facing=false
production_report=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
no production report mutation
```

---

## 2026-06-05 — Add macro narrative compliance and bilingual parity gate

### Decision

Work Package 2 — Macro narrative compliance and bilingual parity gate is completed as an output-contract safety gate in `market-predictions/weekly-etf`.

### Blocks

```text
predictive wording
uncited macro claims
shadow/internal labels
macro_axes leakage
confidence_decomposition leakage
English leakage in Dutch report text
citation parity mismatch
Dutch/English meaning drift
```

### Authority rules

```text
output_contract_gate_only=true
production_report_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
delivery_authority=false
```

---

## 2026-06-05 — Add macro promotion decision contract

### Decision

Work Package 3 — Macro promotion decision contract is completed and merged via PR #51.

```text
merge_commit: 7b7fe1db0b04dd3b1d377463ad59e06927037993
```

The contract defines what must be true before deterministic macro regime output may move from shadow-only evidence into report narrative authority.

### Chosen architecture

```text
control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
tools/validate_macro_regime_promotion_contract.py
fixtures/macro_promotion/not_promoted_valid.json
fixtures/macro_promotion/bad_promoted_without_approval.json
tests/test_macro_regime_promotion_contract.py
```

### Promotion prerequisites

```text
methodology_approved=true
bilingual_parity_approved=true
compliance_validator_passed=true
old_vs_new_comparison_reviewed=true
explicit_control_layer_promotion_decision=true
control_layer_decision=promote_to_report_narrative_authority
client_facing_narrative_authority=true
production_report_narrative_authority=true
blockers=[]
```

### Permanent authority boundaries

The contract does not grant:

```text
portfolio_action_authority
lane_scoring_authority
fundability_authority
funding_authority
portfolio_mutation
```

Those remain false unless a separate future contract explicitly promotes them.

### Consequence

WP1, WP2 and WP3 together permit controlled review of deterministic macro narrative candidates, but do not yet integrate deterministic macro regime into production narrative authority. A future client-surface pilot or production promotion still requires an explicit control-layer decision.
