from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"missing patch marker: {label}")
    return text.replace(old, new, 1)


# polish_runtime_reports.py
path = Path("runtime/polish_runtime_reports.py")
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    "from runtime.macro_report_surface import dashboard_en, dashboard_nl, executive_lines_en, executive_lines_nl\n",
    "from runtime.macro_report_surface import dashboard_en, dashboard_nl, executive_lines_en, executive_lines_nl\n"
    "from runtime.post_execution_report_surface import (\n"
    "    action_buckets,\n"
    "    decision_cockpit_en,\n"
    "    decision_cockpit_nl,\n"
    "    executed_rotation_summary_en,\n"
    "    has_executed_changes,\n"
    "    main_takeaway_en,\n"
    "    main_takeaway_nl,\n"
    ")\n",
    "polish imports",
)
text = text.replace("- **Main takeaway:** **{MAIN_TAKEAWAY_EN}**", "- **Main takeaway:** **{main_takeaway_en(state)}**")
text = text.replace("{DECISION_COCKPIT_EN.strip()}", "{decision_cockpit_en(state)}")
text = text.replace("- **Belangrijkste conclusie:** {MAIN_TAKEAWAY_NL}", "- **Belangrijkste conclusie:** {main_takeaway_nl(state)}")
text = text.replace("{DECISION_COCKPIT_NL.strip()}", "{decision_cockpit_nl(state)}")
old_bottom = '''def _bottom_line_en(state: dict[str, Any]) -> str:\n    return """\n- **What should be exited first:** Determined by the rotation plan when active; otherwise no close is executed by legacy state.\n- **What deserves additional capital first:** SMH remains the best-ranked funded lane, subject to the max-position rule.\n- **What is acceptable but replaceable:** Holdings with high release scores require reduce/replace/override discipline.\n- **Single best portfolio upgrade this week:** Use the rotation artifact as the bridge between evidence and target weights.\n"""\n'''
new_bottom = '''def _bottom_line_en(state: dict[str, Any]) -> str:\n    if has_executed_changes(state):\n        buckets = action_buckets(state)\n        reduced = ", ".join(buckets["reduce"] + buckets["close"]) or "the selected funding source"\n        added = ", ".join(buckets["add"]) or "the selected destination"\n        return f"""\n- **What was reduced or exited first:** {reduced}; the guarded mutation is executed and persisted.\n- **What received additional capital:** {added}; no further capital is deployed after the completed major rotation.\n- **What is acceptable but replaceable:** Holdings with high release scores remain subject to reduce/replace/override discipline.\n- **Single best portfolio upgrade this week:** **{executed_rotation_summary_en(state)}**\n"""\n    return """\n- **What should be exited first:** Determined by the rotation plan when active; otherwise no close is executed by legacy state.\n- **What deserves additional capital first:** SMH remains the best-ranked funded lane, subject to the max-position rule.\n- **What is acceptable but replaceable:** Holdings with high release scores require reduce/replace/override discipline.\n- **Single best portfolio upgrade this week:** Use the rotation artifact as the bridge between evidence and target weights.\n"""\n'''
text = replace_once(text, old_bottom, new_bottom, "dynamic bottom line")
old_ensure = '''def _ensure_decision_cockpit(text: str, *, language: str) -> str:\n    cockpit = DECISION_COCKPIT_NL if language == "nl" else DECISION_COCKPIT_EN\n    marker = "### Besliscockpit" if language == "nl" else "### Decision cockpit"\n'''
new_ensure = '''def _ensure_decision_cockpit(text: str, state: dict[str, Any], *, language: str) -> str:\n    cockpit = decision_cockpit_nl(state) if language == "nl" else decision_cockpit_en(state)\n    marker = "### Besliscockpit" if language == "nl" else "### Decision cockpit"\n'''
text = replace_once(text, old_ensure, new_ensure, "dynamic cockpit helper")
text = text.replace('text = _ensure_decision_cockpit(text, language="en")', 'text = _ensure_decision_cockpit(text, state, language="en")')
text = text.replace('text = _ensure_decision_cockpit(text, language="nl")', 'text = _ensure_decision_cockpit(text, state, language="nl")')
path.write_text(text, encoding="utf-8")


# fix_report_output_contract.py
path = Path("runtime/fix_report_output_contract.py")
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    "from runtime.build_etf_report_state import build_runtime_state\n",
    "from runtime.build_etf_report_state import build_runtime_state\n"
    "from runtime.post_execution_report_surface import (\n"
    "    action_buckets,\n"
    "    executed_rotation_summary_en,\n"
    "    has_executed_changes,\n"
    "    position_action_label_en,\n"
    "    rotation_plan_table_en,\n"
    ")\n",
    "output contract imports",
)
marker = "def action_snapshot_section(state: dict[str, Any]) -> str:\n"
insert = '''def action_snapshot_section(state: dict[str, Any]) -> str:\n    if has_executed_changes(state):\n        buckets = action_buckets(state)\n        joined = lambda key, none="None": ", ".join(buckets[key]) if buckets[key] else none\n        return "\\n".join([\n            "### Add — executed",\n            "- " + joined("add"),\n            "",\n            "### Reduce — executed",\n            "- " + joined("reduce"),\n            "",\n            "### Close — executed",\n            "- " + joined("close"),\n            "",\n            "### Hold",\n            "- " + joined("hold"),\n            "",\n            "### Hold but replaceable",\n            "- " + joined("replaceable"),\n            "",\n            "### Rotation engine status",\n            "- " + executed_rotation_summary_en(state),\n            "- The one-major-rotation budget is consumed for this run; another mutation requires a future validated run.",\n            "",\n            "### Replacement pricing and duel status",\n            "",\n            replacement_duel_v2_markdown(state),\n            "",\n            _replacement_edge_notes(state),\n        ])\n'''
if marker not in text:
    raise SystemExit("missing action_snapshot_section marker")
text = text.replace(marker, insert, 1)
text = text.replace(
    '        action = action_label(decision.get("action_code")) if decision else clean_action(p.get("rotation_action_code") or p.get("suggested_action"))',
    '        action = position_action_label_en(p, state) if has_executed_changes(state) else (action_label(decision.get("action_code")) if decision else clean_action(p.get("rotation_action_code") or p.get("suggested_action")))',
    1,
)
text = text.replace(
    'def rotation_plan_sections(state: dict[str, Any]) -> str:\n    if has_rotation_plan(state):',
    'def rotation_plan_sections(state: dict[str, Any]) -> str:\n    if has_executed_changes(state):\n        return rotation_plan_table_en(state)\n    if has_rotation_plan(state):',
    1,
)
text = text.replace(
    '    if _trade_intents(state):\n        lines.append(f"- Proposed rotation: {_trade_summary(state)}")',
    '    if has_executed_changes(state):\n        lines.append(f"- Executed rotation: {executed_rotation_summary_en(state)}")\n    elif _trade_intents(state):\n        lines.append(f"- Proposed rotation: {_trade_summary(state)}")',
    1,
)
path.write_text(text, encoding="utf-8")


# render_etf_report_from_state.py
path = Path("runtime/render_etf_report_from_state.py")
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    "from runtime.build_etf_report_state import build_runtime_state\n",
    "from runtime.build_etf_report_state import build_runtime_state\n"
    "from runtime.post_execution_report_surface import (\n"
    "    has_executed_changes,\n"
    "    position_action_code,\n"
    "    position_action_label_en,\n"
    "    rotation_plan_table_en,\n"
    ")\n",
    "EN renderer imports",
)
old_row = '''        lines.append(f"| {ticker} | {ETF_NAMES.get(ticker, ticker)} | {p.get('existing_new', 'Existing')} | {f2(p.get('weight_inherited_pct') or p.get('previous_weight_pct'))} | {f2(p.get('target_weight_pct') or w.get(ticker))} | {p.get('suggested_action', 'Hold')} | {p.get('conviction_tier', '')} | {f2(p.get('total_score'))} | {p.get('portfolio_role', '')} | {p.get('better_alternative_exists', 'No')} | {short_reason} |")\n'''
new_row = '''        action = position_action_label_en(p, state) if has_executed_changes(state) else p.get("suggested_action", "Hold")\n        existing_new = "New" if position_action_code(p, state) == "add_executed" else p.get("existing_new", "Existing")\n        inherited = p.get("weight_inherited_pct") if p.get("weight_inherited_pct") is not None else p.get("previous_weight_pct")\n        target = p.get("target_weight_pct") if p.get("target_weight_pct") is not None else w.get(ticker)\n        lines.append(f"| {ticker} | {ETF_NAMES.get(ticker, ticker)} | {existing_new} | {f2(inherited)} | {f2(target)} | {action} | {p.get('conviction_tier', '')} | {f2(p.get('total_score'))} | {p.get('portfolio_role', '')} | {p.get('better_alternative_exists', 'No')} | {short_reason} |")\n'''
text = replace_once(text, old_row, new_row, "EN final action row")
old_post_rotation = '''    if is_post_execution_state(state):\n        return "\\n".join(["| Close | Reduce | Hold | Add / destination | Reflected replace / reduce |", "|---|---|---|---|---|", f"| None | None | SMH, GSG, URNM | GSG | {reflected_rotation_label(state)} |"])\n'''
new_post_rotation = '''    if is_post_execution_state(state) and has_executed_changes(state):\n        return rotation_plan_table_en(state)\n    if is_post_execution_state(state):\n        return "\\n".join(["| Close | Reduce | Hold | Add / destination | Reflected replace / reduce |", "|---|---|---|---|---|", f"| None | None | {', '.join(sorted(active_tickers(state)))} | None | prior guarded rotation already reflected |"] )\n'''
text = replace_once(text, old_post_rotation, new_post_rotation, "EN post execution rotation table")
path.write_text(text, encoding="utf-8")


# render_etf_report_nl_from_state.py
path = Path("runtime/render_etf_report_nl_from_state.py")
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    "from runtime.nl_dates import format_dutch_report_date\n",
    "from runtime.nl_dates import format_dutch_report_date\n"
    "from runtime.post_execution_report_surface import (\n"
    "    action_buckets,\n"
    "    has_executed_changes,\n"
    "    position_action_code,\n"
    "    position_action_label_nl,\n"
    "    rotation_plan_table_nl as post_execution_rotation_plan_table_nl,\n"
    ")\n",
    "NL renderer imports",
)
text = text.replace(
    "        lines.append(f\"| {t} | {nl_action(p.get('suggested_action'))} | {f2(p.get('total_score'))} | {nl_fresh_cash(p.get('fresh_cash_test'))} | {nl_role(p.get('portfolio_role'))} | {POSITION_NEXT_ACTION_NL.get(t, 'Aanhouden en opnieuw toetsen in de volgende run.')} |\")",
    "        action = position_action_label_nl(p, state) if has_executed_changes(state) else nl_action(p.get('suggested_action'))\n        lines.append(f\"| {t} | {action} | {f2(p.get('total_score'))} | {nl_fresh_cash(p.get('fresh_cash_test'))} | {nl_role(p.get('portfolio_role'))} | {POSITION_NEXT_ACTION_NL.get(t, 'Aanhouden en opnieuw toetsen in de volgende run.')} |\")",
    1,
)
old_nl_row = '''        lines.append(f"| {t} | {ETF_NAMES.get(t, t)} | {nl_existing(p.get('existing_new'))} | {f2(p.get('weight_inherited_pct') or p.get('previous_weight_pct'))} | {f2(p.get('target_weight_pct') or w.get(t))} | {nl_action(p.get('suggested_action'))} | {text(p.get('conviction_tier')).replace('Tier', 'Niveau')} | {f2(p.get('total_score'))} | {nl_role(p.get('portfolio_role'))} | {nl_yes_no(p.get('better_alternative_exists'))} | {POSITION_SHORT_REASON_NL.get(t, 'Geen materiële wijziging deze run.')} |")\n'''
new_nl_row = '''        action = position_action_label_nl(p, state) if has_executed_changes(state) else nl_action(p.get("suggested_action"))\n        existing_new = "Nieuw" if position_action_code(p, state) == "add_executed" else nl_existing(p.get("existing_new"))\n        inherited = p.get("weight_inherited_pct") if p.get("weight_inherited_pct") is not None else p.get("previous_weight_pct")\n        target = p.get("target_weight_pct") if p.get("target_weight_pct") is not None else w.get(t)\n        lines.append(f"| {t} | {ETF_NAMES.get(t, t)} | {existing_new} | {f2(inherited)} | {f2(target)} | {action} | {text(p.get('conviction_tier')).replace('Tier', 'Niveau')} | {f2(p.get('total_score'))} | {nl_role(p.get('portfolio_role'))} | {nl_yes_no(p.get('better_alternative_exists'))} | {POSITION_SHORT_REASON_NL.get(t, 'Geen materiële wijziging deze run.')} |")\n'''
text = replace_once(text, old_nl_row, new_nl_row, "NL final action row")
text = text.replace(
    'def rotation_plan_table_nl(state: dict[str, Any]) -> str:\n    close = action_tickers',
    'def rotation_plan_table_nl(state: dict[str, Any]) -> str:\n    if has_executed_changes(state):\n        return post_execution_rotation_plan_table_nl(state)\n    close = action_tickers',
    1,
)
old_vars = '''    holdings = ", ".join(ticker(p.get("ticker")) for p in position_rows(state))\n    add = action_tickers(state, lambda action, p: "add" in action.lower() or "buy" in text(p.get("action_executed_this_run")).lower())\n    review = review_tickers(state)\n'''
new_vars = '''    if has_executed_changes(state):\n        buckets = action_buckets(state)\n        holdings = ", ".join(buckets["hold"]) if buckets["hold"] else "Geen"\n        add = ", ".join(buckets["add"]) if buckets["add"] else "Geen"\n        reduce = ", ".join(buckets["reduce"]) if buckets["reduce"] else "Geen"\n        close = ", ".join(buckets["close"]) if buckets["close"] else "Geen"\n        review = ", ".join(buckets["replaceable"]) if buckets["replaceable"] else "Geen"\n    else:\n        holdings = ", ".join(ticker(p.get("ticker")) for p in position_rows(state))\n        add = action_tickers(state, lambda action, p: "add" in action.lower() or "buy" in text(p.get("action_executed_this_run")).lower())\n        reduce = "Geen"\n        close = "Geen"\n        review = review_tickers(state)\n'''
text = replace_once(text, old_vars, new_vars, "NL action variables")
text = text.replace("| Verlagen | Geen |", "| Verlagen | {reduce} |", 1)
text = text.replace("| Sluiten | Geen |", "| Sluiten | {close} |", 1)
path.write_text(text, encoding="utf-8")


# fix_executed_report_contract.py
path = Path("runtime/fix_executed_report_contract.py")
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    "from typing import Any\n",
    "from typing import Any\n\nfrom runtime.post_execution_report_surface import validate_post_execution_report_consistency\n",
    "executed validator import",
)
text = text.replace(
    "    validate_no_post_execution_proposed_language(text, report_name=path.name)\n    path.write_text(text, encoding=\"utf-8\")",
    "    validate_no_post_execution_proposed_language(text, report_name=path.name)\n    language = \"nl\" if \"## 2. Portefeuille-acties\" in text else \"en\"\n    validate_post_execution_report_consistency(text, state, language=language)\n    path.write_text(text, encoding=\"utf-8\")",
    1,
)
path.write_text(text, encoding="utf-8")

print("ETF_POST_EXECUTION_SURFACE_PATCH_OK")
