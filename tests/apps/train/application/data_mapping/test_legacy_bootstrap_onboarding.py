"""Data Mapping legacy-wide bootstrap onboarding workflow regressions."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import pytest

from apps.train.adapters.mapping import parse_legacy_mapping_csv
from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_mapping_service import (
    DataMappingService,
    RuntimeMappingCatalogProvider,
)
from core.data_definition.model import MappingRequirement
from core.mapping.editor_persistence import runtime_mapping_from_editor_draft


LEGACY_FIXTURE = Path("tests/fixtures/mapping/mapping_tables_legacy_wide.csv")
RUNTIME_FIXTURE = Path("tests/fixtures/mapping/mapping_runtime_equivalent.json")


class _RequirementProvider:
    def __init__(self) -> None:
        self.requirements = (
            MappingRequirement(
                column_key="fan_diameter",
                ml_name="Fan_Diameter",
                mapping_entity="idu",
                mapping_attribute="Fan Diameter",
                trigger_column="idu",
                data_type="number",
                required=False,
            ),
        )

    def load_mapping_requirements(self):  # noqa: ANN201
        return self.requirements


class _MutableRequirementProvider:
    def __init__(self) -> None:
        self.requirements = ()

    def load_mapping_requirements(self):  # noqa: ANN201
        return tuple(self.requirements)


def _missing_service(
    tmp_path: Path,
    *,
    requirement_provider=None,  # noqa: ANN001
) -> tuple[Path, DataMappingService]:
    mapping_file = tmp_path / "mapping.json"
    service = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_file)),
        mapping_requirement_provider=requirement_provider,
        legacy_bootstrap_parser=parse_legacy_mapping_csv,
    )
    return mapping_file, service


def _fixture_rows() -> list[list[str]]:
    with LEGACY_FIXTURE.open(newline="", encoding="utf-8") as source:
        return list(csv.reader(source))


def _write_rows(tmp_path: Path, rows: list[list[str]], name: str) -> Path:
    destination = tmp_path / name
    with destination.open("w", newline="", encoding="utf-8") as target:
        csv.writer(target).writerows(rows)
    return destination


def _copy_runtime(mapping_file: Path) -> bytes:
    payload = RUNTIME_FIXTURE.read_bytes()
    mapping_file.write_bytes(payload)
    return payload


def test_missing_resource_bootstrap_is_unsaved_then_exchange_save_and_reload_round_trip(tmp_path):
    requirement_provider = _RequirementProvider()
    mapping_file, service = _missing_service(
        tmp_path, requirement_provider=requirement_provider
    )

    preview = service.preview_legacy_bootstrap(LEGACY_FIXTURE)

    assert preview.can_apply
    assert not preview.replacement_required
    assert preview.candidate is not None
    assert "Fan Diameter" in preview.candidate.group("idu").columns
    assert not mapping_file.exists()

    snapshot, result = service.apply_legacy_bootstrap(preview)

    assert result.success
    assert snapshot is not None and snapshot.is_valid and snapshot.dirty
    assert "Unsaved legacy bootstrap" in snapshot.source_label
    assert not mapping_file.exists()
    actions = {action.key: action for action in snapshot.actions}
    assert actions["bootstrap_legacy_csv"].enabled
    assert actions["import_mapping_bundle"].enabled
    assert actions["save_mapping_json"].enabled
    assert "mapping_bundle_v1" in actions["import_mapping_bundle"].reason

    refreshed = service.load_snapshot()
    assert refreshed.dirty
    assert "Fan Diameter" in refreshed.draft.group("idu").columns

    review_path = tmp_path / "review.json"
    review_result, reviewed = service.export_snapshot(review_path)
    assert review_result.success and reviewed.dirty and review_path.is_file()

    bundle_path = tmp_path / "mapping_bundle.csv"
    exchange_result, exchanged = service.export_exchange(bundle_path)
    assert exchange_result.success and exchanged.dirty
    import_preview, _ = service.preview_exchange_import(bundle_path)
    assert import_preview.can_apply
    imported, import_result = service.apply_exchange_import(import_preview)
    assert import_result.success
    assert imported.dirty
    assert not mapping_file.exists()

    expected_runtime = runtime_mapping_from_editor_draft(imported.draft)
    save_result, saved = service.save_mapping()
    assert save_result.success
    assert not saved.dirty
    assert json.loads(mapping_file.read_text(encoding="utf-8")) == expected_runtime
    assert "Unsaved legacy bootstrap" not in saved.source_label

    reloaded = DataMappingService(
        RuntimeMappingCatalogProvider(str(mapping_file)),
        mapping_requirement_provider=requirement_provider,
    ).load_snapshot()
    assert not reloaded.dirty
    assert runtime_mapping_from_editor_draft(reloaded.draft) == expected_runtime


@pytest.mark.parametrize("failure_kind", ["header", "duplicate", "numeric"])
def test_invalid_legacy_bootstrap_preserves_dirty_draft_history_and_missing_file(
    tmp_path,
    failure_kind,
):
    mapping_file, service = _missing_service(tmp_path)
    _copy_runtime(mapping_file)
    service.load_snapshot()
    service.edit_cell("idu", 0, "ID Volume", "99.5")
    mapping_file.unlink()
    before_token = service._session.state_token()
    before_revision = service.draft_revision

    rows = _fixture_rows()
    if failure_kind == "header":
        rows[0][0] = "Wrong Header"
    elif failure_kind == "duplicate":
        duplicate = [""] * len(rows[0])
        duplicate[0] = rows[1][0]
        rows.append(duplicate)
    else:
        rows[1][1] = "not-a-number"
    source = _write_rows(tmp_path, rows, f"invalid-{failure_kind}.csv")

    preview = service.preview_legacy_bootstrap(source)

    assert not preview.can_apply
    assert preview.blockers[0].code == "legacy_bootstrap_invalid_source"
    assert service._session.state_token() == before_token
    assert service.draft_revision == before_revision
    assert service.current_snapshot().draft.group("idu").rows[0].value_for("ID Volume") == 99.5
    assert not mapping_file.exists()


def test_existing_runtime_mapping_blocks_bootstrap_without_reading_or_modifying_file(tmp_path):
    mapping_file, service = _missing_service(tmp_path)
    original = _copy_runtime(mapping_file)

    preview = service.preview_legacy_bootstrap(LEGACY_FIXTURE)

    assert not preview.can_apply
    assert preview.blockers[0].code == "legacy_bootstrap_resource_exists"
    assert mapping_file.read_bytes() == original
    assert service.current_snapshot() is None


def test_resource_appearing_after_preview_makes_bootstrap_stale_and_preserves_resource(tmp_path):
    mapping_file, service = _missing_service(tmp_path)
    preview = service.preview_legacy_bootstrap(LEGACY_FIXTURE)
    original = _copy_runtime(mapping_file)

    snapshot, result = service.apply_legacy_bootstrap(preview)

    assert snapshot is None
    assert not result.success and result.stale
    assert mapping_file.read_bytes() == original
    assert service.current_snapshot() is None


def test_draft_change_after_preview_makes_bootstrap_stale_and_preserves_newer_draft(tmp_path):
    mapping_file, service = _missing_service(tmp_path)
    _copy_runtime(mapping_file)
    service.load_snapshot()
    service.edit_cell("idu", 0, "ID Volume", "88.5")
    mapping_file.unlink()
    preview = service.preview_legacy_bootstrap(LEGACY_FIXTURE)
    service.edit_cell("idu", 0, "ID Volume", "77.5")

    snapshot, result = service.apply_legacy_bootstrap(
        preview, allow_replace_current=True
    )

    assert snapshot is not None
    assert not result.success and result.stale
    assert snapshot.draft.group("idu").rows[0].value_for("ID Volume") == 77.5
    assert snapshot.dirty
    assert not mapping_file.exists()


def test_conflicting_current_mapping_requirements_block_bootstrap_without_mutation(tmp_path):
    requirements = _MutableRequirementProvider()
    requirements.requirements = (
        MappingRequirement(
            column_key="fan_attribute_a",
            ml_name="",
            mapping_entity="idu",
            mapping_attribute="Fan Attribute",
            trigger_column="idu",
            data_type="string",
            required=False,
        ),
        MappingRequirement(
            column_key="fan_attribute_b",
            ml_name="",
            mapping_entity="idu",
            mapping_attribute="Fan Attribute",
            trigger_column="idu",
            data_type="number",
            required=True,
        ),
    )
    mapping_file, service = _missing_service(
        tmp_path, requirement_provider=requirements
    )
    before_revision = service.draft_revision

    preview = service.preview_legacy_bootstrap(LEGACY_FIXTURE)

    assert not preview.can_apply
    assert any(issue.code == "mapping_requirement_contract_conflict" for issue in preview.blockers)
    assert service.draft_revision == before_revision
    assert service.current_snapshot() is None
    assert not mapping_file.exists()


def test_mapping_requirement_change_after_preview_makes_bootstrap_stale(tmp_path):
    requirements = _MutableRequirementProvider()
    mapping_file, service = _missing_service(
        tmp_path, requirement_provider=requirements
    )
    preview = service.preview_legacy_bootstrap(LEGACY_FIXTURE)
    requirements.requirements = (
        MappingRequirement(
            column_key="fan_diameter",
            ml_name="",
            mapping_entity="idu",
            mapping_attribute="Fan Diameter",
            trigger_column="idu",
            data_type="number",
            required=False,
        ),
    )

    snapshot, result = service.apply_legacy_bootstrap(preview)

    assert snapshot is None
    assert not result.success and result.stale
    assert not mapping_file.exists()


def test_replacing_cached_unsaved_draft_requires_explicit_confirmation(tmp_path):
    mapping_file, service = _missing_service(tmp_path)
    _copy_runtime(mapping_file)
    service.load_snapshot()
    service.edit_cell("idu", 0, "ID Volume", "123.5")
    mapping_file.unlink()
    before = service.current_snapshot()
    preview = service.preview_legacy_bootstrap(LEGACY_FIXTURE)

    blocked, blocked_result = service.apply_legacy_bootstrap(preview)

    assert blocked is not None
    assert not blocked_result.success and blocked_result.confirmation_required
    assert blocked.draft == before.draft
    assert blocked.dirty
    assert not mapping_file.exists()

    applied, applied_result = service.apply_legacy_bootstrap(
        preview, allow_replace_current=True
    )
    assert applied_result.success
    assert applied is not None and applied.dirty
    assert applied.draft == preview.candidate
    assert not mapping_file.exists()


def test_controller_missing_state_exposes_bootstrap_separately_from_bundle_import(tmp_path):
    mapping_file, service = _missing_service(tmp_path)
    controller = DataMappingController(service)

    missing = controller.refresh()
    missing_actions = {action.key: action for action in missing.actions}

    assert missing.resource_status == "missing"
    assert missing_actions["bootstrap_legacy_csv"].enabled
    assert "import_mapping_bundle" not in missing_actions

    preview = controller.preview_legacy_bootstrap(LEGACY_FIXTURE)
    state = controller.apply_legacy_bootstrap(preview)
    actions = {action.key: action for action in state.actions}

    assert state.dirty
    assert "mapping.json has not been written" in state.message
    assert "Unsaved legacy bootstrap" in state.source_label
    assert actions["bootstrap_legacy_csv"].enabled
    assert actions["import_mapping_bundle"].enabled
    assert not mapping_file.exists()
