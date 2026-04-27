# ETF Review OS — Current State

## Snapshot date
2026-04-27

## What this repository currently is

This repository is now a production-style weekly ETF review system with:
- a production masterprompt in `etf.txt`
- a premium editorial layer in `etf-pro.txt`
- a delivery/rendering script in `send_report.py`
- a production GitHub Actions workflow for execution and email delivery
- a dedicated ETF state-refresh workflow for writing and committing explicit state files
- a non-email validation workflow for runtime and pricing changes
- archived outputs in `output/`
- a control layer in `control/`
- an as-is split scaffold in `prompts/as_is_split/`
- a split-test workflow in `.github/workflows/send-weekly-report-split-test.yml`
- a split-test output folder in `output_split_test/`
- a starter pricing subsystem in `pricing/` on `main` for quota-aware ETF close retrieval and audit output
- a lane-assessment artifact folder in `output/lane_reviews/`
- a helper validator script in `validate_lane_breadth.py`
- an explicit ETF state layer with:
  - `output/etf_portfolio_state.json`
  - `output/etf_valuation_history.csv`
  - `output/etf_trade_ledger.csv`
- a lab-only ETF optimization layer using PyPortfolioOpt
- a lab-only yfinance auto-fetch layer that can populate longer ETF history for the optimizer before each lab run

## What changed in this step

The ETF repository now contains the **next state-maturity step** toward the FX operating model.

The key additions and upgrades are:
- `tools/write_etf_minimum_state.py` now enriches current ETF positions with explicit action, target, score, role, continuity, and current-run change metadata derived from Sections 7, 13, 14, 15, and 16 of the canonical English pro report
- a new `tools/write_etf_trade_ledger.py` builds `output/etf_trade_ledger.csv` from explicit canonical report change rows
- `.github/workflows/refresh-etf-state-from-report.yml` now refreshes and commits the ETF trade ledger alongside portfolio state and valuation history
- `.github/workflows/send-weekly-report.yml` now validates both ETF state derivation and ETF trade-ledger derivation before send
- `output/etf_portfolio_state.json` is now seeded in the richer format
- `output/etf_trade_ledger.csv` now exists as the first ETF change-memory file
- `docs/ETF_MINIMUM_STATE_MODEL.md` now documents the enriched state layer rather than just the original minimum pair

This means ETF is now meaningfully closer to the **state maturity shape** of `weekly-fx`, even though ETF still remains more report-derived than FX.

## Current strengths

- Strong executive look & feel in the ETF report family.
- Clear client-grade delivery standard.
- Production report, pro-editing layer, and delivery script already exist.
- GitHub remains the live source of truth.
- The control layer exists and now reflects the direct-production architecture choice.
- The production prompt now has a broader thematic discovery model with a compact publication filter.
- The production prompt now also requires a mandatory breadth universe and matching lane artifact.
- The premium editorial layer still protects a calm, selective, subscriber-facing tone.
- The premium editorial layer now preserves compact omitted-lane visibility instead of hiding it.
- A quota-aware pricing subsystem starter now exists on `main` and can evolve into the explicit state/input layer.
- Validation and sending are now separated more cleanly at the workflow layer.
- The prompt can now consume a matching pricing audit as an operational input layer when available.
- ETF now has a richer explicit state layer with current portfolio state, valuation history, and a first trade ledger on `main`.
- The ETF optimization lab no longer depends only on a hand-maintained starter CSV; it can auto-populate longer ETF history with yfinance in the lab workflow.

## Current weaknesses

### 1. Production prompt monolith still exists
The production system still relies on `etf.txt` as a large combined prompt mixing:
- strategy logic
- state/input rules
- valuation protocol
- output rules
- delivery expectations
- workflow orchestration
- completion logic

### 2. Breadth enforcement is not yet fully wired into the production send path
The breadth logic is now live in:
- `etf.txt`
- `etf-pro.txt`
- `validate_lane_breadth.py`
- `output/lane_reviews/`

But the final delivery enforcement still needs to be wired more deeply into:
- `send_report.py`
- `.github/workflows/send-weekly-report.yml`

### 3. ETF state is now explicit and richer, but still report-derived
ETF no longer lacks state files, and it now has a first trade ledger. But the current state layer still derives from the canonical English pro report.

That means ETF has improved authority and continuity, but it still does not yet have a fully independent implementation engine equivalent to the more mature FX state model.

The next missing state file remains:
- `output/etf_recommendation_scorecard.csv`

### 4. The pricing subsystem is still evolving
Still pending:
- hardening issuer-page handlers through runtime validation
- evaluating whether Yahoo fallback remains necessary after API coverage testing
- explicit valuation-state outputs beyond report-derived state
- fuller prompt/report consumption of audit-derived state beyond pricing only

### 5. The optimization layer is still lab-only and still not production-authoritative
The new optimizer currently depends on:
- yfinance-fetched or manually supplied ETF lab prices in `lab_inputs/etf_optimizer_prices.csv`
- active fetch settings in `lab_inputs/etf_optimizer_fetch_config.json`
- optional lab constraints in `lab_inputs/etf_optimizer_constraints.json`
- optional lab views in `lab_inputs/etf_optimizer_views.json`

This is the correct next step, but it is still not the production ETF decision engine.

### 6. Live production monitoring is still needed
The updated architecture should now be validated through normal live production runs to confirm:
- no radar bloat
- no drift in executive tone
- no rendering regressions
- better surfacing of previously omitted categories
- stable pricing-pass behavior under free-tier rate limits
- clean use of matching pricing audits without stale carry-over
- correct one-to-one report and lane-artifact pairing
- stable ETF state refresh after each canonical pro report push
- stable ETF trade-ledger regeneration after each canonical pro report push

## Target architecture

### ChatGPT side
- One dedicated ChatGPT Project called **ETF Review OS**.
- Project instructions that reinforce the operating model.
- A lean bootstrap model using `control/PROJECT_BOOTSTRAP.md` as the default standing upload.
- Live GitHub reads for changing repo files.

### GitHub side
- GitHub remains the source of truth for prompts, scripts, workflows, outputs, and control docs.
- The production prompt now uses open discovery + dynamic lane ranking + compact publication.
- The production prompt now also requires a mandatory breadth universe and a matching lane artifact per report.
- The split scaffold remains available as a reference and optional architecture workbench, not as a required gate for this change.
- ETF is moving toward an explicit pricing/state layer in `pricing/` plus machine-readable audit output in `output/pricing/`.
- ETF is also moving toward a machine-readable lane-assessment layer in `output/lane_reviews/`.
- ETF now has an explicit state layer in:
  - `output/etf_portfolio_state.json`
  - `output/etf_valuation_history.csv`
  - `output/etf_trade_ledger.csv`
- ETF also has a lab-only optimization layer that can evolve later into a richer state-aware research stack once more explicit ETF state files exist.
- ETF also has a lab-only yfinance fetch layer that can auto-populate longer ETF history for optimizer runs while keeping production pricing authority separate.

### Delivery side
- Delivery remains in `send_report.py` plus GitHub Actions.
- `etf-pro.txt` remains the premium editorial compression layer.
- The ETF executive look & feel remains the non-negotiable presentation reference for the report family.
- Production email send is now gated to actual production report output pushes.
- Runtime and pricing code changes are now validated separately without sending email.
- The send path now checks that the latest pro report can derive the enriched ETF state model and the ETF trade ledger before delivery.
- The final step still required is to wire lane breadth validation directly into the render/send path more deeply if needed.

## Immediate priorities

### Priority A — validate live breadth behavior in production
Still required:
- confirm major omitted domains now appear as promoted lanes or compact challengers
- confirm the published radar remains compact and decision-useful
- confirm omitted-lane language reads naturally in the premium layer

### Priority B — finish send-path enforcement
Still required:
- wire `validate_lane_breadth.py` logic directly into `send_report.py`
- wire breadth validation into `.github/workflows/send-weekly-report.yml`
- fail before send if the report lacks the matching lane artifact or omitted-lane proof block

### Priority C — stabilize and extend explicit ETF state
Still required:
- validate the new state refresh workflow over normal live runs
- confirm state files stay in sync with the canonical English pro report
- confirm trade-ledger rows stay in sync with explicit Section 14 change rows
- add `output/etf_recommendation_scorecard.csv`
- make valuation authority less dependent on report parsing over time
- tighten deterministic conflict resolution between report intent and implementation facts

### Priority D — reduce monolith risk later without weakening production
Still required:
- keep the four-layer architecture explicit in future changes
- gradually move boundary logic out of the monolith where safe
- preserve production reliability and executive presentation quality while doing so

### Priority E — validate whether the optimization lab is useful enough to keep extending
Still required:
- use the yfinance auto-fetch path to generate a real longer ETF history
- run the manual optimizer workflow again on fetched history
- inspect whether optimizer outputs add insight without weakening breadth discipline
- decide whether the next extension should be a Riskfolio-Lib comparison layer or whether the optimizer should stay a thin QA tool only

## Recommended session start sequence

For any future ETF architecture session:
1. read `control/SYSTEM_INDEX.md`
2. read this file
3. read `control/NEXT_ACTIONS.md`
4. only then open the specific execution file relevant to the task

## Current role split

### Manual by user
- maintain the ChatGPT Project bootstrap model
- add and manage repository secrets in GitHub UI
- review live report quality as subscriber/end-user
- review and merge implementation PRs when appropriate
- review or edit the ETF optimizer fetch config when optimization testing is desired

### Can be done by assistant
- refine the production prompt
- refine the premium editorial layer
- update GitHub control files
- review and improve scripts/workflows
- strengthen pricing/state authority rules
- harden continuity logic and executive presentation behavior
- extend the pricing subsystem
- extend lane breadth enforcement and validation
- extend the ETF explicit state layer
- extend the ETF optimization lab
- extend the ETF optimizer fetch layer

## Current status label

**The ETF production prompt and premium editorial layer now require a mandatory breadth assessment universe, a matching machine-readable lane artifact, and compact visibility for omitted-but-assessed lanes; ETF now also has a richer explicit state layer with `output/etf_portfolio_state.json`, `output/etf_valuation_history.csv`, and `output/etf_trade_ledger.csv`; the send path validates that both state derivation and trade-ledger derivation are possible before delivery; a dedicated workflow now refreshes and commits the ETF state files on canonical report pushes; and ETF also includes a first lab-only PyPortfolioOpt optimization layer plus a yfinance auto-fetch history path, while the next production-critical steps remain deeper send-path hardening and extending the explicit state model with a recommendation scorecard.**
