"""KS C 9306 CSPF and HSPF engine composition."""

from .context import KSEngineContext
from .cspf_engine import KSCSPFSeasonalMixin
from .cspf_performance import KSCSPFPerformanceMixin
from .cspf_points import KSCSPFPointResolverMixin
from .hspf_cases import KSHSPFCaseEngineMixin
from .hspf_curves import KSHSPFPerformanceMixin
from .hspf_engine import KSHSPFSeasonalMixin
from .hspf_points import KSHSPFPointResolverMixin
from .input import KSInputPreparationMixin


class KSC9306CSPFEngine(
    KSEngineContext,
    KSInputPreparationMixin,
    KSCSPFPointResolverMixin,
    KSCSPFPerformanceMixin,
    KSCSPFSeasonalMixin,
):
    """KS-specific CSPF point, intersection, seasonal, and rounding owner."""


class KSC9306HSPFEngine(
    KSEngineContext,
    KSInputPreparationMixin,
    KSHSPFPointResolverMixin,
    KSHSPFPerformanceMixin,
    KSHSPFCaseEngineMixin,
    KSHSPFSeasonalMixin,
):
    """KS-specific HSPF point, curve, fallback, and seasonal owner."""
