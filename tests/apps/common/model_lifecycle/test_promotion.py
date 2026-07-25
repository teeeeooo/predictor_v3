"""Promotion, rollback, Bootstrap, and atomic pointer tests."""

from dataclasses import replace
import json

import pytest

from apps.common.model_lifecycle import (
    ActiveModelResolver,
    LifecycleRecoveryRequiredError,
    ModelLifecycleRepository,
    ModelPromotionService,
)

from .conftest import incompatible_snapshot, publish_candidate


def test_only_compatible_candidate_promotes(repository, registry_snapshot):
    publish_candidate(repository, registry_snapshot, "candidate-a")
    result = ModelPromotionService(
        repository, lambda: registry_snapshot
    ).promote("candidate-a", expected_revision=0)

    assert result.status == "active"
    assert repository.read_active().candidate_id == "candidate-a"


def test_stale_activation_revision_is_rejected(repository, registry_snapshot):
    publish_candidate(repository, registry_snapshot, "candidate-a")
    publish_candidate(repository, registry_snapshot, "candidate-b")
    service = ModelPromotionService(repository, lambda: registry_snapshot)
    assert service.promote("candidate-a", expected_revision=0).status == "active"

    result = service.promote("candidate-b", expected_revision=0)

    assert result.status == "blocked"
    assert "stale Active reference revision" in result.message
    assert repository.read_active().candidate_id == "candidate-a"


def test_active_revision_guard_is_required_and_cannot_be_null(
    repository, registry_snapshot
):
    publish_candidate(repository, registry_snapshot, "candidate-a")
    service = ModelPromotionService(repository, lambda: registry_snapshot)

    with pytest.raises(TypeError, match="expected_revision"):
        service.promote("candidate-a")
    blocked = service.promote("candidate-a", expected_revision=None)
    with pytest.raises(TypeError, match="expected_revision"):
        repository.replace_active(
            "candidate-a",
            activated_at="2026-07-23T00:00:00+00:00",
            source="test",
        )
    with pytest.raises(ValueError, match="non-negative integer"):
        repository.replace_active(
            "candidate-a",
            activated_at="2026-07-23T00:00:00+00:00",
            source="test",
            expected_revision=None,
        )

    assert blocked.status == "blocked"
    assert "non-negative integer" in blocked.message
    assert repository.read_active(optional=True) is None


def test_competing_promotions_and_stale_rollback_preserve_latest_active(
    repository, registry_snapshot
):
    for candidate_id in ("candidate-a", "candidate-b", "candidate-c"):
        publish_candidate(repository, registry_snapshot, candidate_id)
    service = ModelPromotionService(repository, lambda: registry_snapshot)

    assert service.promote("candidate-a", expected_revision=0).revision == 1
    assert service.promote("candidate-b", expected_revision=1).revision == 2
    stale_promotion = service.promote("candidate-c", expected_revision=1)
    stale_rollback = service.rollback("candidate-a", expected_revision=1)

    assert stale_promotion.status == "blocked"
    assert stale_rollback.status == "blocked"
    active = repository.read_active()
    assert (active.candidate_id, active.revision) == ("candidate-b", 2)
    assert [item.candidate_id for item in active.history] == [
        "candidate-a",
        "candidate-b",
    ]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("generation_id", "stale", "Definition generation"),
        ("registry_fingerprint", "stale", "registry fingerprint"),
        ("ordered_ml_fingerprint", "stale", "ordered ML fingerprint"),
        ("preprocessing_version", "v-next", "preprocessing version"),
    ),
)
def test_current_compatibility_mismatch_blocks_promotion(
    repository, registry_snapshot, field, value, message
):
    publish_candidate(repository, registry_snapshot, "candidate-a")
    current = incompatible_snapshot(registry_snapshot, field, value)

    result = ModelPromotionService(repository, lambda: current).promote(
        "candidate-a", expected_revision=0
    )

    assert result.status == "blocked"
    assert message in result.message
    assert repository.read_active(optional=True) is None


def test_feature_order_tamper_blocks_without_changing_active(
    repository, registry_snapshot
):
    publish_candidate(repository, registry_snapshot, "candidate-a")
    service = ModelPromotionService(repository, lambda: registry_snapshot)
    assert service.promote("candidate-a", expected_revision=0).status == "active"
    second = publish_candidate(repository, registry_snapshot, "candidate-b")
    payload = __import__("json").loads(
        (second.path / "manifest.json").read_text(encoding="utf-8")
    )
    payload["targets"][0]["feature_names"].reverse()
    (second.path / "manifest.json").write_text(
        __import__("json").dumps(payload), encoding="utf-8"
    )

    result = service.promote("candidate-b", expected_revision=1)

    assert result.status == "blocked"
    assert repository.read_active().candidate_id == "candidate-a"


def test_unpublished_experimental_feature_candidate_is_blocked(
    repository, registry_snapshot
):
    candidate = publish_candidate(repository, registry_snapshot, "candidate-a")
    payload = __import__("json").loads(
        (candidate.path / "manifest.json").read_text(encoding="utf-8")
    )
    payload["contains_unpublished_features"] = True
    (candidate.path / "manifest.json").write_text(
        __import__("json").dumps(payload), encoding="utf-8"
    )

    result = ModelPromotionService(
        repository, lambda: registry_snapshot
    ).promote("candidate-a", expected_revision=0)

    assert result.status == "blocked"
    assert "unpublished experimental features" in result.message
    assert repository.read_active(optional=True) is None


def test_pointer_write_failure_preserves_existing_active(tmp_path, registry_snapshot):
    fail = {"enabled": False}
    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle",
        failure_hook=lambda stage: (
            (_ for _ in ()).throw(OSError("pointer failure"))
            if fail["enabled"] and stage == "before_active_replace" else None
        ),
    )
    publish_candidate(repository, registry_snapshot, "candidate-a")
    publish_candidate(repository, registry_snapshot, "candidate-b")
    service = ModelPromotionService(repository, lambda: registry_snapshot)
    assert service.promote("candidate-a", expected_revision=0).status == "active"
    fail["enabled"] = True

    result = service.promote("candidate-b", expected_revision=1)

    assert result.status == "blocked"
    assert repository.read_active().candidate_id == "candidate-a"
    assert repository.read_active().revision == 1


@pytest.mark.parametrize(
    "failure_stage",
    ("before_active_temporary_write", "after_active_temporary_fsync", "before_active_replace"),
)
def test_active_pre_rename_failures_preserve_pointer_and_history(
    tmp_path, registry_snapshot, failure_stage
):
    fail = {"enabled": False}

    def inject(stage):  # noqa: ANN001
        if fail["enabled"] and stage == failure_stage:
            raise OSError(stage)

    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle", failure_hook=inject
    )
    publish_candidate(repository, registry_snapshot, "candidate-a")
    publish_candidate(repository, registry_snapshot, "candidate-b")
    service = ModelPromotionService(repository, lambda: registry_snapshot)
    assert service.promote("candidate-a", expected_revision=0).status == "active"
    before = repository.read_active()
    fail["enabled"] = True

    result = service.promote("candidate-b", expected_revision=1)

    assert result.status == "blocked"
    assert repository.read_active() == before
    assert not list(repository.root.glob(".active-model-*.tmp"))
    assert not list(repository.root.glob(".active-model-*.backup"))
    assert not repository.active_recovery_path.exists()


def test_active_post_rename_durability_failure_rolls_back_pointer_and_history(
    tmp_path, registry_snapshot
):
    fail = {"enabled": False}
    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle",
        failure_hook=lambda stage: (
            (_ for _ in ()).throw(OSError("active fsync"))
            if fail["enabled"] and stage == "after_active_replace" else None
        ),
    )
    publish_candidate(repository, registry_snapshot, "candidate-a")
    publish_candidate(repository, registry_snapshot, "candidate-b")
    service = ModelPromotionService(repository, lambda: registry_snapshot)
    assert service.promote("candidate-a", expected_revision=0).status == "active"
    before = repository.read_active()
    fail["enabled"] = True

    result = service.promote("candidate-b", expected_revision=1)

    assert result.status == "blocked"
    assert "rolled back" in result.message
    assert repository.read_active() == before
    assert not repository.active_recovery_path.exists()


def test_active_failed_rollback_is_controlled_recovery_required(
    tmp_path, registry_snapshot
):
    fail = {"enabled": False}

    def inject(stage):  # noqa: ANN001
        if fail["enabled"] and stage in {
            "after_active_replace",
            "before_active_rollback",
        }:
            raise OSError(stage)

    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle", failure_hook=inject
    )
    publish_candidate(repository, registry_snapshot, "candidate-a")
    publish_candidate(repository, registry_snapshot, "candidate-b")
    service = ModelPromotionService(repository, lambda: registry_snapshot)
    assert service.promote("candidate-a", expected_revision=0).status == "active"
    fail["enabled"] = True

    result = service.promote("candidate-b", expected_revision=1)

    assert result.status == "recovery-required"
    assert repository.active_recovery_path.is_file()
    with pytest.raises(ValueError, match="recovery is required"):
        repository.read_active()
    assert ActiveModelResolver(repository).resolve().status == "recovery-required"
    raw = json.loads(repository.active_reference_path.read_text(encoding="utf-8"))
    assert (raw["candidate_id"], raw["revision"]) == ("candidate-b", 2)
    assert [item["candidate_id"] for item in raw["history"]] == [
        "candidate-a",
        "candidate-b",
    ]
    fail["enabled"] = False

    recovered = repository.recover_active_reference()

    assert recovered is not None
    assert (recovered.candidate_id, recovered.revision) == ("candidate-a", 1)
    assert [item.candidate_id for item in recovered.history] == ["candidate-a"]
    assert not repository.active_recovery_path.exists()


@pytest.mark.parametrize(
    ("failure_stage", "backup_remains"),
    (
        ("before_active_backup_cleanup", True),
        ("before_active_marker_cleanup", False),
    ),
)
def test_committed_active_cleanup_failure_reconciles_forward_idempotently(
    tmp_path, registry_snapshot, failure_stage, backup_remains
):
    fail = {"enabled": False}

    def inject(stage):  # noqa: ANN001
        if fail["enabled"] and stage == failure_stage:
            raise OSError(stage)

    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle", failure_hook=inject
    )
    publish_candidate(repository, registry_snapshot, "candidate-a")
    publish_candidate(repository, registry_snapshot, "candidate-b")
    service = ModelPromotionService(repository, lambda: registry_snapshot)
    assert service.promote("candidate-a", expected_revision=0).status == "active"
    fail["enabled"] = True

    result = service.promote("candidate-b", expected_revision=1)

    assert (result.status, result.candidate_id, result.revision) == (
        "recovery-required",
        "candidate-b",
        2,
    )
    marker = json.loads(
        repository.active_recovery_path.read_text(encoding="utf-8")
    )
    assert marker["status"] == "committed"
    assert marker["intended_candidate_id"] == "candidate-b"
    raw = json.loads(repository.active_reference_path.read_text(encoding="utf-8"))
    assert (raw["candidate_id"], raw["revision"]) == ("candidate-b", 2)
    assert [item["candidate_id"] for item in raw["history"]] == [
        "candidate-a",
        "candidate-b",
    ]
    assert bool(list(repository.root.glob(".active-model-*.backup"))) is backup_remains
    assert ActiveModelResolver(repository).resolve().status == "recovery-required"
    fail["enabled"] = False

    recovered = repository.recover_active_reference()
    repeated = repository.recover_active_reference()

    assert recovered is not None
    assert repeated == recovered
    assert (recovered.candidate_id, recovered.revision) == ("candidate-b", 2)
    assert [item.candidate_id for item in recovered.history] == [
        "candidate-a",
        "candidate-b",
    ]
    assert not repository.active_recovery_path.exists()
    assert not list(repository.root.glob(".active-model-*.backup"))
    assert ActiveModelResolver(repository).resolve().revision == 2


@pytest.mark.parametrize(
    "corruption",
    (
        "latest-candidate",
        "latest-timestamp",
        "duplicate-revision",
        "revision-gap",
        "unsafe-history-candidate",
        "empty-history",
        "malformed-history-record",
        "unsupported-schema",
    ),
)
def test_active_semantic_corruption_is_invalid_and_never_resolved(
    repository, registry_snapshot, corruption
):
    publish_candidate(repository, registry_snapshot, "candidate-a")
    publish_candidate(repository, registry_snapshot, "candidate-b")
    service = ModelPromotionService(repository, lambda: registry_snapshot)
    assert service.promote("candidate-a", expected_revision=0).status == "active"
    assert service.promote("candidate-b", expected_revision=1).status == "active"
    payload = json.loads(
        repository.active_reference_path.read_text(encoding="utf-8")
    )
    if corruption == "latest-candidate":
        payload["history"][-1]["candidate_id"] = "candidate-a"
    elif corruption == "latest-timestamp":
        payload["history"][-1]["activated_at"] = "different"
    elif corruption == "duplicate-revision":
        payload["history"][-1]["revision"] = 1
    elif corruption == "revision-gap":
        payload["history"][-1]["revision"] = 3
        payload["revision"] = 3
    elif corruption == "unsafe-history-candidate":
        payload["history"][0]["candidate_id"] = "../unsafe"
    elif corruption == "empty-history":
        payload["history"] = []
    elif corruption == "malformed-history-record":
        del payload["history"][-1]["candidate_id"]
    else:
        payload["schema_version"] = "active_model_reference.future"
    repository.active_reference_path.write_text(
        json.dumps(payload), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Active reference is corrupt"):
        repository.read_active()
    assert ActiveModelResolver(repository).resolve().status == "invalid-active"


@pytest.mark.parametrize(
    "corruption",
    (
        "top-history-identity",
        "top-history-timestamp",
        "marker-identity",
        "same-revision-different-identity",
    ),
)
def test_committed_recovery_corruption_preserves_marker_and_backup(
    tmp_path, registry_snapshot, corruption
):
    fail = {"enabled": False}

    def inject(stage):  # noqa: ANN001
        if fail["enabled"] and stage == "before_active_backup_cleanup":
            raise OSError(stage)

    repository = ModelLifecycleRepository(
        tmp_path / "lifecycle", failure_hook=inject
    )
    publish_candidate(repository, registry_snapshot, "candidate-a")
    publish_candidate(repository, registry_snapshot, "candidate-b")
    service = ModelPromotionService(repository, lambda: registry_snapshot)
    assert service.promote("candidate-a", expected_revision=0).status == "active"
    fail["enabled"] = True
    assert service.promote(
        "candidate-b", expected_revision=1
    ).status == "recovery-required"
    fail["enabled"] = False

    active = json.loads(
        repository.active_reference_path.read_text(encoding="utf-8")
    )
    marker = json.loads(
        repository.active_recovery_path.read_text(encoding="utf-8")
    )
    if corruption == "top-history-identity":
        active["history"][-1]["candidate_id"] = "candidate-a"
    elif corruption == "top-history-timestamp":
        active["history"][-1]["activated_at"] = "different"
    elif corruption == "marker-identity":
        marker["intended_candidate_id"] = "candidate-a"
    else:
        active["candidate_id"] = "candidate-a"
        active["history"][-1]["candidate_id"] = "candidate-a"
    repository.active_reference_path.write_text(
        json.dumps(active), encoding="utf-8"
    )
    repository.active_recovery_path.write_text(
        json.dumps(marker), encoding="utf-8"
    )
    backups = list(repository.root.glob(".active-model-*.backup"))
    assert len(backups) == 1

    with pytest.raises(LifecycleRecoveryRequiredError):
        repository.recover_active_reference()

    assert repository.active_recovery_path.is_file()
    assert backups[0].is_file()
    assert ActiveModelResolver(repository).resolve().status == "recovery-required"


def test_promotion_and_rollback_keep_one_sequential_active_revision_unit(
    repository, registry_snapshot
):
    publish_candidate(repository, registry_snapshot, "candidate-a")
    publish_candidate(repository, registry_snapshot, "candidate-b")
    service = ModelPromotionService(repository, lambda: registry_snapshot)

    assert service.promote("candidate-a", expected_revision=0).revision == 1
    assert service.promote("candidate-b", expected_revision=1).revision == 2
    assert service.rollback("candidate-a", expected_revision=2).revision == 3

    active = repository.read_active()
    assert (active.candidate_id, active.revision) == ("candidate-a", 3)
    assert [item.revision for item in active.history] == [1, 2, 3]
    assert [item.candidate_id for item in active.history] == [
        "candidate-a",
        "candidate-b",
        "candidate-a",
    ]
    assert active.activated_at == active.history[-1].activated_at


def test_rollback_revalidates_current_compatibility(repository, registry_snapshot):
    publish_candidate(repository, registry_snapshot, "candidate-a")
    publish_candidate(repository, registry_snapshot, "candidate-b")
    current = {"snapshot": registry_snapshot}
    service = ModelPromotionService(repository, lambda: current["snapshot"])
    assert service.promote("candidate-a", expected_revision=0).status == "active"
    assert service.promote("candidate-b", expected_revision=1).status == "active"
    current["snapshot"] = replace(registry_snapshot, generation_id="new")

    result = service.rollback("candidate-a", expected_revision=2)

    assert result.status == "blocked"
    assert repository.read_active().candidate_id == "candidate-b"


def test_bootstrap_resolver_is_controlled_and_candidate_is_not_auto_active(
    repository, registry_snapshot
):
    publish_candidate(repository, registry_snapshot, "candidate-a")

    resolution = ActiveModelResolver(repository).resolve()

    assert resolution.status == "missing-active"
    assert "No Active model" in resolution.message


def test_invalid_active_reference_is_controlled(repository):
    repository.root.mkdir(parents=True)
    repository.active_reference_path.write_text("{invalid", encoding="utf-8")

    resolution = ActiveModelResolver(repository).resolve()

    assert resolution.status == "invalid-active"
    assert resolution.message.startswith("Active model is unavailable:")
