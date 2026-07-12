"""EN 14825 configuration loading and read-only calculation context."""

from __future__ import annotations

import json
import os


class EN14825ConfigContext:
    """Load the unified EN config once and expose its stable sections."""

    def __init__(self, config_path: str | None = None) -> None:
        if config_path is None:
            repo_root = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    )
                )
            )
            config_path = os.path.join(
                repo_root, "data", "region_configs", "en14825.json"
            )

        self.config_path = config_path
        loaded_config = self._load_config(config_path)
        self.config, self.seer_config, self.scop_config = self._split_config(
            loaded_config
        )

    def _load_config(self, config_path: str) -> dict:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"EN14825 config file not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as config_file:
            return json.load(config_file)

    def _split_config(self, config: dict) -> tuple:
        if "seer" not in config or "scop" not in config:
            raise ValueError("EN14825 config must include 'seer' and 'scop' sections.")
        return config, config["seer"], config["scop"]

    def _get_seer_design_value(self, key: str) -> float:
        try:
            return float(self.seer_config["design"][key])
        except KeyError as exc:
            raise ValueError(f"Missing SEER design config key: {key}") from exc

    def _get_seer_default_value(self, key: str) -> float:
        try:
            return float(self.seer_config["defaults"][key])
        except KeyError as exc:
            raise ValueError(f"Missing SEER default config key: {key}") from exc

    def _get_seer_test_point_temps(self) -> dict:
        point_temps = self.seer_config.get("test_point_temps", {})
        required = ("A", "B", "C", "D")
        missing = [key for key in required if key not in point_temps]
        if missing:
            raise ValueError(f"Missing SEER test point temperature(s): {missing}")
        return {key: float(point_temps[key]) for key in required}

    def _get_seer_bin_data(self) -> tuple:
        try:
            bin_data = self.seer_config["bin_data"]
            temps = bin_data["temps"]
            hours = bin_data["hours"]
        except KeyError as exc:
            raise ValueError("Missing SEER cooling bin data config.") from exc
        if len(temps) != len(hours):
            raise ValueError("SEER cooling bin temperature/hour length mismatch.")
        return temps, hours
