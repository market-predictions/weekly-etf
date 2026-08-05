from __future__ import annotations

"""Guarded Weekly ETF delivery entrypoint.

The established renderer remains in ``send_report_runtime_html_legacy``. This
wrapper preserves its import surface and inserts the independent release-
assurance gate only when the file is executed as the transport entrypoint.
"""

import send_report_runtime_html_legacy as _legacy

for _name, _value in vars(_legacy).items():
    if _name not in {"__name__", "__file__", "__package__", "__loader__", "__spec__"}:
        globals()[_name] = _value


if __name__ == "__main__":
    from tools.etf_release_assurance import ensure_release_assurance_from_environment

    assurance_path = ensure_release_assurance_from_environment()
    print(f"ETF_GOVERNANCE_PASS_PRE_SEND | assurance={assurance_path}")
    _legacy.report_module.main()
