"""Predict-only root entrypoint for the PySide6 rewrite."""

from apps.predict.app import main


if __name__ == "__main__":
    raise SystemExit(main())
