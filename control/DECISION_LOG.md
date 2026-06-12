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

---

## 2026-06-06 — Record WP9 deterministic macro narrative promotion decision as not_promoted

### Decision

WP9 creates `output/macro/promotion/macro_regime_promotion_decision_20260605_000000.json` with `status=not_promoted`.

### Consequence

The deterministic macro pilot remains review evidence only. It has no client-facing narrative authority, production report narrative authority, portfolio-action authority, lane-scoring authority, fundability authority, funding authority, portfolio mutation, delivery authority, execution authority, or production report mutation authority. A separate explicit control-layer promotion decision and separate report-integration work package remain required before production report output changes.

---

## 2026-06-12 — Historical output artifacts are immutable by default

### Decision

WP15 defines `control/HISTORICAL_ARTIFACT_CLEANUP_POLICY.md` and records:

```text
historical_output_artifacts_are_immutable_by_default=true
current_baseline_scope=manifest_linked_latest_report_set
cleanup_policy_defined_no_artifact_mutation
```

### Consequence

Older generated outputs may contain stale wording or old markers, but they remain historical evidence by default. Current production truth must be determined from `control/CURRENT_STATE.md` plus the latest manifest-linked report/runtime/pricing/delivery artifacts, not from repo-wide historical grep alone.

Do not bulk-edit, rewrite, delete, squash, or silently regenerate historical output files unless a future explicit cleanup/archive work package defines exact scope, traceability, rollback, and current-baseline verification.
