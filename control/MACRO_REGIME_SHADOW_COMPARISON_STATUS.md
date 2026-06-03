# ETF Macro Regime Shadow Comparison Status

## Snapshot date
2026-06-03

## Current issue

The macro policy-pack authority contract is now validated. The next controlled macro phase was to compare the legacy macro regime path with the deterministic shadow regime/confidence path without changing production authority.

## Root cause

The deterministic classifier and confidence model already existed, and fixture replay was already available, but there was no dedicated durable artifact answering:

```text
What did the legacy macro pack classify?
What did the deterministic shadow classifier classify?
Did they differ?
What was the confidence delta?
Which market and macro axes explain the result?
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
- confidence delta
- market axes and axis scores
- macro-audit axes and macro-axis scores
- confidence decomposition
- workflow metadata
- explicit no-authority guardrails

Updated workflow:

```text
.github/workflows/validate-macro-regime-shadow.yml
```

The workflow now writes legacy-vs-shadow comparison evidence after fixture replay, macro-audit replay, schema validation, and shadow payload validation.

## Commits

```text
4db8400000864d19b55328328065893f173b1780  add macro regime shadow comparison evidence writer
318135659b6039c9b861732f352c3d903815c775  record legacy versus shadow regime comparison evidence
```

## Validation status

Validated by isolated GitHub Actions workflow.

User-provided UI evidence shows:

```text
workflow: Validate ETF macro regime shadow
run: #15
trigger_commit: 318135659b6039c9b861732f352c3d903815c775
status: passed
duration: 27s
observed_at: 2026-06-03
```

Repo evidence from:

```text
output/macro/validation/latest_macro_regime_shadow_comparison.json
```

shows:

```text
status: passed
workflow.name: Validate ETF macro regime shadow
workflow.run_number: 15
workflow.run_id: 26909884800
workflow.commit_sha: 318135659b6039c9b861732f352c3d903815c775
```

## Latest comparison result

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

The regime label is the same, but the artifact currently marks `differs_from_legacy: true` because the shadow confidence differs from legacy confidence by at least 0.05. This is comparison evidence only and does not change production authority.

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

## Authority boundary

Allowed now:

- store and review legacy-vs-shadow comparison evidence
- compare confidence deltas
- inspect market axes and macro-audit axes internally
- use this evidence for methodology review and future promotion discussions

Still blocked:

- client-facing raw macro axes
- client-facing raw macro axis scores
- client-facing deterministic_regime_shadow payload
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

Deterministic regime/confidence shadow comparison evidence: **closed for this stage**.

## Next action

Continue with threshold and confidence review in shadow mode:

```text
config/regime_thresholds.yml
fixtures/macro_regime_shadow/regime_shadow_fixtures.json
macro_regime/confidence.py
tools/replay_macro_regime_shadow_fixtures.py
```

Goal: review whether the current confidence model is too high for mixed macro axes and whether `differs_from_legacy` should be split into separate `regime_label_differs` and `confidence_differs` flags, without changing production authority.
