from pathlib import Path

path = Path("send_report_runtime_html.py")
text = path.read_text(encoding="utf-8")
import_marker = "from runtime.max_position_action_contract import sanitize_over_cap_add_html\n"
import_line = "from runtime.decision_cockpit_html import decision_cockpit_html_from_markdown\n"
if import_line not in text:
    if import_marker not in text:
        raise SystemExit("delivery HTML import marker not found")
    text = text.replace(import_marker, import_marker + import_line, 1)

start_marker = "def _decision_cockpit_html_from_markdown(md_text: str) -> str:\n"
end_marker = "\ndef _inject_decision_cockpit_html"
start = text.find(start_marker)
if start == -1:
    raise SystemExit("legacy delivery cockpit helper start not found")
end = text.find(end_marker, start)
if end == -1:
    raise SystemExit("legacy delivery cockpit helper end not found")
replacement = '''def _decision_cockpit_html_from_markdown(md_text: str) -> str:
    return decision_cockpit_html_from_markdown(md_text)
'''
text = text[:start] + replacement + text[end:]

old = '''    cockpit = _decision_cockpit_html_from_markdown(md_text)

    markers = [
'''
new = '''    cockpit = _decision_cockpit_html_from_markdown(md_text)
    if not cockpit:
        return html

    markers = [
'''
if old not in text:
    raise SystemExit("delivery cockpit injection marker not found")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
print("ETF_DELIVERY_HTML_COCKPIT_AUTHORITY_PATCH_OK")
