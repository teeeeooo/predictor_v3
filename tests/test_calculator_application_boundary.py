import importlib
from pathlib import Path
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
        "apps.calculator.adapters.ahri_calculator_factory",
        "apps.calculator.adapters.en14825_calculator_factory",
        "apps.calculator.adapters.saso_t3_calculator",
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


def test_arc12_completed_ui_surfaces_do_not_own_core_dispatcher_or_config_mutation():
    paths = [
        Path("apps/calculator/ui/sections/iso_iseer_2point_section.py"),
        Path("apps/calculator/ui/batch_dialogs/profiles/iso_iseer_2point.py"),
        Path("apps/calculator/ui/sections/iso_saso_t3_section.py"),
        Path("apps/calculator/ui/batch_dialogs/profiles/saso_t3.py"),
        Path("apps/calculator/ui/sections/hong_kong_cspf_section.py"),
        Path("apps/calculator/ui/sections/hong_kong_cspf_batch_spec.py"),
        Path("apps/calculator/ui/sections/hong_kong_hspf_section.py"),
        Path("apps/calculator/ui/batch_dialogs/profiles/hong_kong_hspf.py"),
        Path("apps/calculator/ui/sections/en14825_seer_section.py"),
        Path("apps/calculator/ui/sections/en14825_scop_section.py"),
        Path("apps/calculator/ui/sections/ahri_seer2_section.py"),
        Path("apps/calculator/ui/sections/ahri_hspf2_section.py"),
    ]

    for path in paths:
        source = path.read_text(encoding="utf-8")
        assert "core.calculators.dispatcher" not in source, path
        assert "create_calculator_for_profile" not in source, path
        assert "calculate_cspf" not in source, path
        assert "calculate_hspf" not in source, path
        assert ".config[" not in source, path


def test_arc12_application_packages_do_not_import_ui_packages_or_runtimes():
    for path in Path("apps/calculator/application").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "apps.calculator.ui" not in source, path
        assert "tkinter" not in source, path
        assert "PySide6" not in source, path


def test_arc12_application_packages_use_outbound_calculator_adapters():
    for path in Path("apps/calculator/application").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "core.calculators.dispatcher" not in source, path

    for path in Path("apps/calculator/application/en14825").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "core.calculators.standards.en14825" not in source, path

    saso_source = Path("apps/calculator/application/saso_t3/usecase.py").read_text(
        encoding="utf-8"
    )
    assert ".config[" not in saso_source
    assert "execute_standard_calculation" in saso_source
    assert "calculator_gateway" not in saso_source
