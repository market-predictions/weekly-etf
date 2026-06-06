# ETF Review OS — Current State

## Snapshot date
2026-06-06

## Repository

```text
market-predictions/weekly-etf
```

## Current status label

**ETF has a latest fully recorded runtime-driven bilingual baseline with pricing-lineage proof and delivery-manifest evidence for workflow run #216 / run `20260605_081216`, a completed report-surface cleanup cycle verified by the same run, WP1 deterministic macro narrative shadow comparison implemented, WP2 macro narrative compliance/bilingual parity implemented, WP3 macro promotion decision contract merged, and WP4 Dutch/bilingual alias consolidation started with a focused regression guard. Deterministic macro regime remains shadow-only and not promoted into production report narrative authority, lane scoring, fundability, portfolio action, funding authority, portfolio mutation, or delivery authority.**

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
- WP1, WP2 and WP3 deterministic macro regime promotion-preparation gates implemented, while production authority remains blocked
- WP4 Dutch terminology consolidation started with a regression guard; full alias consolidation remains open

## Latest production and report-surface evidence

### Latest fully recorded pricing-lineage + delivery-manifest baseline

```text
workflow: Send weekly ETF Pro report
run_number: 216
trigger_commit: ce86dce050a75c2b21481162ad3b6952ebbdb1e7
run_id: 20260605_081216
requested_close_date: 2026-06-04
workflow_status: workflow_success
workflow_conclusion: success
pricing_lineage_status: passed
report_authority_source: runtime_state
english_report_path: output/weekly_analysis_pro_260604_10.md
dutch_report_path: output/weekly_analysis_pro_nl_260604_10.md
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-04_20260605_081216.json
final_run_manifest_path: output/run_manifests/weekly_etf_run_manifest_2026-06-04_20260605_081216.json
total_portfolio_value_eur: 111105.47
```

This proves workflow success, pricing-lineage success, final run-manifest linkage to the redaction-safe delivery manifest, and repo-visible SMTP-send evidence for that baseline. It is **not** an end-recipient inbox receipt.

### Previous fully recorded production validation baseline

```text
workflow: Send weekly ETF Pro report
run_number: 205
trigger_commit: 3bd07f7ff31af77adbd23359d66a8c5ab7ab3343
run_id: 20260604_190001
requested_close_date: 2026-06-03
workflow_status: workflow_success
workflow_conclusion: success
pricing_lineage_status: passed
report_authority_source: portfolio_state_post_execution
english_report_path: output/weekly_analysis_pro_260603.md
dutch_report_path: output/weekly_analysis_pro_nl_260603.md
delivery_manifest_path: output/delivery/weekly_etf_delivery_manifest_2026-06-03_20260604_190001.json
total_portfolio_value_eur: 111596.96
```

This remains a valid earlier production validation baseline and repo-visible SMTP-send evidence. It is **not** an end-recipient inbox receipt.

### Report-surface cleanup evidence in run #216

```text
workflow: Send weekly ETF Pro report
run_number: 216
trigger_commit: ce86dce050a75c2b21481162ad3b6952ebbdb1e7
workflow_conclusion: success
english_pdf: weekly_analysis_pro_260604_10.pdf
dutch_pdf: weekly_analysis_pro_nl_260604_10.pdf
```

Closed issues:

```text
Current Position Review score completeness: fixed
English/Dutch active-position score completeness: fixed
stale GLD current-surface wording: fixed
Dutch delivery enum leakage `No / under review`: fixed
unwanted `Nee / onder herbeoordeling` surface wording: removed from final report view
```

This cleanup evidence is now reconciled with matching delivery and final run manifests, so run #216 is evidence type B: full pricing-lineage + delivery-manifest baseline. It remains **not** inbox-receipt evidence.

## Macro roadmap implementation status

### WP1 — Deterministic macro narrative shadow candidate

```text
status: completed as shadow-only comparison path
files:
  runtime/render_macro_regime_shadow_narrative.py
  tools/validate_macro_regime_shadow_narrative.py
  tests/test_macro_regime_shadow_narrative.py
  output/macro/shadow_narrative/macro_regime_shadow_narrative_20260605_000000.json
reported focused test: python -m pytest tests/test_macro_regime_shadow_narrative.py -q = 4 passed
reported artifact validation: MACRO_REGIME_SHADOW_NARRATIVE_OK
```

Authority boundaries:

```text
client_facing=false
production_report=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
no production report mutation
```

### WP2 — Macro narrative compliance and bilingual parity gate

```text
status: completed on main as output-contract validator/test/fixture package
files:
  tools/validate_macro_narrative_client_surface.py
  fixtures/macro_narrative/safe_shadow_candidate_en_nl.json
  fixtures/macro_narrative/bad_predictive_language.json
  fixtures/macro_narrative/bad_shadow_label_leakage.json
  fixtures/macro_narrative/bad_dutch_parity.json
  tests/test_macro_narrative_client_surface.py
reported focused test: python -m pytest tests/test_macro_narrative_client_surface.py -q = 4 passed
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

Authority boundaries:

```text
output_contract_gate_only=true
production_report_authority=false
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
delivery_authority=false
```

### WP3 — Macro promotion decision contract

```text
status: completed / merged
PR: #51 — WP3: Add macro promotion decision contract
merge_commit: 7b7fe1db0b04dd3b1d377463ad59e06927037993
files:
  control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
  tools/validate_macro_regime_promotion_contract.py
  fixtures/macro_promotion/not_promoted_valid.json
  fixtures/macro_promotion/bad_promoted_without_approval.json
  tests/test_macro_regime_promotion_contract.py
reported focused test from staged harness: python -m pytest tests/test_macro_regime_promotion_contract.py -q = 5 passed
```

WP3 defines the promotion gate required before deterministic macro regime output may move from shadow-only evidence to report narrative authority.

Required promotion gates:

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

Permanent authority boundaries remain false even after narrative promotion unless a separate future contract grants them:

```text
portfolio_action_authority=false
lane_scoring_authority=false
fundability_authority=false
funding_authority=false
portfolio_mutation=false
```

## Dutch / bilingual output-contract status

### WP4 — Dutch / bilingual alias consolidation

```text
status: partially implemented / regression guard added
commit: 25dbd2c12167b20c771e3a98188f4f0125470421
file added:
  tests/test_dutch_terminology_contract.py
validation status: broader validation not yet run in this environment
```

The WP4 regression test protects the current Dutch terminology contract for:

```text
No / under review → Nee / onder herbeoordeling
Smaller / under review → Kleiner / onder herbeoordeling
Hold but replaceable → Aanhouden, maar vervangbaar
```

It also checks that:

```text
runtime.nl_terminology remains the shared source for required markers and forbidden client labels
native Dutch scrub stays guard-only / narrow-alias based
sitecustomize.py does not own client-facing Dutch enum/status aliases
```

Full WP4 consolidation is still pending. Known remaining spread-out alias/migration surfaces include:

```text
runtime/nl_localization.py
runtime/apply_nl_localization.py
runtime/scrub_nl_client_language.py
runtime/delivery_html_overrides.py
runtime/client_facing_sanitizer.py
```

Expected validation for the follow-up pass:

```bash
python tools/validate_etf_dutch_language_quality.py
python tools/validate_etf_delivery_html_contract.py
python -m pytest tests/test_dutch_terminology_contract.py -q
```

Authority boundaries preserved:

```text
portfolio_state_unchanged=true
pricing_unchanged=true
lane_scoring_unchanged=true
fundability_unchanged=true
deterministic_macro_promotion_unchanged=true
production_delivery_authority_unchanged=true
inbox_receipt_claims_unchanged=true
```

## Four-layer operating status

### 1. Decision framework

- Capital re-underwriting discipline remains active.
- Broad lane discovery remains active.
- Valuation-grade challenger discipline remains active.
- Guarded model execution with trade-ledger idempotency remains active.
- Deterministic macro regime, macro axes, WP1 candidate narrative, WP2-passing surfaces, and WP3 promotion artifacts remain non-client-facing and non-authoritative unless explicit future promotion gates pass.
- Green compliance/validator status never equals production promotion by itself.

### 2. Input/state contract

Authoritative production inputs remain:

```text
output/pricing/price_audit_<requested_close_date>_<run_id>.json
output/run_manifests/weekly_etf_run_manifest_<requested_close_date>_<run_id>.json
output/runtime/etf_report_state_<report_token>_<run_id>.json
output/runtime/etf_model_execution_<date>_<run_id>.json
output/etf_portfolio_state.json
output/etf_valuation_history.csv
output/etf_trade_ledger.csv
output/etf_recommendation_scorecard.csv
output/lane_reviews/etf_lane_assessment_<report_token>.json
output/market_history/etf_relative_strength.json
output/macro/latest.json
```

Macro promotion-preparation artifacts are review/audit/control artifacts only:

```text
output/macro/shadow_narrative/macro_regime_shadow_narrative_<run_id>.json
fixtures/macro_narrative/*.json
fixtures/macro_promotion/*.json
control/DETERMINISTIC_MACRO_REGIME_PROMOTION_CONTRACT.md
```

### 3. Output contract

- English is the canonical analytical report.
- Dutch is a native companion render from the same runtime state/key figures.
- Strict branded sections are rendered from runtime state at delivery HTML level.
- Current Position Review / Review huidige posities must show numeric scores for every active ETF position.
- Dutch delivery-surface enum localization must be enforced at delivery runtime, not only markdown scrub time.
- Exited-holding wording, especially stale GLD current-surface wording when GLD is not active, must be blocked.
- WP4 regression guard protects known Dutch enum/localization regressions, but full alias consolidation remains open.
- WP1 deterministic macro narrative candidates must not appear in client-facing reports until WP2 and WP3 gates plus explicit future promotion pass.
- WP2 validates wording/parity safety only.
- WP3 defines the decision contract for narrative authority only; it does not grant portfolio, lane, fundability, funding, mutation or delivery authority.

### 4. Operational runbook

The production path remains:

```text
run-queue request or manual dispatch
→ resolve run identity
→ persistent ETF pricing pass
→ historical relative-strength fetch
→ macro policy pack build, with macro audit shadow-only / non-blocking
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

Strict branded/PDF-visible defects must be fixed in the generating layer:

```text
runtime state defect → fix runtime state builder
markdown-only defect → fix native renderer / polish / linkifier
strict branded panel defect → fix delivery HTML overrides
send-time enum/localization defect → fix delivery runtime / shared localization map
validator gap → add or tighten relevant pre-send gate
```

## Immediate priorities

### Priority A — preserve pricing-lineage and delivery-evidence discipline

Do not weaken pricing lineage, manifest, official portfolio-state, or delivery-evidence boundaries. Delivery evidence remains SMTP-send/report-generation evidence unless a real receipt exists.

### Priority B — complete Dutch alias consolidation

The regression guard is in place. The remaining cleanup is to move repeated/migration aliases into one shared source so native render, markdown validation, Dutch quality validation, delivery HTML validation, and delivery runtime all use the same terminology contract.

### Priority C — macro roadmap remains shadow-first and promotion-gated

WP1, WP2 and WP3 are now complete. Deterministic macro regime still remains shadow-only. The next macro step may be a controlled client-surface pilot only if it remains non-portfolio-authoritative and explicitly respects WP2/WP3.

### Priority D — direct challenger-vs-current-holding scoring

Add diagnostic replacement-edge scoring as a future model enhancement:

```text
map challenger lanes to current holdings
compute direct 1m/3m relative strength edge
include drawdown/volatility edge
feed diagnostic result into replacement-duel notes
```
