"""Trainer application bootstrap for the PySide6 rewrite."""

from apps.train.ui.shell import TrainShell


def create_shell() -> TrainShell:
    """Create the minimal Trainer shell placeholder."""
    return TrainShell()


def main() -> int:
    """Run the Trainer application.

    The executable PySide6 window is added in a later skeleton slice.
    """
    raise RuntimeError("Trainer PySide6 shell launch is not implemented yet.")


if __name__ == "__main__":
    raise SystemExit(main())
