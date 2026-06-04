# ETF Review OS — Current State

## Snapshot date
2026-06-04

## What this repository currently is

`market-predictions/weekly-etf` is now a runtime-driven production-style weekly ETF review system with:

- explicit pricing audits in `output/pricing/`
- explicit run manifests in `output/run_manifests/`
- runtime report-state artifacts in `output/runtime/`
- persisted portfolio state and valuation history
- guarded model execution and trade-ledger idempotency checks
- English canonical and Dutch native companion report generation
- delivery HTML overrides for strict branded sections
- a hard pricing-lineage validator before send
- an approved, shadow-first macro/thesis roadmap
- no-network macro-audit fixture replay wired into the isolated macro-regime shadow workflow
- macro compliance validation covering methodology, planted failures, macro pack surface, and latest committed EN/NL report macro sections
- Stage-1 thesis candidate shadow validation evidence
- a green Stage-2 thesis promotion discipline contract, still contract-only and not promoted

The latest confirmed production validation run is:

```text
workflow: Send weekly ETF Pro report
run_number: 195
trigger_commit: e0a6f075127f1a079ca880accd26923928349f9c
run_id: 20260601_213417
requested_close_date: 2026-06-01
workflow_status: workflow_success
workflow_conclusion: success
pricing_lineage_status: passed
report_authority_source: portfolio_state_post_execution
english_report_path: output/weekly_analysis_pro_260601_04.md
dutch_report_path: output/weekly_analysis_pro_nl_260601_04.md
runtime_state_path: output/runtime/etf_report_state_20260601_20260601_213417.json
pricing_audit_path: output/pricing/price_audit_2026-06-01_20260601_213417.json
portfolio_state_path: output/etf_portfolio_state.json
total_portfolio_value_eur: 110290.91
```

Do **not** claim independent email delivery success from this status alone. The run produced report/PDF artifacts and a successful workflow conclusion, but `delivery_manifest_path` is `null` in the manifest. Delivery success still requires a delivery receipt/manifest or explicit user confirmation.

The latest confirmed isolated macro-regime shadow validation run is:

```text
workflow: Validate ETF macro regime shadow
run_number: 27
workflow_run_id: 26918418953
trigger_commit: 1c84de597cef54c17babb38389c0094cfc8e5c10
status: passed
validated_artifact: output/macro/validation/latest_macro_regime_shadow_validation.json
```

This proves that no-network macro-regime and macro-audit fixtures validate, that the shadow policy-pack builder consumes macro audit input, and that `deterministic_regime_shadow.macro_axes` is populated. It does **not** promote macro/regime output to client-facing, lane-scoring, fundability, or portfolio-action authority.

The latest confirmed isolated macro compliance validation run is:

```text
workflow: Validate ETF macro compliance
run_number: 15
trigger_commit: 28b6ddda28bd7f287bef7e0622ef8e9c70e726eb
status: passed
branch: main
duration: 18s
observed_at: 2026-06-04
source: user-provided GitHub Actions UI screenshot
```

The macro compliance workflow now validates:

```text
macro compliance self-test
macro conflict cap methodology
macro report surface self-test
current macro report surface if pack exists
latest committed English/Dutch report macro sections
safe macro fixture passes
combined blocked macro fixture fails as expected
shadow label leakage fixture fails as expected
orphan macro figure fixture fails as expected
```

This is a compliance/output-surface gate only. It does **not** promote deterministic macro/regime output to client-facing, lane-scoring, fundability, or portfolio-action authority.

The latest confirmed Stage-1 thesis candidate shadow validation run is:

```text
workflow: Validate ETF thesis candidates shadow
run_number: 2
workflow_run_id: 26969716983
trigger_commit: b0579f1f30134b4fdd1b277025867e9db87961da
status: passed
validated_artifact: output/macro/validation/latest_thesis_candidates_validation.json
active_driver_count: 9
candidate_count: 29
observed_at: 2026-06-04
source: user-provided GitHub Actions UI screenshot and repo-visible evidence file
```

This proves the Stage-1 thesis candidate builder and fixtures validate and that repo-visible evidence is written. It does **not** make any candidate client-facing, fundable, lane-scoring-authoritative, or actionable.

The latest confirmed Stage-2 thesis promotion contract validation run is:

```text
workflow: Validate ETF stage 2 thesis promotion contract
run_number: 1
trigger_commit: 09c175276a243593908660332a101778845dbc9f
status: passed
branch: main
duration: 12s
observed_at: 2026-06-04
source: user-provided GitHub Actions UI screenshot
```

This proves the promotion-readiness contract and fixtures validate. It is still contract-only. It does **not** promote thesis candidates into production runtime behavior, lane scoring, fundability, report wording, recommendations, or portfolio actions.

## Four-layer operating status

### 1. Decision framework

The current decision framework remains:

- capital re-underwriting discipline from `control/CAPITAL_REUNDERWRITING_RULES.md`
- broad lane discovery from `control/LANE_DISCOVERY_CONTRACT.md`
- valuation-grade challenger discipline
- guarded model execution with trade-ledger idempotency
- no indefinite `Hold but replaceable` inertia
- macro/thesis modernization approved only as a future phased enhancement
- deterministic macro/regime classification remains shadow-only until later promotion gates pass
- Stage-1 thesis candidates remain internal-only shadow artifacts
- Stage-2 thesis promotion discipline is a contract gate only, not production authority
- macro compliance gates may validate wording/surface safety, but they do not grant decision authority by themselves

Post-execution authority is now explicit:

```text
runtime state = pre-execution pricing/report-state provenance
official portfolio state = post-execution active holdings after guarded execution
client report Section 7 / Section 15 = post-execution official portfolio state when execution occurred in the same run
```

### 2. Input/state contract

Current authoritative state inputs are:

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

Shadow-only macro/regime validation evidence is recorded at:

- `output/macro/validation/latest_macro_regime_shadow_validation.json`
- `output/macro/validation/latest_macro_audit_axis_shadow_validation.json`
- `output/macro/validation/latest_macro_regime_shadow_comparison.json`

Stage-1 thesis candidate shadow validation evidence is recorded at:

- `output/macro/validation/latest_thesis_candidates_validation.json`
- `control/THESIS_CANDIDATES_SHADOW_STATUS_20260604.md`

Stage-2 thesis promotion contract status is recorded at:

- `control/STAGE2_THESIS_PROMOTION_CONTRACT.md`
- `control/STAGE2_THESIS_PROMOTION_CONTRACT_STATUS_20260604.md`
- `tools/validate_stage2_thesis_promotion_contract.py`
- `.github/workflows/validate-stage2-thesis-promotion-contract.yml`
- `fixtures/thesis_promotion/**`

Macro compliance/methodology status is recorded at:

- `control/MACRO_CONFLICT_CAP_METHODOLOGY.md`
- `control/MACRO_CONFLICT_CAP_STATUS_20260604.md`
- `.github/workflows/validate-macro-compliance.yml`
- `tools/validate_macro_compliance.py`

These validation evidence files and control files are review/audit artifacts only. They are not production report, lane-scoring, fundability, or portfolio-action inputs.

The latest confirmed production run proves the chain:

```text
pricing audit
→ runtime state
→ guarded model execution
→ post-execution portfolio state
→ EN/NL report artifacts
→ valuation history
→ run manifest
→ delivery HTML/PDF validation
→ pricing-lineage validator using post-execution report authority
```

The latest isolated macro shadow run proves the separate chain:

```text
macro-regime fixture replay
→ macro-data-audit fixture validation
→ shadow macro policy-pack build with fixture input
→ deterministic_regime_shadow.macro_axes assertion
→ macro-regime shadow payload validation
→ repo-visible validation evidence
```

The latest isolated macro compliance run proves the separate output-surface safety chain:

```text
macro compliance self-test
→ macro conflict cap methodology validation
→ macro report surface self-test
→ macro pack surface validation when output/macro/latest.json exists
→ latest committed EN/NL report macro-section validation
→ safe fixture pass
→ planted failure fixtures fail as expected
```

The latest isolated thesis candidate shadow run proves the separate internal-candidate chain:

```text
Stage-1 driver catalog and beneficiary map validation
→ thesis candidate fixture replay
→ current shadow thesis candidate artifact build
→ thesis candidate validation evidence
→ repo-visible evidence under output/macro/validation/
```

The latest isolated Stage-2 contract run proves the separate promotion-readiness contract chain:

```text
contract text validation
→ safe ready-for-review-not-promoted fixture passes
→ illegally promoted fixture fails as expected
```

### 3. Output contract

The report output contract is now:

- English is the canonical analytical report.
- Dutch is a native companion render from the same runtime state/key figures, not a broad translation of the English markdown and not a second research pass.
- Native Dutch localization/scrub layers are guard-only except for narrow structured runtime-state display-label normalization.
- Section 7 equity curve and Section 15 holdings reconcile to the post-execution official portfolio state when guarded execution occurred in the same run.
- Pricing-basis disclosure dynamically derives required rows from current active holdings, not stale hardcoded ticker sets.
- Pricing-basis disclosure must show requested close, close date used, source, status, and close used for all active holdings.
- Strict branded sections are rendered from runtime state at delivery HTML level, not fixed through markdown-only patches.
- Dutch PDF chart labels are generated in Dutch in the runtime delivery path.
- Client-facing reports must not leak internal plumbing labels.
- Macro-audit-derived `macro_axes`, `macro_axis_scores`, and `deterministic_regime_shadow` must not appear in client-facing reports until future methodology, compliance, bilingual gates, and explicit promotion gates approve them.
- Stage-1 thesis candidates and Stage-2 promotion-chain artifacts must not appear in client-facing reports until explicit promotion gates approve them.
- The isolated macro compliance workflow validates the actual committed EN/NL macro-sensitive report sections, but only as a surface-safety check.

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
→ final manifest update
```

The isolated macro-regime shadow validation path is:

```text
workflow_dispatch or qualifying push
→ replay deterministic regime fixtures
→ replay no-network macro-data-audit fixture through shadow regime stack
→ validate macro policy pack schema
→ validate deterministic_regime_shadow payload and macro_axes presence
→ write macro-regime shadow validation evidence
→ commit evidence under output/macro/validation/
```

The isolated macro compliance validation path is:

```text
workflow_dispatch or qualifying push
→ run macro compliance self-test
→ validate macro conflict cap methodology
→ run macro report surface self-test
→ validate current macro report surface if output/macro/latest.json exists
→ validate latest committed EN/NL report macro sections
→ validate safe macro fixture
→ validate planted failure fixtures with --expect-fail
```

The isolated thesis candidate shadow validation path is:

```text
workflow_dispatch or qualifying push
→ validate Stage-1 thesis candidate fixtures
→ build current shadow thesis candidate artifact
→ write thesis candidate validation evidence
→ commit thesis candidate validation evidence under output/macro/validation/
```

The isolated Stage-2 thesis promotion contract validation path is:

```text
workflow_dispatch or qualifying push
→ validate Stage-2 contract text
→ validate ready-for-review-not-promoted fixture
→ validate illegally promoted fixture fails
```

## Current strengths

- Pricing retrieval and report reconciliation are validated at artifact level.
- Pricing-lineage validation is a hard pre-send gate and passed in a fresh run.
- Post-execution portfolio-state authority is explicit and validated.
- Runtime pipeline produces bilingual report artifacts from the same state/key figures.
- Dutch report generation is native and guard-only, not broad translated markdown.
- Portfolio state and valuation history are persisted after successful valuation/execution.
- Guarded model execution handles fully exited zero-share positions correctly.
- Pricing-basis disclosure derives required tickers dynamically from active Section 15 holdings.
- Challenger pricing/fundability discipline is active.
- Shadow macro audit remains non-authoritative and non-blocking.
- No-network macro-audit fixture replay is wired into the isolated macro-regime shadow workflow and has passed with repo-visible evidence.
- Macro compliance now validates methodology, planted failures, macro pack surface, and latest committed EN/NL macro report sections.
- Stage-1 thesis candidate validation now writes repo-visible shadow evidence.
- Stage-2 thesis promotion discipline now has a green contract-only validator and workflow.

## Current weaknesses / watch items

### 1. Delivery evidence is still separate from workflow success

A successful workflow and generated PDF artifacts are not the same as a delivery receipt. Do not claim delivery unless a delivery manifest/receipt exists or the user confirms receipt.

### 2. Direct visual PDF inspection still needs a renderable artifact

The repo contains generated PDFs/assets, but the GitHub connector exposes binary files as base64 text resources rather than sandbox-renderable files. Visual inspection should use either user-uploaded PDFs or an Actions artifact/download path that can be rendered.

### 3. Independent price verification is not yet upgraded

Rows can remain `fresh_exact_unverified` when one provider gives exact requested-date closes but no independent cross-provider verification has been recorded.

### 4. Macro/thesis promotion remains blocked despite stronger compliance and contract coverage

Macro/thesis controls are materially stronger, including methodology checks, planted-failure fixtures, macro pack surface validation, latest committed EN/NL macro-section validation, Stage-1 thesis candidate shadow evidence, and a Stage-2 promotion contract. That still does not complete promotion. Expanded deterministic macro/thesis content still requires explicit promotion decisions, bilingual parity checks, authority review, and runtime integration before any client-facing or portfolio-authority use.

### 5. Dutch aliases remain partially distributed

Dutch terminology and validator aliases are more controlled, but some narrow runtime-state labels still live in delivery/scrub layers. Further consolidation remains useful.

### 6. Direct challenger-vs-current-holding scoring is still a model enhancement

The system has challenger pricing and broad relative strength, but direct 1m/3m replacement-edge scoring versus each current holding remains a future improvement.

## Immediate priorities

### Priority A — preserve post-execution pricing-lineage regression guard

Going forward:

- do not weaken `tools/validate_etf_pricing_lineage_contract.py`
- keep runtime provenance and post-execution report authority separate
- keep manifest → audit → runtime → official portfolio state → reports → persisted state validation before send
- keep state and valuation history updates deterministic
- keep challenger fundability tied to valuation-grade pricing

### Priority B — add delivery receipt/manifest evidence

Next operational hardening:

- write a delivery receipt/manifest when delivery actually completes
- keep workflow success separate from delivery success

### Priority C — consolidate Dutch language/alias handling

Next cleanup:

- keep Dutch terminology and aliases in one source of truth
- reuse that source from native render, markdown validation, send-time parity checks, Dutch quality validation, and delivery HTML validation
- keep native Dutch guard-only; do not reintroduce broad English-to-Dutch scrub passes

### Priority D — macro/thesis roadmap remains shadow-first and promotion-gated

Current status:

- Phase 2 macro audit remains shadow-only.
- No-network macro-audit fixture replay is wired into CI and green.
- Deterministic regime/confidence output remains shadow-only and non-authoritative.
- Macro-conflict cap methodology is documented as a stable shadow methodology rule.
- Macro compliance covers methodology, macro pack surface, planted failures, and latest committed EN/NL macro report sections.
- Stage-1 thesis candidate shadow evidence is green and repo-visible.
- Stage-2 thesis promotion discipline contract is green and contract-only.

Next architecture track:

- keep deterministic regime/confidence promotion review separate from client-surface wording validation
- do not promote macro axes, shadow regime payload, Stage-1 thesis candidates, Stage-2 promotion chains, lane scoring, fundability, or portfolio-action authority without explicit control-layer promotion
- continue only with shadow methodology, compliance, promotion-readiness contracts, and operational hardening unless a later decision changes authority

### Priority E — add direct challenger-vs-current-holding scoring

Next model enhancement:

- map challenger lanes to the holding they may replace
- compute direct 1m and 3m relative strength versus that holding
- feed direct replacement edge into lane scoring and replacement-duel notes

## Current status label

**ETF has a production-tested runtime-driven bilingual baseline with pricing-lineage proof passed for run `20260601_213417`. The system now distinguishes pre-execution runtime provenance from post-execution official portfolio-state authority. Dutch output is native/guard-only rather than broad-translated markdown. Pricing lineage, guarded execution, Dutch quality, and HTML/PDF render validation are green. Email delivery still requires a separate receipt/manifest or user confirmation. Macro-audit-derived regime axes are validated in isolated shadow CI, macro compliance validates methodology, planted failures, macro pack surface, and latest committed EN/NL macro report sections, Stage-1 thesis candidate shadow evidence is repo-visible and green, and the Stage-2 thesis promotion contract is green but contract-only. Deterministic macro/regime/thesis outputs remain non-client-facing and non-authoritative for lane scoring, fundability, portfolio actions, and report recommendations until explicit promotion gates pass.**
