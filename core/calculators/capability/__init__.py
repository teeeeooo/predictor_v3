"""Canonical execution boundary for production standard calculations."""

from core.calculators.capability.gateway import (
    CapabilityConfigurationError,
    CapabilityNotFoundError,
    CapabilityRequestTypeError,
    StandardCalculationCapabilityError,
    StandardCalculationGateway,
    build_builtin_capability_registry,
    execute_standard_calculation,
)
from core.calculators.capability.requests import (
    AhriHspfRequest,
    AhriHspf2Request,
    AhriSeerRequest,
    AhriSeer2Request,
    BrazilCspfComplianceRequest,
    En14825ScopRequest,
    En14825SeerRequest,
    Iso16358CspfRequest,
    Iso16358HspfRequest,
    KsC9306CspfRequest,
    KsC9306HspfRequest,
)
from core.calculators.capability.results import (
    BrazilCspfComplianceResult,
    BrazilRuleEvaluation,
)
from core.calculators.capability.brazil import BrazilCspfComplianceError

__all__ = [
    "AhriHspfRequest", "AhriHspf2Request", "AhriSeerRequest", "AhriSeer2Request",
    "BrazilCspfComplianceRequest",
    "BrazilCspfComplianceError", "BrazilCspfComplianceResult",
    "BrazilRuleEvaluation", "CapabilityConfigurationError",
    "CapabilityNotFoundError", "CapabilityRequestTypeError", "En14825ScopRequest",
    "En14825SeerRequest", "Iso16358CspfRequest", "Iso16358HspfRequest",
    "KsC9306CspfRequest", "KsC9306HspfRequest", "StandardCalculationCapabilityError",
    "StandardCalculationGateway", "build_builtin_capability_registry",
    "execute_standard_calculation",
]
