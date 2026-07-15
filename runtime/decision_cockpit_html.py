from __future__ import annotations

from html import escape
import re


def _section(md_text: str, start: str, end: str) -> str:
    start_index = md_text.find(start)
    if start_index == -1:
        return ""
    end_index = md_text.find(end, start_index + len(start))
    return md_text[start_index:] if end_index == -1 else md_text[start_index:end_index]


def _plain_markdown_inline(value: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    text = text.replace("**", "").replace("__", "").replace("`", "")
    return " ".join(text.split()).strip()


def decision_cockpit_items_from_markdown(md_text: str) -> tuple[str, list[str]]:
    is_nl = "## 2A. Besliscockpit" in md_text
    if is_nl:
        title = "Besliscockpit"
        block = _section(md_text, "## 2A. Besliscockpit", "## 3. Regime-dashboard")
    else:
        title = "Decision cockpit"
        block = _section(md_text, "## 2A. Decision cockpit", "## 3. Regime Dashboard")

    items: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        item = _plain_markdown_inline(stripped[2:])
        if item:
            items.append(item)
    return title, items


def decision_cockpit_html_from_markdown(md_text: str) -> str:
    title, items = decision_cockpit_items_from_markdown(md_text)
    if not items:
        return ""
    body = "".join(f"<li>{escape(item)}</li>" for item in items)
    return (
        "<div class='note-box decision-cockpit'>"
        f"<h4>{escape(title)}</h4><ul>{body}</ul></div>"
    )
