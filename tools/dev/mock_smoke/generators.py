"""Shared DEV-only mock smoke generation logic."""

from __future__ import annotations

import shutil
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor

from core.ml.artifacts import MODEL_FILE
from core.ml.features import BASE_FEATURES, TARGETS
from core.ml.preprocessing import prepare_pipeline
from core.ml.registry import MODEL_REGISTRY, get_model_config

DEFAULT_OUTPUT_DIR_NAME = "predictor_v3_mock_smoke"
DEFAULT_ROWS = 24
DEFAULT_SEED = 42
PREDICTION_ARTIFACT_NAME = "mock_smoke_model.pkl"
TRAINING_DATA_NAME = "mock_smoke_training_data.csv"
MANIFEST_NAME = "mock_smoke_manifest.json"
PREPROCESS_VERSION = "v1.0"


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
    data["ID Volume"] = 0.012 + index * 0.0002
    data["Evap Area"] = 10.0 + index * 0.08
    data["Evap Volume"] = 0.0018 + index * 0.00003
    data["OD Volume"] = 0.04 + index * 0.0004
    data["Cond Area"] = 18.0 + index * 0.12
    data["Cond Volume"] = 0.004 + index * 0.00005
    data["Comp EER"] = 3.1 + (index % 5) * 0.08
    data["Comp cc"] = 8.0 + index * 0.12
    data["R410A"] = (index % 3 == 0).astype(float)
    data["R32"] = (index % 3 == 1).astype(float)
    data["R290"] = (index % 3 == 2).astype(float)
    data["EEV"] = (index % 2 == 0).astype(float)
    data["Capi"] = (index % 2 == 1).astype(float)

    data["Cooling Power"] = data["Cooling Capa"] / 3.15 + rng.normal(0, 3, rows)
    data["Heating Power"] = data["Heating Capa"] / 3.25 + rng.normal(0, 3, rows)
    data["Cooling Hz"] = 35.0 + index * 0.7
    data["Heating Hz"] = 37.0 + index * 0.65
    data["Ref Qty"] = 650.0 + data["OD Volume"] * 4500.0 + data["ID Volume"] * 3000.0

    return pd.DataFrame({column: data[column] for column in dict.fromkeys(BASE_FEATURES + TARGETS)})


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
        update_mock_smoke_manifest(target_dir, "training_data", output_path, rows=rows, seed=seed)
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
) -> dict[str, object]:
    """Create an inference-compatible deterministic mock model artifact."""
    df = generate_mock_training_frame(rows=rows, seed=seed)
    artifact: dict[str, object] = {
        "models": {},
        "features": {},
        "preprocess_version": PREPROCESS_VERSION,
    }
    models = artifact["models"]
    features = artifact["features"]
    assert isinstance(models, dict)
    assert isinstance(features, dict)

    for target in TARGETS:
        x_target = _target_feature_frame(df, target)
        model = DummyRegressor(strategy="mean")
        model.fit(x_target, df[target])
        models[target] = model
        features[target] = list(x_target.columns)

    return artifact


def write_mock_prediction_artifact(
    output_dir: str | Path | None = None,
    rows: int = DEFAULT_ROWS,
    seed: int = DEFAULT_SEED,
    *,
    write_manifest: bool = False,
) -> Path:
    target_dir = resolve_output_dir(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / PREDICTION_ARTIFACT_NAME
    joblib.dump(build_mock_prediction_artifact(rows=rows, seed=seed), output_path)
    if write_manifest:
        update_mock_smoke_manifest(
            target_dir,
            "prediction_artifact",
            output_path,
            rows=rows,
            seed=seed,
        )
    return output_path


def _utc_now_text() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def update_mock_smoke_manifest(
    output_dir: str | Path,
    entry_name: str,
    output_path: str | Path,
    *,
    rows: int,
    seed: int,
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
    manifest.setdefault("entries", {})[entry_name] = {
        "path": str(Path(output_path).resolve()),
        "seed": seed,
        "rows": rows,
        "created_at": created_at,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def install_local_model(
    artifact_path: str | Path,
    model_file: str | Path = MODEL_FILE,
    *,
    force: bool = False,
) -> Path:
    destination = Path(model_file)
    if destination.exists() and not force:
        raise FileExistsError(
            f"{destination} already exists. Use --force only for DEV mock smoke replacement."
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(artifact_path), destination)
    return destination
