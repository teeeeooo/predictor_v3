from pathlib import Path


def test_ahri_application_adapters_import_without_ui_runtime():
    from apps.calculator.application.ahri import AhriHspf2Adapter, AhriSeer2Adapter

    assert AhriSeer2Adapter.__name__ == "AhriSeer2Adapter"
    assert AhriHspf2Adapter.__name__ == "AhriHspf2Adapter"


def test_ahri_application_package_does_not_import_ui_package():
    for path in (
        Path("apps/calculator/application/ahri/seer2_adapter.py"),
        Path("apps/calculator/application/ahri/hspf2_adapter.py"),
    ):
        source = path.read_text(encoding="utf-8")
        assert "apps.calculator.ui" not in source
        assert "tkinter" not in source
        assert "PySide6" not in source
        assert "core.calculators.dispatcher" not in source
        assert "apps.calculator.adapters.ahri_calculator_factory" in source


def test_ahri_ui_adapter_paths_are_shims():
    for path in (
        Path("apps/calculator/ui/ahri/seer2_adapter.py"),
        Path("apps/calculator/ui/ahri/hspf2_adapter.py"),
    ):
        source = path.read_text(encoding="utf-8")
        assert "core.calculators" not in source
        assert "class " not in source
        assert "application.ahri" in source


def test_ahri_sections_use_application_adapters():
    for path in (
        Path("apps/calculator/ui/sections/ahri_seer2_section.py"),
        Path("apps/calculator/ui/sections/ahri_hspf2_section.py"),
    ):
        source = path.read_text(encoding="utf-8")
        assert "apps.calculator.application.ahri" in source
        assert "core.calculators.dispatcher" not in source
