# Weekly ETF report request

## Requested by
ChatGPT project workbench

## Purpose
Verify the Dutch client-language cleanup for the remaining radar-table phrase:

```text
Healthcare quality and defensive growth
```

The phrase should render as:

```text
Healthcarekwaliteit en defensieve groei
```

## Change under verification

```text
runtime/scrub_nl_client_language.py
```

The phrase was added to the native Dutch structured-state label normalization map and to the forbidden post-scrub token list.

## Expected checks

The run should confirm:

```text
workflow_success
ETF_NL_CLIENT_LANGUAGE_SCRUB_OK
ETF_NL_LANGUAGE_QUALITY_OK
pricing_lineage_status: passed
```

The generated Dutch report should not contain `Healthcare quality and defensive growth`.

## Delivery note

Delivery receipt work remains paused. Workflow success/send acceptance should not be overstated as recipient receipt.
