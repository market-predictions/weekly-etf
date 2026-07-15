from pathlib import Path

path = Path("runtime/polish_runtime_reports.py")
text = path.read_text(encoding="utf-8")
old = '''def _ensure_decision_cockpit(text: str, state: dict[str, Any], *, language: str) -> str:
    cockpit = decision_cockpit_nl(state) if language == "nl" else decision_cockpit_en(state)
    marker = "### Besliscockpit" if language == "nl" else "### Decision cockpit"
    if marker in text:
        return text
    start_heading = "## 1. Kernsamenvatting" if language == "nl" else "## 1. Executive Summary"
    next_heading = "## 2. Portefeuille-acties" if language == "nl" else "## 2. Portfolio Action Snapshot"
    if start_heading in text and next_heading in text:
        return text.replace(next_heading, cockpit.strip() + "\n\n" + next_heading, 1)
    return cockpit.strip() + "\n\n" + text
'''
new = '''def _ensure_decision_cockpit(text: str, state: dict[str, Any], *, language: str) -> str:
    cockpit = decision_cockpit_nl(state) if language == "nl" else decision_cockpit_en(state)
    legacy_heading = "## 2A. Besliscockpit" if language == "nl" else "## 2A. Decision cockpit"
    legacy_end = "## 3. Regime-dashboard" if language == "nl" else "## 3. Regime Dashboard"
    if legacy_heading in text and legacy_end in text:
        cockpit_lines = cockpit.strip().splitlines()
        cockpit_body = "\n".join(cockpit_lines[2:]).strip() if len(cockpit_lines) > 2 else cockpit.strip()
        return replace_between(text, legacy_heading, legacy_end, cockpit_body)
    marker = "### Besliscockpit" if language == "nl" else "### Decision cockpit"
    if marker in text:
        return text
    start_heading = "## 1. Kernsamenvatting" if language == "nl" else "## 1. Executive Summary"
    next_heading = "## 2. Portefeuille-acties" if language == "nl" else "## 2. Portfolio Action Snapshot"
    if start_heading in text and next_heading in text:
        return text.replace(next_heading, cockpit.strip() + "\n\n" + next_heading, 1)
    return cockpit.strip() + "\n\n" + text
'''
if old not in text:
    raise SystemExit("staged dynamic cockpit helper not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("ETF_POST_EXECUTION_LEGACY_COCKPIT_PATCH_OK")
