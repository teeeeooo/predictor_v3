"""Platform-specific user state path for persisted Definition generations."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path


def default_generation_root(
    *,
    platform_name: str | None = None,
    environment: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> Path:
    resolved_platform = platform_name or os.name
    resolved_environment = environment if environment is not None else os.environ
    resolved_home = home or Path.home()
    if resolved_platform == "nt":
        fallback = resolved_home / "AppData" / "Local"
        base = Path(resolved_environment.get("LOCALAPPDATA", fallback))
    else:
        fallback = resolved_home / ".local" / "state"
        base = Path(resolved_environment.get("XDG_STATE_HOME", fallback))
    return base / "predictor_v3" / "data_definition"
