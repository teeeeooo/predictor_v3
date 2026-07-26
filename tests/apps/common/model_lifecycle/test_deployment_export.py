"""Phase 5E immutable Active deployment export contract."""

from __future__ import annotations

import hashlib
import json
from types import SimpleNamespace

import pytest

from apps.common.model_lifecycle.durability_errors import (
    LifecycleRecoveryRequiredError,
)
from apps.common.model_lifecycle.deployment_export import DeploymentExportService
from apps.common.model_lifecycle.promotion import ModelPromotionService
from tests.apps.common.model_lifecycle.conftest import publish_candidate


def _service(repository, registry_snapshot):
    promotion = ModelPromotionService(repository, lambda: registry_snapshot)
    return DeploymentExportService(repository, promotion)


def _activate(repository, candidate_id, expected_revision):  # noqa: ANN001
    return repository.replace_active(
        candidate_id,
        activated_at="2026-07-26T00:00:00+00:00",
        source="test",
        expected_revision=expected_revision,
    )


def test_export_contains_traceable_active_bundle_and_verified_checksums(
    repository,
    registry_snapshot,
    tmp_path,
):
    active_candidate = publish_candidate(
        repository,
        registry_snapshot,
        "candidate-active",
    )
    publish_candidate(repository, registry_snapshot, "candidate-non-active")
    active = _activate(repository, active_candidate.manifest.candidate_id, 0)
    destination = tmp_path / "exports"
    destination.mkdir()

    outcome = _service(repository, registry_snapshot).export_active(
        destination,
        expected_revision=active.revision,
    )

    assert outcome.status == "exported"
    export = destination / outcome.export_id
    assert export.is_dir()
    assert (export / "model.pkl").read_bytes() == active_candidate.model_path.read_bytes()
    manifest = json.loads((export / "manifest.json").read_text(encoding="utf-8"))
    summary = json.loads(
        (export / "export_summary.json").read_text(encoding="utf-8")
    )
    assert manifest["source"]["candidate_id"] == "candidate-active"
    assert manifest["source"]["active_revision"] == active.revision
    assert summary["source_candidate_id"] == "candidate-active"
    checksum_lines = (export / "checksums.sha256").read_text(
        encoding="utf-8"
    ).splitlines()
    for line in checksum_lines:
        digest, name = line.split("  ", 1)
        assert hashlib.sha256((export / name).read_bytes()).hexdigest() == digest
    assert repository.read_active() == active
    assert repository.read_candidate("candidate-active") == active_candidate


def test_export_never_overwrites_existing_identity(
    repository,
    registry_snapshot,
    tmp_path,
):
    candidate = publish_candidate(repository, registry_snapshot, "candidate-a")
    active = _activate(repository, candidate.manifest.candidate_id, 0)
    destination = tmp_path / "exports"
    destination.mkdir()
    service = _service(repository, registry_snapshot)

    first = service.export_active(destination, expected_revision=active.revision)
    marker = destination / first.export_id / "user-marker.txt"
    marker.write_text("preserve", encoding="utf-8")
    second = service.export_active(destination, expected_revision=active.revision)

    assert first.status == "exported"
    assert second.status == "failed"
    assert marker.read_text(encoding="utf-8") == "preserve"
    assert not tuple(destination.glob(".*.staging"))


def test_missing_corrupt_incompatible_and_stale_active_exports_fail_closed(
    repository,
    registry_snapshot,
    tmp_path,
):
    destination = tmp_path / "exports"
    destination.mkdir()
    service = _service(repository, registry_snapshot)
    assert service.export_active(destination, expected_revision=1).status == "failed"

    candidate = publish_candidate(repository, registry_snapshot, "candidate-a")
    active = _activate(repository, candidate.manifest.candidate_id, 0)
    assert service.export_active(
        destination,
        expected_revision=active.revision + 1,
    ).status == "failed"
    candidate.model_path.write_bytes(b"corrupt")
    assert service.export_active(
        destination,
        expected_revision=active.revision,
    ).status == "failed"
    assert tuple(destination.iterdir()) == ()


def test_export_prepublication_failure_cleans_staging(
    repository,
    registry_snapshot,
    tmp_path,
    monkeypatch,
):
    candidate = publish_candidate(repository, registry_snapshot, "candidate-a")
    active = _activate(repository, candidate.manifest.candidate_id, 0)
    destination = tmp_path / "exports"
    destination.mkdir()
    service = _service(repository, registry_snapshot)
    monkeypatch.setattr(
        "apps.common.model_lifecycle.deployment_export_publication._verify_export",
        lambda *_args: (_ for _ in ()).throw(OSError("verify failed")),
    )

    outcome = service.export_active(
        destination,
        expected_revision=active.revision,
    )

    assert outcome.status == "failed"
    assert tuple(destination.iterdir()) == ()
    assert repository.read_active() == active


def test_export_postrename_durability_failure_removes_published_directory(
    repository,
    registry_snapshot,
    tmp_path,
    monkeypatch,
):
    candidate = publish_candidate(repository, registry_snapshot, "candidate-a")
    active = _activate(repository, candidate.manifest.candidate_id, 0)
    destination = tmp_path / "exports"
    destination.mkdir()
    service = _service(repository, registry_snapshot)
    from apps.common.model_lifecycle import deployment_export_publication as module

    original = module._fsync_directory
    calls = 0

    def fail_once(path):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("parent fsync failed")
        return original(path)

    monkeypatch.setattr(module, "_fsync_directory", fail_once)

    outcome = service.export_active(
        destination,
        expected_revision=active.revision,
    )

    assert outcome.status == "failed"
    assert tuple(destination.iterdir()) == ()
    assert repository.read_active() == active


@pytest.mark.parametrize(
    ("setup", "reason_code"),
    (
        ("missing", "missing_active"),
        ("stale", "stale_active_revision"),
        ("recovery", "recovery_required"),
        ("incompatible", "incompatible_active"),
        ("corrupt", "corrupt_active"),
        ("partial", "partial_non_promotable_active"),
        ("conflict", "destination_conflict"),
        ("filesystem", "publication_filesystem_failure"),
        ("internal", "internal_failure"),
    ),
)
def test_export_failures_are_structured_and_ui_message_is_redacted(
    repository,
    registry_snapshot,
    tmp_path,
    monkeypatch,
    setup,
    reason_code,
):
    candidate = publish_candidate(repository, registry_snapshot, "candidate-a")
    active = None
    if setup != "missing":
        active = _activate(repository, candidate.manifest.candidate_id, 0)
    destination = tmp_path / "secret-export-location"
    destination.mkdir()
    service = _service(repository, registry_snapshot)
    expected_revision = active.revision if active is not None else 0

    if setup == "stale":
        expected_revision += 1
    elif setup == "recovery":
        monkeypatch.setattr(
            repository,
            "read_active",
            lambda *args, **kwargs: (_ for _ in ()).throw(
                LifecycleRecoveryRequiredError("secret recovery marker")
            ),
        )
    elif setup == "incompatible":
        monkeypatch.setattr(
            service._promotion,
            "inspect_compatibility",
            lambda _candidate_id: SimpleNamespace(
                status="incompatible",
                diagnostic_message="secret fingerprint",
            ),
        )
    elif setup == "corrupt":
        candidate.model_path.write_bytes(b"secret corrupt artifact")
    elif setup == "partial":
        monkeypatch.setattr(
            service._promotion,
            "inspect_compatibility",
            lambda _candidate_id: SimpleNamespace(
                status="non-promotable",
                diagnostic_message="secret partial target",
            ),
        )
    elif setup == "conflict":
        (destination / f"predictor-v3-candidate-a-r{active.revision}").mkdir()
    elif setup == "filesystem":
        destination = tmp_path / "secret-missing-destination"
    elif setup == "internal":
        monkeypatch.setattr(
            service._promotion,
            "inspect_compatibility",
            lambda _candidate_id: (_ for _ in ()).throw(
                TypeError("secret internal identity")
            ),
        )

    outcome = service.export_active(
        destination,
        expected_revision=expected_revision,
    )

    assert outcome.status == "failed"
    assert outcome.reason_code == reason_code
    assert outcome.preserved_active
    assert outcome.recommended_action
    assert "secret" not in outcome.message
    assert "TypeError" not in outcome.message
    assert outcome.diagnostic
    assert outcome.diagnostic_traceback
