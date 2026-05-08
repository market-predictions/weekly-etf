from __future__ import annotations

import send_report as report_module
from runtime.delivery_html_overrides import build_report_html_with_state

report_module.build_report_html = build_report_html_with_state(report_module.build_report_html, report_module._base)

if __name__ == "__main__":
    report_module.main()
