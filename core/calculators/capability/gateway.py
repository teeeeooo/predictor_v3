"""Registry, handlers, and read-only production gateway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from core.calculators.capability.requests import (
    AhriHspf2Request, AhriSeer2Request, En14825ScopRequest, En14825SeerRequest,
    Iso16358CspfRequest, Iso16358HspfRequest, KsC9306CspfRequest, KsC9306HspfRequest,
)
from core.calculators.dispatcher import create_calculator_for_profile

RequestT = TypeVar("RequestT")


class StandardCalculationCapabilityError(Exception):
    """Base error for contracts owned by the capability boundary."""


class CapabilityNotFoundError(StandardCalculationCapabilityError):
    pass


class CapabilityRequestTypeError(StandardCalculationCapabilityError, TypeError):
    pass


class CapabilityConfigurationError(StandardCalculationCapabilityError):
    pass


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

    def execute(self, request):
        calculator = create_calculator_for_profile(profile_id=request.profile_id)
        return execute_request_with_calculator(request, calculator, self.method_name)


def execute_request_with_calculator(request, calculator, method_name: str | None = None):
    """Test-composition helper; production handlers construct their own calculator."""
    if isinstance(request, Iso16358CspfRequest) and request.test_selection is not None:
        calculator.config["cspf_test_profile"]["test_selection"] = request.test_selection
    if isinstance(request, (Iso16358CspfRequest, KsC9306CspfRequest)):
        kwargs = {}
        if request.declared_capacity is not None:
            kwargs["declared_capacity"] = request.declared_capacity
        return getattr(calculator, method_name or "calculate_cspf")(request.measured_points, **kwargs)
    if isinstance(request, (Iso16358HspfRequest, KsC9306HspfRequest)):
        return getattr(calculator, method_name or "calculate_hspf")(request.measured_points)
    if isinstance(request, (En14825SeerRequest, En14825ScopRequest)):
        resolved_name = method_name or (
            "calculate_seer_with_details" if isinstance(request, En14825SeerRequest)
            else "calculate_scop"
        )
        method = getattr(calculator, resolved_name, None)
        if method is None and resolved_name == "calculate_seer_with_details":
            method = calculator.calculate_seer
        return method(**dict(request.parameters))
    if isinstance(request, AhriSeer2Request):
        return calculator.calculate_seer2(
            request.test_points, system_type=request.system_type,
            p_w_off=request.p_w_off, cd_low=request.cd_low,
        )
    if isinstance(request, AhriHspf2Request):
        return calculator.calculate_hspf2(
            request.test_points, **dict(request.parameters)
        )
    raise CapabilityConfigurationError(
        f"Unsupported built-in request type: {type(request).__name__}"
    )


def build_builtin_capability_registry() -> CapabilityRegistry:
    registry = CapabilityRegistry()
    definitions = (
        ("iso16358.cspf", Iso16358CspfRequest, "calculate_cspf"),
        ("iso16358.hspf", Iso16358HspfRequest, "calculate_hspf"),
        ("ks_c9306.cspf", KsC9306CspfRequest, "calculate_cspf"),
        ("ks_c9306.hspf", KsC9306HspfRequest, "calculate_hspf"),
        ("en14825.seer", En14825SeerRequest, "calculate_seer_with_details"),
        ("en14825.scop", En14825ScopRequest, "calculate_scop"),
        ("ahri210240.seer2", AhriSeer2Request, "calculate_seer2"),
        ("ahri210240.hspf2", AhriHspf2Request, "calculate_hspf2"),
    )
    for capability_id, request_type, method_name in definitions:
        registry.register(_MethodHandler(capability_id, request_type, method_name))
    if registry.capability_ids != tuple(item[0] for item in definitions):
        raise CapabilityConfigurationError("Built-in capability registry is incomplete")
    return registry


_BUILTIN_GATEWAY = StandardCalculationGateway(build_builtin_capability_registry())


def execute_standard_calculation(capability_id: str, request: object):
    """Execute through the immutable built-in production composition."""
    return _BUILTIN_GATEWAY.execute(capability_id, request)
