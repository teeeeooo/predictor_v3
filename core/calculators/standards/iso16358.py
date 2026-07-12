"""Stable ISO 16358 CSPF/HSPF public facade."""

from ._iso16358.context import CONTEXT_ATTRIBUTES, ISO16358ConfigContext
from ._iso16358.engines import ISO16358CSPFEngine, ISO16358HSPFEngine


class ISO16358Calculator:
    """Compatibility facade over separate ISO 16358-1 and -2 engines."""

    def __init__(self, config_path: str):
        self._context = ISO16358ConfigContext(config_path)
        for attribute in CONTEXT_ATTRIBUTES:
            setattr(self, attribute, getattr(self._context, attribute))
        self._cspf_engine = ISO16358CSPFEngine(self._context)
        self._hspf_engine = ISO16358HSPFEngine(self._context)

    def __setattr__(self, name: str, value) -> None:
        object.__setattr__(self, name, value)
        context = self.__dict__.get("_context")
        if context is not None and name in CONTEXT_ATTRIBUTES:
            setattr(context, name, value)

    def __getattr__(self, name: str):
        for owner_name in ("_cspf_engine", "_hspf_engine"):
            owner = self.__dict__.get(owner_name)
            if owner is not None and hasattr(owner, name):
                return getattr(owner, name)
        raise AttributeError(
            f"{type(self).__name__!s} object has no attribute {name!r}"
        )

    def calculate_cspf(
        self,
        measured_inputs: dict,
        declared_capacity: float = None,
    ) -> dict:
        return self._cspf_engine.calculate_cspf(
            measured_inputs, declared_capacity
        )

    def calculate_hspf_iso16358_common(
        self,
        measured_inputs: dict,
        rated_heating_capacity: float | None = None,
        aux_cop: float = 1.0,
    ) -> dict:
        return self._hspf_engine.calculate_hspf_iso16358_common(
            measured_inputs, rated_heating_capacity, aux_cop
        )

    def calculate_hspf(
        self, measured_inputs: dict, aux_cop: float = 1.0
    ) -> dict:
        return self._hspf_engine.calculate_hspf(measured_inputs, aux_cop)
