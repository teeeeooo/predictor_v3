import csv
from pathlib import Path

import pytest

from apps.train.adapters.mapping.legacy_bootstrap import (
    LegacyMappingBootstrapError,
    parse_legacy_mapping_csv,
)
from core.mapping.editor_persistence import runtime_mapping_from_editor_draft
from core.mapping.editor_validation import validate_mapping_editor_draft


FIXTURE = Path("tests/fixtures/mapping/mapping_tables_legacy_wide.csv")


def _fixture_rows() -> list[list[str]]:
    with FIXTURE.open(newline="", encoding="utf-8") as source:
        return list(csv.reader(source))


def _write_rows(tmp_path: Path, rows: list[list[str]]) -> Path:
    destination = tmp_path / "legacy.csv"
    with destination.open("w", newline="", encoding="utf-8") as target:
        csv.writer(target).writerows(rows)
    return destination


def _blank_row(width: int) -> list[str]:
    return [""] * width


def test_fixture_projects_canonical_groups_and_conditional_condenser_identity():
    draft = parse_legacy_mapping_csv(FIXTURE)

    compressor = draft.group("compressor")
    evap = draft.group("evap_index")
    idu = draft.group("idu")
    odu = draft.group("odu")
    condenser = draft.group("odu_cond_specs")
    assert compressor is not None
    assert evap is not None
    assert idu is not None
    assert odu is not None
    assert condenser is not None
    assert compressor.rows[0].values == {
        "Compressor": "Comp A",
        "Comp EER": 3.5,
        "Comp cc": 13,
    }
    assert evap.rows[0].value_for("Evap Area") == 5
    assert isinstance(evap.rows[0].value_for("Evap Volume"), int)
    assert next(row for row in idu.rows if row.source_key == "Q1").value_for("ID Volume") == 52
    assert next(row for row in odu.rows if row.source_key == "Q-480").value_for("OD Volume") == 180

    pfc = next(row for row in condenser.rows if row.source_key == "N-V2MD PFC 1")
    assert pfc.value_for("Fin Type") == "PFC"
    assert pfc.value_for("Pi") == ""
    assert pfc.value_for("Row") == "1"

    validation = validate_mapping_editor_draft(draft)
    runtime = runtime_mapping_from_editor_draft(draft)
    assert validation.save_enabled
    assert "N-V2MD F&T 7 1" in runtime["cond_specs"]
    assert "N-V2MD PFC 1" in runtime["cond_specs"]
    assert "N-V2MD PFC PFC 1" not in runtime["cond_specs"]
    assert "PFC" not in runtime["pi"]


def test_blank_block_key_skips_only_that_block():
    draft = parse_legacy_mapping_csv(FIXTURE)

    assert len(draft.group("compressor").rows) == 3
    assert len(draft.group("evap_index").rows) == 13
    assert len(draft.group("idu").rows) == 9
    assert len(draft.group("odu_cond_specs").rows) == 22


@pytest.mark.parametrize(
    ("key_column", "block", "key"),
    [
        (0, "compressor", "Comp A"),
        (5, "evap_index", "S1-2"),
        (9, "idu", "Q1"),
        (13, "odu", "N-V2MD"),
        (24, "refrigerant", "R410A"),
        (26, "expansion", "EEV"),
    ],
)
def test_duplicate_primary_key_fails_with_context(tmp_path, key_column, block, key):
    rows = _fixture_rows()
    duplicate = _blank_row(len(rows[0]))
    duplicate[key_column] = key
    rows.append(duplicate)

    with pytest.raises(LegacyMappingBootstrapError) as caught:
        parse_legacy_mapping_csv(_write_rows(tmp_path, rows))

    assert caught.value.block == block
    assert caught.value.key == key
    assert caught.value.legacy_row == len(rows)
    assert "duplicate primary key" in caught.value.reason


def test_duplicate_conditional_condenser_identity_fails(tmp_path):
    rows = _fixture_rows()
    duplicate = _blank_row(len(rows[0]))
    duplicate[16:23] = ["N-V2MD", "PFC", "PFC", "1", "ignored", "21", "30"]
    rows.append(duplicate)

    with pytest.raises(LegacyMappingBootstrapError) as caught:
        parse_legacy_mapping_csv(_write_rows(tmp_path, rows))

    assert caught.value.block == "odu_cond_specs"
    assert caught.value.key == "N-V2MD PFC 1"
    assert "duplicate condenser identity" in caught.value.reason


def test_invalid_numeric_value_fails_with_field_context(tmp_path):
    rows = _fixture_rows()
    rows[1][1] = "not-a-number"

    with pytest.raises(LegacyMappingBootstrapError) as caught:
        parse_legacy_mapping_csv(_write_rows(tmp_path, rows))

    assert caught.value.legacy_row == 2
    assert caught.value.block == "compressor"
    assert caught.value.field == "Comp EER"
    assert "numeric" in caught.value.reason


def test_cond_index_is_ignored_validation_evidence(tmp_path):
    rows = _fixture_rows()
    rows[1][20] = "does not match any runtime identity"

    parsed = parse_legacy_mapping_csv(_write_rows(tmp_path, rows))

    assert parsed == parse_legacy_mapping_csv(FIXTURE)


@pytest.mark.parametrize("layout_change", ["header", "row_width"])
def test_required_header_or_layout_mismatch_fails(tmp_path, layout_change):
    rows = _fixture_rows()
    if layout_change == "header":
        rows[0][17] = "Fin Type"
    else:
        rows[1].append("unexpected")

    with pytest.raises(LegacyMappingBootstrapError) as caught:
        parse_legacy_mapping_csv(_write_rows(tmp_path, rows))

    assert caught.value.block == "layout"
    assert "layout" in caught.value.reason or "header" in caught.value.reason


def test_parser_result_is_deterministic():
    first = parse_legacy_mapping_csv(FIXTURE)
    second = parse_legacy_mapping_csv(FIXTURE)

    assert first == second
    assert runtime_mapping_from_editor_draft(first) == runtime_mapping_from_editor_draft(second)
