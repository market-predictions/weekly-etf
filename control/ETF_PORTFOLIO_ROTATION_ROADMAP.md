# ETF Portfolio Rotation Engine — Roadmap

**Repository:** `market-predictions/weekly-etf`  
**Status:** active implementation roadmap  
**Authority:** `control/ETF_PORTFOLIO_ROTATION_CONTRACT_V1.md`

---

## 1. Current issue

The Weekly ETF Review can identify weak incumbents, better alternatives, replacement duels, and capital re-underwriting flags. The current system does not yet convert that evidence into deterministic target weights and trade intents.

The visible symptom is persistent `Hold under review` behavior. The underlying root cause is that the runtime state and report renderer classify recommendations but do not run a true allocation/rotation engine.

---

## 2. Build principle

No ticker-specific rules.

The engine must apply the same decision logic to every incumbent position:

```text
incumbent review
→ capital release score
→ candidate destination score
→ constraints
→ target weights
→ trade intents
→ report and trade ledger
```

---

## 3. Target architecture

```text
pricing audit
→ historical relative strength
→ lane discovery
→ challenger pricing
→ final lane discovery
→ recommendation memory / review-age state
→ portfolio rotation engine
→ rotation validators
→ runtime state with rotation_plan
→ EN/NL report render from rotation_plan
→ trade ledger from trade_intents[]
→ delivery validators
→ email delivery
→ persisted state and memory
```

---

## 4. Phases

### Phase 0 — Contract and roadmap

Status: started.

Files:

```text
control/ETF_PORTFOLIO_ROTATION_CONTRACT_V1.md
control/ETF_PORTFOLIO_ROTATION_ROADMAP.md
```

Done when: contract and roadmap are committed and referenced from control files.

### Phase 1 — Engine skeleton

New file:

```text
runtime/portfolio_rotation_engine.py
```

Responsibilities:

- read current state artifacts;
- compute incumbent reviews;
- compute candidate reviews;
- write deterministic rotation plan JSON;
- write latest rotation-plan pointer.

### Phase 2 — Output contract validator

New file:

```text
tools/validate_etf_rotation_output_contract.py
```

Responsibilities:

- validate schema fields;
- validate target weights reconcile;
- validate trade intents reference valid source/destination tickers;
- validate no passive hold with high release score unless override is present.

### Phase 3 — Discipline validator

New file:

```text
tools/validate_etf_rotation_discipline.py
```

Initial mode:

```text
warning-only
```

Later mode:

```text
blocking
```

### Phase 4 — Recommendation memory persistence

Modify:

```text
tools/write_etf_recommendation_scorecard.py
```

Responsibilities:

- own `weeks_replaceable` increment/reset logic;
- preserve inertia clock across runs;
- preserve override state when applicable.

### Phase 5 — Runtime-state integration

Modify:

```text
runtime/build_etf_report_state.py
```

Add:

```text
--rotation-plan
rotation_plan
target_weights
trade_intents
```

### Phase 6 — Report rendering from rotation plan

Modify:

```text
runtime/render_etf_report_from_state.py
runtime/render_etf_report_nl_from_state.py
```

Replace tables currently derived from `suggested_action` with rotation-plan-derived tables.

### Phase 7 — Trade ledger alignment

Modify:

```text
tools/write_etf_trade_ledger.py
```

Make `trade_intents[]` the canonical source for trade ledger updates.

### Phase 8 — Workflow warning-mode integration

Modify:

```text
.github/workflows/send-weekly-report.yml
```

Insert:

```text
python -m runtime.portfolio_rotation_engine ...
python tools/validate_etf_rotation_output_contract.py ...
python tools/validate_etf_rotation_discipline.py --warning-only ...
```

### Phase 9 — Blocking gate promotion

After clean test runs, remove warning-only mode for the discipline validator.

---

## 5. Report v1 scope

V1 should stay compact:

- Capital Rotation Summary;
- upgraded Final Action Table;
- Position Changes rendered from `trade_intents[]`.

Full analyst-detail score tables are deferred to v2.

---

## 6. Regression guardrails

The build must preserve:

- pricing-lineage discipline;
- bilingual numeric parity;
- Dutch companion generated from same state;
- delivery HTML strict-section validation;
- no subscriber email send from code-only commits;
- no ticker-specific rules;
- no hidden thresholds outside the contract.

---

## 7. Current implementation checkpoint

Phase 0 is complete once this roadmap and the contract are committed. Next implementation task is Phase 1: create the deterministic engine skeleton and standalone rotation plan artifact writer.