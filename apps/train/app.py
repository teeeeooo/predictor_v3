"""Trainer application bootstrap for the PySide6 rewrite."""

import sys

from PySide6.QtWidgets import QApplication

from apps.train.composition import (
    DEFAULT_BOOTSTRAP_MANIFEST_PATH,
    DEFAULT_DEFINITION_ROOT,
    PROJECT_ROOT,
    create_shell,
    default_generation_root,
)


def main() -> int:
    """Run the Trainer application."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = create_shell()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
