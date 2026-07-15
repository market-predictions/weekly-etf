from __future__ import annotations

# Compatibility entrypoint. The governed implementation lives in v2 so the
# production workflow and existing imports retain their stable module path.
from runtime.portfolio_rotation_engine_v2 import *  # noqa: F401,F403


if __name__ == "__main__":
    main()
