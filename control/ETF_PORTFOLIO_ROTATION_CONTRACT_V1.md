# ETF Portfolio Rotation Contract V1

**Repository:** `market-predictions/weekly-etf`  
**Status:** active design-and-build authority  
**Created:** 2026-05-28  
**Purpose:** define the deterministic, ticker-agnostic portfolio rotation layer for the Weekly ETF Review system.

---

## 1. Scope and authority

This contract governs the new ETF portfolio rotation layer. It exists because the current runtime can identify weak positions, review candidates and replacement duels, but it does not yet convert that evidence into target weights, source/destination decisions or share-level trade intents.

This contract is the authority for:

1. rotation decision framework;
2. rotation input/state contract;
3. rotation output contract;
4. rotation operational runbook.

This contract does **not** replace:

- `control/ETF_PRICING_LINEAGE_CONTRACT_V1.md` for price lineage;
- `control/LANE_DISCOVERY_CONTRACT.md` for discovery breadth;
- `control/CAPITAL_REUNDERWRITING_RULES.md` for capital discipline principles;
- `control/ETF_RUNTIME_STATE_CONTRACT.md` for runtime state authority.

The rotation engine must consume those layers. It must not reimplement pricing, discovery or report rendering.

---

## 2. First-principles rule

Every euro of portfolio capital must periodically re-earn its place.

For each incumbent holding, the rotation engine must answer:

```text
Does this position still deserve its current capital weight?
If not, should capital be held as cash, reduced, redeployed to a role-preserving challenger, redeployed to an adjacent challenger, or redeployed portfolio-wide?
```

No ETF-specific rules are allowed. The same rules apply to every incumbent position.

---

## 3. Layer separation

### 3.1 Decision framework

The engine produces one canonical decision per incumbent position:

```text
hold
hold_with_override
reduce
replace_partial
replace_full
close
add_from_cash
```

### 3.2 Input/state contract

The engine consumes current machine-readable artifacts and does not read markdown reports as authority.

Required inputs:

```text
output/etf_portfolio_state.json
output/etf_recommendation_scorecard.csv
output/pricing/price_audit_*.json
output/lane_reviews/etf_lane_assessment_*.json
output/market_history/etf_relative_strength.json
```

Optional input:

```text
control/etf_rotation_overrides.yml
```

### 3.3 Output contract

The engine writes exactly one immutable rotation-plan artifact per production run:

```text
output/runtime/etf_rotation_plan_<report_token>_<run_id>.json
output/runtime/latest_etf_rotation_plan_path.txt
```

The artifact must include:

```text
schema_version
created_at_utc
run_id
report_token
requested_close_date
source_files
policy
incumbent_reviews[]
candidate_reviews[]
rotation_decisions[]
target_weights[]
trade_intents[]
validation_flags
```

### 3.4 Operational runbook

The production path must become:

```text
pricing audit
→ historical relative strength
→ lane discovery
→ challenger pricing
→ final lane discovery
→ recommendation memory / review-age state
→ portfolio rotation engine
→ rotation validators
→ runtime state build with exact rotation plan
→ EN/NL render from rotation plan
→ trade ledger from trade_intents[]
→ delivery validators
→ email delivery
→ persist state, scorecard, ledger and manifest
```

---

## 4. Canonical scoring concepts

### 4.1 Incumbent score

The incumbent score measures whether a current position still deserves capital.

Inputs may include:

```text
thesis_score
implementation_score
pnl_pct
contribution_quality
fresh_cash_test
replaceable_status
weeks_replaceable
better_alternative_exists
factor_overlap_flag
hedge_validity_status
required_next_action
```

### 4.2 Capital release score

The capital release score identifies positions that should fund rotation.

Default score components:

| Signal | Additive score |
|---|---:|
| `fresh_cash_test` says reduce/no | +25 |
| `fresh_cash_test` says smaller/under review | +12 |
| `replaceable_status != None` | +20 |
| `weeks_replaceable >= 2` | +10 |
| `weeks_replaceable >= 3` | +10 |
| `pnl_pct < -5%` | +10 |
| `pnl_pct < -10%` | +15 additional |
| `better_alternative_exists = Yes` | +15 |
| contribution quality is negative/material drag | +10 |
| role validity impaired | +10 |
| role validity failed | +20 |
| factor overlap / concentration flag present | +8 |

### 4.3 Destination score

The destination score ranks candidates that may receive capital.

Default components:

| Signal | Additive score |
|---|---:|
| valuation-grade pricing | +20 |
| fundable candidate | +20 |
| promoted to live radar | +10 |
| structural total score scaled to 0-50 | up to +50 |
| relative strength score positive | +5 to +15 |
| liquidity pass | +10 |
| portfolio differentiation | +5 to +15 |
| direct 3m edge versus holding > 5% | +5 |
| direct 3m edge versus holding > 10% | +10 additional |
| direct 3m edge versus holding > 15% | +10 additional |

Destination score is not enough on its own. It must still pass constraints.

---

## 5. Role-validity states

The engine must derive one of:

```text
role_validity = pass | impaired | fail
```

Generic rules:

- `pass`: thesis and implementation remain acceptable; no major unresolved role question.
- `impaired`: thesis may remain valid, but implementation, contribution, hedge status, factor overlap or relative strength is materially weaker.
- `fail`: the role no longer justifies current capital, or implementation/role validity is broken enough that a normal hold is not acceptable without override.

No ticker-specific mapping is allowed.

---

## 6. Rotation types

### 6.1 Role-preserving replacement

A current position is replaced by a candidate serving the same or very similar portfolio role.

Allowed when:

```text
release_score >= replace threshold
candidate destination_score >= fundable threshold
candidate has valuation-grade pricing
portfolio constraints remain valid
```

### 6.2 Adjacent replacement

A current position is reduced or partially replaced by a related but not identical sleeve.

Allowed when:

```text
role_validity in {impaired, fail}
review age threshold is met
candidate is fundable
portfolio constraints remain valid
```

### 6.3 Portfolio-wide redeployment

Capital is moved from a weak incumbent into the strongest portfolio-wide candidate.

Rules:

- Full portfolio-wide replacement requires `role_validity = fail`.
- Partial portfolio-wide redeployment is allowed when `role_validity = impaired`, `weeks_replaceable >= 2`, release score exceeds threshold, destination score is superior and constraints remain valid.
- Portfolio-wide redeployment may not violate position caps, concentration caps, max churn, liquidity or minimum trade size rules.

---

## 7. Decision thresholds

Default v1 thresholds:

```text
min_trade_size_pct_nav = 2.00
max_single_source_reduction_pct_nav = 5.00
max_major_rotations_per_run = 1
review_age_watch = 1
review_age_forced_decision = 2
review_age_block_passive_hold = 3
release_score_reduce_threshold = 65
release_score_replace_threshold = 80
release_score_close_threshold = 90
destination_score_min_fundable = 70
destination_score_preferred = 80
challenger_edge_partial_threshold = 10
challenger_edge_full_threshold = 20
relative_strength_3m_watch = 5
relative_strength_3m_rotation_candidate = 10
relative_strength_3m_strong = 15
```

Thresholds are contract defaults. Changes require a contract update, not hidden code changes.

---

## 8. Override governance

`hold_with_override` is allowed only as an explicit governed decision.

Required fields:

```text
override_status: none | engine | operator
override_reason_code
override_reason_text
override_source
override_created_at_run_id
override_expires_after_run
```

Allowed engine override reason codes:

```text
candidate_not_valuation_grade
min_trade_size_not_met
max_position_cap_hit
churn_budget_used
role_preservation_required
pricing_lineage_insufficient
liquidity_constraint
insufficient_confirming_window
no_fundable_destination
portfolio_constraint_blocked
```

Operator overrides may be supplied only through a tracked control artifact:

```text
control/etf_rotation_overrides.yml
```

Validators must reject:

- empty overrides;
- free-text-only overrides;
- stale overrides;
- overrides with no run id or expiry;
- overrides that contradict hard constraints.

---

## 9. Recommendation memory and inertia clock

`tools/write_etf_recommendation_scorecard.py` is the intended owner of `weeks_replaceable` increment/reset logic.

Rules:

```text
If position remains under review and no action is taken:
  weeks_replaceable += 1

If position is reduced, replaced or closed:
  weeks_replaceable resets or transitions to resolved status

If position earns a clean hold:
  weeks_replaceable = 0

If position is hold_with_override:
  weeks_replaceable increments unless the override explicitly resolves the issue
```

The rotation engine may read the scorecard, but it must not silently invent persistent memory.

---

## 10. Trade ledger authority

`trade_intents[]` from the rotation plan is the canonical upstream object for trade-ledger changes.

Required flow:

```text
runtime/portfolio_rotation_engine.py
→ output/runtime/etf_rotation_plan_<token>_<run_id>.json
→ trade_intents[]
→ tools/write_etf_trade_ledger.py
→ output/etf_trade_ledger.csv
```

The report and trade ledger must not independently reconstruct trades from `suggested_action` text.

---

## 11. Report scope v1

V1 should be compact and low-render-risk.

Investor-facing sections:

1. Capital Rotation Summary;
2. upgraded Final Action Table;
3. Position Changes table from `trade_intents[]`.

Required columns for v1:

```text
source
destination
current_weight
target_weight
delta_weight
action_code
reason_codes
override_status
```

Full analyst-detail rotation score tables are deferred to v2.

Both English and Dutch reports must consume the same rotation-plan object.

---

## 12. Validators

New validators:

```text
tools/validate_etf_rotation_output_contract.py
tools/validate_etf_rotation_discipline.py
```

Phase 5 behavior:

```text
warning-only
```

Phase 7 behavior:

```text
blocking before delivery
```

The discipline validator must fail or warn if:

```text
position has high release score
and review age exceeds threshold
and action remains passive hold
and no valid override exists
```

---

## 13. Non-goals

The rotation engine must not:

- use ticker-specific rules;
- use markdown reports as primary state;
- weaken pricing lineage requirements;
- turn broad discovery into an automatic buy list;
- execute excessive churn on small score differences;
- let `Hold under review` become an indefinite final state.

---

## 14. Build sequence

1. Store roadmap and contract.
2. Build `runtime/portfolio_rotation_engine.py` skeleton.
3. Add rotation output validator.
4. Add discipline validator in warning mode.
5. Add `weeks_replaceable` persistence owner logic.
6. Wire rotation plan into runtime state.
7. Render EN/NL from rotation plan.
8. Align trade ledger to `trade_intents[]`.
9. Wire workflow warning-only.
10. Promote validator to blocking after clean test runs.

---

## 15. Current status

This contract is created before implementation and is the central reference for the rotation-engine build.