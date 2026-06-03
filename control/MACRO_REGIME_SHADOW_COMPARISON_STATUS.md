# ETF Macro Regime Shadow Comparison Status

## Snapshot date

2026-06-04

## Current issue

The macro policy-pack authority contract is validated. The controlled macro phase is now to compare the legacy macro regime path with the deterministic shadow regime/confidence path without changing production authority.

The latest validation task was to verify the split shadow comparison flags added after the first legacy-vs-shadow comparison evidence run.

## Root cause

The first durable comparison artifact answered the core legacy-vs-shadow questions, but used one combined flag:

```text
differs_from_legacy
```

That flag became true when either the regime label changed or the confidence differed beyond threshold. In the current fixture, the legacy and shadow regime labels are the same, but confidence differs by `0.08`, so the combined flag alone was ambiguous.

The comparison evidence therefore needed separate fields for:

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

## Implemented change

Added comparison evidence writer:

```text
tools/write_macro_regime_shadow_comparison_evidence.py
```

The tool writes:

```text
output/macro/validation/macro_regime_shadow_comparison_<run_id>.json
output/macro/validation/latest_macro_regime_shadow_comparison.json
```

It records:

- legacy regime
- legacy confidence
- legacy confidence source
- deterministic shadow candidate regime
- deterministic shadow candidate confidence
- regime-label difference flag
- confidence-difference flag
- confidence delta
- confidence-difference threshold
- market axes and axis scores
- macro-audit axes and macro-axis scores
- confidence decomposition
- workflow metadata
- explicit no-authority guardrails

Updated workflow:

```text
.github/workflows/validate-macro-regime-shadow.yml
```

The workflow writes legacy-vs-shadow comparison evidence after fixture replay, macro-audit replay, schema validation, and shadow payload validation.

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

## Validation status

Validated by isolated GitHub Actions workflow.

Latest confirmed split-flag workflow evidence:

```text
workflow: Validate ETF macro regime shadow
run_number: 18
workflow_run_id: 26915491624
job: validate-shadow-regime
job_status: completed
job_conclusion: success
trigger_commit: 1255984ff656a58e0581fbb5553ef3684506e964
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
shadow_candidate_confidence: 0.80
regime_label_differs: false
confidence_delta: +0.08
confidence_diff_threshold: 0.05
confidence_differs: true
differs_from_legacy: true
```

Important nuance:

The regime label is the same. The artifact marks `differs_from_legacy: true` only because `confidence_differs: true`. This resolves the earlier ambiguity in the combined flag and keeps the comparison evidence reviewable without changing production authority.

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

Current shadow confidence is `0.80` from method:

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
raw_confidence: 0.7964
min: 0.35
max: 0.82
```

Notes from the artifact:

- confidence measures cross-axis agreement, not forecast accuracy;
- market axes support risk-on narrow leadership;
- macro-audit axes are mixed/restrictive;
- confidence is reduced for mixed or internally conflicting market/macro evidence.

## Authority boundary

Allowed now:

- store and review legacy-vs-shadow comparison evidence
- compare confidence deltas
- inspect market axes and macro-audit axes internally
- use this evidence for methodology review and future promotion discussions
- use split flags to clarify internal comparison evidence

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

This does not promote deterministic macro/regime output to client-facing, lane-scoring, fundability, or portfolio-action authority.

## Next action

Continue with threshold and confidence review in shadow mode:

```text
config/regime_thresholds.yml
fixtures/macro_regime_shadow/regime_shadow_fixtures.json
macro_regime/confidence.py
tools/replay_macro_regime_shadow_fixtures.py
tools/validate_macro_regime_shadow.py
```

Goal: review whether the current confidence model is too high for mixed macro axes and whether a transparent macro-conflict cap or penalty is better than changing base scoring, without changing production authority.