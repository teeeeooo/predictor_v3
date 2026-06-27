"""Trainer application bootstrap for the PySide6 rewrite."""

import sys

from PySide6.QtWidgets import QApplication

from apps.train.ui.shell import TrainShell


def create_shell() -> TrainShell:
    """Create the minimal Trainer shell."""
    return TrainShell()


def main() -> int:
    """Run the Trainer application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = create_shell()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
