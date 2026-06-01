# PDF visual audit — Weekly ETF reports 2026-06-01

## Date
2026-06-01

## Files visually inspected

```text
weekly_analysis_pro_260601_04.pdf
weekly_analysis_pro_nl_260601_04.pdf
```

## Overall result

The latest PDFs render and the major state/pricing fixes are visible. However, the visual audit found several client-facing polish issues that should be fixed before treating this as the final premium baseline.

## Confirmed good

### 1. Dutch chart labels are fixed

The Dutch equity-curve chart uses Dutch labels:

```text
Portefeuillecurve (EUR)
Portefeuillewaarde (EUR)
Datum
```

This confirms the chart-label fix reached the PDF asset, not just markdown.

### 2. Pricing-basis disclosure is visible and complete for active holdings

The pricing disclosure tables show active holdings and EUR/USD with requested date, used date, close/rate, source and status.

### 3. Post-execution portfolio state appears in Section 15 / Section 8

The current-holdings tables show the post-execution active state including CIBR and reduced PPA.

### 4. No obvious black boxes, missing fonts or broken glyphs

The main visual render is stable; tables are dense but generally readable.

## Issues found

### P1 — Dutch replacement analysis is duplicated

In the Dutch PDF, the replacement analysis appears once as an unnumbered table, then the `11 Vervangingsanalyse` section header appears below it, followed by the same table again on the next page.

Observed around Dutch PDF pages 11-12.

Expected:

```text
One section heading
One replacement-analysis table
No duplicate table
```

Likely root cause: the replacement-duel table is injected once as a loose block and once as a numbered section, or the section-ordering logic treats the original markdown section number as a second render target.

### P1 — English section numbering/order has a visible jump

The English analyst report shows `4 Best New Opportunities`, then `11 Replacement Duel Table`, then `5 Portfolio Rotation Plan`. The table itself continues on the following page.

Expected analyst-report numbering should be sequential or the replacement-duel block should not carry stale section number `11` inside the compact analyst report.

### P1 — Position-change wording conflicts with idempotent execution status

Both reports correctly say guarded model rotation is already reflected and no duplicate state/ledger mutation was performed in this run. But later sections are titled as if trades were executed in this same run:

```text
Position changes executed this run
Positiewijzigingen in deze run
```

This is confusing after idempotency protection has already marked the run as no duplicate execution.

Recommended wording:

```text
Position changes reflected in official state
Positiewijzigingen verwerkt in de officiële portefeuillestaat
```

or:

```text
Latest guarded model changes
Laatste bewaakte modelwijzigingen
```

### P1 — Dutch report still contains English execution notes

Dutch position-change notes still include English text such as:

```text
Guarded auto-execution: reduce PPA to fund CIBR.
Guarded auto-execution: buy CIBR funded by PPA.
```

Expected Dutch:

```text
Bewaakte modeluitvoering: PPA verlaagd om CIBR te financieren.
Bewaakte modeluitvoering: CIBR gekocht, gefinancierd uit PPA.
```

### P2 — Portfolio action snapshot is semantically confusing after reflected execution

The first-page summary says no reflected replace/reduce, while later rotation/position-change sections show PPA reduced and CIBR bought/reflected.

The model should distinguish:

```text
No new duplicate mutation in this rerun
```

from:

```text
The official state already includes the PPA -> CIBR rotation
```

### P2 — First visible section starts at 2

Both investor-report PDFs appear to start the visible numbered content at section 2. This may be intentional if the hero summary is considered section 1, but visually it looks like Section 1 is missing. Consider either showing `1 Kernsamenvatting / Executive summary` or removing numeric sequencing from the first investor-report card set.

### P2 — Dense tables remain readable but not premium

The structural radar, position-performance and final-action tables are readable, but dense. This is acceptable for a validation run but should be improved for premium client-grade delivery if time allows.

## Recommended next fixes

1. Fix replacement-duel rendering/section numbering so English and Dutch compact analyst sections are sequential and non-duplicated.
2. Normalize idempotent execution wording in both languages.
3. Localize Dutch execution-note strings in the position-change table.
4. Clarify first-page action snapshot to separate `already reflected` from `new mutation this run`.
5. Add visual/PDF validation fixture or lightweight text validator for duplicate replacement tables and English residue in Dutch execution notes.

## Status

```text
workflow and validators: green
PDF visual audit: pass with client-facing polish defects
email delivery proof: still not proven because delivery_manifest_path is null
```
