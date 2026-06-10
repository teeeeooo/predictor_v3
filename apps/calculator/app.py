"""Calculator application entrypoint."""

from apps.calculator.ui.calculator_app import main as _run_tk_calculator


def main() -> int:
    """Run the Tkinter-based calculator application."""
    _run_tk_calculator()
    return 0


if __name__ == "__main__":
    raise SystemExit(main() or 0)
