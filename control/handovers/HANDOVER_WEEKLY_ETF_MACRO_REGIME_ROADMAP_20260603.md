# Handover — Weekly ETF macro/regime roadmap and next development steps

## Snapshot date

2026-06-03

## Repository

```text
market-predictions/weekly-etf
```

## Fresh-chat prompt

Use this prompt to continue in a new chat:

```text
Continue in market-predictions/weekly-etf.

Start by reading, in this order:
1. control/SYSTEM_INDEX.md
2. control/CURRENT_STATE.md
3. control/NEXT_ACTIONS.md
4. control/MACRO_REPORT_SURFACE_STATUS.md
5. control/MACRO_POLICY_PACK_CONTRACT_STATUS.md
6. control/MACRO_REGIME_SHADOW_COMPARISON_STATUS.md
7. control/handovers/HANDOVER_WEEKLY_ETF_MACRO_REGIME_ROADMAP_20260603.md

Current stage: macro/regime integration is client-surfaced only through the safe report surface. Macro policy pack authority and promotion contract are validated. Legacy-vs-shadow regime comparison evidence is validated. The latest work added split shadow comparison flags (`regime_label_differs`, `confidence_differs`, `confidence_delta`, `confidence_diff_threshold`) but this split-flag change still needs the `Validate ETF macro regime shadow` workflow to be confirmed green.

Do not promote deterministic_regime_shadow, macro_axes, macro_axis_scores, Stage-1 thesis candidates, or active_drivers to client-facing, lane-scoring, fundability, or portfolio-action authority. Continue with shadow-only confidence/threshold calibration review.
```

## Core operating rule for the next chat

Keep the four layers separate:

1. **Decision framework** — what portfolio/recommendation decisions the ETF report is allowed to make.
2. **Input/state contract** — which artifacts are authoritative inputs and which are shadow-only evidence.
3. **Output contract** — what may appear in the English/Dutch client reports and under what validators.
4. **Operational runbook** — GitHub Actions, validators, run manifests, workflows, and evidence files.

Do not collapse these into one giant prompt. Do not change portfolio decision authority while working on shadow macro/regime code.

---

# 1. Current state summary

## Production ETF report baseline

The production Weekly ETF system is runtime-driven and bilingual:

```text
pricing audit
→ relative-strength fetch
→ macro policy pack
→ lane discovery
→ challenger pricing
→ final lane discovery
→ fundability validation
→ rotation plan
→ runtime report state
→ EN/NL markdown reports
→ pricing-basis disclosure
→ polish/localization/linking
→ run manifest
→ persisted valuation state
→ guarded model execution
→ post-execution official portfolio state
→ HTML/PDF validation
→ pricing-lineage pre-send gate
→ send workflow
→ final manifest
```

Important delivery boundary:

```text
workflow_success != independent recipient receipt
```

Delivery receipt work was explicitly paused by the user. Do not claim email recipient receipt until a real delivery manifest/receipt or explicit user confirmation exists.

## Latest production macro/report evidence

The macro report surface and Dutch cleanup were production-validated.

Latest relevant production run evidence:

```text
workflow: Send weekly ETF Pro report
run: #203
trigger_commit: ec41e31aa9a3ebf12258c7e3ea76203c95c4ee06
run_id: 20260603_175012
requested_close_date: 2026-06-02
workflow_status: workflow_success
workflow_conclusion: success
pricing_lineage_status: passed
english_report_path: output/weekly_analysis_pro_260602_06.md
dutch_report_path: output/weekly_analysis_pro_nl_260602_06.md
total_portfolio_value_eur: 112376.10
```

This closed the macro report surface and Dutch client-language cleanup package for this stage.

## Macro report surface status

Closed for this stage.

Key files:

```text
runtime/macro_report_surface.py
tools/validate_macro_report_surface.py
runtime/macro_report_pre_send_guard.py
send_report_runtime_html.py
runtime/scrub_nl_client_language.py
.github/workflows/validate-macro-report-output.yml
.github/workflows/validate-macro-compliance.yml
control/MACRO_REPORT_SURFACE_STATUS.md
```

What was achieved:

- English report now receives macro/geopolitical/regime content through a client-safe surface.
- Dutch report receives native macro/geopolitical/regime content through the same state source.
- Raw shadow fields are not client-surfaced.
- Pre-send guard blocks macro/thesis leakage before SMTP delivery path.
- Dutch phrase `Healthcare quality and defensive growth` was fixed to `Healthcarekwaliteit en defensieve groei` and made forbidden after scrub.

## Macro policy pack contract status

Closed for this stage.

Key files:

```text
schemas/macro_policy_pack.schema.json
runtime/build_macro_policy_pack.py
tools/validate_macro_policy_pack.py
MACRO_METHODOLOGY.md
.github/workflows/validate-macro-policy-pack-contract.yml
control/MACRO_POLICY_PACK_CONTRACT_STATUS.md
```

Validated workflow evidence:

```text
workflow: Validate ETF macro policy pack contract
run: #2
trigger_commit: 359ee240f3484d5240bc49773566080f55782d68
status: passed
duration: 1m 47s
```

What was achieved:

- Macro policy pack now emits field-level authority metadata.
- `field_authority` and `promotion_gates` are required.
- Validator blocks accidental client-surface promotion of shadow fields.
- `deterministic_regime_shadow`, `macro_axes`, `macro_axis_scores`, and `active_drivers` remain blocked from client surface and production decisions.

## Macro regime shadow comparison status

Closed for the legacy-vs-shadow comparison evidence stage.

Key files:

```text
macro_regime/classify.py
macro_regime/confidence.py
runtime/build_macro_policy_pack_shadow.py
tools/validate_macro_regime_shadow.py
tools/write_macro_regime_shadow_comparison_evidence.py
.github/workflows/validate-macro-regime-shadow.yml
output/macro/validation/latest_macro_regime_shadow_comparison.json
control/MACRO_REGIME_SHADOW_COMPARISON_STATUS.md
```

Validated workflow evidence:

```text
workflow: Validate ETF macro regime shadow
run: #15
trigger_commit: 318135659b6039c9b861732f352c3d903815c775
status: passed
duration: 27s
```

Latest validated comparison before split-flag change:

```text
legacy_regime: Risk-on narrow leadership
legacy_confidence: 0.72
legacy_confidence_source: legacy_proxy_static
shadow_candidate_regime: Risk-on narrow leadership
shadow_candidate_confidence: 0.80
confidence_delta: +0.08
differs_from_legacy: true
```

Important nuance:

The label was the same, but the old combined flag `differs_from_legacy` was true because the confidence differed by at least 0.05.

---

# 2. Latest unvalidated code change to verify first

The latest work before this handover split the old combined difference flag into explicit flags.

Updated files:

```text
macro_regime/classify.py
tools/validate_macro_regime_shadow.py
tools/write_macro_regime_shadow_comparison_evidence.py
```

Commits:

```text
249633e67cf75f29ba51c7efe9c70a4ebf4392b9  split shadow regime legacy difference flags
0a9a05577e001dfea6a2e794fd9915ce52614634  validate split shadow regime difference flags
1255984ff656a58e0581fbb5553ef3684506e964  record split shadow regime difference flags in comparison evidence
```

New fields:

```text
regime_label_differs
confidence_differs
confidence_delta
confidence_diff_threshold
```

Backward compatibility rule:

```text
differs_from_legacy = regime_label_differs OR confidence_differs
```

Expected result for the current fixture/comparison:

```text
regime_label_differs: false
confidence_differs: true
confidence_delta: +0.08
differs_from_legacy: true
```

## First task in the fresh chat

Verify the workflow:

```text
Validate ETF macro regime shadow
```

for latest commit:

```text
1255984ff656a58e0581fbb5553ef3684506e964
```

Expected markers:

```text
ETF_MACRO_REGIME_SHADOW_OK
ETF_MACRO_REGIME_SHADOW_COMPARISON_OK
```

Then inspect:

```text
output/macro/validation/latest_macro_regime_shadow_comparison.json
```

Confirm it contains:

```text
schema_version: 1.1
comparison.regime_label_differs
comparison.confidence_differs
comparison.confidence_delta
comparison.confidence_diff_threshold
```

If green, update:

```text
control/MACRO_REGIME_SHADOW_COMPARISON_STATUS.md
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
```

with the split-flag validation evidence.

---

# 3. Authority boundary to preserve

Allowed now:

```text
client-safe descriptive macro/regime summary
current regime from output/macro/latest.json via macro_report_surface
confidence as descriptive model confidence through safe wording
Fed/ECB stance as descriptive policy context
selected policy catalysts marked transfer_to_report: true
portfolio implications as discipline context
legacy lane_adjustments as backward-compatible lane input
shadow comparison evidence for methodology review
```

Still blocked:

```text
raw deterministic_regime_shadow client surface
raw macro_axes client surface
raw macro_axis_scores client surface
Stage-1 thesis candidates client surface
active_drivers client surface
macro direct lane-scoring authority
macro direct fundability authority
macro direct portfolio-trade authority
shadow confidence controlling production recommendations
```

Do not change production behavior while working on confidence calibration.

---

# 4. Roadmap ahead

## Priority 1 — Verify split flags and update control evidence

Current issue:

The split-flag code is committed but not yet confirmed green in workflow evidence.

Next action:

1. Check the `Validate ETF macro regime shadow` run for commit `1255984ff656a58e0581fbb5553ef3684506e964`.
2. Confirm `ETF_MACRO_REGIME_SHADOW_COMPARISON_OK` logs the split flags.
3. Inspect `output/macro/validation/latest_macro_regime_shadow_comparison.json`.
4. Update the status/control files.

Done when:

```text
latest comparison artifact records:
regime_label_differs: false
confidence_differs: true
confidence_delta: 0.08
differs_from_legacy: true
```

## Priority 2 — Shadow-only confidence calibration review

Current issue:

The shadow candidate confidence is `0.80` while macro-audit axes are mixed/restrictive:

```text
volatility: calm
real_rates: restrictive
yield_curve: inverted
inflation_expectations: neutral
policy_rate: restrictive
```

This may be too high for a risk-on regime with narrow leadership and restrictive macro conditions.

Target files:

```text
macro_regime/confidence.py
macro_regime/classify.py
config/regime_thresholds.yml
fixtures/macro_regime_shadow/regime_shadow_fixtures.json
tools/replay_macro_regime_shadow_fixtures.py
tools/validate_macro_regime_shadow.py
```

Recommended approach:

1. Add a shadow-only `macro_conflict_score` or equivalent diagnostic, not production authority.
2. Make the confidence decomposition more explicit:
   - market-axis support
   - breadth penalty
   - hedge/duration penalty
   - macro-audit penalty
   - macro-audit conflict count
3. Review whether restrictive real rates, inverted curve, and restrictive policy rate should cap risk-on confidence.
4. Add/extend fixtures for:
   - risk-on narrow leadership with restrictive macro axes
   - broad risk-on growth with supportive macro axes
   - equity risk-off / policy stress
   - rate-hike repricing
   - mixed regime with conflicting axes
5. Rerun `Validate ETF macro regime shadow`.

Done when:

- confidence components are explainable and deterministic;
- fixture outcomes are stable;
- any changed confidence output is recorded as shadow-only evidence;
- no client/report/portfolio behavior changes.

## Priority 3 — Decide whether to tune confidence or only document it

Do not immediately lower confidence just because it is higher than legacy. First answer:

```text
Is the high confidence caused by strong market axes?
Is the macro-audit penalty already present but too small?
Would a cap be more transparent than changing base scoring?
```

Potential shadow-only design:

```text
if candidate starts with Risk-on and macro_conflict_score >= 3:
    cap confidence at 0.72 or apply a calibrated penalty
```

But do not implement production-impacting promotion. Keep this under `deterministic_regime_shadow`.

## Priority 4 — Update control-layer source of truth

After confidence/split-flag validation, update:

```text
control/CURRENT_STATE.md
control/NEXT_ACTIONS.md
control/MACRO_REGIME_SHADOW_COMPARISON_STATUS.md
control/ETF_SESSION_CHANGELOG.md
```

Known issue:

`control/CURRENT_STATE.md` and `control/NEXT_ACTIONS.md` still contain older production/macro run references in places. They should be refreshed with the newer validated status files, but avoid rewriting them prematurely unless evidence is confirmed.

## Priority 5 — Later macro/thesis phases, still shadow-first

Only after confidence calibration is stable:

```text
config/driver_catalog.yml
config/driver_beneficiary_map.yml
runtime/build_thesis_candidates.py
.github/workflows/validate-thesis-candidates-shadow.yml
```

Goal:

Build Stage-1 thesis candidates as internal artifacts only.

Rules:

- same fixture produces same candidate list;
- candidate lanes must exist in ETF discovery universe;
- no candidate-stage content appears in client reports;
- no fundability or portfolio authority until Stage-2 confirmation gates exist.

## Priority 6 — Non-macro backlog

Keep these in the roadmap but do not mix them into the macro work package unless the user explicitly asks:

### Delivery receipt / manifest evidence

Paused by user. Later:

```text
send_report.py
send_report_runtime_html.py
tools/write_weekly_etf_run_manifest.py
output/run_manifests/
```

Goal: delivery manifest after actual send. Keep separate from recipient receipt.

### Dutch terminology consolidation

Useful cleanup after macro work:

```text
runtime/nl_terminology.py
runtime/nl_localization.py
runtime/apply_nl_localization.py
runtime/scrub_nl_client_language.py
send_report_runtime_html.py
tools/validate_etf_dutch_language_quality.py
```

Goal: reduce scattered one-off Dutch replacements while preserving native Dutch guard-only architecture.

### Direct challenger-vs-current-holding scoring

Future model enhancement:

```text
runtime/score_etf_lanes.py
runtime/discover_etf_lanes.py
pricing/augment_challenger_pricing.py
```

Goal: compare challenger lanes directly against the current holding they may replace over 1m/3m windows, while keeping valuation-grade pricing/fundability gates.

---

# 5. Relevant files by layer

## Decision framework

```text
control/CAPITAL_REUNDERWRITING_RULES.md
control/LANE_DISCOVERY_CONTRACT.md
MACRO_METHODOLOGY.md
control/MACRO_POLICY_PACK_CONTRACT_STATUS.md
control/MACRO_REGIME_SHADOW_COMPARISON_STATUS.md
```

## Input/state contract

```text
output/pricing/*.json
output/run_manifests/*.json
output/runtime/*.json
output/market_history/etf_relative_strength.json
output/macro/latest.json
output/macro/validation/latest_macro_regime_shadow_comparison.json
output/macro/validation/latest_macro_regime_shadow_validation.json
output/macro/validation/latest_macro_audit_axis_shadow_validation.json
```

## Output contract

```text
runtime/macro_report_surface.py
runtime/polish_runtime_reports.py
runtime/macro_report_pre_send_guard.py
tools/validate_macro_report_surface.py
tools/validate_macro_compliance.py
tools/validate_etf_macro_thesis_surface_leakage.py
runtime/scrub_nl_client_language.py
```

## Operational runbook

```text
.github/workflows/send-weekly-report.yml
.github/workflows/validate-macro-report-output.yml
.github/workflows/validate-macro-compliance.yml
.github/workflows/validate-macro-policy-pack-contract.yml
.github/workflows/validate-macro-regime-shadow.yml
tools/write_macro_regime_shadow_comparison_evidence.py
tools/validate_macro_regime_shadow.py
tools/validate_macro_policy_pack.py
tools/replay_macro_regime_shadow_fixtures.py
tools/replay_macro_data_audit_shadow_fixture.py
```

---

# 6. Known validation markers

Use these when reviewing GitHub Actions logs:

```text
ETF_MACRO_REPORT_SURFACE_OK
ETF_MACRO_REPORT_OUTPUT_OK
ETF_MACRO_COMPLIANCE_OK
ETF_MACRO_THESIS_SURFACE_LEAKAGE_OK
ETF_MACRO_REPORT_PRE_SEND_GUARD_OK
ETF_NL_CLIENT_LANGUAGE_SCRUB_OK
ETF_MACRO_POLICY_PACK_OK
ETF_MACRO_POLICY_PACK_SCHEMA_OK
ETF_MACRO_POLICY_PACK_PROMOTION_FIREWALL_OK
ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
ETF_MACRO_DATA_AUDIT_VALID_OK
ETF_MACRO_AUDIT_AXIS_SHADOW_OK
ETF_MACRO_REGIME_SHADOW_OK
ETF_MACRO_REGIME_SHADOW_COMPARISON_OK
```

---

# 7. Do not do next

Do not:

- promote deterministic regime output to production report authority;
- expose raw macro axes or macro axis scores in the client report;
- let shadow confidence drive lane scoring, fundability, or portfolio actions;
- convert Stage-1 thesis candidates into recommendations;
- restart delivery receipt work unless the user asks;
- weaken Dutch validators to make reports pass;
- treat workflow success as recipient receipt;
- update `CURRENT_STATE.md` or `NEXT_ACTIONS.md` with unverified workflow claims.

---

# 8. Suggested first reply in the fresh chat

After reading the required files, the next assistant should say something like:

```text
I have read the control files and the handover. The immediate task is to verify the split shadow-regime difference flags added in commits 249633e, 0a9a055, and 1255984. I will inspect the latest Validate ETF macro regime shadow run for commit 1255984ff656a58e0581fbb5553ef3684506e964 and confirm whether the comparison artifact now records regime_label_differs, confidence_differs, confidence_delta, and confidence_diff_threshold. I will not change production macro/report/portfolio authority.
```
