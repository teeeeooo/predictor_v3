from dataclasses import dataclass

import pytest

from core.calculators.capability import (
    CapabilityConfigurationError,
    CapabilityNotFoundError,
    CapabilityRequestTypeError,
    StandardCalculationGateway,
    build_builtin_capability_registry,
    execute_standard_calculation,
)
from core.calculators.capability import Iso16358CspfRequest, Iso16358HspfRequest
from core.calculators.capability.gateway import CapabilityRegistry


@dataclass(frozen=True)
class _Request:
    value: int


class _Handler:
    capability_id = "test.operation"
    request_type = _Request

    def __init__(self, result):
        self.result = result

    def execute(self, request):
        if request.value < 0:
            raise ValueError("engine validation")
        return self.result


def test_gateway_returns_exact_handler_result_object():
    raw_result = {"value": 1, "diagnostics": []}
    registry = CapabilityRegistry()
    registry.register(_Handler(raw_result))

    result = StandardCalculationGateway(registry).execute(
        "test.operation", _Request(1)
    )

    assert result is raw_result


def test_gateway_preserves_engine_exception_type_and_message():
    registry = CapabilityRegistry()
    registry.register(_Handler({}))

    with pytest.raises(ValueError, match="^engine validation$"):
        StandardCalculationGateway(registry).execute(
            "test.operation", _Request(-1)
        )


def test_gateway_owns_resolution_and_request_type_errors():
    registry = CapabilityRegistry()
    registry.register(_Handler({}))
    gateway = StandardCalculationGateway(registry)

    with pytest.raises(CapabilityNotFoundError) as missing:
        gateway.execute("missing.operation", _Request(1))
    assert isinstance(missing.value.__cause__, KeyError)

    with pytest.raises(CapabilityRequestTypeError):
        gateway.execute("test.operation", object())


def test_registry_rejects_duplicate_registration():
    registry = CapabilityRegistry()
    registry.register(_Handler({}))
    with pytest.raises(CapabilityConfigurationError):
        registry.register(_Handler({}))


def test_builtin_registry_exposes_all_active_operations():
    assert build_builtin_capability_registry().capability_ids == (
        "iso16358.cspf",
        "iso16358.hspf",
        "ks_c9306.cspf",
        "ks_c9306.hspf",
        "en14825.seer",
        "en14825.scop",
        "ahri210240.seer",
        "ahri210240.hspf",
        "ahri210240.seer2",
        "ahri210240.hspf2",
        "brazil.cspf_compliance",
    )


@pytest.mark.parametrize(
    ("capability_id", "calculation_request"),
    (
        ("iso16358.cspf", Iso16358CspfRequest("ks_c9306_cspf", {})),
        ("iso16358.cspf", Iso16358CspfRequest("hong_kong_hspf", {})),
        ("iso16358.hspf", Iso16358HspfRequest("saso_t3_cspf", {})),
    ),
)
def test_builtin_operation_rejects_incompatible_profile_before_construction(
    monkeypatch, capability_id, calculation_request
):
    constructed = False

    def fail_if_constructed(**_kwargs):
        nonlocal constructed
        constructed = True
        raise AssertionError("calculator must not be constructed")

    monkeypatch.setattr(
        "core.calculators.capability.gateway.create_calculator_for_profile",
        fail_if_constructed,
    )

    with pytest.raises(CapabilityConfigurationError):
        execute_standard_calculation(capability_id, calculation_request)
    assert constructed is False


@pytest.mark.parametrize("profile_id", ("missing_profile", "asnzs_excel_hspf_compat"))
def test_unknown_or_disabled_profile_preserves_resolver_value_error(profile_id):
    with pytest.raises(ValueError, match="Calculator profile selector"):
        execute_standard_calculation(
            "iso16358.cspf", Iso16358CspfRequest(profile_id, {})
        )


def test_production_application_does_not_import_standard_engines_or_dispatcher():
    from pathlib import Path

    root = Path(__file__).parents[1]
    production_roots = (
        root / "apps" / "calculator" / "application",
        root / "apps" / "calculator" / "ui",
        root / "apps" / "predict",
    )
    forbidden = (
        "core.calculators.standards",
        "core.calculators.dispatcher",
        "apps.calculator.adapters.core_calculator_dispatcher",
        "execute_request_with_calculator",
    )
    violations = []
    for production_root in production_roots:
        for path in production_root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if any(token in text for token in forbidden):
                violations.append(str(path.relative_to(root)))
    assert violations == []


def test_production_callers_do_not_invoke_standard_methods_outside_capability():
    from pathlib import Path

    root = Path(__file__).parents[1]
    production_roots = (
        root / "apps" / "calculator" / "application",
        root / "apps" / "calculator" / "adapters",
        root / "apps" / "calculator" / "ui",
        root / "apps" / "predict",
    )
    direct_calls = (
        ".calculate_cspf(", ".calculate_hspf(", ".calculate_seer(",
        ".calculate_scop(", ".calculate_seer2(", ".calculate_hspf2(",
    )
    violations = []
    for production_root in production_roots:
        for path in production_root.rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            if any(call in source for call in direct_calls):
                violations.append(str(path.relative_to(root)))
    assert violations == []
