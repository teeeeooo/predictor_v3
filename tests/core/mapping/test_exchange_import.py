"""Slice 2E mapping bundle parser, preview, apply, and round-trip tests."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import pytest

from apps.train.services.data_mapping_service import (
    DataMappingService,
    RuntimeMappingCatalogProvider,
)
from core.data_definition.model import MappingRequirement
from core.mapping.exchange import (
    CANONICAL_GROUP_KEYS,
    parse_mapping_exchange_bundle,
)

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
    raw["vendor_notes"] = {"keep": ["unowned", 1]}
    destination.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    return destination


def _service(tmp_path: Path) -> DataMappingService:
    return DataMappingService(
        RuntimeMappingCatalogProvider(str(_mapping_file(tmp_path))),
        mapping_requirement_provider=RequirementProvider(),
    )


def _official_bundle(tmp_path: Path) -> tuple[DataMappingService, Path]:
    service = _service(tmp_path)
    service.load_snapshot()
    result, _snapshot = service.export_exchange(tmp_path / "official_bundle.csv")
    assert result.success
    return service, tmp_path / "official_bundle.csv"


def _records(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8", newline="") as source:
        return list(csv.reader(source))


def _write_records(path: Path, records: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as output:
        csv.writer(output, lineterminator="\n").writerows(records)


def _blocks(path: Path) -> tuple[list[str], list[list[list[str]]]]:
    records = _records(path)
    assert records[0] == ["__FORMAT__", "mapping_bundle_v1"]
    starts = [
        index
        for index, record in enumerate(records)
        if record and record[0] == "__SECTION__"
    ]
    blocks = [
        [record for record in records[start : starts[index + 1] if index + 1 < len(starts) else len(records)] if record]
        for index, start in enumerate(starts)
    ]
    return [block[0][1] for block in blocks], blocks


def _write_blocks(path: Path, blocks: list[list[list[str]]]) -> None:
    records: list[list[str]] = [["__FORMAT__", "mapping_bundle_v1"]]
    for block in blocks:
        records.append([])
        records.extend(block)
    _write_records(path, records)


def _block(blocks: list[list[list[str]]], key: str) -> list[list[str]]:
    return next(block for block in blocks if block[0] == ["__SECTION__", key])


def _issue_codes(result) -> set[str]:  # noqa: ANN001
    return {issue.code for issue in result.blockers}


def test_official_bundle_parses_from_arbitrary_renamed_path_and_shuffled_sections(tmp_path):
    service, official = _official_bundle(tmp_path)
    names, blocks = _blocks(official)
    shuffled = tmp_path / "renamed_by_external_tool.csv"
    _write_blocks(shuffled, list(reversed(blocks)))

    preview, snapshot = service.preview_exchange_import(shuffled)

    assert preview.can_apply
    assert preview.source_path == shuffled
    assert preview.format_version == "mapping_bundle_v1"
    assert [diff.group_key for diff in preview.group_diffs] == list(CANONICAL_GROUP_KEYS)
    assert snapshot.dirty is False
    assert names == list(CANONICAL_GROUP_KEYS)


def test_import_accepts_blank_lines_quoted_fields_and_zero_row_section(tmp_path):
    service, official = _official_bundle(tmp_path)
    _names, blocks = _blocks(official)
    idu = _block(blocks, "idu")
    idu[2][2] = 'quoted, "value"\nnext'
    refrigerant = _block(blocks, "refrigerant")
    del refrigerant[2:]
    source = tmp_path / "quoted.csv"
    _write_blocks(source, blocks)
    text = source.read_text(encoding="utf-8")
    source.write_text(text.replace("__SECTION__,idu\n", "\n__SECTION__,idu\n"), encoding="utf-8")

    preview, _snapshot = service.preview_exchange_import(source)

    assert preview.can_apply
    assert preview.candidate.group("idu").rows[0].value_for("Size") == 'quoted, "value"\nnext'
    assert preview.candidate.group("refrigerant").rows == ()


def test_import_projects_reordered_headers_to_current_definition_order(tmp_path):
    service, official = _official_bundle(tmp_path)
    _names, blocks = _blocks(official)
    idu = _block(blocks, "idu")
    order = [4, 0, 3, 1, 2]
    idu[1:] = [
        [row[index] for index in order]
        for row in idu[1:]
    ]
    source = tmp_path / "reordered.csv"
    _write_blocks(source, blocks)

    preview, _snapshot = service.preview_exchange_import(source)

    assert preview.can_apply
    assert preview.candidate.group("idu").columns == (
        "IDU",
        "ID Volume",
        "Size",
        "Fan Diameter",
        "Fan Enabled",
    )
    assert preview.candidate.group("idu").rows[0].value_for("Fan Enabled") is True


@pytest.mark.parametrize(
    ("mutator", "code", "field_fragment"),
    (
        (lambda block: block[1].remove("Size"), "import_missing_column", "Size"),
        (lambda block: block[1].__setitem__(2, "Unknown"), "import_unknown_column", "Unknown"),
        (lambda block: block[1].__setitem__(2, "IDU"), "import_duplicate_header", "IDU"),
    ),
)
def test_exact_header_blockers_name_group_and_column(tmp_path, mutator, code, field_fragment):
    service, official = _official_bundle(tmp_path)
    _names, blocks = _blocks(official)
    idu = _block(blocks, "idu")
    mutator(idu)
    source = tmp_path / f"{code}.csv"
    _write_blocks(source, blocks)

    preview, _snapshot = service.preview_exchange_import(source)

    assert not preview.can_apply
    assert code in _issue_codes(type("Result", (), {"blockers": preview.blockers})())
    assert any("IDU" in issue.message and field_fragment in issue.message for issue in preview.blockers)
    if code != "import_unknown_column":
        assert any("Data Definition" in issue.message for issue in preview.blockers)


def test_missing_format_unsupported_duplicate_marker_and_malformed_csv_block(tmp_path):
    service, official = _official_bundle(tmp_path)
    valid = official.read_text(encoding="utf-8")
    cases = {
        "missing.csv": valid.replace("__FORMAT__,mapping_bundle_v1\n", "", 1),
        "unsupported.csv": valid.replace("mapping_bundle_v1", "mapping_bundle_v9", 1),
        "duplicate.csv": valid.replace(
            "__FORMAT__,mapping_bundle_v1\n",
            "__FORMAT__,mapping_bundle_v1\n__FORMAT__,mapping_bundle_v1\n",
            1,
        ),
        "malformed.csv": '__FORMAT__,mapping_bundle_v1\n__SECTION__,idu\n"unterminated\n',
    }

    for name, content in cases.items():
        source = tmp_path / name
        source.write_text(content, encoding="utf-8")
        preview, _snapshot = service.preview_exchange_import(source)
        assert not preview.can_apply, name
    assert "import_format_marker_missing" in _issue_codes(
        type("Result", (), {"blockers": service.preview_exchange_import(tmp_path / "missing.csv")[0].blockers})()
    )
    assert "import_unsupported_format" in _issue_codes(
        type("Result", (), {"blockers": service.preview_exchange_import(tmp_path / "unsupported.csv")[0].blockers})()
    )
    assert "import_duplicate_format_marker" in _issue_codes(
        type("Result", (), {"blockers": service.preview_exchange_import(tmp_path / "duplicate.csv")[0].blockers})()
    )
    assert "import_malformed_csv" in _issue_codes(
        type("Result", (), {"blockers": service.preview_exchange_import(tmp_path / "malformed.csv")[0].blockers})()
    )


def test_duplicate_unknown_missing_sections_and_missing_header_block(tmp_path):
    service, official = _official_bundle(tmp_path)
    _names, blocks = _blocks(official)

    duplicate = tmp_path / "duplicate-section.csv"
    _write_blocks(duplicate, blocks + [_block(blocks, "idu")])
    unknown = tmp_path / "unknown-section.csv"
    _write_blocks(unknown, blocks + [[ ["__SECTION__", "unknown"], ["Value"], ["x"] ]])
    missing = tmp_path / "missing-section.csv"
    _write_blocks(missing, [block for block in blocks if block[0][1] != "expansion"])
    no_header = tmp_path / "missing-header.csv"
    _write_records(no_header, [["__FORMAT__", "mapping_bundle_v1"], ["__SECTION__", "idu"]])

    duplicate_preview, _ = service.preview_exchange_import(duplicate)
    unknown_preview, _ = service.preview_exchange_import(unknown)
    missing_preview, _ = service.preview_exchange_import(missing)
    no_header_preview, _ = service.preview_exchange_import(no_header)

    assert "import_duplicate_section" in _issue_codes(type("Result", (), {"blockers": duplicate_preview.blockers})())
    assert "import_unknown_section" in _issue_codes(type("Result", (), {"blockers": unknown_preview.blockers})())
    assert "import_missing_section" in _issue_codes(type("Result", (), {"blockers": missing_preview.blockers})())
    assert "import_section_header_missing" in _issue_codes(type("Result", (), {"blockers": no_header_preview.blockers})())


def test_duplicate_primary_and_condenser_identities_block(tmp_path):
    service, official = _official_bundle(tmp_path)
    _names, blocks = _blocks(official)
    idu = _block(blocks, "idu")
    idu[2][0] = idu[3][0]
    cond = _block(blocks, "odu_cond_specs")
    cond[3][:4] = cond[2][:4]
    source = tmp_path / "duplicate-identity.csv"
    _write_blocks(source, blocks)

    preview, _snapshot = service.preview_exchange_import(source)

    codes = _issue_codes(type("Result", (), {"blockers": preview.blockers})())
    assert "import_duplicate_key" in codes
    assert "import_duplicate_cond_specs_identity" in codes


def test_invalid_number_boolean_and_required_value_block(tmp_path):
    service, official = _official_bundle(tmp_path)
    _names, blocks = _blocks(official)
    idu = _block(blocks, "idu")
    idu[2][3] = "not-a-number"
    idu[2][4] = "maybe"
    cond = _block(blocks, "odu_cond_specs")
    cond[2][4] = ""
    source = tmp_path / "invalid-values.csv"
    _write_blocks(source, blocks)

    preview, _snapshot = service.preview_exchange_import(source)

    codes = _issue_codes(type("Result", (), {"blockers": preview.blockers})())
    assert "import_invalid_number" in codes
    assert "import_invalid_boolean" in codes
    assert "import_required_value_missing" in codes


def test_blocked_import_preserves_current_draft_dirty_undo_selection_and_runtime(tmp_path):
    service, official = _official_bundle(tmp_path)
    service.edit_cell("idu", 0, "Size", "before-import")
    before = service.current_snapshot()
    runtime_path = Path(before.source_label.split(": ", 1)[-1])
    runtime_before = runtime_path.read_bytes()
    _names, blocks = _blocks(official)
    _block(blocks, "idu")[1].remove("Size")
    blocked_path = tmp_path / "blocked.csv"
    _write_blocks(blocked_path, blocks)

    preview, _snapshot = service.preview_exchange_import(blocked_path)
    after_preview = service.current_snapshot()
    applied, result = service.apply_exchange_import(preview)
    undo_snapshot, undo_result = service.undo()

    assert not preview.can_apply
    assert not result.success
    assert applied.draft == before.draft == after_preview.draft
    assert applied.dirty == before.dirty
    assert runtime_path.read_bytes() == runtime_before
    assert undo_result.applied == 1
    assert undo_snapshot.draft.group("idu").rows[0].value_for("Size") != "before-import"


def test_preview_counts_cancel_and_apply_are_draft_only_and_one_undo_unit(tmp_path):
    service, official = _official_bundle(tmp_path)
    _names, blocks = _blocks(official)
    idu = _block(blocks, "idu")
    idu[2][1] = "999"
    idu.pop()
    idu.append(["NEW", "1", "new", "2", "false"])
    source = tmp_path / "changed.csv"
    _write_blocks(source, blocks)
    runtime_path = Path(service.current_snapshot().source_label.split(": ", 1)[-1])
    runtime_before = runtime_path.read_bytes()
    before = service.current_snapshot()

    preview, _snapshot = service.preview_exchange_import(source)
    diff = next(diff for diff in preview.group_diffs if diff.group_key == "idu")
    canceled_state = service.current_snapshot()
    applied, apply_result = service.apply_exchange_import(preview)

    assert (diff.existing_rows, diff.added_rows, diff.removed_rows, diff.changed_rows, diff.unchanged_rows) == (9, 1, 1, 1, 7)
    assert canceled_state.draft == before.draft
    assert apply_result.success and apply_result.changed
    assert applied.dirty
    assert runtime_path.read_bytes() == runtime_before
    assert applied.draft.group("idu").rows[0].value_for("ID Volume") == 999
    undone, undo_result = service.undo()
    assert undo_result.applied == 1
    assert undone.draft == before.draft


def test_semantic_noop_import_does_not_create_dirty_or_undo_history(tmp_path):
    service, official = _official_bundle(tmp_path)
    preview, _snapshot = service.preview_exchange_import(official)

    applied, result = service.apply_exchange_import(preview)
    undone, undo_result = service.undo()

    assert result.success and not result.changed
    assert not applied.dirty
    assert undo_result.applied == 0
    assert undone.draft == applied.draft


def test_apply_preserves_matching_hidden_payload_unowned_section_and_source_destination(tmp_path):
    service, official = _official_bundle(tmp_path)
    _names, blocks = _blocks(official)
    idu = _block(blocks, "idu")
    idu.pop()
    idu.append(["NEW", "12", "new", "", "false"])
    source = tmp_path / "renamed-external-bundle.csv"
    _write_blocks(source, blocks)
    runtime_path = Path(service.current_snapshot().source_label.split(": ", 1)[-1])
    runtime_before = runtime_path.read_bytes()

    preview, _snapshot = service.preview_exchange_import(source)
    applied, result = service.apply_exchange_import(preview)

    row = next(row for row in applied.draft.group("idu").rows if row.value_for("IDU") == "MOT1")
    new_row = next(row for row in applied.draft.group("idu").rows if row.value_for("IDU") == "NEW")
    assert result.success and result.changed
    assert row.value_for("Hidden Calibration") == {"owner": "runtime"}
    assert new_row.value_for("Hidden Calibration", "") == ""
    assert applied.draft.unowned_sections["vendor_notes"] == {"keep": ["unowned", 1]}
    assert applied.source_label == service.source_label
    assert runtime_path.read_bytes() == runtime_before

    save_result, saved = service.save_mapping()
    reloaded = service.reload_snapshot()
    assert save_result.success
    assert not saved.dirty
    assert not reloaded.dirty
    assert reloaded.draft.group("idu").rows[0].value_for("Hidden Calibration") == {"owner": "runtime"}
    assert reloaded.draft.unowned_sections["vendor_notes"] == {"keep": ["unowned", 1]}


def test_stale_preview_is_rejected_without_applying_candidate(tmp_path):
    service, official = _official_bundle(tmp_path)
    preview, _snapshot = service.preview_exchange_import(official)
    service.edit_cell("idu", 0, "Size", "changed-after-preview")

    applied, result = service.apply_exchange_import(preview)

    assert not result.success
    assert result.stale
    assert applied.draft.group("idu").rows[0].value_for("Size") == "changed-after-preview"


def test_import_parser_does_not_treat_tsv_as_bundle(tmp_path):
    service, _official = _official_bundle(tmp_path)
    tsv = tmp_path / "clipboard.tsv"
    tsv.write_text("IDU\tID Volume\nMOT1\t54\n", encoding="utf-8")

    preview, _snapshot = service.preview_exchange_import(tsv)

    assert not preview.can_apply
    assert "import_format_marker_missing" in _issue_codes(type("Result", (), {"blockers": preview.blockers})())
