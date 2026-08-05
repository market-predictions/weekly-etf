from __future__ import annotations

"""Guarded executed-report fixer with authoritative contradiction cleanup.

Imported callers receive the preserved implementation. Direct execution keeps
all legacy transformations and validations, adding only the execution-aware
removal of explicit no-action claims before the final consistency check.
"""

import sys

import runtime.fix_executed_report_contract_legacy as _legacy


if __name__ != "__main__":
    sys.modules[__name__] = _legacy
else:
    from pathlib import Path

    from runtime.executed_report_contradiction_cleanup import remove_no_action_contradictions

    def patch_report_with_execution_contract(path: Path, state: dict) -> None:
        text = path.read_text(encoding="utf-8")
        text = _legacy._patch_common_text(text)
        text = _legacy._replace_between(
            text,
            "## 14. Position Changes Executed This Run",
            "## 15. Current Portfolio Holdings and Cash",
            _legacy._position_changes_table_en(state),
        )
        text = _legacy._replace_between(
            text,
            _legacy.EN_POSITION_CHANGES_HEADING,
            "## 15. Current Portfolio Holdings and Cash",
            _legacy._position_changes_table_en(state),
        )
        text = text.replace(
            "## 14. Position Changes Executed This Run",
            _legacy.EN_POSITION_CHANGES_HEADING,
        )
        text = _legacy._replace_between(
            text,
            "## 14. Positiewijzigingen in deze run",
            "## 15. Huidige posities en cash",
            _legacy._position_changes_table_nl(state),
        )
        text = _legacy._replace_between(
            text,
            _legacy.NL_POSITION_CHANGES_HEADING,
            "## 15. Huidige posities en cash",
            _legacy._position_changes_table_nl(state),
        )
        text = text.replace(
            "## 14. Positiewijzigingen in deze run",
            _legacy.NL_POSITION_CHANGES_HEADING,
        )
        _legacy.validate_no_post_execution_proposed_language(text, report_name=path.name)
        language = "nl" if "## 2. Portefeuille-acties" in text else "en"
        text = _legacy._replace_legacy_decision_cockpit(text, state, language)
        text = remove_no_action_contradictions(text, state, language)
        _legacy.validate_post_execution_report_consistency(text, state, language=language)
        path.write_text(text, encoding="utf-8")
        print(f"ETF_EXECUTED_REPORT_CONTRACT_PATCHED | report={path.name}")

    _legacy.patch_report = patch_report_with_execution_contract
    _legacy.main()
