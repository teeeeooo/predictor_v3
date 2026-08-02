"""Slice 6 Predict bulk-paste transaction acceptance tests."""

from dataclasses import replace

from apps.predict.adapters.dropdown_option_adapter import DropdownOptionAdapter
from apps.predict.application.bulk_paste import (
    BulkPasteDestination,
    BulkPasteTransaction,
)
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.schema.case_table_schema_adapter import build_case_table_column_schema
from apps.predict.schema.column_schema_adapter import build_predict_column_schema
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow
from tests.helpers.predict_results import accept_result_fixtures


MAPPING = {
    "idu": {"IDU-A": {}},
    "odu": {"ODU-A": {}, "ODU-B": {}},
    "compressor": {"CMP-A": {}},
    "ref_type": {"R32": {}},
    "exp_type": {"EEV": {}},
    "fin_type": {"F&T": {}, "Blue": {}},
    "pi": {"7": {}, "9": {}},
    "row": {"1": {}, "2": {}},
    "odu_cascade": {
        "ODU-A": {
            "Available_Fins": ["F&T"],
            "Available_Pis": ["7"],
            "Available_Rows": ["1"],
        },
        "ODU-B": {
            "Available_Fins": ["Blue"],
            "Available_Pis": ["9"],
            "Available_Rows": ["2"],
        },
    },
    "cond_specs": {
        "ODU-A F&T 7 1": {"Cond Area": 3.5, "Cond Volume": 4.5},
        "ODU-B Blue 9 2": {"Cond Area": 6.5, "Cond Volume": 7.5},
    },
}


class _MappingRepository:
    mapping_file = ""

    def __init__(self, data=MAPPING) -> None:  # noqa: ANN001
        self.data = data
        self.load_count = 0

    def load(self):  # noqa: ANN201
        self.load_count += 1
        return self.data


def _composition(rows: int = 1, mapping=MAPPING):  # noqa: ANN001, ANN201
    return build_predict_workspace_composition(
        initial_empty_rows=rows,
        mapping_repository=_MappingRepository(mapping),
    )


def _destination(composition, key: str, row: int = 0) -> BulkPasteDestination:  # noqa: ANN001
    column = next(item for item in composition.columns if item.key == key)
    return BulkPasteDestination(row, column.feature_identity)


def _state(session: PredictSession):  # noqa: ANN201
    return (
        session.case_order,
        tuple(
            (
                case_id,
                dict(case.input_values),
                dict(case.autofill_values),
                set(case.dirty_fields),
                case.input_revision,
            )
            for case_id in session.case_order
            for case in (session.case_store.get_case(case_id),)
        ),
        dict(session.results_by_case_id),
        session.revision,
        session.case_store._next_case_number,
    )


def test_multi_row_final_combination_expands_rows_and_reuses_mapping_once():
    composition = _composition()
    transaction = composition.bulk_paste_transaction
    before_session_revision = composition.session.revision

    outcome = transaction.apply(
        "ODU-A\tF&T\t7\t1\nODU-B\tBlue\t9\t2\n",
        _destination(composition, "odu"),
    )

    assert outcome.applied
    assert outcome.expanded_rows == 1
    assert composition.mapping_repository.load_count == 1
    first = composition.session.case_store.get_case_at(0)
    second = composition.session.case_store.get_case_at(1)
    assert (first.input_values["fin_type"], first.input_values["pi"], first.input_values["row"]) == ("F&T", "7", "1")
    assert (first.autofill_values["cond_area"], first.autofill_values["cond_volume"]) == (3.5, 4.5)
    assert (second.autofill_values["cond_area"], second.autofill_values["cond_volume"]) == (6.5, 7.5)
    assert (first.input_revision, second.input_revision) == (1, 1)
    assert composition.session.revision == before_session_revision + 1
    assert outcome.issues == ()


def test_explicit_dependents_survive_parent_cascade_but_unpasted_stale_values_clear():
    composition = _composition(rows=2)
    first = composition.session.case_store.get_case_at(0)
    second = composition.session.case_store.get_case_at(1)
    for case in (first, second):
        case.input_values.update(
            {"odu": "ODU-B", "fin_type": "Blue", "pi": "9", "row": "2"}
        )
        case.autofill_values.update({"cond_area": 6.5, "cond_volume": 7.5})

    explicit = composition.bulk_paste_transaction.apply(
        "ODU-A\tF&T\t7\t1", _destination(composition, "odu", 0)
    )
    cleared = composition.bulk_paste_transaction.apply(
        "ODU-A", _destination(composition, "odu", 1)
    )

    assert explicit.applied and cleared.applied
    assert tuple(
        first.input_values[key] for key in ("odu", "fin_type", "pi", "row")
    ) == ("ODU-A", "F&T", "7", "1")
    assert (first.autofill_values["cond_area"], first.autofill_values["cond_volume"]) == (3.5, 4.5)
    assert (second.input_values["fin_type"], second.input_values["pi"], second.input_values["row"]) == ("", "", "")
    assert (second.autofill_values["cond_area"], second.autofill_values["cond_volume"]) == ("", "")


def test_invalid_numeric_and_combination_values_remain_with_precise_issues():
    composition = _composition(rows=2)
    numeric = composition.bulk_paste_transaction.apply(
        "not-a-number\n1200\n", _destination(composition, "cooling_capa")
    )
    combination = composition.bulk_paste_transaction.apply(
        "ODU-A\tBlue\t9\t2", _destination(composition, "odu")
    )

    assert numeric.applied
    assert composition.session.case_store.get_case_at(1).input_values["cooling_capa"] == "1200"
    assert [(item.case_id, item.column_key, item.code) for item in numeric.issues] == [
        (composition.session.case_order[0], "cooling_capa", "invalid_numeric")
    ]
    first = composition.session.case_store.get_case_at(0)
    assert (first.input_values["fin_type"], first.input_values["pi"], first.input_values["row"]) == ("Blue", "9", "2")
    assert {item.column_key for item in combination.issues} >= {"fin_type", "pi", "row"}


def test_missing_mapping_preserves_raw_values_without_fabricated_combination_issues():
    composition = _composition(mapping={})
    outcome = composition.bulk_paste_transaction.apply(
        "ODU-X\tFIN-X\t99\t7", _destination(composition, "odu")
    )

    case = composition.session.case_store.get_case_at(0)
    assert outcome.applied
    assert outcome.issues == ()
    assert tuple(case.input_values[key] for key in ("odu", "fin_type", "pi", "row")) == (
        "ODU-X", "FIN-X", "99", "7"
    )
    assert tuple(case.autofill_values.get(key, "") for key in ("cond_area", "cond_volume")) == ("", "")


def test_only_affected_result_stales_and_pre_paste_late_result_is_rejected():
    composition = _composition(rows=2)
    first_id, second_id = composition.session.case_order
    first_result, second_result = accept_result_fixtures(
        composition,
        ResultRow(first_id, "complete"),
        ResultRow(second_id, "complete"),
    )
    composition.session.allow_result(
        first_result.execution_context,
        composition.runtime_snapshot.target_descriptors,
    )
    composition.session.set_result(ResultRow(first_id, "running"))
    unaffected_revision = composition.session.case_store.get_case(second_id).input_revision

    outcome = composition.bulk_paste_transaction.apply(
        "1000", _destination(composition, "cooling_capa")
    )
    semantics, model = composition.prediction_controller.execution_environment
    late = composition.session.accept_result(first_result, semantics, model)

    assert outcome.affected_case_ids == (first_id,)
    assert not late.accepted
    assert late.reason_code in {"run_not_active", "input_revision_changed"}
    assert composition.session.result_for_case(first_id).status == "pending"
    assert composition.session.result_for_case(first_id).execution_context is None
    assert composition.session.result_for_case(second_id) == second_result
    assert composition.session.case_store.get_case(second_id).input_revision == unaffected_revision


def test_commit_failure_rolls_back_rows_inputs_results_and_case_allocator(monkeypatch):
    composition = _composition()
    case_id = composition.session.case_order[0]
    accept_result_fixtures(composition, ResultRow(case_id, "complete"))
    before = _state(composition.session)
    authority = composition.session._input_transaction_authority
    original = authority._apply_case_state
    calls = 0

    def fail_second(case, staged):  # noqa: ANN001, ANN202
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("injected commit failure")
        return original(case, staged)

    monkeypatch.setattr(authority, "_apply_case_state", fail_second)
    outcome = composition.bulk_paste_transaction.apply(
        "1000\n2000\n", _destination(composition, "cooling_capa")
    )

    assert not outcome.applied
    assert "injected commit failure" in outcome.message
    assert _state(composition.session) == before


def test_precommit_failure_preserves_existing_issue_projection(monkeypatch):
    composition = _composition(rows=2)
    transaction = composition.bulk_paste_transaction
    prior = transaction.apply(
        "bad", _destination(composition, "cooling_capa")
    )
    before = _state(composition.session)
    monkeypatch.setattr(
        transaction,
        "_mapping_loader",
        lambda: (_ for _ in ()).throw(RuntimeError("mapping unavailable")),
    )

    failed = transaction.apply(
        "1200", _destination(composition, "cooling_capa", 1)
    )

    assert not failed.applied
    assert failed.issues == prior.issues == transaction.issues
    assert _state(composition.session) == before


def test_compound_undo_removes_added_rows_and_does_not_revive_result_freshness():
    composition = _composition()
    case_id = composition.session.case_order[0]
    accept_result_fixtures(composition, ResultRow(case_id, "complete"))
    before_revision = composition.session.case_store.get_case(case_id).input_revision
    paste = composition.bulk_paste_transaction.apply(
        "1000\n2000\n", _destination(composition, "cooling_capa")
    )

    undone = composition.bulk_paste_transaction.undo(paste.undo_id)

    case = composition.session.case_store.get_case(case_id)
    assert paste.applied and undone.applied
    assert len(composition.session.case_store) == 1
    assert case.input_values.get("cooling_capa", "") == ""
    assert case.input_revision == before_revision + 2
    assert composition.session.result_for_case(case_id).freshness == "stale"
    assert composition.session.result_for_case(case_id).stale_reason == "input_changed"


def test_feature_identity_anchors_generation_specific_active_input_order():
    session = PredictSession()
    session.case_store.append_empty_rows(1)
    columns = build_predict_column_schema()
    cooling = next(item for item in columns if item.key == "cooling_capa")
    heating = next(item for item in columns if item.key == "heating_capa")
    reordered = (replace(heating, index=0), replace(cooling, index=1)) + tuple(
        item for item in columns if item.key not in {"cooling_capa", "heating_capa"}
    )
    repository = _MappingRepository({})
    adapter = DropdownOptionAdapter(repository, build_case_table_column_schema())
    transaction = BulkPasteTransaction(
        session,
        reordered,
        repository.load,
        adapter.base_options_for_key_from_mapping,
    )

    outcome = transaction.apply(
        "2100\t1100", BulkPasteDestination(0, heating.feature_identity)
    )

    assert outcome.applied
    case = session.case_store.get_case_at(0)
    assert case.input_values["heating_capa"] == "2100"
    assert case.input_values["cooling_capa"] == "1100"
