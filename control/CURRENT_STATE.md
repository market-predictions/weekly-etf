# ETF Review OS — Current State

## Snapshot date
2026-06-05

## What this repository currently is

`market-predictions/weekly-etf` is a runtime-driven production-style weekly ETF review system with:

- explicit pricing audits in `output/pricing/`
- explicit run manifests in `output/run_manifests/`
- redaction-safe delivery manifests in `output/delivery/`
- runtime report-state artifacts in `output/runtime/`
- persisted portfolio state, valuation history, and trade ledger
- guarded model execution with trade-ledger idempotency checks
- English canonical and Dutch native companion report generation
- delivery HTML overrides for strict branded sections
- hard pricing-lineage validation before send
- delivery-manifest evidence linked from the final run manifest
- shadow-first macro/thesis roadmap controls
- macro compliance, WP1 deterministic macro narrative shadow-candidate path, WP2 macro narrative client-surface/parity gate, Stage-1 thesis candidate, and Stage-2 thesis promotion-contract gates that are green/present but still non-authoritative for production decisions

## Latest production and report-surface evidence

### Latest fully recorded production validation baseline

```text
workflow: Send weekly ETF Pro report
run_number: 205
trigger_commit: 3bd07f7ff31af77adbd23359d66a8c5ab7ab3343
run_id: 20260604_190001
requested_close_date: 2026-06-03
report_token: 260603
workflow_status: workflow_success
workflow_conclusion: success
pricing_lineage_status: passed
report_authority_source: portfolio_state_post_execution
english_report_path: output/weekly_analysis_pro_260603.md
dutch_report_path: output/weekly_analysis_pro_nl_260603.md
runtime_state_path: output/runtime/etf_report_state_20260603_20260604_190001.json
pricing_audit_path: output/pricing/price_audit_2026-06-03_20260604_190001.json
portfolio_state_path: output/etf_portfolio_state.json
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-03_20260604_190001.json
total_portfolio_value_eur: 111596.96
```

This proves workflow success, pricing-lineage success, post-execution report authority, and repo-visible SMTP-send evidence for that baseline. The delivery evidence means `smtplib.sendmail()` returned without raising and per-language delivery manifests were written. It is **not** an end-recipient inbox receipt.

### Latest report-surface cleanup verification

```text
workflow: Send weekly ETF Pro report
run_number: 216
trigger_commit: ce86dce050a75c2b21481162ad3b6952ebbdb1e7
branch: main
workflow_conclusion: success
observed_at: 2026-06-05
source: user-provided GitHub Actions UI screenshot plus visual inspection of generated report artifacts
english_pdf: weekly_analysis_pro_260604_10.pdf
dutch_pdf: weekly_analysis_pro_nl_260604_10.pdf
```

The `_10` report-surface cleanup cycle is closed for the issues under review:

```text
Current Position Review score completeness: fixed
English/Dutch active-position score completeness: fixed
stale GLD current-surface wording: fixed
Dutch delivery enum leakage `No / under review`: fixed
unwanted `Nee / onder herbeoordeling` surface wording: removed from the final report view
workflow_status: success
```

This is report-generation / visual report-surface evidence. It does **not** by itself replace the full delivery manifest baseline above unless the corresponding delivery manifest and final run manifest are separately inspected.

### WP1 deterministic macro narrative shadow candidate evidence

```text
Work Package 1 — Deterministic macro narrative shadow candidate
repository: market-predictions/weekly-etf
status: implemented as shadow-only comparison path
reported focused test: python -m pytest tests/test_macro_regime_shadow_narrative.py -q = 4 passed
reported artifact validation: MACRO_REGIME_SHADOW_NARRATIVE_OK
```

Repo-visible WP1 files:

```text
runtime/render_macro_regime_shadow_narrative.py
tools/validate_macro_regime_shadow_narrative.py
tests/test_macro_regime_shadow_narrative.py
output/macro/shadow_narrative/macro_regime_shadow_narrative_20260605_000000.json
```

WP1 authority boundaries:

```text
client_facing=false
production_report=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
no production report mutation
```

The committed sample artifact compares current English/Dutch macro report wording with a deterministic regime shadow narrative candidate. It references:

```text
current_report_en_path=output/weekly_analysis_pro_260604_10.md
current_report_nl_path=output/weekly_analysis_pro_nl_260604_10.md
macro_regime_artifact_path=output/macro/validation/latest_macro_regime_shadow_validation.json
```

The sample artifact remains review-only. It does not insert text into the production report, delivery workflow, portfolio state, lane scoring, fundability logic, or execution behavior.

### WP2 macro narrative compliance and bilingual parity gate evidence

```text
Work Package 2 — Macro narrative compliance and bilingual parity gate
repository: market-predictions/weekly-etf
status: implemented on main as output-contract validator/test/fixture package
reported focused test: python -m pytest tests/test_macro_narrative_client_surface.py -q = 4 passed
```

Repo-visible WP2 files:

```text
tools/validate_macro_narrative_client_surface.py
fixtures/macro_narrative/safe_shadow_candidate_en_nl.json
fixtures/macro_narrative/bad_predictive_language.json
fixtures/macro_narrative/bad_shadow_label_leakage.json
fixtures/macro_narrative/bad_dutch_parity.json
tests/test_macro_narrative_client_surface.py
```

WP2 blocks:

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

WP2 authority boundaries:

```text
output_contract_gate_only=true
production_report_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
delivery_authority=false
```

The validator is a client-surface safety gate only. It does not promote deterministic macro regime output into production report authority.

## Four-layer operating status

### 1. Decision framework

The current decision framework remains:

- capital re-underwriting discipline from `control/CAPITAL_REUNDERWRITING_RULES.md`
- broad lane discovery from `control/LANE_DISCOVERY_CONTRACT.md`
- valuation-grade challenger discipline
- guarded model execution with trade-ledger idempotency
- no indefinite `Hold but replaceable` inertia
- explicit separation between workflow success, pricing-lineage success, SMTP-send evidence, and final inbox receipt
- macro/thesis modernization approved only as future phased enhancement
- deterministic macro/regime classification and deterministic macro narrative candidates remain shadow-only until later promotion gates pass
- WP2 may validate candidate client-surface wording/parity, but it does not itself grant report narrative authority
- Stage-1 thesis candidates remain internal-only shadow artifacts
- Stage-2 thesis promotion discipline is a contract gate only, not production authority
- macro compliance gates may validate wording/surface safety, but they do not grant decision authority by themselves

Post-execution authority remains:

```text
runtime state = pre-execution pricing/report-state provenance
official portfolio state = post-execution active holdings after guarded execution
client report Section 7 / Section 15 = post-execution official portfolio state when execution occurred in the same run
```

### 2. Input/state contract

Authoritative production inputs remain:

- `output/pricing/price_audit_<requested_close_date>_<run_id>.json`
- `output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json`
- `output/runtime/etf_report_state_<report_token>_<run_id>.json`
- `output/runtime/etf_model_execution_<date>_<run_id>.json`
- `output/etf_portfolio_state.json`
- `output/etf_valuation_history.csv`
- `output/etf_trade_ledger.csv`
- `output/etf_recommendation_scorecard.csv`
- `output/lane_reviews/etf_lane_assessment_<report_token>.json`
- `output/market_history/etf_relative_strength.json`
- `output/macro/latest.json`

Delivery evidence is recorded at:

- `output/delivery/latest_weekly_etf_delivery_manifest_path.txt`
- `output/delivery/weekly_etf_delivery_manifest_<requested_close_date>_<run_id>.json`
- `control/DELIVERY_MANIFEST_STATUS_20260604.md`

Macro/thesis validation artifacts and control files remain review/audit artifacts only. They are not production report, lane-scoring, fundability, or portfolio-action authority unless a future control-layer decision explicitly promotes them.

WP1 adds a macro narrative comparison artifact path at:

- `output/macro/shadow_narrative/macro_regime_shadow_narrative_<run_id>.json`

WP2 adds a client-surface compliance/parity validator path for future macro narrative candidates:

- `tools/validate_macro_narrative_client_surface.py`
- `fixtures/macro_narrative/*.json`

Those artifacts are explicitly output-contract gates only.

### 3. Output contract

The report output contract is now:

- English is the canonical analytical report.
- Dutch is a native companion render from the same runtime state/key figures, not broad-translated markdown and not a second research pass.
- Native Dutch localization/scrub layers are guard-only except for narrow structured runtime-state display-label normalization.
- Section 7 equity curve and Section 15 holdings reconcile to the post-execution official portfolio state when guarded execution occurred in the same run.
- Pricing-basis disclosure dynamically derives required rows from current active holdings, not stale hardcoded ticker sets.
- Pricing-basis disclosure must show requested close, close date used, source, status, and close used for all active holdings.
- Strict branded sections are rendered from runtime state at delivery HTML level, not fixed through markdown-only patches.
- Current Position Review / Review huidige posities must show numeric scores for every active ETF position.
- Dutch delivery-surface enum localization must be enforced at the delivery HTML/runtime layer, not only in markdown scrubbers.
- Stale exited-holding wording, especially GLD as a current active hedge/review item when not active, must be blocked from current report surfaces.
- Dutch PDF chart labels are generated in Dutch in the runtime delivery path.
- Client-facing reports must not leak internal plumbing labels.
- Delivery evidence must be repo-visible and linked from the final run manifest after successful send.
- Macro-audit-derived `macro_axes`, `macro_axis_scores`, and `deterministic_regime_shadow` must not appear in client-facing reports until future methodology, compliance, bilingual gates, and explicit promotion gates approve them.
- WP1 deterministic macro narrative shadow candidates must not appear in client-facing reports until future compliance, bilingual parity, and explicit promotion gates approve them.
- WP2 must pass before any future deterministic macro narrative candidate can be considered client-surface safe, but a WP2 pass does not by itself promote the candidate.
- Stage-1 thesis candidates and Stage-2 promotion-chain artifacts must not appear in client-facing reports until explicit promotion gates approve them.

### 4. Operational runbook

The current production path is:

```text
run-queue request or manual dispatch
→ resolve run identity
→ persistent ETF pricing pass
→ historical relative-strength fetch
→ macro policy pack build, with Phase 2 macro audit shadow-only / non-blocking
→ first-pass lane discovery
→ challenger pricing augmentation
→ final lane discovery
→ challenger fundability validation
→ portfolio rotation plan
→ runtime report state
→ EN/NL native markdown reports
→ pricing-basis disclosure
→ report polish / localization / ticker links
→ run manifest
→ persisted valuation state
→ guarded ETF model execution
→ post-execution official portfolio state
→ delivery HTML/PDF validation
→ Dutch quality validation
→ hard pricing-lineage pre-send gate
→ PDF/email delivery workflow step
→ redaction-safe delivery manifest summary
→ final manifest update with delivery_manifest_path
```

Strict branded or PDF-visible report-surface defects must be fixed in the layer that actually generates the final PDF/HTML:

```text
runtime state defect → fix runtime state builder
markdown-only defect → fix native renderer / polish / linkifier
strict branded panel defect → fix delivery HTML overrides
send-time enum/localization defect → fix delivery runtime / shared localization map
validator gap → add or tighten the relevant pre-send gate
```

WP1 shadow narrative operation is separate from production delivery:

```text
current EN/NL report markdown
+ output/macro/validation/latest_macro_regime_shadow_validation.json
→ runtime/render_macro_regime_shadow_narrative.py
→ output/macro/shadow_narrative/macro_regime_shadow_narrative_<run_id>.json
→ tools/validate_macro_regime_shadow_narrative.py
```

WP2 client-surface compliance/parity validation is separate from production promotion:

```text
future macro narrative candidate EN/NL surface artifact
→ tools/validate_macro_narrative_client_surface.py
→ predictive/internal/leakage/citation/parity/meaning-drift checks
```

This path is an output-contract safety gate only and must not mutate the production report.

## Current strengths

- Pricing retrieval and report reconciliation are validated at artifact level.
- Pricing-lineage validation is a hard pre-send gate and passed in the recorded production baseline.
- Post-execution portfolio-state authority is explicit and validated.
- Runtime pipeline produces bilingual report artifacts from the same state/key figures.
- Dutch report generation is native and guard-only, not broad translated markdown.
- Portfolio state and valuation history are persisted after successful valuation/execution.
- Guarded model execution handles fully exited zero-share positions correctly.
- Pricing-basis disclosure derives required tickers dynamically from active Section 15 holdings.
- Challenger pricing/fundability discipline is active.
- Delivery manifest evidence is repo-visible and linked from the final run manifest for the recorded production baseline.
- Current Position Review score completeness is fixed for the latest inspected report-surface cycle.
- Stale GLD current-surface wording is fixed for the latest inspected report-surface cycle.
- Dutch delivery enum leakage for `No / under review` is fixed in the latest successful run #216 visual check.
- Shadow macro audit remains non-authoritative and non-blocking.
- Macro compliance validates methodology, planted failures, macro pack surface, and committed EN/NL macro report sections.
- WP1 deterministic macro narrative shadow comparison path is implemented as non-authoritative review evidence.
- WP2 macro narrative compliance and bilingual parity gate is implemented as an output-contract safety validator.
- Stage-1 thesis candidate validation writes repo-visible shadow evidence.
- Stage-2 thesis promotion discipline has a green contract-only validator and workflow.

## Current weaknesses / watch items

### 1. Delivery evidence proves SMTP send, not inbox receipt

The delivery manifest summary proves `smtplib.sendmail()` returned without raising and that per-language delivery manifests were written. It does not prove end-recipient inbox placement or user receipt.

### 2. Direct visual PDF inspection depends on renderable artifacts

The latest `_10` PDFs were visually inspected through user-uploaded report artifacts and the run #216 UI screenshot. For future visual inspections, use uploaded PDFs or a renderable Actions artifact/download path; the GitHub connector may expose binary files as base64 text resources rather than sandbox-renderable files.

### 3. Independent price verification is not yet upgraded

Rows can remain `fresh_exact_unverified` when one provider gives exact requested-date closes but no independent cross-provider verification has been recorded.

### 4. Macro/thesis promotion remains blocked despite stronger compliance and contract coverage

Macro/thesis controls are materially stronger, including methodology checks, planted-failure fixtures, macro pack surface validation, EN/NL macro-section validation, WP1 shadow narrative comparison, WP2 macro narrative client-surface/parity gate, Stage-1 thesis candidate shadow evidence, and a Stage-2 promotion contract. That still does not complete promotion. Expanded deterministic macro/thesis content still requires explicit promotion decisions, bilingual parity checks, authority review, and runtime integration before any client-facing or portfolio-authority use.

### 5. Dutch aliases remain partially distributed

Dutch terminology and validator aliases are more controlled, and the latest delivery enum leakage is fixed. However, some narrow runtime-state labels still live in delivery/scrub/startup layers. Further consolidation remains useful so one Dutch label change does not require patches across multiple files.

### 6. Direct challenger-vs-current-holding scoring is still a model enhancement

The system has challenger pricing and broad relative strength, but direct 1m/3m replacement-edge scoring versus each current holding remains a future improvement.

## Immediate priorities

### Priority A — preserve post-execution pricing-lineage and delivery-evidence regression guards

Going forward:

- do not weaken `tools/validate_etf_pricing_lineage_contract.py`
- keep runtime provenance and post-execution report authority separate
- keep manifest → audit → runtime → official portfolio state → reports → persisted state validation before send
- keep state and valuation history updates deterministic
- keep challenger fundability tied to valuation-grade pricing
- keep delivery summary redaction-safe
- keep workflow success, pricing-lineage success, SMTP-send evidence, and inbox receipt distinct

### Priority B — consolidate Dutch language/alias handling

Next cleanup:

- keep Dutch terminology and aliases in one source of truth
- reuse that source from native render, markdown validation, send-time parity checks, Dutch quality validation, and delivery HTML validation
- keep native Dutch guard-only; do not reintroduce broad English-to-Dutch scrub passes
- preserve the rule that delivery-surface localization for strict branded panels must happen at delivery runtime, not only markdown scrub time

### Priority C — macro/thesis roadmap remains shadow-first and promotion-gated

Current status:

- Phase 2 macro audit remains shadow-only.
- No-network macro-audit fixture replay is wired into CI and green.
- Deterministic regime/confidence output remains shadow-only and non-authoritative.
- WP1 deterministic macro narrative shadow candidate path is implemented and non-authoritative.
- WP2 macro narrative compliance and bilingual parity gate is implemented and non-authoritative.
- Macro-conflict cap methodology is documented as a stable shadow methodology rule.
- Macro compliance covers methodology, macro pack surface, planted failures, and latest committed EN/NL macro report sections.
- Stage-1 thesis candidate shadow evidence is green and repo-visible.
- Stage-2 thesis promotion discipline contract is green and contract-only.

Next architecture track:

- continue with WP3 macro promotion decision contract after its branch is refreshed/rebased and merged
- keep deterministic regime/confidence promotion review separate from client-surface wording validation
- do not promote macro axes, shadow regime payload, WP1 shadow narrative candidates, WP2-passing client-surface candidates, Stage-1 thesis candidates, Stage-2 promotion chains, lane scoring, fundability, or portfolio-action authority without explicit control-layer promotion
- continue only with shadow methodology, compliance, promotion-readiness contracts, and operational hardening unless a later decision changes authority

### Priority D — add direct challenger-vs-current-holding scoring

Next model enhancement:

- map challenger lanes to the holding they may replace
- compute direct 1m and 3m relative strength versus that holding
- feed direct replacement edge into lane scoring and replacement-duel notes

## Current status label

**ETF has a production-tested runtime-driven bilingual baseline with pricing-lineage proof and delivery-manifest evidence passed for run `20260604_190001`, plus a completed report-surface cleanup cycle verified after successful workflow run #216 on commit `ce86dce050a75c2b21481162ad3b6952ebbdb1e7`, WP1 deterministic macro narrative shadow-candidate comparison implemented as non-authoritative review evidence, and WP2 macro narrative compliance/bilingual parity implemented as a non-authoritative output-contract safety gate. The system distinguishes pre-execution runtime provenance, post-execution official portfolio-state authority, pricing-lineage validation, SMTP-send evidence, report-surface validation, macro narrative shadow comparison, client-surface compliance/parity validation, and inbox receipt. Current Position Review score completeness, stale GLD current-surface cleanup, and Dutch delivery enum leakage are fixed for the latest inspected `_10` English/Dutch reports. Delivery evidence remains SMTP-send/report-generation evidence only, not end-recipient inbox receipt. Macro-audit-derived regime axes, WP1 deterministic macro narrative candidates, WP2-passing candidate surfaces, Stage-1 thesis candidates, and Stage-2 promotion artifacts remain non-client-facing and non-authoritative for lane scoring, fundability, portfolio actions, and report recommendations until explicit promotion gates pass.**
