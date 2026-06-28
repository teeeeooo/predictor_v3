import importlib
import sys

import pytest

from apps.calculator.application import profile_resolver as app_resolver
from apps.calculator.ui import profile_resolver as ui_resolver


def test_application_profile_resolver_matches_ui_compatibility_shim():
    assert app_resolver.calculation_mode_labels() == ui_resolver.calculation_mode_labels()
    assert app_resolver.region_labels() == ui_resolver.region_labels()
    assert app_resolver.two_point_profile_labels() == ui_resolver.two_point_profile_labels()

    assert app_resolver.supported_metrics_for("Hong Kong") == ui_resolver.supported_metrics_for(
        "Hong Kong"
    )
    assert (
        app_resolver.resolve_profile_id("Hong Kong", "CSPF")
        == ui_resolver.resolve_profile_id("Hong Kong", "CSPF")
        == "hong_kong_cspf"
    )
    assert (
        app_resolver.resolve_two_point_profile_id("India ISEER")
        == ui_resolver.resolve_two_point_profile_id("India ISEER")
        == "india_iseer_cspf"
    )
    assert (
        app_resolver.resolve_calculation_mode_profile_id("SASO T3")
        == ui_resolver.resolve_calculation_mode_profile_id("SASO T3")
        == "saso_t3_cspf"
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "apps.calculator.application",
        "apps.calculator.application.profile_resolver",
        "apps.calculator.adapters",
        "apps.calculator.adapters.core_calculator_dispatcher",
    ],
)
def test_application_boundary_modules_do_not_import_ui_runtimes(module_name):
    qt_binding = "Py" + "Qt5"
    pyside_binding = "Py" + "Side6"

    before = set(sys.modules)
    for name in list(sys.modules):
        if name == module_name:
            del sys.modules[name]

    importlib.import_module(module_name)

    loaded_after_import = set(sys.modules) - before
    tkinter_loaded = any(
        name == "tkinter" or name.startswith("tkinter.") for name in loaded_after_import
    )
    pyqt_loaded = any(name.startswith(qt_binding) for name in loaded_after_import)
    pyside_loaded = any(
        name.startswith(pyside_binding) for name in loaded_after_import
    )

    assert not tkinter_loaded
    assert not pyqt_loaded
    assert not pyside_loaded


def test_core_calculator_dispatcher_adapter_delegates_to_core_dispatcher(monkeypatch):
    from apps.calculator.adapters import core_calculator_dispatcher

    calls = []
    sentinel = object()

    def fake_create_calculator_for_profile(**kwargs):
        calls.append(kwargs)
        return sentinel

    monkeypatch.setattr(
        core_calculator_dispatcher,
        "_create_core_calculator",
        fake_create_calculator_for_profile,
    )

    result = core_calculator_dispatcher.create_calculator_for_profile(
        profile_id="hong_kong_cspf",
        standard="ISO_16358",
        region="hong_kong",
        metric="CSPF",
        mode="cooling",
    )

    assert result is sentinel
    assert calls == [
        {
            "profile_id": "hong_kong_cspf",
            "standard": "ISO_16358",
            "region": "hong_kong",
            "metric": "CSPF",
            "mode": "cooling",
        }
    ]
