from __future__ import annotations

from pathlib import Path


class PatchError(RuntimeError):
    pass


def replace_once(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return False
    if old not in text:
        raise PatchError(f"Expected integration anchor missing in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return True


def patch_linkifier() -> bool:
    path = Path("runtime/link_runtime_report_tickers.py")
    changed = False
    changed |= replace_once(
        path,
        "from runtime.polish_runtime_reports import DECISION_COCKPIT_EN, DECISION_COCKPIT_NL\n",
        "from runtime.polish_runtime_reports import DECISION_COCKPIT_EN, DECISION_COCKPIT_NL\n"
        "from runtime.report_freshness_contract import apply_report_freshness_contract, load_runtime_state\n",
    )
    changed |= replace_once(
        path,
        """    output_dir = Path(args.output_dir)\n    for pattern in (EN_RE, NL_RE):\n        report_path = latest_report(output_dir, pattern)\n        report_path.write_text(linkify_report(report_path.read_text(encoding=\"utf-8\")), encoding=\"utf-8\")\n        print(f\"ETF_LINKIFY_OK | report={report_path.name}\")\n""",
        """    output_dir = Path(args.output_dir)\n    state = load_runtime_state()\n    for pattern, language in ((EN_RE, \"en\"), (NL_RE, \"nl\")):\n        report_path = latest_report(output_dir, pattern)\n        text = report_path.read_text(encoding=\"utf-8\")\n        if state:\n            text = apply_report_freshness_contract(text, state, language)\n        report_path.write_text(linkify_report(text), encoding=\"utf-8\")\n        print(\n            f\"ETF_LINKIFY_OK | report={report_path.name} | \"\n            f\"freshness_contract={'applied' if state else 'skipped_no_runtime_state'}\"\n        )\n""",
    )
    return changed


def patch_delivery_entrypoint() -> bool:
    path = Path("send_report_runtime_html.py")
    changed = False
    changed |= replace_once(
        path,
        "from runtime.equity_curve_svg_contract import replace_pdf_equity_png_with_svg\n",
        "from runtime.equity_curve_svg_contract import replace_pdf_equity_png_with_svg\n"
        "from runtime.standalone_html_equity_embed import with_standalone_html_equity_embed\n",
    )
    changed |= replace_once(
        path,
        "report_module.generate_delivery_assets_for_run = _with_macro_pre_send_guard(report_module.generate_delivery_assets_for_run)\n",
        "report_module.generate_delivery_assets_for_run = _with_macro_pre_send_guard(\n"
        "    with_standalone_html_equity_embed(report_module.generate_delivery_assets_for_run, report_module)\n"
        ")\n",
    )
    return changed


def patch_macro_builder() -> bool:
    path = Path("runtime/build_macro_policy_pack.py")
    changed = False
    changed |= replace_once(
        path,
        "from datetime import date, datetime, timezone\n",
        "from datetime import date, datetime, timedelta, timezone\n",
    )
    changed |= replace_once(
        path,
        """def _ecb_june_2026_hike_applies(report_date: str | None) -> bool:\n    report = _date_or_none(report_date)\n    hike = _date_or_none(ECB_JUNE_2026_HIKE_DATE)\n    return bool(report and hike and report >= hike)\n\n\n""",
        """def _ecb_june_2026_hike_applies(report_date: str | None) -> bool:\n    report = _date_or_none(report_date)\n    hike = _date_or_none(ECB_JUNE_2026_HIKE_DATE)\n    return bool(report and hike and report >= hike)\n\n\ndef _event_is_in_report_week(report_date: str | None, event_date: str | None, lookback_days: int = 6) -> bool:\n    report = _date_or_none(report_date)\n    event = _date_or_none(event_date)\n    return bool(report and event and report - timedelta(days=lookback_days) <= event <= report)\n\n\n""",
    )
    changed |= replace_once(
        path,
        '"likely_direction": "Rate hike delivered; the next step remains data- and inflation-dependent.",',
        '"likely_direction": "Following the 11 June 2026 rate increase, the next step remains data- and inflation-dependent.",',
    )
    changed |= replace_once(
        path,
        "    if _ecb_june_2026_hike_applies(report_date):\n        catalysts.insert(\n",
        "    if _event_is_in_report_week(report_date, ECB_JUNE_2026_HIKE_DATE):\n        catalysts.insert(\n",
    )
    changed |= replace_once(
        path,
        'return ["Keep SMH as the earned leader, but do not confuse narrow leadership with broad diversification.", "Require replacement duels for SPY overlap, PPA implementation quality and PAVE versus GRID before funding challengers.", "Keep cash discipline because the regime supports selectivity more than broad risk expansion."]',
        'return ["Keep SMH as the earned leader, but do not confuse narrow leadership with broad diversification.", "Require replacement reviews for factor overlap and implementation-sensitive defense and infrastructure holdings before funding challengers.", "Keep cash discipline because the regime supports selectivity more than broad risk expansion."]',
    )
    changed |= replace_once(
        path,
        'return ["Stay invested, but make new capital pass a stricter macro and relative-strength filter.", "Treat SPY, PPA, PAVE and GLD as active review items rather than passive holds.", "Do not fund replacement candidates until the pricing basis and direct duel evidence are visible."]',
        'return ["Stay invested, but make new capital pass a stricter macro and relative-strength filter.", "Treat implementation-sensitive and weak-contribution positions as active reviews rather than passive holds.", "Do not fund replacement candidates until the pricing basis and direct duel evidence are visible."]',
    )
    changed |= replace_once(
        path,
        '"cross_asset_confirmation": ["Semiconductor leadership supports SMH, but SPY overlap must remain explicit.", "Small-cap and duration signals are not strong enough to justify broad beta expansion.", "Gold is treated as a hedge review item unless price behavior improves."],',
        '"cross_asset_confirmation": ["Semiconductor leadership supports SMH, but factor overlap must remain explicit.", "Small-cap and duration signals are not strong enough to justify broad beta expansion.", "Hedge exposures must re-earn their role through current contribution and price behavior."],',
    )
    changed |= replace_once(
        path,
        """def _active_drivers_placeholder() -> list[dict[str, Any]]:\n    return []\n\n\n""",
        """def _active_drivers_placeholder() -> list[dict[str, Any]]:\n    return []\n\n\ndef _regime_delta_lines(pack: dict[str, Any]) -> list[str]:\n    regime = pack.get(\"regime\") or {}\n    memory = pack.get(\"regime_memory\") or {}\n    current = str(memory.get(\"current_regime\") or regime.get(\"current\") or \"Unknown\")\n    prior = str(memory.get(\"prior_regime\") or regime.get(\"previous\") or \"Unknown\")\n    breadth = str(memory.get(\"breadth_trend\") or \"mixed\").replace(\"_\", \" \")\n    cross = str(memory.get(\"cross_asset_confirmation\") or \"mixed\").replace(\"_\", \" \")\n    if memory.get(\"regime_changed_this_run\") and prior not in {\"\", \"Unknown\"}:\n        return [\n            f\"The regime changed versus the prior review from {prior} to {current}; \"\n            f\"market breadth is {breadth} and cross-asset confirmation is {cross}.\"\n        ]\n    return [\n        \"No material regime change was recorded versus the prior review; \"\n        f\"the {current} backdrop remained intact, market breadth is {breadth}, \"\n        f\"and cross-asset confirmation is {cross}.\"\n    ]\n\n\n""",
    )
    changed |= replace_once(
        path,
        """    pack[\"regime_memory\"] = update_regime_memory(pack)\n    _validate_pack(pack)\n""",
        """    pack[\"regime_memory\"] = update_regime_memory(pack)\n    pack[\"regime\"][\"what_changed\"] = _regime_delta_lines(pack)\n    _validate_pack(pack)\n""",
    )
    return changed


def patch_macro_surface() -> bool:
    path = Path("runtime/macro_report_surface.py")
    return replace_once(
        path,
        '        "what_changed": f"Macro-, beleids- en regime-input komen nu uit de runtime macro-pack; portefeuilleacties blijven afhankelijk van prijs, relatieve sterkte en portefeuillediscipline. Kernpunt: {changed}",\n',
        '        "what_changed": changed,\n',
    )


def main() -> None:
    changes = {
        "runtime/link_runtime_report_tickers.py": patch_linkifier(),
        "send_report_runtime_html.py": patch_delivery_entrypoint(),
        "runtime/build_macro_policy_pack.py": patch_macro_builder(),
        "runtime/macro_report_surface.py": patch_macro_surface(),
    }
    changed = [path for path, value in changes.items() if value]
    print(
        "ETF_REPORT_FRESHNESS_INTEGRATION_PATCH_OK | "
        f"changed={','.join(changed) if changed else 'none_already_applied'}"
    )


if __name__ == "__main__":
    main()
