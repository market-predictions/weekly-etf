from pathlib import Path

path = Path("runtime/additive_cockpit_front_page.py")
text = path.read_text(encoding="utf-8")

import_anchor = "from runtime import render_cockpit_front_page as cockpit\n"
import_line = "from runtime.cockpit_email_safe_surface import render_email_safe_cockpit_front_page\n"
if import_line not in text:
    if import_anchor not in text:
        raise SystemExit("import anchor missing")
    text = text.replace(import_anchor, import_anchor + import_line, 1)

branch_anchor = "    return_class = \"etf-cockpit-positive\" if since >= 0 else \"etf-cockpit-negative\"\n"
branch = '''    if str(render_mode).strip().lower().startswith("email"):
        html = render_email_safe_cockpit_front_page(
            output_dir=output_dir,
            state_path=state_path,
            macro_path=macro_path,
            language=language,
            report_date=report_date,
            text=text,
            summary=summary,
            regime=regime,
            confidence=confidence,
            action_title=action_title,
            action_note=action_note,
            points=points,
            nav=nav,
            since=since,
            drawdown=drawdown,
            cash=cash,
            cash_pct=cash_pct,
            position_count=len(cockpit._positions(state)),
            largest_ticker=largest_ticker,
            largest_weight=largest_weight,
            fx_rate=cockpit._float((state.get("fx_basis") or {}).get("rate")),
            discipline=discipline,
            next_trigger=next_trigger,
        )
        lowered = html.lower()
        leaked = [token for token in cockpit.INTERNAL_SURFACE_TOKENS if token in lowered]
        preview_tokens = [
            "preview lane",
            "preview-only cockpit",
            "no delivery claim",
            "not promoted to production",
            "voorbeeldcockpit",
            "geen leveringsclaim",
            "niet naar productie gepromoveerd",
        ]
        leaked.extend(token for token in preview_tokens if token in lowered)
        if leaked:
            raise RuntimeError(
                "Delivery cockpit leaked forbidden wording: "
                + ", ".join(sorted(set(leaked)))
            )
        return CockpitFrontPageFragment(css="", html=html, language=language)

'''
if "render_email_safe_cockpit_front_page(" not in text:
    if branch_anchor not in text:
        raise SystemExit("render branch anchor missing")
    text = text.replace(branch_anchor, branch + branch_anchor, 1)

path.write_text(text, encoding="utf-8")
