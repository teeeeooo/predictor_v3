"""Predict application bootstrap for the PySide6 rewrite."""

from apps.predict.ui.shell import PredictShell


def create_shell() -> PredictShell:
    """Create the minimal Predict shell placeholder."""
    return PredictShell()


def main() -> int:
    """Run the Predict application.

    The executable PySide6 window is added in a later skeleton slice.
    """
    raise RuntimeError("Predict PySide6 shell launch is not implemented yet.")


if __name__ == "__main__":
    raise SystemExit(main())
