from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import joblib
import pytest

from apps.common.model_lifecycle.closeout.canonical import (
    content_sha256,
    file_sha256,
)
from apps.common.model_lifecycle.closeout.contracts import (
    LOCKED_FINAL_TEST_RESULT_VERSION,
    build_locked_final_test,
)
from apps.common.model_lifecycle.closeout.store import LifecycleCloseoutStore
from apps.train.application.confirmation.locked_test_evaluator import (
    LockedFinalTestEvaluator,
)

NOW = "2026-07-29T00:00:00+00:00"
HASH = "a" * 64


def _membership(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("r", encoding="utf-8", newline="") as source:
        reader = csv.reader(source)
        next(reader)
        for row in reader:
            digest.update(
                json.dumps(row, separators=(",", ":")).encode("utf-8")
            )
            digest.update(b"\n")
    return digest.hexdigest()


def _persisted_manifest_sha256(manifest) -> str:  # noqa: ANN001
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


def _fence_case(tmp_path: Path):
    root = tmp_path / "lifecycle"
    store = LifecycleCloseoutStore(root)
    dataset = tmp_path / "locked.csv"
    dataset.write_text(
        "x,truth-a,truth-b\n1,2,4\n2,4,8\n",
        encoding="utf-8",
    )
    meaning = {
        "target_roles": {
            "production_required": ["target-a", "target-b"],
        },
        "training_data": {"content_sha256": HASH},
        "definition_runtime": {
            "bundle_files": {"manifest.json": {"sha256": HASH}},
        },
        "evaluation_contract": {"metric": "r2", "seed": 42},
        "feature_contract": {"ordered": ["x"]},
    }
    snapshot = {"snapshot_id": "snapshot-1", "meaning": meaning}
    seal = build_locked_final_test(
        data_sha256=file_sha256(dataset),
        ordered_membership_sha256=_membership(dataset),
        target_identities=["target-a", "target-b"],
        split_policy="external holdout",
        created_at=NOW,
        creation_identity="preselection",
        evaluation_contract={
            "metric_contract": content_sha256(
                meaning["evaluation_contract"]
            ),
            "schema_contract": content_sha256({
                "targets": meaning["target_roles"],
                "features": meaning["feature_contract"],
            }),
        },
        required_source_hashes={
            "snapshot": content_sha256(snapshot),
            "training_data": HASH,
            "definition_bundle": content_sha256(
                meaning["definition_runtime"]["bundle_files"]
            ),
            "evaluation_contract": content_sha256(
                meaning["evaluation_contract"]
            ),
        },
        dataset_reference={
            "path": str(dataset),
            "sha256": file_sha256(dataset),
        },
        created_before_selection=True,
    )
    store.write_locked_final_test(seal)
    store.consume_locked_final_test(
        seal["seal_id"],
        confirmation_id="confirmation-1",
        consumed_at=NOW,
    )
    staging = root / ".staging" / "candidate-confirmation-1-stage"
    staging.mkdir(parents=True)
    joblib.dump({}, staging / "model.pkl")
    manifest_payload = {
        "candidate_id": "candidate-confirmation-1",
        "source": "confirmation",
        "model_sha256": file_sha256(staging / "model.pkl"),
        "targets": ["target-a", "target-b"],
    }
    manifest = SimpleNamespace(
        candidate_id="candidate-confirmation-1",
        source="confirmation",
        model_sha256=manifest_payload["model_sha256"],
        targets=tuple(
            SimpleNamespace(identity=identity)
            for identity in ("target-a", "target-b")
        ),
        to_payload=lambda: manifest_payload,
    )
    result_meaning = {
        "seal_id": seal["seal_id"],
        "confirmation_id": "confirmation-1",
        "candidate_id": manifest.candidate_id,
        "candidate_manifest_sha256": _persisted_manifest_sha256(manifest),
        "data_sha256": seal["data_sha256"],
        "ordered_membership_sha256": seal["ordered_membership_sha256"],
        "target_results": [
            {"target_identity": identity, "status": "complete"}
            for identity in ("target-a", "target-b")
        ],
        "passed": True,
    }
    result = {
        "schema_version": LOCKED_FINAL_TEST_RESULT_VERSION,
        "result_id": (
            f"locked-final-result-{content_sha256(result_meaning)}"
        ),
        **result_meaning,
        "created_at": NOW,
    }
    store.write_locked_final_test_result(result)
    repository = SimpleNamespace(
        validate_staged_candidate=lambda path, value: (
            path == staging and value is manifest
        ) or (_ for _ in ()).throw(AssertionError("wrong staged Candidate")),
    )
    evaluator = LockedFinalTestEvaluator(
        repository,
        SimpleNamespace(),
        store,
        clock=lambda: SimpleNamespace(isoformat=lambda: NOW),
    )
    return evaluator, store, dataset, snapshot, seal, staging, manifest, result


def test_locked_finalization_integrity_fence_accepts_exact_linkage(
    tmp_path: Path,
) -> None:
    (
        evaluator,
        store,
        _dataset,
        snapshot,
        seal,
        staging,
        manifest,
        result,
    ) = _fence_case(tmp_path)

    evaluator.finalization_integrity_fence(
        seal,
        snapshot,
        confirmation_id="confirmation-1",
        candidate_id=manifest.candidate_id,
        candidate_path=staging,
        manifest=manifest,
        result=result,
    )

    assert store.read_locked_final_test(seal["seal_id"])["status"] == "consumed"
    assert store.read_locked_final_test_result(result["result_id"]) == result
    assert not (store.root / "candidates").exists()


@pytest.mark.parametrize(
    "drift",
    ("dataset", "membership", "split", "targets", "seal_version", "result"),
)
def test_locked_evidence_drift_blocks_before_public_candidate(
    tmp_path: Path,
    drift: str,
) -> None:
    (
        evaluator,
        store,
        dataset,
        snapshot,
        seal,
        staging,
        manifest,
        result,
    ) = _fence_case(tmp_path)
    if drift == "dataset":
        dataset.write_text(
            dataset.read_text(encoding="utf-8") + "3,6,12\n",
            encoding="utf-8",
        )
    elif drift in {"membership", "split", "targets", "seal_version"}:
        seal_path = (
            store.locked_tests / seal["seal_id"] / "seal.json"
        )
        payload = json.loads(seal_path.read_text(encoding="utf-8"))
        if drift == "membership":
            payload["ordered_membership_sha256"] = "b" * 64
        elif drift == "split":
            payload["split_policy"] = "changed split"
        elif drift == "targets":
            payload["target_identities"] = ["target-a"]
        else:
            payload["schema_version"] = "corrupt.version"
        seal_path.write_text(
            json.dumps(payload, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    else:
        result_path = (
            store.locked_test_results / result["result_id"] / "result.json"
        )
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        payload["created_at"] = "2026-07-29T00:00:01+00:00"
        result_path.write_text(
            json.dumps(payload, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )

    with pytest.raises((ValueError, OSError)):
        evaluator.finalization_integrity_fence(
            seal,
            snapshot,
            confirmation_id="confirmation-1",
            candidate_id=manifest.candidate_id,
            candidate_path=staging,
            manifest=manifest,
            result=result,
        )

    assert store.read_locked_final_test(seal["seal_id"])["status"] == "consumed"
    assert not (store.root / "candidates").exists()
