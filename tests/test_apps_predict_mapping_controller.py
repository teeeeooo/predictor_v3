"""Predict app input edit controller mapping tests."""

from apps.predict.controllers.input_edit_controller import InputEditController
from apps.predict.state.predict_session import PredictSession


class FakeMappingRepository:
    def __init__(self, mapping_data: dict) -> None:
        self._mapping_data = mapping_data

    def load(self) -> dict:
        return self._mapping_data


SAMPLE_MAPPING = {
    "idu": {"IDU-A": {"ID Volume": 1.25}},
    "odu": {"ODU-A": {"OD Volume": 2.5}},
    "odu_cascade": {
        "ODU-A": {
            "Available_Fins": ["F&T"],
            "Available_Pis": ["7"],
            "Available_Rows": ["1"],
        }
    },
    "cond_specs": {
        "ODU-A F&T 7 1": {
            "Cond Area": 3.5,
            "Cond Volume": 4.5,
        }
    },
}


def test_input_edit_controller_applies_simple_autofill():
    session = PredictSession()
    case = session.case_store.append_empty_rows(1)[0]
    session.case_store.update_cell_value(case.case_id, "idu", "IDU-A")
    controller = InputEditController(session, FakeMappingRepository(SAMPLE_MAPPING))

    controller.handle_cell_edited(case.case_id, "idu")

    assert case.autofill_values["id_volume"] == 1.25


def test_input_edit_controller_clears_result_after_autofill_update():
    session = PredictSession()
    case = session.case_store.append_empty_rows(1)[0]
    session.case_store.update_cell_value(case.case_id, "idu", "IDU-A")
    session.set_result(session.result_for_case(case.case_id))
    controller = InputEditController(session, FakeMappingRepository(SAMPLE_MAPPING))

    controller.handle_cell_edited(case.case_id, "idu")

    assert case.case_id not in session.results_by_case_id


def test_input_edit_controller_applies_cond_specs_to_auto_values():
    session = PredictSession()
    case = session.case_store.append_empty_rows(1)[0]
    case.input_values.update(
        {
            "odu": "ODU-A",
            "fin_type": "F&T",
            "pi": "7",
            "row": "1",
        }
    )
    controller = InputEditController(session, FakeMappingRepository(SAMPLE_MAPPING))

    controller.handle_cell_edited(case.case_id, "row")

    assert case.autofill_values["cond_area"] == 3.5
    assert case.autofill_values["cond_volume"] == 4.5
