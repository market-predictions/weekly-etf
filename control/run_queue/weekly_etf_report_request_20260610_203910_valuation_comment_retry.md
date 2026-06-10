# Weekly ETF report request — valuation history comment scrub retry

## Purpose

Retry the weekly ETF delivery after adding a post-render contract scrub for stale Section 7 valuation-history comments.

## Fixes included before this retry

```text
e058a6cdef9650627d0904a50da6c568bf2e9342 — Sanitize valuation history comments in report contract
c5696f1f0f5b26a625eb8739418d29a34ec1a574 — Test valuation history comment scrub
```

## Problem being verified

The prior `_07` delivery correctly removed the stale current-action wording:

```text
GLD → GSG guarded model rotation
```

but Section 7 still exposed historical client-facing valuation comments that sounded like current GLD/PPA state:

```text
Fresh five-of-six pricing recovery; GLD carried forward
Fresh five-of-six repricing; PPA carried forward
Prijsherstel voor vijf van zes posities; goudpositie doorgeschoven
Verse herprijzing voor vijf van zes posities; PPA doorgeschoven
```

## Required validation focus

Fresh English and Dutch reports/PDFs must not contain the stale client-facing phrases above.

Expected neutral replacements:

```text
Partial pricing recovery using latest verified marks
Partial fresh repricing using latest verified marks
Gedeeltelijk prijsherstel op basis van laatst geverifieerde koersen
Gedeeltelijke herprijzing op basis van laatst geverifieerde koersen
```

## Constraints

This is wording/surface cleanup only.

No policy relaxation.
No scoring change.
No trade-intent change.
No execution-authority change.
No portfolio-state or trade-ledger mutation beyond the existing guarded workflow behavior.

## Operational note

Avoid additional direct commits to `main` while this workflow is running so the final artifact push can fast-forward cleanly.
