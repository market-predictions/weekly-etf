# Weekly ETF cockpit side-by-side review

token: `260714`
report_date: `2026-07-14`
schema_version: `cockpit_side_by_side_review_v2`
review_type: `evidence_based_side_by_side_preview_only`
promotion_status: `not_promoted`

This review compares the selected current classic report with the current cockpit preview using runtime state and artifact content.

## Review conclusion

`ready_for_promotion_decision`

## Blocking findings

- none

## Selected sources

- **Classic EN markdown:** `output/weekly_analysis_pro_260714_04.md`
- **Classic EN HTML:** `output/weekly_analysis_pro_260714_04_delivery.html`
- **Classic NL markdown:** `output/weekly_analysis_pro_nl_260714_04.md`
- **Classic NL HTML:** `output/weekly_analysis_pro_nl_260714_04_delivery.html`
- **Cockpit EN:** `output/cockpit_preview/weekly_analysis_pro_cockpit_260714_01.html`
- **Cockpit NL:** `output/cockpit_preview/weekly_analysis_pro_nl_cockpit_260714_01.html`
- **Runtime state:** `output/runtime/etf_report_state_20260714_20260715_175910_executed.json`

## Evidence-based findings

### `readability` — PASS

- **Classic report:** The selected classic report contains 41,286 review characters and preserves full context.
- **Cockpit:** The cockpit contains 6,079 review characters and is faster to scan.
- **Evidence:** `classic_en_chars=41286`; `cockpit_en_chars=6079`
- **Required fix:** Keep the cockpit concise while retaining the selected classic report as the evidence layer.

### `density` — PASS

- **Classic report:** The classic report is intentionally information-dense.
- **Cockpit:** Cockpit-to-classic text ratio is 0.15.
- **Evidence:** `density_ratio=0.1472`
- **Required fix:** Preserve the lower-density front-page role; do not move audit tables into the cockpit.

### `visual_hierarchy` — PASS

- **Classic report:** The classic report remains report-led and section-dense.
- **Cockpit:** The cockpit uses a masthead, decision cards, performance metrics and a separate discipline block.
- **Evidence:** `data-cockpit-front-page`; `class="card"`; `class="metrics"`; `class="discipline"`
- **Required fix:** Preserve the existing cockpit hierarchy.

### `decision_clarity` — PASS

- **Classic report:** The classic decision cockpit includes the executed action and an explicit next-action trigger: True.
- **Cockpit:** The cockpit decision surface is aligned with the classic report.
- **Evidence:** `action_present=True`; `classic_trigger=True`; `cockpit_trigger=True`; `summary_contradiction=False`
- **Required fix:** No change required.

### `executed_action_clarity` — PASS

- **Classic report:** The classic report names the guarded URNM-to-XBI rotation and the consumed rotation budget.
- **Cockpit:** The cockpit names each executed direction and shows the pre/post weights.
- **Evidence:** `URNM reduced`; `XBI added`; `URNM 7.0% → 2.0%`; `XBI 0.0% → 5.0%`; `URNM afgebouwd`; `XBI toegevoegd`; `URNM 7,0% → 2,0%`; `XBI 0,0% → 5,0%`
- **Required fix:** Keep the runtime-derived bilingual action contract.

### `current_weight_accuracy` — PASS

- **Classic report:** The classic report and runtime state identify SMH as the largest position and preserve current post-execution weights.
- **Cockpit:** The cockpit shows SMH at 28.1% and the current executed transitions.
- **Evidence:** `SMH`; `28.1%`; `URNM 7.0% → 2.0%`; `XBI 0.0% → 5.0%`
- **Required fix:** Continue using current-over-previous authority precedence.

### `performance_risk_accuracy` — PASS

- **Classic report:** The classic report records NAV 110224.86 EUR and since-inception return 10.22%.
- **Cockpit:** The cockpit displays €110,225 and +10.2% with the current largest-position risk.
- **Evidence:** `€110,225`; `+10.2%`; `€110.225`; `+10,2%`
- **Required fix:** Keep NAV and return derived from runtime state plus valuation history.

### `trust_provenance_clarity` — PASS

- **Classic report:** The classic report keeps the full pricing, holdings and audit context.
- **Cockpit:** The WP07 provenance strip now exposes runtime state, pricing audit, run manifest, no-delivery and no-promotion status.
- **Evidence:** `output/runtime/etf_report_state_20260714_20260715_175910_executed.json`; `output/pricing/price_audit_2026-07-14_20260715_175910.json`; `output/run_manifests/weekly_etf_run_manifest_2026-07-14_20260715_175910.json`; `No delivery claim`; `Not promoted to production`; `nl_delivery_status=True`; `nl_promotion_status=True`
- **Required fix:** Treat the WP07 provenance requirement as closed; preserve the visible evidence strip.

### `bilingual_semantic_parity` — PASS

- **Classic report:** The English and Dutch classic reports are companion surfaces from the same report state.
- **Cockpit:** English and Dutch cockpit surfaces are semantically parallel.
- **Evidence:** `core_parity=True`; `dutch_punctuation_bug=False`; `hybrid_labels=none`
- **Required fix:** No change required.

### `premium_look_and_feel` — PASS

- **Classic report:** The classic report is client-grade but text-heavy.
- **Cockpit:** The cockpit presents a coherent premium entry surface.
- **Evidence:** `hierarchy_pass=True`; `readability_pass=True`; `parity_status=pass`
- **Required fix:** No change required.

### `audit_evidence_preservation` — PASS

- **Classic report:** The selected current classic markdown remains the complete audit and rationale layer.
- **Cockpit:** The cockpit is additive, references the authority artifacts and does not replace the classic report.
- **Evidence:** `output/weekly_analysis_pro_260714_04.md`; `output/weekly_analysis_pro_nl_260714_04.md`; `output/runtime/etf_report_state_20260714_20260715_175910_executed.json`
- **Required fix:** Preserve the classic report and current provenance references.

## Next package

`WP_COCKPIT_SURFACE_PROMOTION_DECISION_REVIEW`

This review promotes and sends nothing.
