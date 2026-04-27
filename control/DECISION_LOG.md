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

---

## 2026-04-18 — Let the production prompt consume a matching pricing audit when available
### Decision
The production ETF prompt should explicitly read and use the latest valid matching pricing audit from `output/pricing/` when one exists for the requested close date.

### Chosen architecture
- `etf.txt` prefers a same-date matching pricing audit as the operational summary of the pricing pass
- ad hoc repeated retrieval is still allowed if the audit is missing, stale, inconsistent, or too incomplete
- pricing-audit use is limited to the operational pricing layer and does not silently overrule date freshness requirements

### Reason
This reduces repeated manual retrieval for the same run date, aligns the prompt with the new pricing subsystem, and moves ETF closer to a clean input/state contract without yet requiring full explicit state-file adoption.

---

## 2026-04-21 — Make breadth assessment explicit through a lane artifact and visible omitted-lane proof
### Decision
Broader discovery should no longer remain only a prompt intention. ETF should now treat breadth as an explicit production requirement with a matching machine-readable lane artifact and a compact visible omitted-lane block in the report.

### Chosen architecture
- **Mandatory breadth assessment universe** across major investable buckets each run
- **Matching machine-readable lane artifact** in `output/lane_reviews/`
- **Compact omitted-lane proof** in the published report through a `Notable lanes assessed but not promoted this week` block
- **Premium editorial preservation** of omitted but relevant challengers instead of smoothing them away
- **Helper validator** in `validate_lane_breadth.py` to harden the architecture ahead of final send-path wiring

### Reason
The prior open-discovery patch improved the conceptual architecture, but broad discovery could still disappear from visible output. This decision makes breadth auditable, visible, and eventually enforceable before send.

### Files updated
- `etf.txt`
- `etf-pro.txt`
- `output/lane_reviews/.gitkeep`
- `output/lane_reviews/README.md`
- `validate_lane_breadth.py`
- `control/CURRENT_STATE.md`
- `control/NEXT_ACTIONS.md`
- `control/DECISION_LOG.md`

### Remaining follow-through
The final step is still to wire the breadth validator directly into:
- `send_report.py`
- `.github/workflows/send-weekly-report.yml`

so that non-compliant production reports fail before subscriber delivery.

---

## 2026-04-23 — Adopt English-canonical plus Dutch-companion bilingual delivery pattern
### Decision
ETF bilingual publication should use one canonical English pro report and one Dutch companion report derived from that completed English report.

### Chosen architecture
- **English pro report** remains the canonical production report for the run
- **Dutch pro companion** is a faithful language render, not a second research pass
- **One lane artifact** remains tied to the English canonical report only
- **Paired filenames** are used for English and Dutch outputs by matching date and version
- **One workflow run** may now validate, render, and send both language versions when a matching Dutch companion exists
- **Two separate emails and two PDFs** are sent when the bilingual pair exists

### Reason
This preserves analytical determinism while allowing premium bilingual distribution with minimal drift risk.

### Files updated
- `etf-pro.txt`
- `etf-pro-nl.txt`
- `send_report.py`
- `.github/workflows/send-weekly-report.yml`
- `control/BILINGUAL_OUTPUT_RULES.md`
- `control/NL_TERMINOLOGY.md`
- `control/SYSTEM_INDEX.md`
- `control/DECISION_LOG.md`

---

## 2026-04-27 — Add first lab-only ETF optimization layer with PyPortfolioOpt
### Decision
ETF now includes a first **lab-only optimization workbench** using PyPortfolioOpt and an explicit lab input contract.

### Chosen architecture
- `tools/generate_pyportfolioopt_optimization_lab.py`
- `.github/workflows/lab-pyportfolioopt-optimization.yml`
- `docs/ETF_OPTIMIZATION_LAB.md`
- `lab_inputs/README.md`
- `lab_inputs/etf_optimizer_prices_template.csv`
- `lab_inputs/etf_optimizer_constraints_template.json`
- `lab_inputs/etf_optimizer_views_template.json`

### Reason
The optimization bucket in the systematic-trading reference repo remained one of the most relevant unharvested areas for Weekly Reviews, especially for ETF and later Index. A low-risk first step is to add a separate optimization lab rather than trying to force optimizer output into the production review flow immediately. PyPortfolioOpt’s current documentation and repository describe support for classical efficient frontier optimization, Black-Litterman allocation, and hierarchical risk parity, which makes it a strong first tool for this lab layer. citeturn539570search1turn539570search2turn539570search3

### Consequence
- ETF now has a manual, artifact-only optimizer layer
- optimizer runs depend on explicit lab inputs rather than silently inferred production state
- the optimization layer does not send email and does not override the ETF decision framework
- the next likely extension, if useful, is a Riskfolio-Lib comparison layer for richer constrained-risk research. Riskfolio-Lib’s current docs describe support for hierarchical clustering portfolios and a wide range of risk measures and constraints, which is why it remains the strongest second candidate after PyPortfolioOpt. citeturn539570search0turn539570search5

---

## 2026-04-27 — Use yfinance as the first auto-fetch history source for the ETF optimization lab
### Decision
The ETF optimization lab should auto-populate its long daily ETF history with **yfinance** before each manual optimizer run.

### Chosen architecture
- `tools/fetch_etf_optimizer_prices_yfinance.py`
- `lab_inputs/etf_optimizer_fetch_config.json`
- updated `.github/workflows/lab-pyportfolioopt-optimization.yml` to fetch first, optimize second

### Reason
The systematic-trading reference repo highlighted free and partly free market-data options, and the cleanest first ETF history source for this lab is yfinance directly. The current yfinance API docs show `yfinance.download` supports multiple tickers, daily intervals, `period` or `start/end`, and returns market data in one call. OpenBB’s ETF historical docs also show ETF history can be requested with `provider='yfinance'`, which confirms that yfinance-backed ETF history is a reasonable first source for this lab layer. citeturn449898search2turn449898search1turn691774search0

### Consequence
- the ETF lab no longer depends only on a hand-maintained starter CSV
- the optimizer can now run on a longer fetched ETF history with the same manual workflow entrypoint
- yfinance remains a **lab-only** history source here and does not become the production pricing authority automatically
- if the fetched-history path proves useful, a later option is to compare or replace it with an OpenBB wrapper using the same underlying provider. citeturn691774search0turn691774search2

---

## 2026-04-27 — Introduce a minimum explicit ETF state model aligned to FX direction
### Decision
ETF should now have a first **minimum explicit production state layer** instead of relying only on prior-report parsing and prompt continuity.

### Chosen architecture
- `tools/write_etf_minimum_state.py`
- `.github/workflows/refresh-etf-state-from-report.yml`
- `output/etf_portfolio_state.json`
- `output/etf_valuation_history.csv`
- `docs/ETF_MINIMUM_STATE_MODEL.md`
- a pre-send derivation check in `.github/workflows/send-weekly-report.yml`

### Reason
FX already showed the value of machine-readable implementation state for continuity, validation, and downstream tooling. ETF is not ready to mirror the full FX state stack yet, but it is ready for the minimum pair of files that establishes current portfolio state and valuation history explicitly. The right first step is to derive these from the canonical English pro report, specifically Section 15 for holdings/totals and Section 7 for valuation history, while keeping the design compatible with later extensions such as trade ledger and recommendation scorecard.

### Consequence
- ETF now has a minimum machine-readable state layer on `main`
- the production send path now validates that the latest pro report can be converted into that minimum state model before delivery
- state persistence is handled by a dedicated repo-native refresh workflow rather than a riskier commit-from-send step
- the next state extensions should be `output/etf_trade_ledger.csv` and `output/etf_recommendation_scorecard.csv`
- ETF remains behind FX in state maturity, but the authority model is now moving in the same direction for uniformity
