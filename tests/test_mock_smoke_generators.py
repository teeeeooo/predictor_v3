"""Focused tests for DEV-only mock smoke generators."""

from __future__ import annotations

import subprocess
import sys
import json
from pathlib import Path

import pandas as pd
import pytest

from core.mapping.autofill import build_autofill_updates
from core.mapping.paths import MAPPING_JSON_FILE
from core.ml.features import BASE_FEATURES, TARGETS
from core.ml.artifacts import MODEL_FILE, TRAIN_DATA_FILE
from core.ml.catalog_fingerprint import CATALOG_FINGERPRINT_KEY
from core.ml.inference import load_model, predict_row
from core.predictor_schema.columns import INPUT_COLS
from tools.dev.mock_smoke import generators as mock_generators
from tools.dev.mock_smoke.generators import (
    CASE_INPUT_NAME,
    MAPPING_NAME,
    PREDICTION_ARTIFACT_NAME,
    MANIFEST_NAME,
    TRAINING_DATA_NAME,
    cleanup_from_manifest,
    generate_mock_smoke_bundle,
    install_local_model,
    install_local_mapping,
    install_local_train_data,
    mock_mapping_data,
    sha256_file,
    write_mock_case_input,
    write_mock_mapping,
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
    artifact_path = write_mock_prediction_artifact(output_dir=tmp_path, predict_delay_ms=1)

    assert artifact_path == tmp_path / PREDICTION_ARTIFACT_NAME
    model_data = load_model(artifact_path)
    predictions = predict_row(model_data, _sample_row())

    assert CATALOG_FINGERPRINT_KEY in model_data
    assert set(predictions) == set(TARGETS)
    assert all(isinstance(value, float) for value in predictions.values())


def test_mock_mapping_generator_supports_autofill(tmp_path):
    mapping_path = write_mock_mapping(output_dir=tmp_path)
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))

    for section in (
        "idu",
        "evap_index",
        "odu",
        "compressor",
        "fin_type",
        "pi",
        "row",
        "odu_cascade",
        "cond_specs",
    ):
        assert section in mapping

    row_values = {
        "idu": "MOCK_IDU_A",
        "evap_index": "MOCK_EVAP_A",
        "odu": "MOCK_ODU_A",
        "fin_type": "F&T",
        "pi": "7",
        "row": "1",
        "compressor": "MOCK_COMP_A",
    }
    updates = {}
    for key in ("idu", "evap_index", "odu", "compressor"):
        result = build_autofill_updates(row_values, key, mapping)
        updates.update({update.key: update.value for update in result.updates})
    cond_result = build_autofill_updates(row_values, "row", mapping)
    updates.update({update.key: update.value for update in cond_result.updates})

    assert updates["id_volume"] == 0.015
    assert updates["evap_area"] == 12.5
    assert updates["evap_volume"] == 0.002
    assert updates["od_volume"] == 0.045
    assert updates["cond_area"] == 25.0
    assert updates["cond_volume"] == 0.005
    assert updates["comp_eer"] == 3.5
    assert updates["comp_cc"] == 10.5


def test_mock_case_input_tsv_matches_input_cols_and_mapping_values(tmp_path):
    tsv_path = write_mock_case_input(output_dir=tmp_path, rows=3)
    rows = [line.split("\t") for line in tsv_path.read_text(encoding="utf-8").splitlines()]

    assert len(rows) == 3
    assert all(len(row) == len(INPUT_COLS) for row in rows)
    first = dict(zip(INPUT_COLS, rows[0]))
    assert first["idu"] == "MOCK_IDU_A"
    assert first["evap_index"] == "MOCK_EVAP_A"
    assert first["odu"] == "MOCK_ODU_A"
    assert first["compressor"] == "MOCK_COMP_A"
    assert first["fin_type"] == "F&T"
    assert first["pi"] == "7"
    assert first["row"] == "1"
    assert first["ref_type"] == "R32"
    assert first["exp_type"] == "EEV"
    assert "MOCK_IDU_A" in mock_mapping_data()["idu"]


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


def test_mapping_and_train_data_install_refuse_existing_without_force(tmp_path, monkeypatch):
    mapping_path = write_mock_mapping(output_dir=tmp_path / "output")
    train_path = write_mock_training_data(output_dir=tmp_path / "output")
    existing_mapping = tmp_path / "data" / "mapping.json"
    existing_training = tmp_path / "data" / "Practice_4.csv"
    existing_mapping.parent.mkdir()
    existing_mapping.write_text("{}", encoding="utf-8")
    existing_training.write_text("existing", encoding="utf-8")
    monkeypatch.setattr(mock_generators, "MAPPING_JSON_FILE", str(existing_mapping))
    monkeypatch.setattr(mock_generators, "TRAIN_DATA_FILE", str(existing_training))

    with pytest.raises(FileExistsError):
        install_local_mapping(mapping_path, force=False)
    with pytest.raises(FileExistsError):
        install_local_train_data(train_path, force=False)

    assert existing_mapping.read_text(encoding="utf-8") == "{}"
    assert existing_training.read_text(encoding="utf-8") == "existing"


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


def test_mock_bundle_generation_is_isolated_and_manifested(tmp_path):
    prod_paths = [Path(MODEL_FILE), Path(MAPPING_JSON_FILE), Path(TRAIN_DATA_FILE)]
    existed = {path: path.exists() for path in prod_paths}

    paths = generate_mock_smoke_bundle(
        output_dir=tmp_path,
        rows=4,
        seed=3,
        predict_delay_ms=2,
        write_manifest=True,
    )

    assert paths["prediction_artifact"] == tmp_path / PREDICTION_ARTIFACT_NAME
    assert paths["mapping"] == tmp_path / MAPPING_NAME
    assert paths["case_input"] == tmp_path / CASE_INPUT_NAME
    assert paths["training_data"] == tmp_path / TRAINING_DATA_NAME
    manifest = json.loads((tmp_path / MANIFEST_NAME).read_text(encoding="utf-8"))
    assert set(manifest["entries"]) == {
        "prediction_artifact",
        "mapping",
        "case_input",
        "training_data",
    }
    assert manifest["entries"]["prediction_artifact"]["predict_delay_ms"] == 2
    for path in prod_paths:
        assert path.exists() is existed[path]


def test_cleanup_removes_only_matching_generated_files(tmp_path):
    paths = generate_mock_smoke_bundle(output_dir=tmp_path, rows=2, write_manifest=True)
    removed = cleanup_from_manifest(paths["manifest"])

    assert paths["prediction_artifact"] in removed
    assert paths["mapping"] in removed
    assert paths["case_input"] in removed
    assert paths["training_data"] in removed
    assert paths["manifest"] in removed
    assert not paths["prediction_artifact"].exists()


def test_cleanup_refuses_sha_mismatch(tmp_path):
    paths = generate_mock_smoke_bundle(output_dir=tmp_path, rows=2, write_manifest=True)
    paths["case_input"].write_text("tampered\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="sha mismatch"):
        cleanup_from_manifest(paths["manifest"])

    assert paths["case_input"].exists()


def test_generated_sha_helper_changes_with_content(tmp_path):
    sample = tmp_path / "mock_smoke_sample.out"
    sample.write_text("a", encoding="utf-8")
    first = sha256_file(sample)
    sample.write_text("b", encoding="utf-8")
    assert sha256_file(sample) != first


def test_predict_smoke_runner_cli_succeeds_and_cleans_up(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "tools/dev/mock_smoke/run_mock_predict_smoke.py",
            "--output-dir",
            str(tmp_path),
            "--rows",
            "4",
            "--predict-delay-ms",
            "5",
            "--with-cancel",
            "--cleanup",
            "--force",
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "predict smoke complete rows: 4" in result.stdout
    assert "predict cancel rows:" in result.stdout
    assert not (tmp_path / MANIFEST_NAME).exists()


def test_train_shell_smoke_runner_cli_succeeds_and_cleans_up(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "tools/dev/mock_smoke/run_mock_train_shell_smoke.py",
            "--output-dir",
            str(tmp_path),
            "--cleanup",
            "--force",
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "train shell smoke: tabs/status/active controls OK" in result.stdout
    assert "trainer execution: production adapter composed" in result.stdout
    assert not (tmp_path / MANIFEST_NAME).exists()


def test_train_execution_smoke_runner_cli_succeeds_and_cleans_up(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "tools/dev/mock_smoke/run_mock_train_execution_smoke.py",
            "--output-dir",
            str(tmp_path),
            "--rows",
            "6",
            "--cleanup",
            "--force",
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "optional real core training smoke: skipped" in result.stdout
    assert "train execution smoke complete model:" in result.stdout
    assert "predict after train rows: 6" in result.stdout
    assert not (tmp_path / MANIFEST_NAME).exists()


def test_repo_local_mock_outputs_are_gitignored():
    repo_root = Path(__file__).resolve().parents[1]
    checks = subprocess.run(
        [
            "git",
            "check-ignore",
            ".dev_artifacts/mock_smoke/model.pkl",
            ".mock_smoke/mock_smoke_training_data.csv",
            ".mock_smoke/mock_smoke_case_input.tsv",
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
    assert ".mock_smoke/mock_smoke_case_input.tsv" in ignored
    assert ".mock_smoke/mock_smoke_manifest.json" in ignored
    assert "predictor_v3_mock_smoke/mock_smoke_model.pkl" in ignored
