"""Registry, handlers, and read-only production gateway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from core.calculators.capability.brazil import BrazilCspfComplianceHandler
from core.calculators.capability.compatibility import validate_profile_for_capability
from core.calculators.capability.errors import (
    CapabilityConfigurationError,
    CapabilityNotFoundError,
    CapabilityRequestTypeError,
    StandardCalculationCapabilityError,
)
from core.calculators.capability.requests import (
    AhriHspf2Request, AhriSeer2Request, En14825ScopRequest, En14825SeerRequest,
    BrazilCspfComplianceRequest,
    Iso16358CspfRequest, Iso16358HspfRequest, KsC9306CspfRequest, KsC9306HspfRequest,
)
from core.calculators.dispatcher import create_calculator_for_profile
from core.calculators.profiles import (
    CalculatorProfile,
    list_calculator_profiles,
    resolve_calculator_profile,
)

RequestT = TypeVar("RequestT")


class CapabilityHandler(Protocol, Generic[RequestT]):
    capability_id: str
    request_type: type[RequestT]
    def execute(self, request: RequestT): ...


class CapabilityRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, CapabilityHandler] = {}

    def register(self, handler: CapabilityHandler) -> None:
        capability_id = getattr(handler, "capability_id", None)
        request_type = getattr(handler, "request_type", None)
        if not isinstance(capability_id, str) or not capability_id:
            raise CapabilityConfigurationError("Handler must declare a capability_id")
        if not isinstance(request_type, type):
            raise CapabilityConfigurationError(
                f"Handler {capability_id!r} must declare a request type"
            )
        if capability_id in self._handlers:
            raise CapabilityConfigurationError(
                f"Duplicate capability registration: {capability_id!r}"
            )
        self._handlers[capability_id] = handler

    def resolve(self, capability_id: str) -> CapabilityHandler:
        try:
            return self._handlers[capability_id]
        except KeyError as exc:
            raise CapabilityNotFoundError(
                f"Unknown standard calculation capability: {capability_id!r}"
            ) from exc

    @property
    def capability_ids(self) -> tuple[str, ...]:
        return tuple(self._handlers)


class StandardCalculationGateway:
    def __init__(self, registry: CapabilityRegistry) -> None:
        self._registry = registry

    @property
    def capability_ids(self) -> tuple[str, ...]:
        return self._registry.capability_ids

    def execute(self, capability_id: str, request: object):
        handler = self._registry.resolve(capability_id)
        if not isinstance(request, handler.request_type):
            raise CapabilityRequestTypeError(
                f"{capability_id!r} requires {handler.request_type.__name__}; "
                f"received {type(request).__name__}"
            )
        return handler.execute(request)


@dataclass(frozen=True)
class _MethodHandler:
    capability_id: str
    request_type: type
    method_name: str
    calculator_id: str
    metrics: tuple[str, ...]
    mode: str
    standard: str

    def execute(self, request):
        profile = resolve_calculator_profile(profile_id=request.profile_id)
        self._validate_profile(profile)
        calculator = create_calculator_for_profile(profile_id=request.profile_id)
        return _invoke_calculator(request, calculator, self.method_name)

    def _validate_profile(self, profile: CalculatorProfile) -> None:
        validate_profile_for_capability(
            profile,
            self.capability_id,
            calculator_id=self.calculator_id,
            metrics=self.metrics,
            mode=self.mode,
            standard=self.standard,
        )


def _invoke_calculator(request, calculator, method_name: str):
    if isinstance(request, Iso16358CspfRequest) and request.test_selection is not None:
        calculator.config["cspf_test_profile"]["test_selection"] = request.test_selection
    if isinstance(request, (Iso16358CspfRequest, KsC9306CspfRequest)):
        kwargs = {}
        if request.declared_capacity is not None:
            kwargs["declared_capacity"] = request.declared_capacity
        return getattr(calculator, method_name)(request.measured_points, **kwargs)
    if isinstance(request, (Iso16358HspfRequest, KsC9306HspfRequest)):
        return getattr(calculator, method_name)(request.measured_points)
    if isinstance(request, (En14825SeerRequest, En14825ScopRequest)):
        method = getattr(calculator, method_name, None)
        if method is None and method_name == "calculate_seer_with_details":
            method = calculator.calculate_seer
        return method(**dict(request.parameters))
    if isinstance(request, AhriSeer2Request):
        return calculator.calculate_seer2(
            request.test_points,
            system_type=request.system_type,
            p_w_off=request.p_w_off,
            cd_low=request.cd_low,
            product_classification=request.product_classification,
            options=dict(request.parameters),
        )
    if isinstance(request, AhriHspf2Request):
        return calculator.calculate_hspf2(
            request.test_points,
            product_classification=request.product_classification,
            **dict(request.parameters),
        )
    raise CapabilityConfigurationError(
        f"Unsupported built-in request type: {type(request).__name__}"
    )


def build_builtin_capability_registry() -> CapabilityRegistry:
    registry = CapabilityRegistry()
    definitions = (
        ("iso16358.cspf", Iso16358CspfRequest, "calculate_cspf", "iso16358", ("CSPF", "ISEER"), "cooling", "ISO_16358"),
        ("iso16358.hspf", Iso16358HspfRequest, "calculate_hspf", "iso16358", ("HSPF",), "heating", "ISO_16358"),
        ("ks_c9306.cspf", KsC9306CspfRequest, "calculate_cspf", "ks_c9306", ("CSPF",), "cooling", "KS_C_9306"),
        ("ks_c9306.hspf", KsC9306HspfRequest, "calculate_hspf", "ks_c9306", ("HSPF",), "heating", "KS_C_9306"),
        ("en14825.seer", En14825SeerRequest, "calculate_seer_with_details", "en14825", ("SEER",), "cooling", "EN_14825"),
        ("en14825.scop", En14825ScopRequest, "calculate_scop", "en14825", ("SCOP",), "heating", "EN_14825"),
        ("ahri210240.seer2", AhriSeer2Request, "calculate_seer2", "ahri_seer2", ("SEER2",), "cooling", "AHRI_210_240"),
        ("ahri210240.hspf2", AhriHspf2Request, "calculate_hspf2", "ahri_hspf2", ("HSPF2",), "heating", "AHRI_210_240"),
    )
    for definition in definitions:
        registry.register(_MethodHandler(*definition))
    registry.register(BrazilCspfComplianceHandler())
    expected_ids = tuple(item[0] for item in definitions) + (
        "brazil.cspf_compliance",
    )
    if registry.capability_ids != expected_ids:
        raise CapabilityConfigurationError("Built-in capability registry is incomplete")
    registered_ids = set(registry.capability_ids)
    for profile in list_calculator_profiles(enabled_only=False):
        if profile.capability_ids is None:
            continue
        if not profile.capability_ids or not set(profile.capability_ids) <= registered_ids:
            raise CapabilityConfigurationError(
                f"Profile {profile.profile_id!r} has an invalid capability allowlist"
            )
    return registry


_BUILTIN_GATEWAY = StandardCalculationGateway(build_builtin_capability_registry())


def execute_standard_calculation(capability_id: str, request: object):
    """Execute through the immutable built-in production composition."""
    return _BUILTIN_GATEWAY.execute(capability_id, request)
