"""Locked holdout evaluation through the shared Core prediction route."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from apps.common.model_lifecycle.closeout.canonical import (
    canonical_payload,
    content_sha256,
    file_sha256,
)
from apps.common.model_lifecycle.closeout.contracts import (
    LOCKED_FINAL_TEST_RESULT_VERSION,
)
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.common.model_lifecycle.candidate_contracts import CandidateManifest
from apps.common.model_lifecycle.repository import ModelLifecycleRepository
from apps.common.runtime_generation.repository import (
    DataDefinitionGenerationRepository,
)
from apps.predict.application.runtime_snapshot import (
    build_predict_runtime_snapshot,
)
from core.ml.inference import predict_row


class LockedFinalTestEvaluator:
    def __init__(
        self,
        repository: ModelLifecycleRepository,
        generations: DataDefinitionGenerationRepository,
        store: LifecycleCloseoutStore,
        *,
        clock,  # noqa: ANN001
    ) -> None:
        self._repository = repository
        self._generations = generations
        self._store = store
        self._clock = clock

    def preflight(self, seal: dict[str, Any], snapshot: dict[str, Any]) -> None:
        dataset = Path(seal["dataset_reference"]["path"])
        if not dataset.is_file() or dataset.is_symlink():
            raise ValueError("locked final-test dataset is unavailable")
        if file_sha256(dataset) != seal["data_sha256"]:
            raise ValueError("locked final-test dataset bytes changed")
        membership = _ordered_membership(dataset)
        if membership != seal["ordered_membership_sha256"]:
            raise ValueError("locked final-test membership changed")
        meaning = snapshot["meaning"]
        required = meaning["target_roles"]["production_required"]
        if seal["target_identities"] != required:
            raise ValueError("locked final-test Target order differs")
        expected = {
            "snapshot": content_sha256(snapshot),
            "training_data": meaning["training_data"]["content_sha256"],
            "definition_bundle": content_sha256(
                meaning["definition_runtime"]["bundle_files"]
            ),
            "evaluation_contract": content_sha256(
                meaning["evaluation_contract"]
            ),
        }
        if seal["required_source_hashes"] != expected:
            raise ValueError("locked final-test source hashes differ from snapshot")
        evaluation = seal["evaluation_contract"]
        if evaluation["schema_contract"] != content_sha256(
            {
                "targets": meaning["target_roles"],
                "features": meaning["feature_contract"],
            }
        ):
            raise ValueError("locked final-test schema contract differs")
        if evaluation["metric_contract"] != content_sha256(
            meaning["evaluation_contract"]
        ):
            raise ValueError("locked final-test evaluation contract differs")

    def evaluate(
        self,
        seal: dict[str, Any],
        *,
        confirmation_id: str,
        candidate_id: str,
    ) -> dict[str, Any]:
        candidate = self._repository.read_candidate(candidate_id)
        return self.evaluate_staged(
            seal,
            confirmation_id=confirmation_id,
            candidate_id=candidate_id,
            candidate_path=candidate.path,
            manifest=candidate.manifest,
            candidate_manifest_sha256=file_sha256(
                candidate.path / "manifest.json"
            ),
        )

    def evaluate_staged(
        self,
        seal: dict[str, Any],
        *,
        confirmation_id: str,
        candidate_id: str,
        candidate_path: Path,
        manifest: CandidateManifest,
        candidate_manifest_sha256: str | None = None,
    ) -> dict[str, Any]:
        generation = self._generations.read_generation(
            manifest.definition_generation_id
        )
        runtime = build_predict_runtime_snapshot(generation)
        model_data = joblib.load(candidate_path / "model.pkl")
        dataset = Path(seal["dataset_reference"]["path"])
        if (
            file_sha256(dataset) != seal["data_sha256"]
            or _ordered_membership(dataset)
            != seal["ordered_membership_sha256"]
        ):
            raise ValueError("locked final-test bytes changed at evaluation")
        target_by_identity = {
            item.identity: item.ml_name for item in manifest.targets
        }
        truth_columns = dict(runtime.target_result_keys)
        truth: dict[str, list[float]] = {
            identity: [] for identity in seal["target_identities"]
        }
        predicted: dict[str, list[float]] = {
            identity: [] for identity in seal["target_identities"]
        }
        with dataset.open("r", encoding="utf-8-sig", newline="") as source:
            for row in csv.DictReader(source):
                typed = {
                    key: _typed_value(value) for key, value in row.items()
                }
                output = predict_row(
                    model_data,
                    typed,
                    targets=tuple(target_by_identity.values()),
                    derived_snapshot=runtime.derived,
                    zero_fill_policies=runtime.zero_fill_policy_by_ml_name,
                    ordered_input_features=runtime.ordered_input_ml_names,
                )
                for identity, ml_name in target_by_identity.items():
                    truth[identity].append(
                        float(typed[truth_columns[ml_name]])
                    )
                    predicted[identity].append(float(output[ml_name]))
        target_results = []
        passed = True
        thresholds = seal["evaluation_contract"].get("pass_thresholds", {})
        for identity in seal["target_identities"]:
            actual, forecast = truth[identity], predicted[identity]
            metrics = {
                "r2": float(r2_score(actual, forecast)),
                "mae": float(mean_absolute_error(actual, forecast)),
                "rmse": float(mean_squared_error(actual, forecast) ** 0.5),
            }
            if not all(math.isfinite(value) for value in metrics.values()):
                passed = False
            for metric, rule in thresholds.get(identity, {}).items():
                value = metrics[metric]
                passed = passed and (
                    value >= rule["value"]
                    if rule["direction"] == "minimum"
                    else value <= rule["value"]
                )
            target_results.append({
                "target_identity": identity,
                "status": "complete",
                "metrics": metrics,
            })
        meaning = {
            "seal_id": seal["seal_id"],
            "confirmation_id": confirmation_id,
            "candidate_id": candidate_id,
            "candidate_manifest_sha256": (
                candidate_manifest_sha256
                or _persisted_manifest_sha256(manifest)
            ),
            "data_sha256": file_sha256(dataset),
            "ordered_membership_sha256": _ordered_membership(dataset),
            "target_results": target_results,
            "passed": passed,
        }
        result = canonical_payload({
            "schema_version": LOCKED_FINAL_TEST_RESULT_VERSION,
            "result_id": f"locked-final-result-{content_sha256(meaning)}",
            **meaning,
            "created_at": self._clock().isoformat(),
        })
        self._store.write_locked_final_test_result(result)
        return result

    def finalization_integrity_fence(
        self,
        seal: dict[str, Any],
        snapshot: dict[str, Any],
        *,
        confirmation_id: str,
        candidate_id: str,
        candidate_path: Path,
        manifest: CandidateManifest,
        result: dict[str, Any],
    ) -> None:
        """Revalidate all locked evidence before public Candidate visibility."""
        initial = self._store.read_initial_locked_final_test(seal["seal_id"])
        if initial != seal:
            raise ValueError("locked final-test seal payload changed")
        consumed = self._store.read_locked_final_test(seal["seal_id"])
        expected_consumed_meaning = {
            key: value for key, value in consumed.items()
            if key not in {
                "status",
                "consumed_at",
                "consumed_by_confirmation_id",
            }
        }
        if (
            consumed["status"] != "consumed"
            or consumed.get("consumed_by_confirmation_id") != confirmation_id
            or expected_consumed_meaning != {
                key: value for key, value in seal.items() if key != "status"
            }
        ):
            raise ValueError("locked final-test seal consumption changed")
        self.preflight(consumed, snapshot)

        persisted_result = self._store.read_locked_final_test_result(
            result["result_id"]
        )
        if persisted_result != result:
            raise ValueError("locked final-test result bytes changed")
        manifest_sha256 = _persisted_manifest_sha256(manifest)
        expected_targets = tuple(seal["target_identities"])
        result_targets = tuple(
            item.get("target_identity")
            for item in result["target_results"]
        )
        if (
            result["seal_id"] != seal["seal_id"]
            or result["confirmation_id"] != confirmation_id
            or result["candidate_id"] != candidate_id
            or result["candidate_manifest_sha256"] != manifest_sha256
            or result["data_sha256"] != seal["data_sha256"]
            or result["ordered_membership_sha256"]
            != seal["ordered_membership_sha256"]
            or result_targets != expected_targets
        ):
            raise ValueError(
                "locked final-test result/Candidate linkage changed"
            )
        if (
            manifest.candidate_id != candidate_id
            or manifest.source != "confirmation"
            or tuple(item.identity for item in manifest.targets)
            != expected_targets
            or file_sha256(candidate_path / "model.pkl")
            != manifest.model_sha256
        ):
            raise ValueError("staged confirmation Candidate identity changed")
        self._repository.validate_staged_candidate(candidate_path, manifest)


def _ordered_membership(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        try:
            next(reader)
        except StopIteration as exc:
            raise ValueError("locked final-test dataset has no header") from exc
        for row in reader:
            digest.update(
                json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode(
                    "utf-8"
                )
            )
            digest.update(b"\n")
    return digest.hexdigest()


def _persisted_manifest_sha256(manifest: CandidateManifest) -> str:
    encoded = (
        json.dumps(
            manifest.to_payload(),
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n"
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _typed_value(value: str) -> str | float:
    try:
        return float(value)
    except ValueError:
        return value
