"""KS C 9306 configuration loading and shared calculation context."""

from __future__ import annotations

import json
import os


CONTEXT_ATTRIBUTES = ("config", "bin_hours", "Cd", "_config_path")


class KSC9306ConfigContext:
    def __init__(
        self,
        config: dict,
        bin_hours=None,
        default_cd: float = 0.25,
        config_path: str | None = None,
    ) -> None:
        self.config = config
        self.bin_hours = (
            bin_hours if bin_hours is not None else config.get("bin_hours", [])
        )
        self.Cd = default_cd
        self._config_path = config_path

    @classmethod
    def from_config_path(cls, config_path: str) -> "KSC9306ConfigContext":
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
        with open(config_path, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
        config.pop("_comment", None)
        return cls(
            config,
            bin_hours=config.get("bin_hours", []),
            default_cd=config.get("Cd", 0.25),
            config_path=config_path,
        )


class KSEngineContext:
    def __init__(self, context: KSC9306ConfigContext) -> None:
        self._context = context

    def __getattr__(self, name: str):
        try:
            return getattr(self._context, name)
        except AttributeError:
            raise AttributeError(
                f"{type(self).__name__!s} object has no attribute {name!r}"
            ) from None
