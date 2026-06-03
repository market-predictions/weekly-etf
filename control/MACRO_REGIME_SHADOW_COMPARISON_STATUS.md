# ETF Macro Regime Shadow Comparison Status

## Snapshot date

2026-06-04

## Current issue

The macro policy-pack authority contract is validated. The controlled macro phase compares the legacy macro regime path with the deterministic shadow regime/confidence path without changing production authority.

The prior ambiguity in `differs_from_legacy` has been resolved with split flags, and the latest confidence-calibration task reviewed whether the shadow confidence was too high for a market-led risk-on narrow regime while macro-audit axes were mixed/restrictive.

## Root cause

The original comparison artifact used one combined flag:

```text
differs_from_legacy
```

That flag became true when either the regime label changed or the confidence differed beyond threshold. In the current fixture, the legacy and shadow regime labels were the same, but confidence differed by `0.08`, so the combined flag alone was ambiguous.

Separately, the shadow confidence model gave `0.80` for `Risk-on narrow leadership` even though macro-audit axes included restrictive real rates, an inverted yield curve, and a restrictive policy rate. That was too opaque for methodology review because the confidence decomposition did not explicitly expose a macro-conflict diagnostic or cap.

## Implemented change

### Split comparison flags

The comparison evidence now records:

```text
regime_label_differs
confidence_differs
confidence_delta
confidence_diff_threshold
```

while retaining backward compatibility:

```text
differs_from_legacy = regime_label_differs OR confidence_differs
```

### Macro-conflict confidence calibration

Updated:

```text
config/regime_thresholds.yml
macro_regime/confidence.py
tools/replay_macro_regime_shadow_fixtures.py
fixtures/macro_regime_shadow/regime_shadow_fixtures.json
```

The confidence model now records shadow-only diagnostic components:

```text
macro_conflict_score
macro_conflict_cap_threshold
risk_on_macro_conflict_cap
confidence_cap_applied
uncapped_confidence
```

The specific calibration rule is intentionally narrow:

```text
if macro audit is present
and candidate regime starts with Risk-on
and macro_conflict_score >= macro_conflict_cap_threshold
and raw confidence > risk_on_macro_conflict_cap:
    cap shadow confidence at risk_on_macro_conflict_cap
```

Current config values:

```text
macro_conflict_cap_threshold: 0.75
risk_on_macro_conflict_cap: 0.72
```

The replay tool now supports optional per-fixture macro-audit input through:

```text
macro_data_audit_fixture
```

and validates expected macro axes and expected confidence components when a fixture declares them.

A new fixture was added:

```text
risk_on_narrow_restrictive_macro
```

This fixture isolates the exact case under review: market-led risk-on narrow leadership with restrictive macro-audit axes.

## Commits

Initial comparison evidence:

```text
4db8400000864d19b55328328065893f173b1780  add macro regime shadow comparison evidence writer
318135659b6039c9b861732f352c3d903815c775  record legacy versus shadow regime comparison evidence
```

Split-flag change:

```text
249633e67cf75f29ba51c7efe9c70a4ebf4392b9  split shadow regime legacy difference flags
0a9a05577e001dfea6a2e794fd9915ce52614634  validate split shadow regime difference flags
1255984ff656a58e0581fbb5553ef3684506e964  record split shadow regime difference flags in comparison evidence
```

Confidence calibration:

```text
0e984bb3b69141939d2c9cef46e7666da6f5b20c  add shadow macro conflict confidence settings
5dfedfa68d23abe2b5c66634c872faf1419f55c0  apply shadow macro conflict confidence cap
4500e8f74e4199d5d5f3ef35d426e3c634fab7af  replay macro-audit conflict fixture
27e4bf1341999aa49df1c5bfb51f983fd59b0c8b  add risk-on macro conflict replay fixture
```

## Validation status

Validated by isolated GitHub Actions workflow.

Latest confirmed workflow evidence:

```text
workflow: Validate ETF macro regime shadow
run_number: 22
workflow_run_id: 26917489620
job: validate-shadow-regime
job_status: completed
job_conclusion: success
trigger_commit: 27e4bf1341999aa49df1c5bfb51f983fd59b0c8b
source_ref: main
status: passed
validated_artifact: output/macro/validation/latest_macro_regime_shadow_comparison.json
schema_version: 1.1
```

The workflow job completed successfully, including the steps:

```text
Replay deterministic regime fixtures
Replay macro-audit fixture through shadow regime stack
Validate macro policy pack schema
Validate shadow regime payload
Write shadow validation evidence
Write legacy-vs-shadow comparison evidence
Commit shadow validation evidence
```

Expected markers for log review remain:

```text
ETF_MACRO_REGIME_FIXTURE_REPLAY_OK
ETF_MACRO_DATA_AUDIT_VALID_OK
ETF_MACRO_AUDIT_AXIS_SHADOW_OK
ETF_MACRO_REGIME_SHADOW_OK
ETF_MACRO_REGIME_SHADOW_COMPARISON_OK
```

## Latest comparison result

```text
legacy_regime: Risk-on narrow leadership
legacy_confidence: 0.72
legacy_confidence_source: legacy_proxy_static
shadow_candidate_regime: Risk-on narrow leadership
shadow_candidate_confidence: 0.72
regime_label_differs: false
confidence_delta: 0.00
confidence_diff_threshold: 0.05
confidence_differs: false
differs_from_legacy: false
```

The prior shadow confidence of `0.80` is now recorded as:

```text
uncapped_confidence: 0.7964
```

and the capped shadow confidence is:

```text
raw_confidence: 0.72
confidence: 0.72
```

## Market axes

```text
equity: risk_on
semiconductor_leadership: strong
breadth: narrow
duration: neutral
hedge: gold_weak
commodities: inflation_bid
```

## Macro-audit axes

```text
volatility: calm
real_rates: restrictive
yield_curve: inverted
inflation_expectations: neutral
policy_rate: restrictive
```

## Confidence decomposition snapshot

Current shadow confidence is `0.72` from method:

```text
deterministic_axis_agreement_v1_shadow
```

Current component snapshot:

```text
base: 0.45
axis_alignment: 0.60
macro_alignment: 0.60
macro_signal_strength: 0.42
signal_strength: 0.7196
conflict_score: 0.1875
macro_conflict_score: 1.0
macro_conflict_cap_threshold: 0.75
risk_on_macro_conflict_cap: 0.72
confidence_cap_applied: true
uncapped_confidence: 0.7964
raw_confidence: 0.72
min: 0.35
max: 0.82
```

Notes from the artifact:

- confidence measures cross-axis agreement, not forecast accuracy;
- market axes support risk-on narrow leadership;
- macro-audit axes are mixed/restrictive;
- confidence is reduced for mixed or internally conflicting market/macro evidence;
- macro conflict diagnostic score is `1.0`;
- risk-on confidence was capped by the shadow macro-conflict rule.

## Authority boundary

Allowed now:

- store and review legacy-vs-shadow comparison evidence
- compare confidence deltas
- inspect market axes and macro-audit axes internally
- use this evidence for methodology review and future promotion discussions
- use split flags to clarify internal comparison evidence
- use macro-conflict diagnostics for shadow-only confidence calibration review

Still blocked:

- client-facing raw macro axes
- client-facing raw macro axis scores
- client-facing deterministic_regime_shadow payload
- client-facing Stage-1 thesis candidates or active drivers
- using shadow candidate for production lane scoring
- using shadow confidence for fundability
- using shadow output for portfolio actions or trades

The evidence artifact explicitly states:

```text
shadow_only: true
client_facing_authority: false
decision_impact: none_shadow_comparison_only
lane_scoring_authority: false
fundability_authority: false
portfolio_action_authority: false
production_report_path_changed: false
promotion_status: not_promoted
```

## Work-package status

Legacy-vs-shadow comparison evidence with split difference flags: **closed for this stage**.

Shadow confidence calibration for the current restrictive-macro risk-on case: **closed for this stage**.

This does not promote deterministic macro/regime output to client-facing, lane-scoring, fundability, or portfolio-action authority.

## Next action

Continue with broader shadow fixture coverage and methodology review before any promotion:

```text
fixtures/macro_regime_shadow/regime_shadow_fixtures.json
macro_regime/confidence.py
tools/replay_macro_regime_shadow_fixtures.py
MACRO_METHODOLOGY.md
tools/validate_macro_compliance.py
```

Recommended next step: add 2-3 more macro-audit fixture variants so the cap does not overfit one case:

```text
broad risk-on with supportive macro axes
risk-off with supportive macro axes
rate-hike repricing with accommodative-policy conflict
```

Then decide whether the macro-conflict cap belongs in the stable methodology or remains a temporary shadow calibration rule.