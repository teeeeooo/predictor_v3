from dataclasses import dataclass

import pytest

from core.calculators.capability import (
    CapabilityConfigurationError,
    CapabilityNotFoundError,
    CapabilityRequestTypeError,
    StandardCalculationGateway,
    build_builtin_capability_registry,
)
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
        "ahri210240.seer2",
        "ahri210240.hspf2",
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
    )
    violations = []
    for production_root in production_roots:
        for path in production_root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if any(token in text for token in forbidden):
                violations.append(str(path.relative_to(root)))
    assert violations == []
