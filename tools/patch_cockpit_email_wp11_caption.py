from pathlib import Path

path = Path("runtime/cockpit_email_safe_surface.py")
text = path.read_text(encoding="utf-8")
old = '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%;border-collapse:collapse"><tr><td class="etf-cockpit-chart-title"'
new = '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" class="etf-cockpit-chart-caption" style="width:100%;border-collapse:collapse"><tr><td class="etf-cockpit-chart-title"'
if old not in text:
    raise SystemExit("caption anchor missing")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
