"""Passive readiness slots for Arc 15A Data Definition reports."""

from __future__ import annotations

import csv
from pathlib import Path

from core.data_definition.model import ProjectedFeatureRow
from core.data_definition.report_model import ReadinessCheck


def build_readiness_checks(
    projected_features: tuple[ProjectedFeatureRow, ...],
    training_data_path: str | Path | None = None,
) -> tuple[ReadinessCheck, ...]:
    """Return passive readiness checks without retraining or model inspection."""
    training_check = (
        _training_header_check(projected_features, Path(training_data_path))
        if training_data_path is not None
        else ReadinessCheck(
            name="training_headers",
            status="not_evaluated",
            message=(
                "Caller did not provide a training data path for the Arc 15A "
                "passive header check."
            ),
        )
    )
    return (
        training_check,
        ReadinessCheck(
            name="model_activation",
            status="not_evaluated",
            message="Arc 15A does not inspect model artifacts or activate models.",
        ),
        ReadinessCheck(
            name="restart_impact",
            status="not_evaluated",
            message="Schema changes remain restart-required; no live reload is attempted.",
        ),
    )


def _training_header_check(
    projected_features: tuple[ProjectedFeatureRow, ...],
    data_path: Path,
) -> ReadinessCheck:
    if not data_path.is_file():
        return ReadinessCheck(
            name="training_headers",
            status="unavailable",
            message=f"Training data path is not a file for passive header check: {data_path}",
        )
    headers = _read_headers(data_path)
    if not headers:
        return ReadinessCheck(
            name="training_headers",
            status="unavailable",
            message=f"Training data header row is empty: {data_path}",
        )
    required = {
        row.ml_name
        for row in projected_features
        if row.active and row.role in {"input", "auto", "one_hot", "result"}
    }
    missing = sorted(required - headers)
    if missing:
        return ReadinessCheck(
            name="training_headers",
            status="missing",
            message=f"Missing training header(s): {', '.join(missing)}",
        )
    return ReadinessCheck(
        name="training_headers",
        status="ok",
        message="Training data headers cover projected active raw feature rows.",
    )


def _read_headers(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.reader(csv_file)
        try:
            return {header.strip() for header in next(reader) if header.strip()}
        except StopIteration:
            return set()
