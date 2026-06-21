"""Tests for the calculator application package entrypoints."""


def test_entrypoint_imports_do_not_run_gui():
    """Verify that importing any entrypoint does not run GUI or execute main loop."""
    # Importing these should be a side-effect-free import
    import apps.calculator.app
    import app_calculator

    assert apps.calculator.app is not None
    assert app_calculator is not None


def test_apps_calculator_app_main_delegation(monkeypatch):
    """Verify that apps.calculator.app.main calls apps.calculator.ui.calculator_app.main."""
    called = False

    def mock_run_tk_calculator():
        nonlocal called
        called = True

    # Monkeypatch the imported _run_tk_calculator
    import apps.calculator.app
    monkeypatch.setattr(apps.calculator.app, "_run_tk_calculator", mock_run_tk_calculator)

    exit_code = apps.calculator.app.main()
    assert exit_code == 0
    assert called is True


def test_app_calculator_delegates_to_canonical_main():
    """Verify that app_calculator.main is the canonical main function."""
    import app_calculator
    import apps.calculator.app

    assert app_calculator.main is apps.calculator.app.main
