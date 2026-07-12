"""Stable EN 14825 SEER/SCOP public facade."""

from ._en14825.context import EN14825ConfigContext
from ._en14825.performance import EN14825PerformanceCurve
from ._en14825.scop_context import SCOPClimateContext
from ._en14825.scop_engine import SCOPSeasonalEngine
from ._en14825.scop_performance import SCOPPerformanceCurve
from ._en14825.scop_points import SCOPPointResolver
from ._en14825.seer_engine import SEERSeasonalEngine
from ._en14825.seer_points import SEERPointResolver


class EN14825Calculator:
    """Compatibility facade over private EN configuration and engines."""

    def __init__(self, config_path: str = None):
        self._context = EN14825ConfigContext(config_path)
        for attribute in ("config_path", "config", "seer_config", "scop_config"):
            setattr(self, attribute, getattr(self._context, attribute))

        self._performance = EN14825PerformanceCurve()
        self._seer_points = SEERPointResolver(self._context, self._performance)
        self._seer_engine = SEERSeasonalEngine(
            self._context, self._seer_points, self._performance
        )
        self._scop_climate = SCOPClimateContext(self._context)
        self._scop_points = SCOPPointResolver(
            self._scop_climate, self._performance
        )
        self._scop_performance = SCOPPerformanceCurve(self._performance)
        self._scop_engine = SCOPSeasonalEngine(
            self._context,
            self._scop_climate,
            self._scop_points,
            self._performance,
            self._scop_performance,
        )

    def __setattr__(self, name: str, value) -> None:
        object.__setattr__(self, name, value)
        context = self.__dict__.get("_context")
        if context is not None and name in (
            "config_path",
            "config",
            "seer_config",
            "scop_config",
        ):
            setattr(context, name, value)

    def __getattr__(self, name: str):
        """Preserve relied-upon private helper access during the extraction."""
        for owner_name in (
            "_context",
            "_performance",
            "_seer_points",
            "_seer_engine",
            "_scop_climate",
            "_scop_points",
            "_scop_performance",
            "_scop_engine",
        ):
            owner = self.__dict__.get(owner_name)
            if owner is not None and hasattr(owner, name):
                return getattr(owner, name)
        raise AttributeError(
            f"{type(self).__name__!s} object has no attribute {name!r}"
        )

    def calculate_seer(
        self,
        test_points: dict,
        p_to: float,
        p_sb: float,
        p_ck: float,
        p_off: float,
        p_design_c: float,
        t_design_c: float = None,
        cd: float = None,
        *,
        appliance_type: str = None,
    ) -> dict:
        return self._seer_engine.calculate_seer(
            test_points,
            p_to,
            p_sb,
            p_ck,
            p_off,
            p_design_c,
            t_design_c,
            cd,
            appliance_type=appliance_type,
        )

    def calculate_seer_with_details(
        self,
        test_points: dict,
        p_to: float,
        p_sb: float,
        p_ck: float,
        p_off: float,
        p_design_c: float,
        t_design_c: float = None,
        cd: float = None,
        *,
        appliance_type: str = None,
    ) -> dict:
        return self._seer_engine.calculate_seer_with_details(
            test_points,
            p_to,
            p_sb,
            p_ck,
            p_off,
            p_design_c,
            t_design_c,
            cd,
            appliance_type=appliance_type,
        )

    def calculate_scop(
        self,
        test_points: dict,
        p_to: float,
        p_sb: float,
        p_ck: float,
        p_off: float,
        p_design_h: float,
        climate: str,
        cd: float = None,
        appliance_type: str = None,
        tbiv_temp_c: float = None,
        tol_temp_c: float = None,
    ) -> dict:
        return self._scop_engine.calculate_scop(
            test_points,
            p_to,
            p_sb,
            p_ck,
            p_off,
            p_design_h,
            climate,
            cd,
            appliance_type,
            tbiv_temp_c,
            tol_temp_c,
        )
