# ETF Review OS — Decision Log

Use this file to capture stable architecture decisions so future sessions do not need to rediscover them.

---

## 2026-07-17 — Future client surfaces use one shared internal-language contract

### Decision

Future English and Dutch ETF report Markdown and delivery HTML must pass one shared deterministic internal-language contract before delivery.

The contract removes implementation-layer wording such as `shadow engine`, `runtime macro pack`, raw rotation/execution terminology, `release score`, raw override reasons, `review-only`, runtime-valuation wording, churn/discipline-gate language, `run(s)` and repeated punctuation.

### Consequence

The language contract is output-contract authority only. It may improve wording and fail the pre-send gate, but it must not change numbers, percentages, ticker links, portfolio decisions, pricing authority, macro/thesis authority, lane scoring, fundability, execution or historical artifacts.

The supplementary deterministic regime comparison may use client-safe language, but all explicit false-authority fields remain false. Historical reports remain immutable and may be replayed only as read-only validation input.

Persistent decision and evidence:

```text
control/decisions/REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP_DECISION_20260717.md
control/evidence/REPORT_SURFACE_INTERNAL_LANGUAGE_CLEANUP_EVIDENCE_20260717.json
```

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

---

## 2026-06-17 — Stage-2 promotion bridge defines eligibility only

### Decision

A Stage-2 promotion bridge may define future promotion-review eligibility, but it does not grant Stage-2 client-facing authority, production report authority, lane-scoring authority, fundability authority, portfolio-action authority, delivery authority, execution authority, or historical-output mutation authority.

### Consequence

The bridge is a decision-framework, input/state-contract, and output-contract design layer only. It may specify evidence prerequisites, bilingual alias dependency, leakage/compliance gates, and future implementation gates, but Stage-2 output remains shadow-only until a later explicit control-layer promotion decision and separate implementation package exist.

---

## 2026-06-17 — Stage-2 promotion review schema defines review shape only

### Decision

A Stage-2 promotion review artifact schema may define how future evidence is reviewed, but it does not grant Stage-2 client-facing authority, production report authority, lane-scoring authority, fundability authority, portfolio-action authority, delivery authority, execution authority, or historical-output mutation authority.

### Consequence

The schema is an input/state-contract, output-contract, and operational-runbook validation layer only. It may define allowed review statuses, source-artifact references, required false/no-authority fields, and validation checks, but it must not create production promotion artifacts or wire Stage-2 output into reports, scoring, fundability, portfolio actions, delivery, execution, or historical output mutation.

---

## 2026-06-17 — Stage-2 promotion review checklist validates completeness only

### Decision

A Stage-2 promotion review checklist may validate whether future review evidence is complete, but it does not grant Stage-2 client-facing authority, production report authority, lane-scoring authority, fundability authority, portfolio-action authority, delivery authority, execution authority, or historical-output mutation authority.

### Consequence

The checklist is an operational-runbook, input/state-contract, and output-contract validation layer only. It may calculate non-promotional checklist readiness status and validate source references, no-authority fields, and forbidden review text, but it must not create live production promotion artifacts or wire Stage-2 output into reports, scoring, fundability, portfolio actions, delivery, execution, or historical output mutation.

---

## 2026-06-17 — Stage-2 promotion review fixtures prove pass/fail behavior only

### Decision

A Stage-2 promotion review fixture set may prove pass/fail behavior for future review artifacts, but it does not create live promotion artifacts and does not grant Stage-2 client-facing authority, production report authority, lane-scoring authority, fundability authority, portfolio-action authority, delivery authority, execution authority, or historical-output mutation authority.

### Consequence

The fixture set is an input/state-contract, output-contract, and operational-runbook validation layer only. It may replay deterministic pass and planted-failure artifacts for schema/checklist behavior, but it must not create live review artifacts under output, production promotion artifacts, report wording, scoring, fundability, portfolio actions, delivery, execution, or historical output mutation.

---

## 2026-07-17 — Every non-zero ETF position counts toward the maximum

### Decision

Every unique ticker with `shares > 0` counts as one active position. Zero-share rows do not count, duplicate active ticker rows are invalid, and there is no generic residual-position exception. The default maximum is eight active positions.

The current nine-position state is classified `close_first`. A no-trade review may preserve that state, but any proposed trade while above the limit must reduce the active count and may not open a new ticker. At exactly eight positions, opening a new ticker requires another ticker to reach zero shares in the same projected whole-share execution. A partial reduction that leaves positive shares does not free a slot.

### Consequence

The standard production preflight evaluates projected whole-share quantities before guarded mutation and fails closed on a count breach. Current matching English and Dutch report surfaces disclose the actual count; historical reports with a different ticker set remain unchanged.

This decision does not select a holding to close and does not authorize portfolio mutation or delivery. A separately claimed, current-evidence close-first review is required before any count-reducing execution.

Persistent decision and evidence:

```text
control/decisions/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_DECISION_20260717.md
control/evidence/PORTFOLIO_POSITION_COUNT_CONSTRAINT_RECONCILIATION_EVIDENCE_20260717.json
```

---

## 2026-07-18 — Close-first review selects URNM-to-cash as a review option

### Decision

The no-mutation close-first review uses fresh completed-close data, current lane quality, holding continuity, relative strength, contribution, portfolio-role evidence, liquidity and preservation credits to compare all nine active positions.

For the 2026-07-17 evidence date, URNM is the supported review source. The reviewed path closes all 48 URNM shares, opens no new ticker, restores the active count from nine to eight and retains the estimated proceeds as cash.

URNM remains first when position-size and implementation-practicality points are removed. XLU ranks second. Position size is therefore not the selection authority.

### Consequence

This is review evidence only. It does not change the official portfolio or grant implementation authority. A separate explicitly approved package must refresh prices, rerun the same rubric and stop without changes if the source or evidence changes materially.

Persistent records:

```text
control/evidence/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EVIDENCE_20260718.json
control/decisions/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_DECISION_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_EN_20260718.md
control/reviews/PORTFOLIO_CLOSE_FIRST_EXECUTION_REVIEW_NL_20260718.md
```
