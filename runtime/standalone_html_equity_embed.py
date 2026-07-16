from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable


class StandaloneHtmlEquityError(RuntimeError):
    pass


EQUITY_IMG_RE = re.compile(
    r"(<img\b(?=[^>]*\balt=[\"'](?:Equity curve|Portefeuillecurve)[\"'])[^>]*\bsrc=[\"'])"
    r"(?:#harmful-link|cid:equitycurve|data:image/png;base64,[^\"']*)"
    r"([\"'][^>]*>)",
    flags=re.IGNORECASE,
)
EQUITY_SRC_FALLBACK_RE = re.compile(
    r"(<img\b[^>]*\bsrc=[\"'])"
    r"(?:#harmful-link|cid:equitycurve)"
    r"([\"'][^>]*>)",
    flags=re.IGNORECASE,
)


def _set_equity_image_src(html: str, image_src: str) -> str:
    updated, count = EQUITY_IMG_RE.subn(
        lambda match: match.group(1) + image_src + match.group(2),
        html,
        count=1,
    )
    if count == 1:
        return updated

    matches = list(EQUITY_SRC_FALLBACK_RE.finditer(html))
    if len(matches) == 1:
        return EQUITY_SRC_FALLBACK_RE.sub(
            lambda match: match.group(1) + image_src + match.group(2),
            html,
            count=1,
        )

    raise StandaloneHtmlEquityError(
        "Could not resolve exactly one equity-curve image element after client sanitization."
    )


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
    standalone_html = _set_equity_image_src(standalone_html, image_src)
    lowered = standalone_html.lower()
    if "data:image/png;base64," not in lowered:
        raise StandaloneHtmlEquityError(
            f"Standalone HTML does not contain an embedded equity graph: {html_path}"
        )
    if "cid:equitycurve" in lowered:
        raise StandaloneHtmlEquityError(
            f"Standalone HTML still depends on MIME CID resolution: {html_path}"
        )
    if "#harmful-link" in lowered:
        raise StandaloneHtmlEquityError(
            f"Standalone HTML still contains a sanitized equity source: {html_path}"
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
    """Restore the correct equity image source for each delivery surface.

    The client-facing sanitizer treats CID and data-URI image sources as unsafe
    and rewrites the equity image to ``#harmful-link``. The MIME email body needs
    the CID source, while a standalone attached HTML file needs an embedded data
    URI. This wrapper restores only the identified equity image after all normal
    HTML sanitization and leaves every other link untouched.
    """

    def _wrapped(output_dir: Path, report_path_en: Path, mode: str = "standard") -> dict[str, Any]:
        bundle = generate_assets_for_run(output_dir, report_path_en, mode=mode)
        for language in ("en", "nl"):
            assets = bundle.get(language)
            if not isinstance(assets, dict):
                continue
            chart_path = Path(assets["equity_curve_png"])
            if not chart_path.is_file() or chart_path.stat().st_size <= 0:
                raise StandaloneHtmlEquityError(
                    f"MIME email equity PNG is missing or empty for language={language}."
                )

            email_html = _set_equity_image_src(
                str(assets.get("html_email") or ""),
                "cid:equitycurve",
            )
            if "cid:equitycurve" not in email_html.lower() or "#harmful-link" in email_html.lower():
                raise StandaloneHtmlEquityError(
                    f"MIME email HTML does not contain a valid CID equity reference for language={language}."
                )
            assets["html_email"] = email_html
            assets["html_email_image_mode"] = "mime_cid"

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
    if "#harmful-link" in lowered:
        raise StandaloneHtmlEquityError(f"Standalone HTML still contains #harmful-link: {path}")
    if "equity_curve_chart_placeholder" in lowered:
        raise StandaloneHtmlEquityError(f"Equity placeholder leaked into {path}")
