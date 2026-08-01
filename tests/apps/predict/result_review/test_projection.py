"""Result Review projection and full-row clipboard regressions."""

import csv
from dataclasses import replace
from io import StringIO

import pytest

from apps.predict.application.result_review import (
    RESULT_REVIEW_COLUMNS,
    ResultReviewProjection,
)
from apps.predict.application.result_review.presentation import display_value
from apps.predict.application.result_review.projection import SUMMARY_GROUPS
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.state.result_row import ResultRow
from tests.helpers.predict_results import accept_result_fixtures


EXPECTED_HEADERS = (
    "Case",
    "상태",
    "냉방능력",
    "난방능력",
    "사양 요약",
    "EER",
    "COP",
    "냉방 주파수",
    "난방 주파수",
    "냉매량",
)


def _composition(rows=1):
    return build_predict_workspace_composition(initial_empty_rows=rows)


def _fill_case(case, cooling=3500.0, heating=4200.0):  # noqa: ANN001
    case.input_values.update(
        {
            "cooling_capa": cooling,
            "heating_capa": heating,
            "idu": "IDU-A",
            "evap_index": "EV-1",
            "odu": "ODU-B",
            "fin_type": "Louver",
            "pi": "1.8",
            "row": "2",
            "compressor": "COMP-C",
            "ref_type": "R32",
            "exp_type": "EEV",
        }
    )


def _accept(composition, case_id, *, status="complete", values=None, message=""):
    return accept_result_fixtures(
        composition,
        ResultRow(case_id, status, values or {}, message),
    )[0]


def test_exact_columns_and_ordinals_follow_live_canonical_order():
    composition = _composition(2)
    projection = composition.result_review_projection
    first, second = composition.session.case_order

    assert tuple(item.header for item in RESULT_REVIEW_COLUMNS) == EXPECTED_HEADERS
    assert [(row.case_ordinal, row.case_id) for row in projection.rows()] == [
        (1, first),
        (2, second),
    ]

    inserted = composition.session.case_store.insert_empty_rows(0)[0]
    assert [(row.case_ordinal, row.case_id) for row in projection.rows()] == [
        (1, inserted.case_id),
        (2, first),
        (3, second),
    ]

    composition.session.case_store.remove_rows((first,))
    assert [(row.case_ordinal, row.case_id) for row in projection.rows()] == [
        (1, inserted.case_id),
        (2, second),
    ]
    assert projection.session is composition.session


@pytest.mark.parametrize(
    ("status", "message"),
    (
        ("pending", ""),
        ("running", "working"),
        ("complete", ""),
        ("partial", "partial evidence"),
        ("error", "failed"),
        ("invalid", "bad input"),
        ("cancelled", "cancelled"),
    ),
)
def test_all_canonical_statuses_project_with_issue_access(status, message):
    composition = _composition()
    case_id = composition.session.case_order[0]
    _fill_case(composition.session.case_store.get_case(case_id))
    if status in {"pending", "running", "invalid"}:
        composition.session.set_result(ResultRow(case_id, status, message=message))
    else:
        _accept(composition, case_id, status=status, message=message)

    row = composition.result_review_projection.rows()[0]

    assert row.status == status
    assert row.message == message
    if message:
        assert any(issue.message == message for issue in row.issues)


def test_stale_result_uses_pinned_capacity_then_fresh_result_replaces_it():
    composition = _composition()
    case = composition.session.case_store.get_case(composition.session.case_order[0])
    _fill_case(case, cooling=2835.100025, heating=4200.654321)
    _accept(
        composition,
        case.case_id,
        values={
            "cooling_power": 1000.0,
            "heating_power": 1200.0,
            "cooling_hz": 57.123456789,
            "heating_hz": 61.987654321,
            "ref_qty": 1.23456789,
        },
    )
    original = composition.result_review_projection.rows()[0]
    raw_eer = original.eer.raw_value

    case.set_input_value("cooling_capa", 7000.0)
    stale = composition.result_review_projection.rows()[0]

    assert stale.freshness == "stale"
    assert stale.cooling_capacity.source_kind == "execution_evidence"
    assert stale.cooling_capacity.raw_value == 2835.100025
    assert stale.eer.raw_value == raw_eer
    assert display_value(stale, "status") == "완료 · 오래됨 (재실행 필요)"
    assert display_value(stale, "eer") == "2.84"
    assert raw_eer == 2.835100025

    _accept(composition, case.case_id, values={"cooling_power": 1000.0})
    fresh = composition.result_review_projection.rows()[0]
    assert fresh.freshness == "current"
    assert fresh.cooling_capacity.raw_value == 7000.0
    assert fresh.eer.raw_value == 7.0


def test_partial_availability_and_unexecuted_current_capacity_do_not_invent_values():
    composition = _composition(2)
    pending_id, partial_id = composition.session.case_order
    pending = composition.session.case_store.get_case(pending_id)
    partial = composition.session.case_store.get_case(partial_id)
    _fill_case(pending, cooling=3100, heating="")
    _fill_case(partial, cooling=3500, heating=4200)
    _accept(
        composition,
        partial_id,
        status="partial",
        values={"cooling_power": 1000.0},
    )

    pending_row, partial_row = composition.result_review_projection.rows()

    assert pending_row.cooling_capacity.source_kind == "current_case_input"
    assert pending_row.cooling_capacity.raw_value == 3100
    assert display_value(pending_row, "heating_capacity") == "—"
    assert display_value(partial_row, "eer") == "3.50"
    assert display_value(partial_row, "cop") == "—"
    assert display_value(partial_row, "cooling_frequency") == "—"
    assert partial_row.cop.reason_code == "power_unavailable"


def test_summary_uses_stable_identities_current_labels_and_preserves_full_text():
    composition = _composition()
    case = composition.session.case_store.get_case(composition.session.case_order[0])
    descriptors = []
    values = {}
    expected_groups = []
    grouped_ids = {identity for group in SUMMARY_GROUPS for identity in group}
    for descriptor in composition.runtime_snapshot.column_descriptors:
        if descriptor.feature_identity in grouped_ids:
            suffix = descriptor.feature_identity[-6:]
            descriptor = replace(
                descriptor,
                key=f"renamed_{suffix}",
                label=f"Generation Label {suffix}",
            )
            value = f"full value {suffix} / no truncation"
            values[descriptor.key] = value
        descriptors.append(descriptor)
    case.input_values.update(values)
    projection = ResultReviewProjection(composition.session, tuple(descriptors))

    for group in SUMMARY_GROUPS:
        expected_groups.append(
            " + ".join(
                f"Generation Label {identity[-6:]}: full value {identity[-6:]} / no truncation"
                for identity in group
            )
        )
    expected = " · ".join(expected_groups)

    assert projection.rows()[0].specification_summary == expected
    assert "no truncation" in projection.rows()[0].specification_summary


def test_clipboard_keeps_visible_fields_first_raw_evidence_and_provenance():
    composition = _composition(2)
    first, second = composition.session.case_order
    for ordinal, case_id in enumerate((first, second), start=1):
        case = composition.session.case_store.get_case(case_id)
        _fill_case(case, cooling=2835.100025 + ordinal, heating=4200 + ordinal)
        _accept(
            composition,
            case_id,
            values={
                "cooling_power": 1000.123456789 + ordinal,
                "heating_power": 1200.987654321 + ordinal,
                "cooling_hz": 57.123456789 + ordinal,
                "heating_hz": 61.987654321 + ordinal,
                "ref_qty": 1.23456789 + ordinal,
            },
        )

    before_revision = composition.session.revision
    before_results = dict(composition.session.results_by_case_id)
    document = composition.result_review_projection.clipboard_document((second, first))
    grid = document.grid()

    assert grid[0][:10] == EXPECTED_HEADERS
    assert [row[0] for row in grid[1:]] == [1, 2]
    assert grid[1][5] == document.source_rows[0].eer.raw_value
    assert grid[1][5] != float(display_value(document.source_rows[0], "eer"))
    assert grid[1][10] == 1001.123456789
    assert grid[1][11] == 1201.987654321
    assert grid[1][12] == "current"
    assert grid[1][13] == first
    assert grid[1][14].startswith("test-result-")
    assert document.source_rows[0].target_outcomes == before_results[first].target_outcomes
    assert composition.session.revision == before_revision
    assert dict(composition.session.results_by_case_id) == before_results
    assert document.to_tsv().splitlines()[0].split("\t")[:10] == list(EXPECTED_HEADERS)


def test_stale_clipboard_exports_historical_capacity_and_power_not_current_edit():
    composition = _composition()
    case = composition.session.case_store.get_case(composition.session.case_order[0])
    _fill_case(case, cooling=3500, heating=4200)
    accepted = _accept(
        composition,
        case.case_id,
        values={"cooling_power": 987.654321, "heating_power": 1234.56789},
    )
    case.set_input_value("cooling_capa", 9999)

    grid_row = composition.result_review_projection.clipboard_document(
        (case.case_id,)
    ).grid()[1]

    assert grid_row[2] == 3500.0
    assert grid_row[1] == "완료 · 오래됨 (재실행 필요)"
    assert grid_row[10] == 987.654321
    assert grid_row[12] == "stale"
    assert grid_row[14] == accepted.execution_context.run_id


def test_unavailable_clipboard_cells_are_blank_not_numeric_placeholders():
    composition = _composition()
    case_id = composition.session.case_order[0]
    row = composition.result_review_projection.clipboard_document((case_id,)).grid()[1]

    assert row[2:4] == ("", "")
    assert row[5:10] == ("", "", "", "", "")
    assert row[10:12] == ("", "")


def test_clipboard_tsv_preserves_summary_source_tabs_and_newlines():
    composition = _composition()
    case_id = composition.session.case_order[0]
    case = composition.session.case_store.get_case(case_id)
    _fill_case(case)
    case.input_values["idu"] = "IDU\tA\nfull"
    document = composition.result_review_projection.clipboard_document((case_id,))

    decoded = list(csv.reader(StringIO(document.to_tsv()), delimiter="\t"))

    assert len(decoded) == 2
    assert decoded[1][4] == document.source_rows[0].specification_summary
    assert "IDU\tA\nfull" in decoded[1][4]
