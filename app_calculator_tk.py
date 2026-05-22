"""Tkinter calculator-only entrypoint — feasibility spike.

This is NOT a replacement for ``app_calculator.py``. The PyQt5
calculator entrypoint (``app_calculator.py`` → ``ui/calc_window.py``)
remains the reference / production-direction implementation. See
``docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md``
for the decision criteria that gate whether this spike continues.

No PyQt5 import is allowed in this module or in ``ui_tk/``.
"""

from ui_tk.calculator_app import main


if __name__ == "__main__":
    main()
