"""Headless Experiment Specification and campaign entrypoint."""

from apps.train.interfaces.headless.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
