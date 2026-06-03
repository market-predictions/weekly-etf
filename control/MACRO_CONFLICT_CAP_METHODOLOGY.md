# Macro Conflict Cap Methodology

Status: stable shadow methodology rule.

This note records an internal validation rule for the deterministic macro regime shadow layer. It does not change report wording or production decisions.

The rule applies only when a risk-on shadow candidate has strong disagreement from audited macro axes. In that case, shadow confidence is capped at the configured risk-on macro conflict cap.

Current settings:

- macro_conflict_cap_threshold: 0.75
- risk_on_macro_conflict_cap: 0.72

Confidence is a descriptive cross-axis agreement score, not a forecast probability.

Non-risk-on disagreements are diagnostic only at this stage. They expose macro_conflict_score for review but do not cap confidence.

Validation artifacts should continue to record macro_conflict_score, confidence_cap_applied, uncapped_confidence, and raw_confidence.

This remains shadow-only. It has no client-facing, lane-scoring, fundability, or portfolio-action authority.
