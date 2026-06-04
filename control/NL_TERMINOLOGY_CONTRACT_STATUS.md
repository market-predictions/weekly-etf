# Dutch Terminology Contract Status

## Date
2026-06-04

## Status

Dutch terminology / alias consolidation is implemented, workflow-proven, repo-visible evidence-proven, and updated to protect the native Dutch report architecture.

This is a Dutch quality and terminology guard only. It does not promote macro/thesis artifacts, alter portfolio scoring, change fundability, or change production recommendations.

## Architecture rule

The agreed output architecture is:

```text
runtime state / key figures
→ English native render
→ Dutch native render from the same runtime state
→ guard-only Dutch validation for native reports
```

It is not:

```text
English report
→ broad translation / scrub pass
→ Dutch report
```

The Dutch report is independently constructed from the same runtime state and key figures as the English report. It is not a second research pass and not a translation of the English markdown.

## Current alias centralization rule

`runtime/nl_terminology.py` is the central source of truth for Dutch terminology, table labels, report labels, decision wording, trigger wording, allowed English tokens, forbidden Dutch/client-surface tokens, and known legacy cleanup maps.

`runtime/nl_localization.py` now keeps backward-compatible alias names, but sources these objects directly from `runtime.nl_terminology`:

```text
DUTCH_DISCLAIMER
ALLOWED_ENGLISH_TERMS
LABELS -> term.REPORT_LABELS
TABLE_LABELS
ACTION_REPLACEMENTS
PHRASE_REPLACEMENTS
DECISION_TRANSLATIONS
TRIGGER_TRANSLATIONS
FORBIDDEN_NL_STRINGS
```

The terminology validator explicitly checks these aliases by object identity so duplicated local dictionaries cannot silently reappear.

## Repo-visible proof

Evidence file:

```text
output/macro/validation/latest_nl_terminology_contract_validation.json
```

Prior repo-visible evidence reports:

```text
artifact_type: nl_terminology_contract_validation_evidence
status: passed
workflow.name: Validate ETF Dutch terminology contract
workflow.run_number: 10
workflow.run_id: 26770580704
workflow.commit_sha: d32dbf6813084892efa565277c479a11951c698c
validated_markers:
  - ETF_NL_TERMINOLOGY_CONTRACT_OK
```

Latest UI-confirmed workflow evidence for alias centralization:

```text
workflow: Validate ETF Dutch terminology
run_number: 16
trigger_commit: 25aac7a823ddf9eaaca3362a33cf07c050b53b9f
status: passed
branch: main
duration: 13s
observed_at: 2026-06-04
source: user-provided GitHub Actions UI screenshot
```

The screenshot shows the green check for:

```text
validate Dutch localization aliases use central terminology
Validate ETF Dutch terminology #16
commit 25aac7a
```

## Files updated in latest alias-centralization pass

```text
runtime/nl_localization.py
tools/validate_nl_terminology_contract.py
.github/workflows/send-weekly-report.yml
```

## What changed

- `runtime/render_etf_report_from_state.py` writes the Dutch report from `render_nl_native(state)`.
- `runtime/apply_nl_localization.py` treats native Dutch reports as guard-only: official disclaimer replacement and deterministic artifact cleanup only.
- `runtime/scrub_nl_client_language.py` treats native Dutch reports as guard-only and does not run broad English-to-Dutch replacement maps over native Dutch prose.
- `runtime/nl_localization.py` now sources its core terminology aliases directly from `runtime.nl_terminology` instead of maintaining duplicate dictionaries.
- `tools/validate_nl_terminology_contract.py` now validates that alias centralization contract explicitly.
- The production send workflow now runs `tools/validate_nl_terminology_contract.py` inside the Dutch quality step before Dutch report/client-surface validation.
- Broad localization/scrub behavior remains available only for legacy/non-native text.

The terminology contract now proves:

```text
legacy/non-native text may still be localized
native Dutch text remains guard-only
native Dutch text keeps valid wording such as `Nog geen alternatief...`
English leakage in native Dutch is not silently translated
English leakage fails Dutch quality validation
runtime.nl_localization aliases are sourced from runtime.nl_terminology
```

## Workflow proof

Workflow-proven by repo-visible evidence and by GitHub Actions screenshots supplied by the user.

Earlier evidence from screenshot:

```text
workflow: Validate ETF Dutch terminology contract
run title: validate native Dutch guard-only architecture #10
trigger: push
commit: d32dbf6
branch: main
status: success
job: validate-nl-terminology-contract
total duration: 16s
```

Latest evidence from screenshot:

```text
workflow: Validate ETF Dutch terminology
run title: validate Dutch localization aliases use central terminology
run_number: 16
trigger: push
commit: 25aac7a
branch: main
status: success
total duration: 13s
```

Expected markers:

```text
ETF_NL_TERMINOLOGY_CONTRACT_OK
ETF_NL_TERMINOLOGY_EVIDENCE_OK
```

## Failure/fix history

The isolated workflow exposed useful contract issues:

1. `Neetable` existed intentionally as a forbidden-after-scrub guard token, but the validator incorrectly treated all guard tokens as client-facing values.
2. `Toevoegened` was repairable by the scrub layer, so the contract was adjusted to require known-bad tokens to be repaired or blocked, not always present in the forbidden list.
3. The self-test placed decision phrases after `## 17. Disclaimer`, so `_replace_disclaimer()` correctly removed them before phrase translation. The fixture was moved before the disclaimer section.
4. The native Dutch localization order was corrected so exact decision/trigger phrase translations ran before generic cleanup.
5. After the user correctly pointed out that Dutch should not be a translation of English, native Dutch reports were moved to guard-only localization/scrub mode.
6. `runtime/nl_localization.py` duplicated central terminology maps; this was corrected by direct aliasing to `runtime.nl_terminology` and validated by the contract.

## Authority boundary

This Dutch terminology work is not a macro/thesis production promotion.

It does not change:

```text
client-facing investment logic
lane scoring
fundability
portfolio actions
final recommendations
macro/thesis authority
```

The evidence explicitly records:

```text
quality_guard_only: true
client_facing_investment_logic_changed: false
macro_thesis_promotion: false
lane_scoring_authority: false
fundability_authority: false
portfolio_action_authority: false
production_recommendation_authority: false
```

## Work-package status

Dutch terminology alias centralization: closed for this stage and validated by user-provided GitHub Actions UI evidence.

## Next action

Run or observe the next production ETF report validation to prove the full report flow passes with the centralized terminology contract now executed in `.github/workflows/send-weekly-report.yml` before Dutch quality validation.
