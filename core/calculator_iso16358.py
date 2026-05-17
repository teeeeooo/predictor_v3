"""ISO 16358 CSPF/HSPF common standard calculator (new series).

This module is intentionally a Step 3 skeleton. During Step 2, preserved
legacy callers must import ``core.calculator_iso16358_legacy`` explicitly.
"""


class ISO16358Calculator:
    """New ISO 16358 calculator contract placeholder."""

    def __init__(self, config_path: str):
        raise NotImplementedError(
            "New ISO16358Calculator is not yet implemented. "
            "Use core.calculator_iso16358_legacy.ISO16358Calculator until "
            "Step 3 implementation lands."
        )

    def calculate_cspf(
        self,
        measured_inputs: dict,
        declared_capacity: float = None,
    ) -> dict:
        raise NotImplementedError(
            "New ISO16358Calculator.calculate_cspf is not yet implemented."
        )

    def calculate_hspf(self, measured_inputs: dict) -> dict:
        raise NotImplementedError(
            "New ISO16358Calculator.calculate_hspf is not yet implemented."
        )
