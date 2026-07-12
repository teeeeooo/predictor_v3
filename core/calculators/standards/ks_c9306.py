"""Stable KS C 9306 CSPF/HSPF public facade."""

from ._ks_c9306.context import CONTEXT_ATTRIBUTES, KSC9306ConfigContext
from ._ks_c9306.engines import KSC9306CSPFEngine, KSC9306HSPFEngine


class KSC9306Calculator:
    """Compatibility facade over independent KS CSPF and HSPF owners."""

    def __init__(self, config: dict, bin_hours=None, default_cd: float = 0.25):
        self._wire_context(
            KSC9306ConfigContext(config, bin_hours, default_cd)
        )

    @classmethod
    def from_config_path(cls, config_path: str) -> "KSC9306Calculator":
        instance = cls.__new__(cls)
        instance._wire_context(KSC9306ConfigContext.from_config_path(config_path))
        return instance

    def _wire_context(self, context: KSC9306ConfigContext) -> None:
        self._context = context
        for attribute in CONTEXT_ATTRIBUTES:
            setattr(self, attribute, getattr(context, attribute))
        self._cspf_engine = KSC9306CSPFEngine(context)
        self._hspf_engine = KSC9306HSPFEngine(context)

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
        self, measured_inputs: dict, declared_capacity: float = None
    ) -> dict:
        return self._cspf_engine.calculate_cspf(
            measured_inputs, declared_capacity
        )

    def calculate_hspf(
        self, measured_inputs: dict, aux_cop: float = 1.0
    ) -> dict:
        return self._hspf_engine.calculate_hspf(measured_inputs, aux_cop)
