"""Stable AHRI 210/240 HSPF2 public facade and product dispatch."""

from ._ahri.hspf2_context import HSPF2ConfigContext
from ._ahri.hspf2_dual import HSPF2DualStageEngine
from ._ahri.hspf2_points import HSPF2PointResolver
from ._ahri.hspf2_triple_northern import HSPF2TripleNorthernEngine
from ._ahri.hspf2_variable import HSPF2VariableCapacityEngine
from ._ahri.product import (
    DUAL_STAGE,
    TRIPLE_CAPACITY_NORTHERN,
    VARIABLE_CAPACITY,
    normalize_product_classification,
)


class AHRIHSPF2Calculator:
    """Compatibility facade for variable, dual, and triple northern HSPF2 paths."""

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
        self._dual_engine = HSPF2DualStageEngine(self._context)
        self._triple_engine = HSPF2TripleNorthernEngine(self._context)

    def get_test_point_schema(self, mode: str = None) -> dict:
        return self._point_resolver.get_test_point_schema(mode)

    def normalize_public_test_points(self, test_points: dict) -> dict:
        return self._point_resolver.normalize_public_test_points(test_points)

    def calculate_hspf2_v3(self, test_points: dict, **kwargs) -> dict:
        return self._variable_engine.calculate(test_points, **kwargs)

    def calculate_hspf2(
        self,
        test_points: dict,
        *,
        product_classification: str = VARIABLE_CAPACITY,
        **kwargs,
    ) -> dict:
        product = normalize_product_classification(product_classification, metric="HSPF2")
        if product == VARIABLE_CAPACITY:
            return self.calculate_hspf2_v3(test_points, **kwargs)
        if product == DUAL_STAGE:
            return self._dual_engine.calculate(test_points, **kwargs)
        if product == TRIPLE_CAPACITY_NORTHERN:
            return self._triple_engine.calculate(test_points, **kwargs)
        raise ValueError(f"Unsupported HSPF2 product classification: {product!r}")
