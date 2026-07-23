"""Stable user-state paths for the default model lifecycle workspace."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path

DEFAULT_WORKSPACE_ID = "default"


def default_model_lifecycle_root(
    *,
    platform_name: str | None = None,
    environment: Mapping[str, str] | None = None,
    home: Path | None = None,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
) -> Path:
    if workspace_id != DEFAULT_WORKSPACE_ID:
        raise ValueError("Phase 5B supports only the default workspace")
    resolved_platform = platform_name or os.name
    resolved_environment = environment if environment is not None else os.environ
    resolved_home = home or Path.home()
    if resolved_platform == "nt":
        base = Path(resolved_environment.get(
            "LOCALAPPDATA", resolved_home / "AppData" / "Local"
        ))
    else:
        base = Path(resolved_environment.get(
            "XDG_STATE_HOME", resolved_home / ".local" / "state"
        ))
    return base / "predictor_v3" / "model_lifecycle" / "workspaces" / workspace_id
