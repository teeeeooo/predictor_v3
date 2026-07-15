"""Slice 2D mapping exchange export contract tests."""

from __future__ import annotations

import csv
import json
import os
import shutil
from pathlib import Path

import pytest

from apps.train.services.data_mapping_service import (
    DataMappingService,
    RuntimeMappingCatalogProvider,
)
from core.data_definition.model import MappingRequirement
from core.mapping.exchange import CANONICAL_GROUP_KEYS

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


def _mapping_file(tmp_path: Path) -> Path:
    destination = tmp_path / "runtime_mapping.json"
    shutil.copy2(RUNTIME_FIXTURE, destination)
    raw = json.loads(destination.read_text(encoding="utf-8"))
    raw["idu"]["MOT1"]["Fan Diameter"] = 54
    raw["idu"]["MOT1"]["Fan Enabled"] = True
    raw["idu"]["MOT1"]["Hidden Calibration"] = {"owner": "runtime"}
    destination.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    return destination


def _service(tmp_path: Path) -> DataMappingService:
    return DataMappingService(
        RuntimeMappingCatalogProvider(str(_mapping_file(tmp_path))),
        mapping_requirement_provider=RequirementProvider(),
    )


def _csv_records(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8", newline="") as source:
        return list(csv.reader(source))


def _bundle_sections(path: Path) -> tuple[list[str], dict[str, list[list[str]]]]:
    records = _csv_records(path)
    assert records[0] == ["__FORMAT__", "mapping_bundle_v1"]
    order: list[str] = []
    sections: dict[str, list[list[str]]] = {}
    current: list[list[str]] | None = None
    for record in records[1:]:
        if not record:
            continue
        if record[0] == "__SECTION__":
            order.append(record[1])
            current = []
            sections[record[1]] = current
            continue
        assert current is not None
        current.append(record)
    return order, sections


def test_exchange_export_writes_canonical_files_from_current_dirty_draft(tmp_path):
    service = _service(tmp_path)
    service.load_snapshot()
    service.edit_cell("idu", 0, "ID Volume", "54.5")
    service.edit_cell("idu", 0, "Fan Enabled", "yes")
    service.edit_cell("idu", 0, "Size", 'S,"1\nline')
    runtime_before = (tmp_path / "runtime_mapping.json").read_bytes()

    result, snapshot = service.export_exchange(tmp_path / "renamed_bundle")

    bundle_path = tmp_path / "renamed_bundle.csv"
    assert result.success
    assert result.bundle_path == bundle_path
    assert snapshot.dirty
    assert {path.name for path in tmp_path.glob("*.csv")} == {
        *{f"{group_key}.csv" for group_key in CANONICAL_GROUP_KEYS},
        "renamed_bundle.csv",
    }
    assert (tmp_path / "runtime_mapping.json").read_bytes() == runtime_before

    idu_records = _csv_records(tmp_path / "idu.csv")
    assert idu_records[0] == ["IDU", "ID Volume", "Size", "Fan Diameter", "Fan Enabled"]
    assert idu_records[1] == ["MOT1", "54.5", 'S,"1\nline', "54", "true"]
    assert "Hidden Calibration" not in idu_records[0]
    cond_records = _csv_records(tmp_path / "odu_cond_specs.csv")
    pfc_row = next(row for row in cond_records[1:] if row[:2] == ["N-SI", "PFC"])
    assert pfc_row[2] == ""

    order, sections = _bundle_sections(bundle_path)
    assert order == list(CANONICAL_GROUP_KEYS)
    for group_key in CANONICAL_GROUP_KEYS:
        assert sections[group_key] == _csv_records(tmp_path / f"{group_key}.csv")


def test_exchange_export_is_deterministic_for_same_draft(tmp_path):
    service = _service(tmp_path)
    service.load_snapshot()
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    first, _ = service.export_exchange(first_dir / "bundle.csv")
    second, _ = service.export_exchange(second_dir / "bundle.csv")

    assert first.success and second.success
    for group_key in CANONICAL_GROUP_KEYS:
        assert (first_dir / f"{group_key}.csv").read_bytes() == (
            second_dir / f"{group_key}.csv"
        ).read_bytes()
    assert (first_dir / "bundle.csv").read_bytes() == (second_dir / "bundle.csv").read_bytes()


def test_invalid_draft_blocks_exchange_without_creating_targets(tmp_path):
    service = _service(tmp_path)
    service.edit_cell("idu", 0, "ID Volume", "not-a-number")
    destination = tmp_path / "blocked" / "bundle.csv"

    result, _snapshot = service.export_exchange(destination)

    assert not result.success
    assert any(issue.code == "invalid_number" for issue in result.issues)
    assert not destination.parent.exists()


def test_bundle_name_is_normalized_and_canonical_group_names_are_reserved(tmp_path):
    service = _service(tmp_path)

    plan = service.plan_exchange_export(tmp_path / "bundle")
    reserved = service.plan_exchange_export(tmp_path / "IDU.CSV")

    assert plan.success
    assert plan.bundle_path == tmp_path / "bundle.csv"
    assert not reserved.success
    assert any(issue.code == "exchange_bundle_name_reserved" for issue in reserved.issues)


def test_existing_casefold_target_is_reported_for_overwrite_confirmation(tmp_path):
    service = _service(tmp_path)
    existing = tmp_path / "IDU.CSV"
    existing.write_bytes(b"old")

    plan = service.plan_exchange_export(tmp_path / "bundle.csv")

    assert plan.success
    assert existing in plan.existing_paths


def test_confirmed_export_replaces_all_existing_targets_as_one_package(tmp_path):
    service = _service(tmp_path)
    target_paths = [tmp_path / f"{group_key}.csv" for group_key in CANONICAL_GROUP_KEYS]
    target_paths.append(tmp_path / "bundle.csv")
    for path in target_paths:
        path.write_bytes(b"old package")

    result, _snapshot = service.export_exchange(tmp_path / "bundle.csv")

    assert result.success
    assert len(result.existing_paths) == 8
    assert all(path.read_bytes() != b"old package" for path in target_paths)
    assert all(path.is_file() for path in target_paths)


def test_staging_writer_failure_preserves_existing_package(tmp_path, monkeypatch):
    service = _service(tmp_path)
    target_paths = [tmp_path / f"{group_key}.csv" for group_key in CANONICAL_GROUP_KEYS]
    target_paths.append(tmp_path / "bundle.csv")
    before = {}
    for path in target_paths:
        path.write_bytes(f"old:{path.name}".encode())
        before[path] = path.read_bytes()

    calls = 0

    def fail_after_first(path: Path, payload: bytes) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("synthetic staging writer failure")
        path.write_bytes(payload)

    monkeypatch.setattr(
        "core.mapping.exchange.export._write_staged_file",
        fail_after_first,
    )
    result, _snapshot = service.export_exchange(tmp_path / "bundle.csv")

    assert not result.success
    assert "synthetic staging writer failure" in result.message
    assert {path: path.read_bytes() for path in target_paths} == before
    assert not list(tmp_path.glob(".bundle.exchange-*"))


@pytest.mark.parametrize("existing_count", (8, 2))
def test_publish_mid_failure_rolls_back_existing_and_new_targets(
    tmp_path,
    monkeypatch,
    existing_count,
):
    service = _service(tmp_path)
    target_paths = [tmp_path / f"{group_key}.csv" for group_key in CANONICAL_GROUP_KEYS]
    target_paths.append(tmp_path / "bundle.csv")
    before: dict[Path, bytes] = {}
    for path in target_paths[:existing_count]:
        path.write_bytes(f"old:{path.name}".encode())
        before[path] = path.read_bytes()

    real_replace = os.replace
    published: list[Path] = []
    published_existing: list[Path] = []
    published_new: list[Path] = []

    def fail_fourth_publish(source, destination):
        source_path = Path(source)
        destination_path = Path(destination)
        is_publish = source_path.suffix == ".csv" and ".exchange-" in str(source_path.parent)
        if is_publish:
            if len(published) == 3:
                raise OSError("synthetic publish failure after three targets")
            replaced_existing = destination_path.exists()
            real_replace(source, destination)
            assert destination_path.is_file()
            published.append(destination_path)
            (published_existing if replaced_existing else published_new).append(
                destination_path
            )
            return
        real_replace(source, destination)

    monkeypatch.setattr("core.mapping.exchange.export.os.replace", fail_fourth_publish)
    result, _snapshot = service.export_exchange(tmp_path / "bundle.csv")

    assert not result.success
    assert "synthetic publish failure after three targets" in result.message
    assert len(published) == 3
    assert len(published_existing) == min(existing_count, 3)
    assert len(published_new) == max(0, 3 - existing_count)
    if existing_count == 2:
        assert published_existing == target_paths[:2]
        assert published_new == [target_paths[2]]
    assert {path: path.read_bytes() for path in before} == before
    assert all(not path.exists() for path in published_new)
    assert all(not path.exists() for path in target_paths[existing_count:])
    assert not list(tmp_path.glob(".bundle.exchange-*"))
