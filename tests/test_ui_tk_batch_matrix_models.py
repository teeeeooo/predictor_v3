from ui_tk.batch_matrix_models import (
    CSEC,
    CSPF,
    DECLARED_CAPACITY,
    FULL_CAPACITY,
    FULL_POWER,
    HALF_CAPACITY,
    HALF_POWER,
    HONG_KONG_CSPF_MATRIX_SPEC,
    MatrixCellKind,
    MatrixPhysicalRowType,
)
from ui_tk.sections.hong_kong_cspf_batch_spec import (
    CSEC as EXISTING_CSEC,
    CSPF as EXISTING_CSPF,
    HONG_KONG_CSPF_BATCH_SPEC,
)


def test_hong_kong_matrix_maps_one_logical_case_to_two_physical_rows():
    spec = HONG_KONG_CSPF_MATRIX_SPEC

    assert spec.physical_row_count(0) == 0
    assert spec.physical_row_count(1) == 2
    assert spec.physical_row_count(2) == 4

    assert spec.logical_case_index_from_physical_row(0) == 0
    assert spec.row_type_from_physical_row(0) is MatrixPhysicalRowType.CAPACITY
    assert spec.logical_case_index_from_physical_row(1) == 0
    assert spec.row_type_from_physical_row(1) is MatrixPhysicalRowType.POWER
    assert spec.logical_case_index_from_physical_row(2) == 1
    assert spec.row_type_from_physical_row(2) is MatrixPhysicalRowType.CAPACITY


def test_hong_kong_matrix_case_column_is_not_repeated_on_second_row():
    spec = HONG_KONG_CSPF_MATRIX_SPEC

    first = spec.resolve_cell((0, 0))
    second = spec.resolve_cell((1, 0))

    assert first.kind is MatrixCellKind.CASE
    assert spec.display_text((0, 0), {}, {}) == "1"
    assert second.kind is MatrixCellKind.BLANK_READ_ONLY
    assert spec.is_blank_read_only((1, 0))
    assert spec.is_read_only((1, 0))
    assert not spec.is_editable((1, 0))
    assert spec.display_text((1, 0), {}, {}) == ""


def test_hong_kong_matrix_row_type_column_labels_both_physical_rows():
    spec = HONG_KONG_CSPF_MATRIX_SPEC

    assert spec.display_text((0, 1), {}, {}) == "Capacity"
    assert spec.display_text((1, 1), {}, {}) == "Power"
    assert spec.is_read_only((0, 1))
    assert spec.is_read_only((1, 1))


def test_hong_kong_matrix_input_key_mapping_for_declared_full_and_half_points():
    spec = HONG_KONG_CSPF_MATRIX_SPEC

    assert spec.resolve_input_key((0, 2)) == DECLARED_CAPACITY
    assert spec.is_not_applicable((1, 2))
    assert spec.resolve_input_key((1, 2)) is None

    assert spec.resolve_input_key((0, 3)) == FULL_CAPACITY
    assert spec.resolve_input_key((1, 3)) == FULL_POWER
    assert spec.resolve_input_key((0, 4)) == HALF_CAPACITY
    assert spec.resolve_input_key((1, 4)) == HALF_POWER

    for position in ((0, 2), (0, 3), (1, 3), (0, 4), (1, 4)):
        assert spec.resolve_cell(position).kind is MatrixCellKind.INPUT
        assert spec.is_editable(position)


def test_hong_kong_matrix_keys_match_existing_batch_profile_contract():
    spec = HONG_KONG_CSPF_MATRIX_SPEC

    assert spec.input_keys == HONG_KONG_CSPF_BATCH_SPEC.input_keys
    assert spec.result_keys == (EXISTING_CSPF, EXISTING_CSEC)


def test_hong_kong_matrix_result_metrics_display_on_first_row_only():
    spec = HONG_KONG_CSPF_MATRIX_SPEC
    result_data = {CSPF: "4.939", CSEC: "729.0"}

    cspf_first = spec.resolve_cell((0, 5))
    cspf_second = spec.resolve_cell((1, 5))
    csec_first = spec.resolve_cell((0, 6))
    csec_second = spec.resolve_cell((1, 6))

    assert cspf_first.kind is MatrixCellKind.RESULT
    assert cspf_first.result_key == CSPF
    assert spec.display_text((0, 5), {}, result_data) == "4.939"
    assert cspf_second.kind is MatrixCellKind.BLANK_READ_ONLY
    assert spec.display_text((1, 5), {}, result_data) == ""

    assert csec_first.kind is MatrixCellKind.RESULT
    assert csec_first.result_key == CSEC
    assert spec.display_text((0, 6), {}, result_data) == "729.0"
    assert csec_second.kind is MatrixCellKind.BLANK_READ_ONLY
    assert spec.display_text((1, 6), {}, result_data) == ""


def test_hong_kong_matrix_editable_targets_include_input_cells_only():
    spec = HONG_KONG_CSPF_MATRIX_SPEC
    values = {
        (0, 0): "case should not mutate",
        (0, 2): "3500",
        (1, 2): "declared power row should not mutate",
        (0, 3): "3600",
        (1, 3): "900",
        (0, 5): "result should not mutate",
        (1, 5): "blank result row should not mutate",
    }

    assert spec.editable_targets(values) == {
        (0, 2): "3500",
        (0, 3): "3600",
        (1, 3): "900",
    }


def test_hong_kong_matrix_display_text_reads_case_and_result_data():
    spec = HONG_KONG_CSPF_MATRIX_SPEC
    case_data = {
        DECLARED_CAPACITY: "3500",
        FULL_CAPACITY: "3600",
        FULL_POWER: "900",
        HALF_CAPACITY: "1700",
        HALF_POWER: "380",
    }

    assert spec.display_text((0, 2), case_data, {}) == "3500"
    assert spec.display_text((0, 3), case_data, {}) == "3600"
    assert spec.display_text((1, 3), case_data, {}) == "900"
    assert spec.display_text((0, 4), case_data, {}) == "1700"
    assert spec.display_text((1, 4), case_data, {}) == "380"


def test_hong_kong_matrix_snapshot_restore_is_logical_case_based():
    spec = HONG_KONG_CSPF_MATRIX_SPEC
    cases = [
        {
            DECLARED_CAPACITY: "3500",
            FULL_CAPACITY: "3600",
            FULL_POWER: "900",
            HALF_CAPACITY: "1700",
            HALF_POWER: "380",
            CSPF: "4.939",
            CSEC: "729.0",
            "unknown": "ignored",
        },
        {DECLARED_CAPACITY: "4200", FULL_CAPACITY: "4300"},
    ]

    snapshot = spec.snapshot_cases(cases)
    restored = spec.restore_cases(snapshot)

    assert len(snapshot) == 2
    assert snapshot[0][DECLARED_CAPACITY] == "3500"
    assert snapshot[0][CSPF] == "4.939"
    assert "unknown" not in snapshot[0]
    assert restored == [dict(row) for row in snapshot]
    assert spec.physical_row_count(len(restored)) == 4
