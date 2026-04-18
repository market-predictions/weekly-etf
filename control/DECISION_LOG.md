# ETF Review OS — Decision Log

Use this file to capture stable architecture decisions so future sessions do not need to rediscover them.

---

## 2026-03-28 — Adopt Project + GitHub + Actions architecture
### Decision
The ETF flow will no longer be treated conceptually as one giant prompt-centered system.

### Chosen architecture
- **ChatGPT Project** = working memory and recurring workspace
- **GitHub repo** = explicit source of truth for prompts, scripts, outputs, and control docs
- **GitHub Actions + scripts** = real execution and delivery layer
- **Optional Custom GPT** = architect/reviewer only, not the primary runtime container

### Reason
This separates:
- thinking/work context
- system state and audit trail
- production execution

That reduces brittleness and makes debugging easier.

---

## 2026-03-28 — Add a control layer to the ETF repo
### Decision
A new `control/` layer is introduced to guide future sessions.

### Initial files
- `control/SYSTEM_INDEX.md`
- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `control/DECISION_LOG.md`
- `control/CHATGPT_PROJECT_INSTRUCTIONS.md`
- `control/OPTIONAL_CUSTOM_GPT_SPEC.md`

### Reason
The previous setup had strong execution files, but no single authoritative session-start path.

---

## 2026-03-28 — ETF should move toward explicit state files
### Decision
ETF should evolve toward explicit implementation files similar in spirit to the FX system.

### Planned direction
Potential future files:
- `output/etf_portfolio_state.json`
- `output/etf_trade_ledger.csv`
- `output/etf_valuation_history.csv`
- `output/etf_recommendation_scorecard.csv`

### Reason
Relying mainly on prior report parsing is functional but weaker than using explicit state files for implementation facts.

---

## 2026-03-28 — Do not use the optional GPT as the production runner
### Decision
If a helper GPT is created, it should be used for:
- architecture review
- prompt refactoring
- script/workflow review
- consistency checking

It should **not** be treated as the canonical production runtime.

### Reason
Projects and GitHub together are better suited for long-running context plus state and auditability. A GPT is better as a specialist tool than as the main container.

---

## 2026-03-31 — Add lean bootstrap model for ETF Project
### Decision
The ETF project should use a lean bootstrap approach rather than uploading changing repo files as standing project context.

### Chosen file
- `control/PROJECT_BOOTSTRAP.md`

### Reason
This keeps the ChatGPT Project lightweight and reinforces GitHub as the live source of truth.

---

## 2026-03-31 — Introduce ETF as-is split scaffold in `prompts/as_is_split/`
### Decision
ETF now has a parallel split architecture for safe prompt decomposition without changing production behavior.

### Added structure
- `prompts/as_is_split/ETF_RUNTIME_SPLIT.txt`
- `prompts/as_is_split/01_DECISION_FRAMEWORK.md`
- `prompts/as_is_split/02_INPUT_STATE_CONTRACT.md`
- `prompts/as_is_split/03_OUTPUT_CONTRACT.md`
- `prompts/as_is_split/04_OPERATIONAL_RUNBOOK.md`
- `prompts/as_is_split/05_SECTION_MAP.md`

### Reason
This makes the four-layer architecture explicit while keeping `etf.txt` protected as production.

---

## 2026-03-31 — Keep ETF executive look & feel as the family reference standard
### Decision
The ETF review remains the visual/design reference point for the report family.

### Implication
Any split architecture, workflow refactor, or output-contract extraction must preserve:
- the existing executive hierarchy
- the premium email-first feel
- compact table discipline
- appendix separation
- PDF/HTML parity

### Reason
The goal of the split is architectural clarity, not a downgrade or redesign of the ETF client experience.

---

## 2026-03-31 — Split-test outputs must remain operationally separate from production
### Decision
ETF split-test outputs must be written to `output_split_test/` and handled by a dedicated split-test workflow.

### Files
- `output_split_test/`
- `.github/workflows/send-weekly-report-split-test.yml`

### Reason
This preserves production safety and allows genuine output comparison without polluting the production report family.

---

## 2026-04-17 — Replace fixed structural-lane gating with open discovery and compact executive publication
### Decision
The production ETF prompt should no longer use a small fixed structural lane list as the front-end discovery gate.

### Chosen architecture
- **Open internal discovery** across broad investable domains each run
- **Dynamic candidate-lane construction** before publication
- **Persistent taxonomy** as a back-end memory layer, not a front-end gate
- **Compact executive publication** of only the best-ranked 5-8 lanes
- **Continuity memory** for retained lanes, new entrants, dropped lanes, and near-miss challengers

### Reason
This reduces omission risk, keeps the report aligned with real macro and geopolitical change, and preserves the premium executive standard by compressing after discovery rather than before it.

### Implementation rule
This architecture change is promoted directly into the production prompt and control layer without requiring a new split-style comparison run.

### Files updated
- `etf.txt`
- `etf-pro.txt`
- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `control/DECISION_LOG.md`

---

## 2026-04-18 — Add starter pricing subsystem on main
### Decision
ETF now has a starter explicit pricing subsystem on `main` rather than leaving pricing entirely as ad hoc retrieval inside the prompt.

### Added structure
- `pricing/`
- `output/pricing/`
- pricing clients for Twelve Data, FMP, and Alpha Vantage
- quota-aware cache and budget manager
- pricing pass CLI and audit writer

### Reason
This creates the first machine-readable implementation layer for fresh ETF closes and moves ETF toward explicit input/state authority.

---

## 2026-04-18 — Separate runtime validation from subscriber email send
### Decision
The production send workflow must not be triggered by pricing, prompt, script, or workflow code changes.

### Chosen architecture
- `.github/workflows/send-weekly-report.yml` is reserved for actual production report-output pushes and manual dispatch
- `.github/workflows/validate-etf-runtime.yml` handles pricing, prompt, runtime, and render validation without sending email

### Reason
This prevents accidental duplicate subscriber emails when implementation code changes are merged into `main` and keeps the workflow layer operational rather than editorial.
