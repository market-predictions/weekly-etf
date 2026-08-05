from __future__ import annotations

"""Guarded Weekly ETF delivery entrypoint.

Imported callers receive the preserved renderer module itself, so monkeypatching,
module globals and legacy regression behavior remain unchanged. The independent
release-assurance gate is added only when this path is executed as transport.
"""

import sys

import send_report_runtime_html_legacy as _legacy


if __name__ != "__main__":
    sys.modules[__name__] = _legacy
else:
    from tools.etf_release_assurance import ensure_release_assurance_from_environment

    assurance_path = ensure_release_assurance_from_environment()
    print(f"ETF_GOVERNANCE_PASS_PRE_SEND | assurance={assurance_path}")
    _legacy.report_module.main()
