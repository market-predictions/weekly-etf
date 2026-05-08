from __future__ import annotations

import send_report as _sr
from runtime.delivery_html_overrides import build_report_html_with_state

# Patch the delivery renderer at runtime. This avoids fragile markdown shaping for
# the branded PDF panels and lets Section 2 and Current Position Review be built
# directly from runtime state as controlled HTML.
_sr.build_report_html = build_report_html_with_state(_sr.build_report_html, _sr._base)

if __name__ == "__main__":
    _sr.main()
