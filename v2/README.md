# Weekly ETF Review — v2

A weekly, rules-based model portfolio of European UCITS ETFs, published as a
4-page report in Dutch and English. Goal and definition of done: `../OUTCOME.md`;
working rules for AI assistants: `../AGENTS.md`. The previous setup is archived in branch
`archive/v1-pre-outcome-model-2026-11-15`.

**Design rule:** code computes and decides; the AI only writes commentary, and
every number in that commentary must already exist in the computed facts.

## The weekly cycle

`.github/workflows/v2-weekly.yml` runs every **Thursday 05:00 UTC** on
**Wednesday's** closing prices (`python -m v2.run_weekly`):

1. **Prices** – daily EUR closes for the universe (Yahoo) → `state/prices.csv`.
2. **Cross-check** – every held position against Alpha Vantage. Missing price or
   >1% disagreement **blocks** the run. Verifier missing → flagged, run continues.
3. **Decide** – rank the universe, apply `policy.yml`, produce trades with reasons.
4. **Save state** – `state/portfolio.json`, `trades.csv`, `valuations.csv`, `history.csv`.
5. **Report** – facts → commentary (AI or fixed fallback) → PDF ×2 → checks.
6. **Deliver** – per `delivery.yml` (`off` / `trial` / `live`).
7. **Commit** – state and report are committed **only if every step succeeded**.
   A failed run leaves the saved state untouched, alerts the owner, and can
   simply be rerun. A second run for the same week does nothing.

Rehearsal (Actions → *Weekly ETF Review (v2)* → *Run workflow*, rehearsal on):
replays the latest saved week on a scratch copy, sends the email to the owner
only, and never touches the saved state.

## Portfolio design

- **Core (fixed):** VWCE (world equity) + EUNA (global bonds, EUR-hedged), 57% in normal markets, max 60%.
  Kept on purpose: an 11-year test (2016–2026) showed that dropping the core adds volatility
  without adding return (see the decision of 2026-11-15).
- **Satellites:** 5 slots of ~8% (3 when defensive), chosen weekly from the scan.
- **Inflation rule:** when euro-area inflation (latest published HICP y/y) is ≥ 3% and not
  lower than 3 months earlier, the bond core is held in IBGS (short euro government bonds)
  instead of EUNA. The switch is one change (sell + buy together). Missing or stale
  inflation data never triggers a switch. Adopted 2026-11-15 after `research.py`
  (train 2016–21 / test 2022–26): the only one of four candidate improvements that
  held up out of sample — on a single inflation episode, so treat it as a risk rule.
- **Positioning:** the aim is to keep up with the benchmark while limiting large losses.
  Research found no statistically demonstrable alpha (standard error ≈ 2–3 pts/yr);
  the report must not claim or imply outperformance.
- **Reference funds** (`sleeve: reference`, e.g. IWDA, SXR8): shown for context, never bought.
- **Benchmark:** 70% VWCE / 30% EUNA, rebalanced weekly — the same risk balance as the core.
  The defensive switch uses VWCE's own trend (`trend_reference`).

## Files

| File | Role |
|---|---|
| `universe.yml` | Every instrument the scan may rank (ISIN, EUR line, role, tags, verification status) |
| `policy.yml` | The investment rules (core, satellites, defensive switch, cash, turnover, costs) and the benchmark |
| `delivery.yml` | `off` / `trial` (owner only) / `live` (readers) |
| `sources.py` | Price sources (Yahoo primary, Alpha Vantage cross-check) |
| `market.py` | Refresh `state/prices.csv` |
| `engine.py` | `scan()` ranking and `decide()` trades — pure functions, no network |
| `macro.py` | ECB, New York Fed, Eurostat indicators with dates and staleness flags |
| `facts.py` | Every number the report may state, incl. attribution vs the benchmark |
| `narrate.py` | AI commentary + number check; deterministic fallback text |
| `render.py` | HTML/PDF layout and layout checks |
| `mailer.py` | Email (addresses only from secrets; repo and logs are public) |
| `run_weekly.py` | The weekly cycle above |
| `acceptance.py` | Checks against `OUTCOME.md` (run on every PR: `python -m v2.acceptance`) |
| `simulate.py`, `probe.py`, `backfill.py` | Historical test, source probe, one-off backfill from 14 Aug 2026 |

## Secrets

| Secret | Use |
|---|---|
| `ALPHA_VANTAGE_API_KEY` | Cross-check of held positions |
| `MRKT_RPRTS_SMTP_HOST/PORT/USER/PASS`, `MRKT_RPRTS_MAIL_FROM` | Sending |
| `MRKT_RPRTS_MAIL_TO`, `MRKT_RPRTS_MAIL_TO_NL` | Readers (live mode) |
| `V2_TRIAL_TO` (optional) | Owner address for trial emails and alerts; falls back to `MRKT_RPRTS_MAIL_FROM` |
| `OPENAI_API_KEY` (optional) | AI commentary; without it the fallback text is used |

## Operating

- **Go live:** set `mode: live` in `delivery.yml` (one commit).
- **Change a rule:** edit `policy.yml`, then run `python -m v2.simulate` and compare
  `evidence/simulation_*` before committing.
- **Add a fund:** add it to `universe.yml` with `status: to_verify`, run the probe
  (`python -m v2.probe`), then set `status: verified` if the EUR line and name match.
- **A run failed:** read the alert's log link. `RUN_BLOCKED` lines say why
  (missing/disagreeing price, market closed, report check). Fix, then rerun the
  workflow manually with rehearsal off.

## Known limits

- Price returns only: distributions of `Dist` funds are not added back.
- Yahoo is an unofficial source and Alpha Vantage likely shares its exchange feed;
  the cross-check catches wrong symbols and dates, not a shared bad print.
- The number check proves every number exists in the facts, not that it is
  attached to the right item.
- The historical test uses a universe chosen in Nov 2026 (hindsight bias).
