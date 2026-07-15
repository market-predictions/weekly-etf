from pathlib import Path

path = Path("runtime/fix_executed_report_contract.py")
text = path.read_text(encoding="utf-8")
old_import = "from runtime.post_execution_report_surface import validate_post_execution_report_consistency\n"
new_import = '''from runtime.post_execution_report_surface import (
    decision_cockpit_en,
    decision_cockpit_nl,
    validate_post_execution_report_consistency,
)
'''
if old_import not in text:
    raise SystemExit("post-execution report surface import marker not found")
text = text.replace(old_import, new_import, 1)

marker = "def patch_report(path: Path, state: dict[str, Any]) -> None:\n"
helper = '''def _replace_legacy_decision_cockpit(text: str, state: dict[str, Any], language: str) -> str:
    if language == "nl":
        start = "## 2A. Besliscockpit"
        end = "## 3. Regime-dashboard"
        cockpit = decision_cockpit_nl(state)
    else:
        start = "## 2A. Decision cockpit"
        end = "## 3. Regime Dashboard"
        cockpit = decision_cockpit_en(state)
    if start not in text or end not in text:
        return text
    lines = cockpit.strip().splitlines()
    body = "\\n".join(lines[2:]).strip() if len(lines) > 2 else cockpit.strip()
    return _replace_between(text, start, end, body)


'''
if marker not in text:
    raise SystemExit("patch_report marker not found")
text = text.replace(marker, helper + marker, 1)
old = '''    language = "nl" if "## 2. Portefeuille-acties" in text else "en"
    validate_post_execution_report_consistency(text, state, language=language)
'''
new = '''    language = "nl" if "## 2. Portefeuille-acties" in text else "en"
    text = _replace_legacy_decision_cockpit(text, state, language)
    validate_post_execution_report_consistency(text, state, language=language)
'''
if old not in text:
    raise SystemExit("post-execution validation marker not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("ETF_POST_EXECUTION_FINAL_CONTRACT_COCKPIT_PATCH_OK")
