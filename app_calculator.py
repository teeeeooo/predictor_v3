"""Calculator application root entrypoint.

This delegates execution to the canonical apps.calculator.app entrypoint.
"""

from apps.calculator.app import main


if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)
