# Dutch ETF Report Quality Roadmap

## Goal

Turn the Dutch Weekly ETF Review into a standalone, premium Dutch investor report for professional readers at Dutch banks, wealth managers, and investment firms.

The Dutch report must remain numerically and analytically aligned with the English canonical report, but the Dutch wording, labels, tables and executive copy must read as native institutional Dutch.

---

## Phase 1 — Must fix before next Dutch publication

### 1. Block mixed English/Dutch sentences
- Status: in progress
- Implementation:
  - strengthen `runtime/nl_localization.py`
  - strengthen `tools/validate_etf_dutch_language_quality.py`
- Acceptance:
  - sentences such as `Keep SMH...`, `but vers kapitaal...`, `Require replacement duels...` fail validation.

### 2. Translate table headers and table enum values through fixed mappings
- Status: in progress
- Implementation:
  - expand canonical maps in `runtime/nl_localization.py`
  - use `control/NL_TERMINOLOGY.md` as human-readable contract
- Acceptance:
  - no client-facing `Theme`, `Primary ETF`, `Why it matters`, `Existing`, `Yes`, `No`, `None`, `Hold`, `Add`, `Current status` leakage except allowed official names/tickers.

### 3. Remove internal workflow language from the Dutch report
- Status: in progress
- Implementation:
  - block `Section`, `runtime`, `state-led`, `output/`, `pricing_audit`, `workflow`, `manifest`, `artifact`, `placeholder`
- Acceptance:
  - operational runbook terms remain in audit/manifest files, not in client-facing Dutch report.

### 4. Replace low-quality literal translations
- Status: in progress
- Implementation:
  - replace `verdiende leider`, `prijsbewijs`, `actiebias`, `thesisfit`, `reviewpositie`, `nuttige ballast`
- Acceptance:
  - executive sections use institutional Dutch: `best onderbouwde kernpositie`, `koersbevestiging`, `beslissingsrichting`, `aansluiting op de beleggingscase`, `positie onder actieve herbeoordeling`.

### 5. Make the cover fully Dutch
- Status: in progress
- Implementation:
  - translate report title/subtitle and cover cards
  - keep ticker/product/index names intact
- Acceptance:
  - no `Investor Report`, `Analyst Report`, `PRIMARY REGIME`, `GEOPOLITICAL REGIME`, `MAIN TAKEAWAY` on the Dutch cover.

### 6. Add hard Dutch quality validator for English decision words
- Status: in progress
- Implementation:
  - expand `tools/validate_etf_dutch_language_quality.py`
- Acceptance:
  - workflow blocks English decision words in Dutch client report unless they are explicitly whitelisted market terms.

---

## Phase 2 — Improve native Dutch report generation

### 7. Native Dutch templates for executive summary, conclusion and action tables
- Status: planned
- Implementation:
  - render key Dutch sections from runtime state instead of translating English prose sentence-by-sentence
- Acceptance:
  - Kernsamenvatting, Conclusie, Portefeuille-acties and actietabellen read like originally written Dutch.

### 8. Dutch chart titles and axes
- Status: planned
- Implementation:
  - make chart labels language-aware in delivery generation
- Acceptance:
  - Dutch PDF chart uses Dutch title/axis labels where practical.

### 9. Better institutional style rules
- Status: planned
- Implementation:
  - add style checks for compactness, tone and client-facing wording
- Acceptance:
  - no casual phrasing, no half-translated table cells, no operational notes.

### 10. Human-readable glossary for each report section
- Status: started
- Implementation:
  - maintain `control/NL_TERMINOLOGY.md`
- Acceptance:
  - adding or changing Dutch wording requires a single terminology update plus code mapping if needed.

---

## Testing milestones

### Test 1 — Validator-only test
Run after Phase 1 implementation. Expected outcome: Dutch markdown validation fails if mixed language remains, or passes if the localization layer catches all known cases.

### Test 2 — Fresh bilingual report generation
Run after validator-only test passes. Review:
- cover language
- executive summary
- table headers/values
- replacement analysis
- section 7/15 wording
- input-for-next-run section
- delivery HTML/PDF output

### Test 3 — Production delivery
Only after the generated Dutch report is visually and linguistically acceptable.

---

## Authority rules

- English remains analytical source of truth.
- Dutch report must preserve numeric parity and portfolio-state parity.
- Dutch report must not contain internal workflow language.
- Dutch report may keep accepted market English terms where they are standard in Dutch investment language.
- Tickers, official product names and index names remain unchanged.
