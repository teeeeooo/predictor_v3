"""Stable AHRI 210/240 HSPF2 public facade."""

from ._ahri.hspf2_context import HSPF2ConfigContext
from ._ahri.hspf2_legacy import HSPF2LegacyEngine
from ._ahri.hspf2_points import HSPF2PointResolver
from ._ahri.hspf2_variable import HSPF2VariableCapacityEngine


class AHRIHSPF2Calculator:
    """Compatibility facade for variable-capacity and legacy HSPF2 paths."""

    def __init__(self, config_path: str):
        self._context = HSPF2ConfigContext(config_path)
        for attribute in (
            "config",
            "bin_temps",
            "bin_hours",
            "canonical_hspf2_bin_tables",
            "test_point_schema",
            "test_point_aliases",
            "test_point_temps",
            "constants",
            "defaults",
        ):
            setattr(self, attribute, getattr(self._context, attribute))
        self._point_resolver = HSPF2PointResolver(self.test_point_schema, self.test_point_aliases)
        self._variable_engine = HSPF2VariableCapacityEngine(self._context, self._point_resolver)
        self._legacy_engine = HSPF2LegacyEngine(self._context, self._point_resolver)

    def get_test_point_schema(self, mode: str = None) -> dict:
        return self._point_resolver.get_test_point_schema(mode)

    def legacy_to_canonical(self, test_points: dict) -> dict:
        return self._point_resolver.legacy_to_canonical(test_points)

    def canonical_to_internal_usage(self, test_points: dict) -> dict:
        return self._point_resolver.canonical_to_internal_usage(test_points)

    def calculate_hspf2_v2(self, test_points: dict, **kwargs) -> dict:
        return self._legacy_engine.calculate(test_points, **kwargs)

    def calculate_hspf2_v3(self, test_points: dict, **kwargs) -> dict:
        return self._variable_engine.calculate(test_points, **kwargs)

    def calculate_hspf2(self, test_points: dict, **kwargs) -> dict:
        return self.calculate_hspf2_v3(test_points, **kwargs)
