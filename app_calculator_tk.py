"""Tkinter calculator-only temporary compatibility entrypoint (deprecated).

This is a temporary compatibility entrypoint that delegates to the canonical
apps.calculator.app entrypoint. Root ``app_calculator.py`` also delegates to
the same canonical entrypoint.

No PyQt5 import is allowed in this module.
"""

from apps.calculator.app import main


if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)
