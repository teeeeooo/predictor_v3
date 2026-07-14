"""Audit correction regression for typed Data Mapping mutations."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from apps.train.services.data_mapping_service import (
    DataMappingService,
    RuntimeMappingCatalogProvider,
)
from apps.train.services.data_mapping_types import DataMappingCellEdit
from core.data_definition.model import MappingRequirement

RUNTIME_FIXTURE = Path("tests/fixtures/mapping/mapping_runtime_equivalent.json")


class RequirementProvider:
    def load_mapping_requirements(self):
        return (
            MappingRequirement(
                column_key="fan_diameter",
                ml_name="Fan_Diameter",
                mapping_entity="idu",
                mapping_attribute="Fan Diameter",
                trigger_column="idu",
                data_type="number",
                required=False,
            ),
            MappingRequirement(
                column_key="fan_enabled",
                ml_name="Fan_Enabled",
                mapping_entity="idu",
                mapping_attribute="Fan Enabled",
                trigger_column="idu",
                data_type="boolean",
                required=False,
            ),
        )


def _mapping_file(tmp_path: Path, *, enabled: bool = True) -> Path:
    destination = tmp_path / "runtime_mapping.json"
    shutil.copy2(RUNTIME_FIXTURE, destination)
    raw = json.loads(destination.read_text(encoding="utf-8"))
    raw["idu"]["MOT1"]["Fan Diameter"] = 54
    raw["idu"]["MOT1"]["Fan Enabled"] = enabled
    destination.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    return destination


def _service(tmp_path: Path, *, enabled: bool = True) -> DataMappingService:
    return DataMappingService(
        RuntimeMappingCatalogProvider(str(_mapping_file(tmp_path, enabled=enabled))),
        mapping_requirement_provider=RequirementProvider(),
    )


def test_numeric_inputs_are_canonical_and_semantic_restoration_is_clean(tmp_path):
    service = _service(tmp_path)
    service.load_snapshot()

    same = service.edit_cell("idu", 0, "ID Volume", "54")
    assert not same.dirty
    assert same.draft.group("idu").rows[0].value_for("ID Volume") == 54
    assert type(same.draft.group("idu").rows[0].value_for("ID Volume")) is int

    changed = service.edit_cell("idu", 0, "ID Volume", "55")
    assert changed.dirty
    restored = service.edit_cell("idu", 0, "ID Volume", "54.0")
    assert not restored.dirty
    assert restored.draft.group("idu").rows[0].value_for("ID Volume") == 54

    decimal = service.edit_cell("idu", 0, "ID Volume", "54.5")
    assert decimal.dirty
    assert decimal.draft.group("idu").rows[0].value_for("ID Volume") == 54.5
    assert type(decimal.draft.group("idu").rows[0].value_for("ID Volume")) is float


@pytest.mark.parametrize(
    ("baseline", "alias"),
    ((True, "true"), (True, "yes"), (True, "1"), (False, "false"), (False, "no"), (False, "0")),
)
def test_boolean_aliases_restore_canonical_baseline_without_dirty(tmp_path, baseline, alias):
    service = _service(tmp_path, enabled=baseline)
    service.load_snapshot()

    snapshot = service.edit_cell("idu", 0, "Fan Enabled", alias)

    value = snapshot.draft.group("idu").rows[0].value_for("Fan Enabled")
    assert value is baseline
    assert not snapshot.dirty


def test_semantically_equal_numeric_and_boolean_batch_is_clean(tmp_path):
    service = _service(tmp_path)
    service.load_snapshot()

    snapshot, result = service.edit_cells(
        "idu",
        (
            DataMappingCellEdit(0, "ID Volume", "54.0"),
            DataMappingCellEdit(0, "Fan Diameter", "54.0"),
            DataMappingCellEdit(0, "Fan Enabled", "yes"),
        ),
    )

    row = snapshot.draft.group("idu").rows[0]
    assert result.applied == 0
    assert not snapshot.dirty
    assert row.value_for("ID Volume") == 54
    assert row.value_for("Fan Diameter") == 54
    assert row.value_for("Fan Enabled") is True


def test_invalid_typed_batch_stays_raw_validates_and_one_undo_restores_clean(tmp_path):
    service = _service(tmp_path)
    service.load_snapshot()

    invalid, result = service.edit_cells(
        "idu",
        (
            DataMappingCellEdit(0, "ID Volume", "abc"),
            DataMappingCellEdit(0, "Fan Enabled", "maybe"),
        ),
    )

    row = invalid.draft.group("idu").rows[0]
    assert result.applied == 2
    assert invalid.dirty
    assert row.value_for("ID Volume") == "abc"
    assert row.value_for("Fan Enabled") == "maybe"
    assert {issue.code for issue in invalid.validation_errors} >= {
        "invalid_number",
        "invalid_boolean",
    }

    restored, undo = service.undo()
    assert undo.applied == 1
    assert not restored.dirty
    assert restored.draft.group("idu").rows[0].value_for("ID Volume") == 54
    assert restored.draft.group("idu").rows[0].value_for("Fan Enabled") is True


def test_invalid_input_can_be_replaced_by_original_semantic_value(tmp_path):
    service = _service(tmp_path)
    service.load_snapshot()

    assert service.edit_cell("idu", 0, "ID Volume", "bad").dirty
    assert not service.edit_cell("idu", 0, "ID Volume", "54.0").dirty
    assert service.edit_cell("idu", 0, "Fan Enabled", "bad").dirty
    restored = service.edit_cell("idu", 0, "Fan Enabled", "true")
    assert not restored.dirty
    assert restored.validation_errors == ()
