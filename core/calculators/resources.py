"""Static Calculator profile-resource resolution for source and bundled layouts."""

from __future__ import annotations

from pathlib import Path


_RESOURCE_ROOT = Path(__file__).resolve().parents[2]


def resolve_calculator_resource_path(config_path: str) -> str:
    """Resolve a manifest-owned resource without cwd or runtime discovery."""
    path = Path(config_path)
    if path.is_absolute():
        return str(path)
    return str(_RESOURCE_ROOT / path)
