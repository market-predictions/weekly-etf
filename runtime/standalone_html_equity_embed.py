from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


class StandaloneHtmlEquityError(RuntimeError):
    pass


def _embed_standalone_html(assets: dict[str, Any], report_module: Any) -> None:
    chart_path = Path(assets["equity_curve_png"])
    html_path = Path(assets["html_path"])
    if not chart_path.is_file() or chart_path.stat().st_size <= 0:
        raise StandaloneHtmlEquityError(f"Equity-curve PNG is missing or empty: {chart_path}")

    image_src = report_module.png_to_data_uri(chart_path)
    standalone_html = report_module.build_report_html(
        assets["md_text_clean"],
        assets["report_date_str"],
        image_src=image_src,
        render_mode="email",
    )
    lowered = standalone_html.lower()
    if "data:image/png;base64," not in lowered:
        raise StandaloneHtmlEquityError(
            f"Standalone HTML does not contain an embedded equity graph: {html_path}"
        )
    if "cid:equitycurve" in lowered:
        raise StandaloneHtmlEquityError(
            f"Standalone HTML still depends on MIME CID resolution: {html_path}"
        )
    if "equity_curve_chart_placeholder" in lowered:
        raise StandaloneHtmlEquityError(
            f"Standalone HTML still exposes the equity placeholder: {html_path}"
        )

    html_path.write_text(standalone_html, encoding="utf-8")
    assets["html_standalone"] = standalone_html
    assets["html_standalone_image_mode"] = "embedded_data_uri"


def with_standalone_html_equity_embed(
    generate_assets_for_run: Callable[..., dict[str, Any]],
    report_module: Any,
) -> Callable[..., dict[str, Any]]:
    """Keep CID HTML for the MIME email body and persist self-contained HTML files.

    The existing delivery generator correctly creates a CID-backed ``html_email``
    for the multipart email. A CID cannot resolve when the attached HTML file is
    opened by itself, so this wrapper rebuilds only the persisted HTML artifact
    with an embedded data URI. PDF generation and the email body remain unchanged.
    """

    def _wrapped(output_dir: Path, report_path_en: Path, mode: str = "standard") -> dict[str, Any]:
        bundle = generate_assets_for_run(output_dir, report_path_en, mode=mode)
        for language in ("en", "nl"):
            assets = bundle.get(language)
            if not isinstance(assets, dict):
                continue
            email_html = str(assets.get("html_email") or "")
            if Path(assets["equity_curve_png"]).is_file() and "cid:equitycurve" not in email_html.lower():
                raise StandaloneHtmlEquityError(
                    f"MIME email HTML lost its CID equity reference for language={language}."
                )
            _embed_standalone_html(assets, report_module)
        return bundle

    return _wrapped


def validate_standalone_html_equity(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    lowered = html.lower()
    if "data:image/png;base64," not in lowered:
        raise StandaloneHtmlEquityError(f"Embedded equity graph missing from {path}")
    if "cid:equitycurve" in lowered:
        raise StandaloneHtmlEquityError(f"Standalone HTML still contains cid:equitycurve: {path}")
    if "equity_curve_chart_placeholder" in lowered:
        raise StandaloneHtmlEquityError(f"Equity placeholder leaked into {path}")
