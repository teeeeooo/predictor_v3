"""Shared DEV-only mock smoke generation logic."""

from __future__ import annotations

import shutil
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from core.data_definition.contract import load_manifest, scoped_fingerprints
from core.mapping.condenser_identity import (
    canonical_condenser_pi,
    condenser_spec_key,
)
from core.mapping.paths import MAPPING_JSON_FILE
from core.ml.artifacts import MODEL_FILE
from core.ml.artifacts import TRAIN_DATA_FILE
from core.ml.catalog_fingerprint import attach_catalog_fingerprint
from core.ml.features import BASE_FEATURES, TARGETS
from core.ml.preprocessing import prepare_pipeline
from core.ml.registry import MODEL_REGISTRY, get_model_config
from core.predictor_schema.columns import INPUT_COLS
from tools.dev.mock_smoke.models import SlowDummyRegressor

DEFAULT_OUTPUT_DIR_NAME = "predictor_v3_mock_smoke"
DEFAULT_ROWS = 24
DEFAULT_SEED = 42
PREDICTION_ARTIFACT_NAME = "mock_smoke_model.pkl"
TRAINING_DATA_NAME = "mock_smoke_training_data.csv"
MAPPING_NAME = "mock_smoke_mapping.json"
CASE_INPUT_NAME = "mock_smoke_case_input.tsv"
MANIFEST_NAME = "mock_smoke_manifest.json"
PREPROCESS_VERSION = "v1.0"
MOCK_IDU = "Q1"
MOCK_EVAP = "S1-2"
MOCK_ODU = "N-V2MD"
MOCK_COMPRESSOR = "Comp A"
MOCK_FIN_TYPE = "F&T"
MOCK_PI = "7"
MOCK_ROW = "1"
MOCK_REF_TYPE = "R32"
MOCK_EXP_TYPE = "EEV"
PHASE1_MAPPING_FIXTURE = Path(__file__).resolve().parents[3] / (
    "tests/fixtures/mapping/mapping_runtime_equivalent.json"
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_output_dir() -> Path:
    return repo_root().parent / DEFAULT_OUTPUT_DIR_NAME


def resolve_output_dir(output_dir: str | Path | None) -> Path:
    return Path(output_dir).expanduser().resolve() if output_dir else default_output_dir()


def generate_mock_training_frame(rows: int = DEFAULT_ROWS, seed: int = DEFAULT_SEED) -> pd.DataFrame:
    """Build deterministic synthetic data for smoke-only training flow checks."""
    if rows < 5:
        raise ValueError("mock smoke training data requires at least 5 rows")

    rng = np.random.default_rng(seed)
    index = np.arange(rows, dtype=float)
    data: dict[str, np.ndarray] = {}

    data["Cooling Capa"] = 2500.0 + index * 75.0 + rng.normal(0, 8, rows)
    data["Heating Capa"] = 2800.0 + index * 80.0 + rng.normal(0, 8, rows)
    mapping = mock_mapping_data()
    selections = mock_training_selection_rows(rows)
    resolved = [_resolved_mapping_values(selection, mapping) for selection in selections]
    for column in (
        "ID Volume",
        "Evap Area",
        "Evap Volume",
        "OD Volume",
        "Cond Area",
        "Cond Volume",
        "Comp EER",
        "Comp cc",
    ):
        data[column] = np.asarray([item[column] for item in resolved], dtype=float)
    for option in ("R410A", "R32", "R290"):
        data[option] = np.asarray(
            [float(selection["ref_type"] == option) for selection in selections]
        )
    for option in ("EEV", "Capi"):
        data[option] = np.asarray(
            [float(selection["exp_type"] == option) for selection in selections]
        )

    data["Cooling Power"] = data["Cooling Capa"] / 3.15 + rng.normal(0, 3, rows)
    data["Heating Power"] = data["Heating Capa"] / 3.25 + rng.normal(0, 3, rows)
    data["Cooling Hz"] = 35.0 + index * 0.7
    data["Heating Hz"] = 37.0 + index * 0.65
    data["Ref Qty"] = 650.0 + data["OD Volume"] * 4500.0 + data["ID Volume"] * 3000.0

    return pd.DataFrame({column: data[column] for column in dict.fromkeys(BASE_FEATURES + TARGETS)})


def mock_mapping_data() -> dict[str, object]:
    return json.loads(PHASE1_MAPPING_FIXTURE.read_text(encoding="utf-8"))


def mock_case_input_rows(rows: int = 12) -> list[dict[str, object]]:
    if rows < 1:
        raise ValueError("mock smoke case input requires at least 1 row")
    case_rows: list[dict[str, object]] = []
    for index in range(rows):
        case_rows.append(
            {
                "cooling_capa": 3500 + index * 25,
                "heating_capa": 3900 + index * 25,
                "idu": MOCK_IDU,
                "evap_index": MOCK_EVAP,
                "odu": MOCK_ODU,
                "fin_type": MOCK_FIN_TYPE,
                "pi": MOCK_PI,
                "row": MOCK_ROW,
                "compressor": MOCK_COMPRESSOR,
                "ref_type": MOCK_REF_TYPE,
                "exp_type": MOCK_EXP_TYPE,
            }
        )
    return case_rows


def mock_training_selection_rows(rows: int = DEFAULT_ROWS) -> list[dict[str, object]]:
    """Return mapping-backed selectors paired by row with mock training data."""
    selections = mock_case_input_rows(rows)
    for index, selection in enumerate(selections):
        if index % 2 == 0:
            continue
        selection.update(
            {"fin_type": "PFC", "pi": "", "ref_type": "R410A", "exp_type": "Capi"}
        )
    return selections


def _resolved_mapping_values(
    selection: dict[str, object],
    mapping: dict[str, object],
) -> dict[str, object]:
    fin = selection["fin_type"]
    cond_key = condenser_spec_key(
        selection["odu"],
        fin,
        canonical_condenser_pi(fin, selection["pi"]),
        selection["row"],
    )
    return {
        **mapping["idu"][selection["idu"]],
        **mapping["evap_index"][selection["evap_index"]],
        **mapping["odu"][selection["odu"]],
        **mapping["compressor"][selection["compressor"]],
        **mapping["cond_specs"][cond_key],
    }


def write_mock_mapping(
    output_dir: str | Path | None = None,
    *,
    write_manifest: bool = False,
) -> Path:
    target_dir = resolve_output_dir(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / MAPPING_NAME
    output_path.write_text(
        json.dumps(mock_mapping_data(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if write_manifest:
        update_mock_smoke_manifest(
            target_dir,
            "mapping",
            output_path,
            purpose="predict autofill mapping smoke",
        )
    return output_path


def write_mock_case_input(
    output_dir: str | Path | None = None,
    rows: int = 12,
    *,
    write_manifest: bool = False,
) -> Path:
    target_dir = resolve_output_dir(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / CASE_INPUT_NAME
    lines = []
    for row in mock_case_input_rows(rows):
        lines.append("\t".join(str(row.get(column, "")) for column in INPUT_COLS))
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if write_manifest:
        update_mock_smoke_manifest(
            target_dir,
            "case_input",
            output_path,
            rows=rows,
            purpose="paste-ready unified table input smoke",
        )
    return output_path


def write_mock_training_data(
    output_dir: str | Path | None = None,
    rows: int = DEFAULT_ROWS,
    seed: int = DEFAULT_SEED,
    *,
    write_manifest: bool = False,
) -> Path:
    target_dir = resolve_output_dir(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / TRAINING_DATA_NAME
    generate_mock_training_frame(rows=rows, seed=seed).to_csv(output_path, index=False)
    if write_manifest:
        update_mock_smoke_manifest(
            target_dir,
            "training_data",
            output_path,
            rows=rows,
            seed=seed,
            purpose="training data smoke",
        )
    return output_path


def _target_feature_frame(df: pd.DataFrame, target: str) -> pd.DataFrame:
    for model_key in MODEL_REGISTRY:
        config = get_model_config(model_key)
        if target not in config["targets"]:
            continue
        x_full, _ = prepare_pipeline(df, config)
        target_rules = config.get("target_rules", {}).get(target, {})
        if "exclude" in target_rules:
            x_full = x_full.drop(
                columns=[column for column in target_rules["exclude"] if column in x_full.columns]
            )
        if "allowed" in target_rules:
            x_full = x_full[[column for column in x_full.columns if column in target_rules["allowed"]]]
        return x_full
    raise KeyError(f"target is not registered: {target}")


def build_mock_prediction_artifact(
    rows: int = DEFAULT_ROWS,
    seed: int = DEFAULT_SEED,
    predict_delay_ms: int = 0,
) -> dict[str, object]:
    """Create an inference-compatible deterministic mock model artifact."""
    df = generate_mock_training_frame(rows=rows, seed=seed)
    manifest = load_manifest(repo_root() / "config" / "data_definition" / "manifest.json")
    fingerprints = scoped_fingerprints(manifest)
    artifact: dict[str, object] = attach_catalog_fingerprint(
        {
            "models": {},
            "features": {},
            "preprocess_version": PREPROCESS_VERSION,
            "training_contract": {
                "generation_id": manifest.generation.generation_id,
                "registry_fingerprint": fingerprints.target_registry,
                "ordered_ml_fingerprint": fingerprints.ordered_ml,
                "derived_semantics_fingerprint": fingerprints.derived_semantics,
                "one_hot_fingerprint": fingerprints.one_hot,
            },
        }
    )
    models = artifact["models"]
    features = artifact["features"]
    assert isinstance(models, dict)
    assert isinstance(features, dict)

    for target in TARGETS:
        x_target = _target_feature_frame(df, target)
        model = SlowDummyRegressor(delay_ms=predict_delay_ms, strategy="mean")
        model.fit(x_target, df[target])
        models[target] = model
        features[target] = list(x_target.columns)

    return artifact


def write_mock_prediction_artifact(
    output_dir: str | Path | None = None,
    rows: int = DEFAULT_ROWS,
    seed: int = DEFAULT_SEED,
    predict_delay_ms: int = 0,
    *,
    write_manifest: bool = False,
) -> Path:
    target_dir = resolve_output_dir(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / PREDICTION_ARTIFACT_NAME
    joblib.dump(
        build_mock_prediction_artifact(
            rows=rows,
            seed=seed,
            predict_delay_ms=predict_delay_ms,
        ),
        output_path,
    )
    if write_manifest:
        update_mock_smoke_manifest(
            target_dir,
            "prediction_artifact",
            output_path,
            rows=rows,
            seed=seed,
            predict_delay_ms=predict_delay_ms,
            purpose="prediction model smoke",
        )
    return output_path


def _utc_now_text() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: str | Path) -> str:
    hasher = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def update_mock_smoke_manifest(
    output_dir: str | Path,
    entry_name: str,
    output_path: str | Path,
    *,
    rows: int | None = None,
    seed: int | None = None,
    predict_delay_ms: int | None = None,
    purpose: str = "DEV-only mock smoke output",
    installed_path: str | Path | None = None,
) -> Path:
    """Upsert one generated-output entry in the DEV smoke manifest."""
    target_dir = Path(output_dir).resolve()
    manifest_path = target_dir / MANIFEST_NAME
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {
            "schema_version": "1.0",
            "purpose": "DEV-only mock smoke reproducibility",
            "output_dir": str(target_dir),
            "entries": {},
        }

    created_at = _utc_now_text()
    manifest["updated_at"] = created_at
    output = Path(output_path).resolve()
    entry = {
        "path": str(Path(output_path).resolve()),
        "sha256": sha256_file(output),
        "created_at": created_at,
        "purpose": purpose,
    }
    if rows is not None:
        entry["rows"] = rows
    if seed is not None:
        entry["seed"] = seed
    if predict_delay_ms is not None:
        entry["predict_delay_ms"] = predict_delay_ms
    if installed_path is not None:
        installed = Path(installed_path).resolve()
        entry["installed_path"] = str(installed)
        entry["installed_sha256"] = sha256_file(installed)
    manifest.setdefault("entries", {})[entry_name] = entry
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def install_generated_file(
    source_path: str | Path,
    destination_path: str | Path,
    *,
    force: bool = False,
) -> Path:
    destination = Path(destination_path)
    if destination.exists() and not force:
        raise FileExistsError(
            f"{destination} already exists. Use --force only for DEV mock smoke replacement."
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(source_path), destination)
    return destination


def install_local_model(
    artifact_path: str | Path,
    model_file: str | Path = MODEL_FILE,
    *,
    force: bool = False,
) -> Path:
    return install_generated_file(artifact_path, model_file, force=force)


def install_local_mapping(mapping_path: str | Path, *, force: bool = False) -> Path:
    return install_generated_file(mapping_path, MAPPING_JSON_FILE, force=force)


def install_local_train_data(csv_path: str | Path, *, force: bool = False) -> Path:
    return install_generated_file(csv_path, TRAIN_DATA_FILE, force=force)


def generate_mock_smoke_bundle(
    output_dir: str | Path | None = None,
    rows: int = 12,
    seed: int = DEFAULT_SEED,
    predict_delay_ms: int = 0,
    *,
    write_manifest: bool = True,
    install_model: bool = False,
    install_mapping: bool = False,
    install_train_data: bool = False,
    force: bool = False,
) -> dict[str, Path]:
    target_dir = resolve_output_dir(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "prediction_artifact": write_mock_prediction_artifact(
            target_dir,
            rows=max(rows, 5),
            seed=seed,
            predict_delay_ms=predict_delay_ms,
            write_manifest=write_manifest,
        ),
        "mapping": write_mock_mapping(target_dir, write_manifest=write_manifest),
        "case_input": write_mock_case_input(target_dir, rows=rows, write_manifest=write_manifest),
        "training_data": write_mock_training_data(
            target_dir,
            rows=max(rows, 5),
            seed=seed,
            write_manifest=write_manifest,
        ),
    }
    if install_model:
        installed = install_local_model(paths["prediction_artifact"], force=force)
        if write_manifest:
            update_mock_smoke_manifest(
                target_dir,
                "prediction_artifact",
                paths["prediction_artifact"],
                rows=max(rows, 5),
                seed=seed,
                predict_delay_ms=predict_delay_ms,
                purpose="prediction model smoke",
                installed_path=installed,
            )
    if install_mapping:
        installed = install_local_mapping(paths["mapping"], force=force)
        if write_manifest:
            update_mock_smoke_manifest(
                target_dir,
                "mapping",
                paths["mapping"],
                purpose="predict autofill mapping smoke",
                installed_path=installed,
            )
    if install_train_data:
        installed = install_local_train_data(paths["training_data"], force=force)
        if write_manifest:
            update_mock_smoke_manifest(
                target_dir,
                "training_data",
                paths["training_data"],
                rows=max(rows, 5),
                seed=seed,
                purpose="training data smoke",
                installed_path=installed,
            )
    paths["manifest"] = target_dir / MANIFEST_NAME
    return paths


def cleanup_from_manifest(
    manifest_path: str | Path,
    *,
    remove_local_model: bool = False,
    remove_local_mapping: bool = False,
    remove_local_train_data: bool = False,
) -> list[Path]:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    removed: list[Path] = []
    for entry_name, entry in manifest.get("entries", {}).items():
        path = Path(entry.get("path", ""))
        _remove_manifest_path(path, entry.get("sha256", ""), removed)
        installed_path = Path(entry.get("installed_path", "")) if entry.get("installed_path") else None
        if installed_path is None:
            continue
        allow = (
            entry_name == "prediction_artifact" and remove_local_model
            or entry_name == "mapping" and remove_local_mapping
            or entry_name == "training_data" and remove_local_train_data
        )
        if allow:
            _remove_manifest_path(installed_path, entry.get("installed_sha256", ""), removed)
    manifest_file = Path(manifest_path)
    if manifest_file.exists():
        manifest_file.unlink()
        removed.append(manifest_file)
    return removed


def _remove_manifest_path(path: Path, expected_sha256: str, removed: list[Path]) -> None:
    if not path.exists():
        return
    if not path.name.startswith("mock_smoke_") and path.name not in {
        "model.pkl",
        "mapping.json",
        "Practice_4.csv",
    }:
        raise RuntimeError(f"refusing to remove non-mock-smoke path: {path}")
    if expected_sha256 and sha256_file(path) != expected_sha256:
        raise RuntimeError(f"refusing to remove sha mismatch: {path}")
    path.unlink()
    removed.append(path)
