"""Email delivery for Weekly ETF EU v2.

Addresses come only from GitHub secrets and are never printed (the repo and its
logs are public). Modes (v2/delivery.yml):
  off   – send nothing
  trial – one email with both PDFs to the owner only (V2_TRIAL_TO, else MRKT_RPRTS_MAIL_FROM)
  live  – EN PDF to MRKT_RPRTS_MAIL_TO, NL PDF to MRKT_RPRTS_MAIL_TO_NL (falls back to MAIL_TO)
Alerts always go to the owner only.
"""
from __future__ import annotations

import html
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent


def mode() -> str:
    return (yaml.safe_load((ROOT / "delivery.yml").read_text()) or {}).get("mode", "off")


def _addrs(value: str | None) -> list[str]:
    return [a.strip() for a in (value or "").replace(";", ",").split(",") if a.strip()]


def owner() -> list[str]:
    return _addrs(os.environ.get("V2_TRIAL_TO")) or _addrs(os.environ.get("MRKT_RPRTS_MAIL_FROM"))


def _send(msg: EmailMessage, to: list[str]) -> None:
    host = os.environ["MRKT_RPRTS_SMTP_HOST"]
    port = int(os.environ.get("MRKT_RPRTS_SMTP_PORT") or 587)
    user, pw = os.environ["MRKT_RPRTS_SMTP_USER"], os.environ["MRKT_RPRTS_SMTP_PASS"]
    msg["From"] = os.environ["MRKT_RPRTS_MAIL_FROM"]
    msg["To"] = ", ".join(to)
    ctx = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=ctx, timeout=60) as s:
            s.login(user, pw)
            s.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=60) as s:
            s.starttls(context=ctx)
            s.login(user, pw)
            s.send_message(msg)


def _body(c: dict, f: dict, lang: str) -> str:
    p = f["portfolio"]
    intro = {"en": "This week's review is attached as a PDF.", "nl": "De review van deze week zit als pdf in de bijlage."}[lang]
    parts = "".join(f"<p>{html.escape(c[k])}</p>" for k in ("what_happened", "why", "what_we_do") if c.get(k))
    return (f"<html><body style=\"font-family:Arial,sans-serif;font-size:14px;color:#1d1d1b;max-width:620px\">"
            f"<h2 style=\"font-size:18px\">{html.escape(c['headline'])}</h2>{parts}<p style=\"color:#6b6a66\">{intro}</p>"
            f"<p style=\"color:#8a8882;font-size:12px\">{'Model portfolio · rules-based · not personal advice' if lang == 'en' else 'Modelportefeuille · regelgebaseerd · geen persoonlijk advies'}</p>"
            f"</body></html>")


def _attach(msg: EmailMessage, pdf: Path) -> None:
    msg.add_attachment(pdf.read_bytes(), maintype="application", subtype="pdf", filename=pdf.name)


def deliver(facts: dict, commentary: dict, pdfs: dict[str, Path], dry_run: bool = False, label: str = "TRIAL") -> dict:
    m = mode()
    date_ = facts["report_date"]
    subj = {"en": f"Weekly ETF Review – {date_}", "nl": f"Wekelijkse ETF Review – {date_}"}
    plan = []
    if m == "trial":
        msg = EmailMessage()
        msg["Subject"] = f"[{label}] {subj['nl']} / {subj['en']}"
        msg.set_content("Trial run – HTML required.")
        msg.add_alternative(_body(commentary["nl"], facts, "nl") + _body(commentary["en"], facts, "en"), subtype="html")
        _attach(msg, pdfs["nl"])
        _attach(msg, pdfs["en"])
        plan.append(("trial", msg, owner()))
    elif m == "live":
        for lang, to in (("en", _addrs(os.environ.get("MRKT_RPRTS_MAIL_TO"))),
                         ("nl", _addrs(os.environ.get("MRKT_RPRTS_MAIL_TO_NL")) or _addrs(os.environ.get("MRKT_RPRTS_MAIL_TO")))):
            msg = EmailMessage()
            msg["Subject"] = subj[lang]
            msg.set_content(commentary[lang]["headline"])
            msg.add_alternative(_body(commentary[lang], facts, lang), subtype="html")
            _attach(msg, pdfs[lang])
            plan.append((f"live_{lang}", msg, to))
    result = {"mode": m, "dry_run": dry_run, "messages": []}
    for name, msg, to in plan:
        if not to:
            raise SystemExit(f"DELIVERY_BLOCKED: no recipients configured for {name}")
        if not dry_run:
            _send(msg, to)
        result["messages"].append({"name": name, "recipients": len(to), "sent": not dry_run})
    print("DELIVERY " + str(result))
    return result


def alert(text: str) -> None:
    to = owner()
    if not to or not os.environ.get("MRKT_RPRTS_SMTP_HOST"):
        print("ALERT_NOT_SENT (no owner address or SMTP config)")
        return
    msg = EmailMessage()
    msg["Subject"] = "[ALERT] Weekly ETF Review run failed – nothing was sent to readers"
    msg.set_content(text)
    _send(msg, to)
    print("ALERT_SENT")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "alert":
        alert(" ".join(sys.argv[2:]) or "Weekly run failed.")
