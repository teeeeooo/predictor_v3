from pathlib import Path


def test_en14825_application_adapters_import_without_ui_runtime():
    from apps.calculator.application.en14825 import ScopAdapter, SeerAdapter

    assert SeerAdapter.__name__ == "SeerAdapter"
    assert ScopAdapter.__name__ == "ScopAdapter"


def test_en14825_application_package_does_not_import_ui_package():
    for path in (
        Path("apps/calculator/application/en14825/seer_adapter.py"),
        Path("apps/calculator/application/en14825/scop_adapter.py"),
        Path("apps/calculator/application/en14825/seer_models.py"),
        Path("apps/calculator/application/en14825/scop_models.py"),
    ):
        source = path.read_text(encoding="utf-8")
        assert "apps.calculator.ui" not in source
        assert "tkinter" not in source
        assert "PySide6" not in source


def test_en14825_ui_adapter_paths_are_shims():
    for path in (
        Path("apps/calculator/ui/en14825/seer_adapter.py"),
        Path("apps/calculator/ui/en14825/scop_adapter.py"),
    ):
        source = path.read_text(encoding="utf-8")
        assert "core.calculators" not in source
        assert "class " not in source
        assert "application.en14825" in source


def test_en14825_sections_use_application_adapters():
    for path in (
        Path("apps/calculator/ui/sections/en14825_seer_section.py"),
        Path("apps/calculator/ui/sections/en14825_scop_section.py"),
    ):
        source = path.read_text(encoding="utf-8")
        assert "apps.calculator.application.en14825" in source
        assert "core.calculators" not in source
