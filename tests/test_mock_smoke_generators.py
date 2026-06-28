"""Focused tests for DEV-only mock smoke generators."""

from __future__ import annotations

import subprocess
import sys
import json
from pathlib import Path

import pandas as pd
import pytest

from core.ml.features import BASE_FEATURES, TARGETS
from core.ml.inference import load_model, predict_row
from tools.dev.mock_smoke.generators import (
    PREDICTION_ARTIFACT_NAME,
    MANIFEST_NAME,
    TRAINING_DATA_NAME,
    install_local_model,
    write_mock_prediction_artifact,
    write_mock_training_data,
)


def _sample_row() -> dict[str, float]:
    return {
        "Cooling Capa": 3500.0,
        "Heating Capa": 3900.0,
        "ID Volume": 0.015,
        "Evap Area": 12.5,
        "Evap Volume": 0.002,
        "OD Volume": 0.045,
        "Cond Area": 25.0,
        "Cond Volume": 0.005,
        "Comp EER": 3.5,
        "Comp cc": 10.5,
        "R410A": 0.0,
        "R32": 1.0,
        "R290": 0.0,
        "EEV": 1.0,
        "Capi": 0.0,
    }


def test_mock_prediction_artifact_loads_and_predicts_all_targets(tmp_path):
    artifact_path = write_mock_prediction_artifact(output_dir=tmp_path)

    assert artifact_path == tmp_path / PREDICTION_ARTIFACT_NAME
    model_data = load_model(artifact_path)
    predictions = predict_row(model_data, _sample_row())

    assert set(predictions) == set(TARGETS)
    assert all(isinstance(value, float) for value in predictions.values())


def test_prediction_generator_default_does_not_write_production_model(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    production_model = repo_root / "model" / "model.pkl"
    existed_before = production_model.exists()

    subprocess.run(
        [
            sys.executable,
            "-B",
            "tools/dev/mock_smoke/generate_mock_prediction_artifact.py",
            "--output-dir",
            str(tmp_path),
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )

    assert (tmp_path / PREDICTION_ARTIFACT_NAME).exists()
    assert production_model.exists() is existed_before


def test_install_local_model_refuses_existing_file_without_force(tmp_path):
    artifact_path = write_mock_prediction_artifact(output_dir=tmp_path / "output")
    existing_model = tmp_path / "model" / "model.pkl"
    existing_model.parent.mkdir()
    existing_model.write_bytes(b"existing")

    with pytest.raises(FileExistsError):
        install_local_model(artifact_path, existing_model)

    assert existing_model.read_bytes() == b"existing"


def test_mock_training_data_contains_required_columns(tmp_path):
    csv_path = write_mock_training_data(output_dir=tmp_path)

    assert csv_path == tmp_path / TRAINING_DATA_NAME
    df = pd.read_csv(csv_path)
    assert len(df) >= 5
    assert set(BASE_FEATURES).issubset(df.columns)
    assert set(TARGETS).issubset(df.columns)


def test_mock_manifest_accumulates_generated_outputs(tmp_path):
    artifact_path = write_mock_prediction_artifact(
        output_dir=tmp_path,
        rows=8,
        seed=7,
        write_manifest=True,
    )
    csv_path = write_mock_training_data(
        output_dir=tmp_path,
        rows=9,
        seed=11,
        write_manifest=True,
    )

    manifest = json.loads((tmp_path / MANIFEST_NAME).read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "1.0"
    assert manifest["output_dir"] == str(tmp_path.resolve())
    assert manifest["entries"]["prediction_artifact"]["path"] == str(artifact_path)
    assert manifest["entries"]["prediction_artifact"]["seed"] == 7
    assert manifest["entries"]["prediction_artifact"]["rows"] == 8
    assert "created_at" in manifest["entries"]["prediction_artifact"]
    assert manifest["entries"]["training_data"]["path"] == str(csv_path)
    assert manifest["entries"]["training_data"]["seed"] == 11
    assert manifest["entries"]["training_data"]["rows"] == 9


def test_repo_local_mock_outputs_are_gitignored():
    repo_root = Path(__file__).resolve().parents[1]
    checks = subprocess.run(
        [
            "git",
            "check-ignore",
            ".dev_artifacts/mock_smoke/model.pkl",
            ".mock_smoke/mock_smoke_training_data.csv",
            ".mock_smoke/mock_smoke_manifest.json",
            "predictor_v3_mock_smoke/mock_smoke_model.pkl",
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )

    ignored = set(checks.stdout.splitlines())
    assert ".dev_artifacts/mock_smoke/model.pkl" in ignored
    assert ".mock_smoke/mock_smoke_training_data.csv" in ignored
    assert ".mock_smoke/mock_smoke_manifest.json" in ignored
    assert "predictor_v3_mock_smoke/mock_smoke_model.pkl" in ignored
