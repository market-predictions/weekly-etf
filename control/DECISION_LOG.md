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

---

## 2026-06-13 — Protect ETF issuer and product names from localization

### Decision

ETF issuer names, fund family names, and product names are protected product terms. Dutch localization may translate table labels and prose, but must not translate inside names such as `iShares`, `SPDR`, `VanEck`, `Sprott`, `Global X`, or official ETF product names.

### Consequence

Broad replacements such as `Shares → Aantal aandelen` must not corrupt product names. Client-surface cleanup and validators must repair or fail on product-name corruption such as:

```text
iAantal aandelen
SPDR Gold Aantal aandelen
```

ETF/product-name protection is an output-contract rule. It does not change portfolio state, pricing, scoring, fundability, funding, or execution authority.

---

## 2026-06-13 — Deterministic macro/regime shadow artifacts require explicit no-authority fields

### Decision

Deterministic macro/regime shadow payloads, fixtures, and evidence artifacts must include explicit false authority fields rather than relying only on `shadow_only=true`.

Required false authority fields include:

```text
client_facing_authority=false
production_report_narrative_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
portfolio_mutation=false
historical_output_mutation=false
```

The deterministic regime fixture baseline must also cover every regime label defined in `config/regime_thresholds.yml`.

### Consequence

A passing deterministic regime fixture replay proves only fixture coverage and shadow consistency. It does not grant report narrative authority, client-facing authority, portfolio-action authority, lane-scoring authority, fundability authority, or portfolio mutation authority. Any promotion still requires a separate explicit control-layer promotion decision and later report-integration work package.

---

## 2026-06-13 — WP20 deterministic regime engine remains not_promoted

### Decision

WP20 creates:

```text
output/macro/promotion/deterministic_regime_engine_promotion_review_20260613_000000.json
```

with:

```text
status=not_promoted
client_facing_narrative_authority=false
production_report_narrative_authority=false
control_layer_decision=not_promoted
explicit_control_layer_promotion_decision=false
```

### Consequence

The deterministic regime engine may remain useful as shadow evidence, but it does not become a production report narrative source. It must not be wired into English/Dutch client reports, lane scoring, fundability, or portfolio actions until a later package satisfies methodology, bilingual, compliance, and explicit control-layer promotion gates.

---

## 2026-06-13 — Deterministic regime client-safe surface must use a narrow DTO

### Decision

WP21 defines:

```text
control/DETERMINISTIC_REGIME_CLIENT_SAFE_SURFACE_DESIGN.md
```

A future deterministic regime client-safe surface must be derived from a narrow sanitized DTO rather than from the full shadow payload or full macro pack.

The future DTO may expose only sanitized fields such as:

```text
regime_label_en / regime_label_nl
confidence_band_en / confidence_band_nl
comparison_status_en / comparison_status_nl
short_explanation_en / short_explanation_nl
discipline_note_en / discipline_note_nl
authority_disclaimer_en / authority_disclaimer_nl
```

### Consequence

Raw deterministic fields remain blocked from direct report use:

```text
deterministic_regime_shadow
macro_axes
macro_axis_scores
macro_evidence
confidence_decomposition
raw authority fields
workflow metadata
fixture names
```

WP21 is design-only and does not grant client-facing authority, production report narrative authority, portfolio-action authority, lane-scoring authority, fundability authority, portfolio mutation authority, production report integration, or historical-output mutation.

---

## 2026-06-13 — Safe-surface chain may proceed only to a separate integration proposal

### Decision

WP24 records that the WP21/WP22/WP23 chain is ready for a separate integration-proposal package, but not for direct production integration.

Reviewed chain:

```text
WP21: safe output contract
WP22: safe-surface validator
WP23: helper-only DTO/rendering layer
```

### Consequence

A future package may propose an integration path, but production report integration remains false until a later explicit implementation package is approved. Deterministic regime output still has no production report narrative authority, portfolio-action authority, lane-scoring authority, fundability authority, portfolio mutation authority, or historical-output mutation authority.

---

## 2026-06-13 — WP25 proposal does not authorize implementation

### Decision

WP25 records only a proposed future implementation shape for the deterministic regime report surface.

It allows a separate implementation package to be considered only if explicitly approved:

```text
WP26 — Deterministic regime report integration implementation
```

### Consequence

WP25 does not change production report rendering and does not integrate deterministic regime output into English or Dutch reports. It does not grant production report narrative authority, client-facing authority, automatic promotion, portfolio-action authority, lane-scoring authority, fundability authority, portfolio mutation authority, or historical-output mutation authority.

---

## 2026-06-17 — Stage-1 and Stage-2 macro/thesis shadow artifacts remain blocked from client surfaces

### Decision

Stage-1 thesis candidates, Stage-2 confirmation artifacts, driver IDs, driver catalogs, beneficiary maps, raw authority fields, and shadow-only status labels must be blocked from all current client-facing ETF report surfaces unless a later explicit control-layer promotion decision changes that authority.

### Consequence

The leakage firewall is an output-contract and operational-runbook guard only. It does not promote macro/thesis artifacts into report wording, lane scoring, fundability, portfolio rotation, delivery, or execution authority.

---

## 2026-06-17 — Macro/thesis bilingual aliases are terminology only

### Decision

Macro/thesis bilingual aliases may define sanitized future client-safe terminology, but they do not grant client-facing authority, report integration authority, lane-scoring authority, fundability authority, portfolio-action authority, delivery authority, execution authority, or historical-output mutation authority.

### Consequence

The alias source is an input/state and output-contract preparation layer only. It must not be wired into production report rendering, Dutch report generation, lane scoring, fundability checks, portfolio rotation, recommendations, delivery HTML, or historical output files without a separate explicit future work package and control-layer authority decision.
