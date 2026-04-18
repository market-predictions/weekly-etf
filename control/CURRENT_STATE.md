# ETF Review OS — Current State

## Snapshot date
2026-04-18

## What this repository currently is

This repository is now a production-style weekly ETF review system with:
- a production masterprompt in `etf.txt`
- a premium editorial layer in `etf-pro.txt`
- a delivery/rendering script in `send_report.py`
- a production GitHub Actions workflow for execution and email delivery
- a non-email validation workflow for runtime and pricing changes
- archived outputs in `output/`
- a control layer in `control/`
- an as-is split scaffold in `prompts/as_is_split/`
- a split-test workflow in `.github/workflows/send-weekly-report-split-test.yml`
- a split-test output folder in `output_split_test/`
- a starter pricing subsystem in `pricing/` on `main` for quota-aware ETF close retrieval and audit output

## What changed in this step

The production ETF prompt has now been updated directly to move from a small fixed structural-lane gate toward:
- broad internal discovery across investable domains
- dynamic candidate-lane construction
- compact executive publication of the best-ranked lanes
- stronger continuity memory for retained, new, dropped, and near-miss lanes

A first implementation slice of an explicit ETF pricing subsystem is now merged into `main`. This includes:
- source registry and rate-limit config
- cache and budget manager
- symbol-driven close resolver
- API clients for Twelve Data, FMP, and Alpha Vantage
- FX resolver
- pricing-pass CLI entrypoint
- pricing audit output folder scaffold

A follow-up repair pass has also now aligned the pricing models, cache helpers, and close resolver after merge-conflict drift.

Workflow safety has also been tightened:
- the production send workflow now triggers only on production ETF report output pushes
- a separate validation workflow now handles pricing, prompt, and runtime code changes without sending email

This moves ETF toward explicit implementation state rather than relying only on ad hoc retrieval inside the prompt, while reducing the risk of duplicate subscriber emails from non-report code changes.

## Current strengths

- Strong executive look & feel in the ETF report family.
- Clear client-grade delivery standard.
- Production report, pro-editing layer, and delivery script already exist.
- GitHub remains the live source of truth.
- The control layer exists and now reflects the direct-production architecture choice.
- The production prompt now has a broader thematic discovery model with a compact publication filter.
- The premium editorial layer still protects a calm, selective, subscriber-facing tone.
- A quota-aware pricing subsystem starter now exists on `main` and can evolve into the explicit state/input layer.
- Validation and sending are now separated more cleanly at the workflow layer.

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

### 2. Explicit ETF state files still do not yet exist in production
ETF still relies mainly on prior report parsing and the pricing-pass logic inside `etf.txt` on main.
Planned future state files remain:
- `output/etf_portfolio_state.json`
- `output/etf_trade_ledger.csv`
- `output/etf_valuation_history.csv`
- `output/etf_recommendation_scorecard.csv`
- `output/pricing/price_audit_YYYYMMDD.json`

### 3. Delivery-layer review is still needed against the new discovery model
The prompt now supports broader internal discovery and stronger lane continuity memory, but the rendering layer still needs practical review for:
- variable radar composition
- continuity language placement
- compact HTML/PDF behavior
- appendix cleanliness

### 4. The pricing subsystem is only a starter slice so far
Still pending:
- issuer-page handlers
- Yahoo fallback parser
- richer holding snapshots and valuation-state outputs
- direct prompt consumption of the pricing audit
- explicit shortlist pricing for challengers and alternatives

### 5. Live production monitoring is still needed
The updated architecture should now be validated through normal live production runs to confirm:
- no radar bloat
- no drift in executive tone
- no rendering regressions
- better surfacing of previously omitted categories
- stable pricing-pass behavior under free-tier rate limits

## Target architecture

### ChatGPT side
- One dedicated ChatGPT Project called **ETF Review OS**.
- Project instructions that reinforce the operating model.
- A lean bootstrap model using `control/PROJECT_BOOTSTRAP.md` as the default standing upload.
- Live GitHub reads for changing repo files.

### GitHub side
- GitHub remains the source of truth for prompts, scripts, workflows, outputs, and control docs.
- The production prompt now uses open discovery + dynamic lane ranking + compact publication.
- The split scaffold remains available as a reference and optional architecture workbench, not as a required gate for this change.
- ETF is moving toward an explicit pricing/state layer in `pricing/` plus machine-readable audit output in `output/pricing/`.

### Delivery side
- Delivery remains in `send_report.py` plus GitHub Actions.
- `etf-pro.txt` remains the premium editorial compression layer.
- The ETF executive look & feel remains the non-negotiable presentation reference for the report family.
- Production email send is now gated to actual production report output pushes.
- Runtime and pricing code changes are now validated separately without sending email.

## Immediate priorities

### Priority A — validate live dynamic discovery in production
Still required:
- confirm broader internal discovery does not weaken executive selectivity
- confirm the published radar remains compact and decision-useful
- confirm lane entry/exit language reads naturally in the premium layer

### Priority B — review rendering and delivery behavior
Still required:
- review `send_report.py`
- confirm HTML/PDF rendering remains clean with variable radar composition
- confirm the continuity-memory additions do not create visual clutter

### Priority C — move ETF toward explicit implementation state
Still required:
- extend the pricing subsystem beyond the starter layer
- add explicit ETF state files
- make valuation authority less dependent on report parsing
- tighten deterministic conflict resolution between report intent and implementation facts

### Priority D — reduce monolith risk later without weakening production
Still required:
- keep the four-layer architecture explicit in future changes
- gradually move boundary logic out of the monolith where safe
- preserve production reliability and executive presentation quality while doing so

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

### Can be done by assistant
- refine the production prompt
- refine the premium editorial layer
- update GitHub control files
- review and improve scripts/workflows
- strengthen pricing/state authority rules
- harden continuity logic and executive presentation behavior
- extend the starter pricing subsystem

## Current status label

**Production prompt updated for open discovery + dynamic lane ranking, compact executive publication preserved; a starter pricing subsystem is now merged on `main`, workflow safety has been tightened so non-report code changes do not send subscriber email, and the next step is to extend the explicit pricing/state layer toward real production valuation authority.**
