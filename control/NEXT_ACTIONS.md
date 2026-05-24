# ETF Review OS — Next Actions

## Status legend
- `[USER]` = must be done manually by you in UI or external systems
- `[ASSISTANT]` = I can do directly in chat/repo
- `[JOINT]` = I prepare, you apply/approve

---

## Phase 1 — protect the validated runtime and delivery baseline

### 1. Keep using the control-layer start sequence
- Owner: `[JOINT]`
- Status: active standing rule
- Action: every meaningful ETF architecture, debugging, prompt, state, workflow, delivery, discovery, localization, or lab-optimization session starts with:
  1. `control/SYSTEM_INDEX.md`
  2. `control/CURRENT_STATE.md`
  3. `control/NEXT_ACTIONS.md`
  4. only then the minimum relevant execution file(s)
- Done when: sessions no longer rediscover the architecture.

### 2. Treat the current runtime + delivery HTML path as the production baseline
- Owner: `[JOINT]`
- Status: active baseline
- Current baseline:
  ```text
  pricing audit
  → historical relative strength
  → first-pass lane discovery
  → targeted challenger pricing
  → final lane discovery
  → runtime state
  → EN/NL markdown render
  → full valuation-history Section 7 equity curve
  → pricing-basis disclosure
  → polish/linkify
  → Dutch localization contract pass
  → equity-curve history validation
  → Dutch language quality validation
  → bilingual numeric parity validation
  → delivery HTML overrides
  → bilingual delivery HTML contract validation
  → PDF/email delivery
  ```
- Action: do not repair strict branded sections through markdown post-processing.
- Done when: Section 2, Current Position Review, Portfolio Rotation Plan, Vervangingsanalyse, and Section 7 equity curve stay governed by runtime/delivery contracts and validator checks.

### 3. Keep workflow behavior operational only
- Owner: `[ASSISTANT]`
- Status: active standing rule
- Action:
  - production send workflow should be for production report-output pushes, manual dispatch, or safe run-queue requests only
  - code changes should not silently resend subscriber emails
  - do not claim delivery success without a real receipt, manifest, or explicit user confirmation of received delivery
- Done when: delivery status remains verifiable.

### 4. Protect the full valuation-history equity curve
- Owner: `[ASSISTANT]`
- Status: done / active regression guard
- Result:
  - Section 7 now uses `output/etf_valuation_history.csv` plus current runtime NAV.
  - The embedded equity-curve chart now shows intermediate valuation dates.
  - `tools/validate_etf_equity_curve_history.py` is wired into `.github/workflows/send-weekly-report.yml`.
  - Workflow marker: `ETF_EQUITY_CURVE_HISTORY_OK`.
- Action going forward:
  - do not hardcode Section 7 as only start/latest
  - if valuation history changes, preserve Section 7 ↔ Section 15 reconciliation
- Done when: every fresh report has at least the historical valuation points plus current NAV and latest Section 7 NAV reconciles with Section 15 total NAV.

---

## Phase 1B — implement ETF pricing-lineage contract

### 5. Use `ETF_PRICING_LINEAGE_CONTRACT_V1` as authority
- Owner: `[ASSISTANT]`
- Status: active priority
- Source files:
  - `control/ETF_PRICING_LINEAGE_CONTRACT_V1.md`
  - `control/ETF_PRICING_LINEAGE_CHANGELOG.md`
- Action:
  - treat the fresh-closing-price issue as unresolved until the contract is implemented
  - track all pricing-lineage changes in the dedicated changelog
  - preserve root `changelog.md` visibility for repo-level changes
- Done when: the contract is implemented and the hard lineage validator passes before delivery.

### 6. Add immutable run identity and manifest
- Owner: `[ASSISTANT]`
- Status: next implementation step
- Target files:
  - `pricing/run_pricing_pass.py`
  - `pricing/audit_writer.py`
  - `.github/workflows/send-weekly-report.yml`
  - new `output/run_manifests/` writer/helper as needed
- Action:
  - create a run id for each production pricing run
  - write immutable audit files using requested close date plus run id
  - write a central run manifest under `output/run_manifests/`
  - pass exact audit/runtime/report paths through later workflow steps instead of reselecting latest files
- Done when: one report can be traced to one exact audit and manifest.

### 7. Upgrade price row schema and status semantics
- Owner: `[ASSISTANT]`
- Status: planned
- Target files:
  - `pricing/models.py`
  - `pricing/clients/twelve_data.py`
  - `pricing/clients/yahoo_history.py`
  - `pricing/clients/fmp.py`
  - `pricing/clients/alpha_vantage.py`
  - `pricing/source_registry.yaml`
  - `pricing/symbol_resolver.py`
- Action:
  - add selected close, selected close type, provider symbol, provider exchange where available, finality flag, verification block, and pricing tier
  - replace generic fresh labels with `fresh_exact_close`, `fresh_exact_unverified`, `prior_valid_close`, `carried_forward`, `unresolved`, and `blocked`
- Done when: no close row can be mislabeled fresh when the returned close date differs from the requested close date.

### 8. Persist successful ETF valuation state
- Owner: `[ASSISTANT]`
- Status: planned
- Target files:
  - `runtime/build_etf_report_state.py`
  - `runtime/render_etf_report_from_state.py`
  - state writer/helper as needed
  - `output/etf_portfolio_state.json`
  - `output/etf_valuation_history.csv`
- Action:
  - update canonical portfolio state after successful pricing/runtime valuation
  - append or replace the current requested close date in valuation history deterministically
  - ensure future runs start from the last successful priced state, not stale report-derived values
- Done when: the latest successful report NAV equals persisted portfolio state and valuation history.

### 9. Enforce challenger pricing tiers
- Owner: `[ASSISTANT]`
- Status: planned
- Target files:
  - `pricing/augment_challenger_pricing.py`
  - `runtime/discover_etf_lanes.py`
  - `runtime/score_etf_lanes.py`
  - replacement-duel validator files
- Action:
  - keep broad discovery candidates research-grade
  - require valuation-grade pricing for replacement-duel challengers
  - require valuation-grade pricing before any promoted challenger is shown as fundable/actionable
- Done when: broad discovery is still efficient, but fundable challengers cannot appear without valuation-grade pricing.

### 10. Add hard pricing-lineage validator
- Owner: `[ASSISTANT]`
- Status: planned
- Target file:
  - `tools/validate_etf_pricing_lineage_contract.py`
- Action:
  - validate manifest → audit → runtime state → report tables → Section 7 NAV → Section 15 NAV → persisted portfolio state → valuation history
  - fail before render/send if any piece diverges
- Done when: a visible close-price disclosure is no longer enough; the full lineage must pass.

---

## Phase 2 — Dutch premium report quality roadmap

### 11. Maintain the Dutch quality roadmap
- Owner: `[ASSISTANT]`
- Status: started
- Source files:
  - `control/NL_REPORT_QUALITY_ROADMAP.md`
  - `control/NL_REPORT_LANGUAGE_CONTRACT.md`
  - `control/NL_TERMINOLOGY.md`
- Action:
  - keep roadmap phases explicit
  - do not let one-off Dutch phrase fixes replace the language-contract layer
- Done when: Dutch report improvements are tracked as an operating roadmap, not ad-hoc fixes.

### 12. Block mixed English/Dutch sentences before next Dutch publication
- Owner: `[ASSISTANT]`
- Status: implemented; needs test run
- Changed files:
  - `runtime/nl_localization.py`
  - `tools/validate_etf_dutch_language_quality.py`
- Action:
  - validate that mixed sentences such as `Keep SMH...`, `but vers kapitaal...`, `Require replacement duels...`, and `Aanhouden under review` fail before send
- Done when: the Dutch language quality validator fails any mixed-language decision sentence.

### 13. Translate table headers and enum values through controlled mappings
- Owner: `[ASSISTANT]`
- Status: implemented; needs test run
- Changed files:
  - `runtime/nl_localization.py`
  - `runtime/apply_nl_localization.py`
  - `control/NL_TERMINOLOGY.md`
- Action:
  - validate table labels such as Theme, Primary ETF, Why it matters, Existing, Yes, No, None, Hold, Add, Current status, Why I’m considering it
- Done when: table labels and enum values in the Dutch report are mapped through the Dutch terminology contract.

### 14. Remove internal workflow language from the Dutch client report
- Owner: `[ASSISTANT]`
- Status: implemented; needs test run
- Changed files:
  - `runtime/nl_localization.py`
  - `tools/validate_etf_dutch_language_quality.py`
- Action:
  - block `Section`, `runtime`, `state-led`, `output/`, `pricing_audit`, `workflow`, `manifest`, `artifact`, and placeholder language where client-facing
- Done when: operational runbook terms remain in audit/manifest files only.

### 15. Replace low-quality literal translations
- Owner: `[ASSISTANT]`
- Status: implemented; needs test run
- Changed files:
  - `runtime/nl_localization.py`
  - `control/NL_TERMINOLOGY.md`
- Action:
  - replace `verdiende leider`, `prijsbewijs`, `actiebias`, `thesisfit`, `reviewpositie`, `nuttige ballast`, `vers kapitaal`
- Done when: executive sections and tables use institutional Dutch such as `best onderbouwde kernpositie`, `koersbevestiging`, `beslissingsrichting`, `aansluiting op de beleggingscase`, and `positie onder actieve herbeoordeling`.

### 16. Make Dutch cover and chart language Dutch
- Owner: `[ASSISTANT]`
- Status: implemented; needs render test
- Changed file:
  - `send_report_runtime_html.py`
- Action:
  - validate Dutch delivery HTML/PDF cover no longer shows Investor Report, Analyst Report, PRIMARY REGIME, GEOPOLITICAL REGIME, MAIN TAKEAWAY
  - validate chart labels are Dutch where practical
- Done when: Dutch PDF cover and equity-curve labels read as Dutch client-facing output.

### 17. Native Dutch templates for key sections
- Owner: `[ASSISTANT]`
- Status: planned after first test result
- Target files:
  - `runtime/render_etf_report_from_state.py`
  - `runtime/apply_nl_localization.py`
  - `runtime/nl_localization.py`
- Action:
  - render Kernsamenvatting, Conclusie, Portefeuille-acties, Review huidige posities and Vervangingsanalyse from runtime state using Dutch-native templates rather than sentence-by-sentence translation
- Done when: these sections read as originally written Dutch.

### 18. Human-readable Dutch glossary per section
- Owner: `[ASSISTANT]`
- Status: started
- Source file:
  - `control/NL_TERMINOLOGY.md`
- Action:
  - expand glossary when new sections/tables are added
- Done when: changing Dutch report wording requires one terminology update plus one code mapping if needed.

---

## Phase 3 — ChatGPT-triggerable report generation

### 19. Use safe report request queue for ChatGPT-initiated fresh reports
- Owner: `[ASSISTANT]`
- Status: active baseline
- Action: when the user asks ChatGPT to generate a fresh Weekly ETF Review, create a request file under:
  ```text
  control/run_queue/weekly_etf_report_request_YYYYMMDD_HHMMSS.md
  ```
- Do not create trigger files under `output/`.
- Done when: the send workflow is triggered by the run-queue request path and no placeholder report files are introduced.

### 20. Run one Dutch quality confirmation workflow
- Owner: `[JOINT]`
- Status: deferred behind pricing-lineage implementation unless specifically requested
- Action:
  - trigger a fresh report only after the user agrees to test the Phase 1 Dutch quality changes
  - inspect validator output and the received PDF
- Done when: the Dutch report passes automated validators and visual inspection for premium Dutch language quality.

---

## Phase 4 — improve portfolio decision quality

### 21. Continue direct challenger-vs-current-holding scoring
- Owner: `[ASSISTANT]`
- Action:
  - map challenger lanes to likely funded holdings they could replace
  - compare challenger 1m and 3m returns directly versus the target holding
  - add direct replacement edge to lane scoring
  - add direct duel fields to lane artifacts
  - surface the direct edge in replacement-duel notes
- Done when: replacement candidates are compared against the actual holding they would replace, not only versus SPY.

### 22. Expand and curate the discovery universe
- Owner: `[ASSISTANT]`
- Source file:
  - `config/etf_discovery_universe.yml`
- Action:
  - add additional sectors, factor ETFs, region ETFs, commodity ETFs, defensive exposures, and non-U.S. exposures
  - keep each lane investable, differentiated, and scored
- Done when: the universe is broad enough to surface new candidates without becoming noisy.

### 23. Add better macro/fundamental freshness inputs
- Owner: `[ASSISTANT]`
- Action:
  - add machine-readable macro/regime input file
  - add policy/geopolitical catalyst tags
  - add current official or market-based freshness notes where possible
- Done when: discovery is no longer only config-driven.

---

## Current checkpoint

**The active engineering checkpoint is now ETF pricing-lineage hardening. The close-price disclosure table is visible and internally useful, but the fresh-closing-price issue remains open until immutable audit identity, explicit run manifests, state persistence, challenger pricing tiers, and the hard pricing-lineage validator are implemented.**
