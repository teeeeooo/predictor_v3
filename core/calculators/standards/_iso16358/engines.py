"""ISO 16358 CSPF and HSPF engine composition."""

from .context import ISOEngineContext
from .cspf_engine import CSPFSeasonalMixin
from .cspf_performance import CSPFPerformanceMixin
from .cspf_points import CSPFPointResolverMixin
from .cspf_result import CSPFResultMixin
from .hspf_cases import HSPFCaseEngineMixin
from .hspf_curves import HSPFCommonCurveMixin
from .hspf_engine import HSPFSeasonalMixin
from .hspf_extended import HSPFExtendedPerformanceMixin
from .hspf_load import HSPFLoadContextMixin
from .hspf_points import HSPFCommonPointMixin
from .hspf_snapshot import HSPFPerformanceSnapshotMixin
from .input import ISOInputPreparationMixin


class ISO16358CSPFEngine(
    ISOEngineContext,
    ISOInputPreparationMixin,
    CSPFPointResolverMixin,
    CSPFPerformanceMixin,
    CSPFResultMixin,
    CSPFSeasonalMixin,
):
    """ISO 16358-1 profile resolution, performance, and seasonal aggregation."""


class ISO16358HSPFEngine(
    ISOEngineContext,
    ISOInputPreparationMixin,
    HSPFCommonCurveMixin,
    HSPFExtendedPerformanceMixin,
    HSPFCommonPointMixin,
    HSPFLoadContextMixin,
    HSPFPerformanceSnapshotMixin,
    HSPFCaseEngineMixin,
    HSPFSeasonalMixin,
):
    """ISO 16358-2 supported-profile seasonal calculation owner."""
