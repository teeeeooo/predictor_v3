"""Mapping-backed dropdown option tests for the unified Predict table."""

import inspect
import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QStyleOptionViewItem

from apps.predict.adapters.dropdown_option_adapter import DropdownOptionAdapter
from apps.predict.controllers.input_edit_controller import InputEditController
from apps.predict.mapping.mapping_repository import PredictMappingRepository
from apps.predict.schema.case_table_schema_adapter import build_case_table_column_schema
from apps.predict.state.predict_session import PredictSession
from apps.predict.ui.tables import case_table_model, case_table_view, delegates
from apps.predict.ui.workspace import PredictWorkspace


class FakeMappingRepository:
    def __init__(self, mapping_data: dict) -> None:
        self._mapping_data = mapping_data
        self.mapping_file = "/tmp/predict-mapping-test.json"

    def load(self) -> dict:
        return self._mapping_data


SAMPLE_MAPPING = {
    "idu": {"IDU-B": {}, "IDU-A": {}},
    "odu": {"ODU-A": {}, "ODU-B": {}},
    "compressor": {"CMP-A": {}},
    "ref_type": {"R410A": {}, "R32": {}},
    "exp_type": {"EEV": {}, "Capi": {}},
    "fin_type": {"F&T": {}, "Plate": {}},
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
        "ODU-A F&T 7 1": {
            "Cond Area": 3.5,
            "Cond Volume": 4.5,
        },
        "ODU-B Blue 9 2": {
            "Cond Area": 6.5,
            "Cond Volume": 7.5,
        }
    },
}


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _session_with_case() -> PredictSession:
    session = PredictSession()
    session.case_store.append_empty_rows(1)
    return session


def _column_index(workspace: PredictWorkspace, key: str) -> int:
    return next(
        index for index, column in enumerate(workspace.case_model.columns) if column.key == key
    )


def _dispose_workspace(workspace: PredictWorkspace) -> None:
    workspace.close()
    workspace.deleteLater()
    QApplication.processEvents()


def test_table_model_view_delegate_do_not_import_mapping_repository():
    for module in (case_table_model, case_table_view, delegates):
        source = inspect.getsource(module)
        assert "PredictMappingRepository" not in source
        assert "apps.predict.mapping" not in source
        assert "core.mapping" not in source


def test_workspace_does_not_parse_raw_mapping_options():
    source = inspect.getsource(PredictWorkspace)

    assert ".mapping_repository.load()" not in source
    assert "mapping_data.get" not in source
    assert "section.keys()" not in source


def test_dropdown_option_adapter_returns_mapping_backed_base_options():
    adapter = DropdownOptionAdapter(
        FakeMappingRepository(SAMPLE_MAPPING),
        build_case_table_column_schema(),
    )

    assert adapter.base_options_for_key("idu") == ("IDU-A", "IDU-B")
    assert adapter.base_options_for_key("odu") == ("ODU-A", "ODU-B")
    assert adapter.base_options_for_key("compressor") == ("CMP-A",)
    assert adapter.base_options_for_key("ref_type") == ("R32", "R410A")
    assert adapter.base_options_for_key("exp_type") == ("Capi", "EEV")
    assert adapter.base_options_for_key("missing") == ()


def test_dropdown_option_adapter_returns_empty_for_missing_ref_and_exp_sections():
    adapter = DropdownOptionAdapter(
        FakeMappingRepository({}),
        build_case_table_column_schema(),
    )

    assert adapter.base_options_for_key("ref_type") == ()
    assert adapter.base_options_for_key("exp_type") == ()
    assert "R410A" not in adapter.base_options_for_key("ref_type")
    assert "EEV" not in adapter.base_options_for_key("exp_type")


def test_dropdown_option_adapter_prefers_row_specific_options():
    adapter = DropdownOptionAdapter(
        FakeMappingRepository(SAMPLE_MAPPING),
        build_case_table_column_schema(),
    )

    assert adapter.options_for_key("fin_type", ("F&T",)) == ("F&T",)


def test_dropdown_option_adapter_keeps_calculated_empty_row_options():
    adapter = DropdownOptionAdapter(
        FakeMappingRepository(SAMPLE_MAPPING),
        build_case_table_column_schema(),
    )

    assert adapter.options_for_key("fin_type", ()) == ()


def test_dropdown_option_adapter_reports_mapping_status(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text("{}", encoding="utf-8")
    repository = FakeMappingRepository(SAMPLE_MAPPING)
    repository.mapping_file = str(mapping_file)
    adapter = DropdownOptionAdapter(repository, build_case_table_column_schema())

    status = adapter.mapping_status()

    assert status.status == "loaded"
    assert status.mapping_path == str(mapping_file)


def test_dropdown_option_adapter_reports_invalid_cached_mapping_status(tmp_path):
    mapping_file = tmp_path / "mapping.json"
    mapping_file.write_text("[]", encoding="utf-8")
    repository = FakeMappingRepository([])
    repository.mapping_file = str(mapping_file)
    repository.load()
    adapter = DropdownOptionAdapter(repository, build_case_table_column_schema())

    status = adapter.mapping_status()

    assert status.status == "invalid"
    assert adapter.base_options_for_key("ref_type") == ()


def test_odu_edit_updates_dependent_row_option_state_and_clears_stale_values():
    session = _session_with_case()
    case = session.case_store.get_case_at(0)
    case.input_values.update(
        {
            "odu": "ODU-A",
            "fin_type": "old",
            "pi": "old",
            "row": "old",
        }
    )
    case.autofill_values.update({"cond_area": "old-area", "cond_volume": "old-volume"})
    controller = InputEditController(session, FakeMappingRepository(SAMPLE_MAPPING))

    controller.handle_cell_edited(case.case_id, "odu")

    assert controller.dropdown_options_for_case(case.case_id, "fin_type") == ("F&T",)
    assert controller.dropdown_options_for_case(case.case_id, "pi") == ("7",)
    assert controller.dropdown_options_for_case(case.case_id, "row") == ("1",)
    assert case.input_values["fin_type"] == ""
    assert case.input_values["pi"] == ""
    assert case.input_values["row"] == ""
    assert case.autofill_values["cond_area"] == ""
    assert case.autofill_values["cond_volume"] == ""


def test_odu_unselected_uses_base_fin_pi_row_sections():
    session = _session_with_case()
    case = session.case_store.get_case_at(0)
    case.input_values["odu"] = ""
    controller = InputEditController(session, FakeMappingRepository(SAMPLE_MAPPING))

    controller.handle_cell_edited(case.case_id, "odu")

    assert controller.dropdown_options_for_case(case.case_id, "fin_type") == (
        "F&T",
        "Plate",
    )
    assert controller.dropdown_options_for_case(case.case_id, "pi") == ("7", "9")
    assert controller.dropdown_options_for_case(case.case_id, "row") == ("1", "2")


def test_odu_change_replaces_row_specific_options():
    session = _session_with_case()
    case = session.case_store.get_case_at(0)
    controller = InputEditController(session, FakeMappingRepository(SAMPLE_MAPPING))

    case.input_values["odu"] = "ODU-A"
    controller.handle_cell_edited(case.case_id, "odu")
    case.input_values["odu"] = "ODU-B"
    controller.handle_cell_edited(case.case_id, "odu")

    assert controller.dropdown_options_for_case(case.case_id, "fin_type") == ("Blue",)
    assert controller.dropdown_options_for_case(case.case_id, "pi") == ("9",)
    assert controller.dropdown_options_for_case(case.case_id, "row") == ("2",)


def test_cond_specs_autofill_after_fin_pi_row_selection():
    session = _session_with_case()
    case = session.case_store.get_case_at(0)
    case.input_values.update(
        {
            "odu": "ODU-B",
            "fin_type": "Blue",
            "pi": "9",
            "row": "2",
        }
    )
    controller = InputEditController(session, FakeMappingRepository(SAMPLE_MAPPING))

    controller.handle_cell_edited(case.case_id, "row")

    assert case.autofill_values["cond_area"] == 6.5
    assert case.autofill_values["cond_volume"] == 7.5


def test_unmatched_cond_specs_combination_clears_stale_cond_values():
    session = _session_with_case()
    case = session.case_store.get_case_at(0)
    case.input_values.update(
        {
            "odu": "ODU-A",
            "fin_type": "F&T",
            "pi": "9",
            "row": "1",
        }
    )
    case.autofill_values.update({"cond_area": "stale", "cond_volume": "stale"})
    controller = InputEditController(session, FakeMappingRepository(SAMPLE_MAPPING))

    controller.handle_cell_edited(case.case_id, "pi")

    assert case.autofill_values["cond_area"] == ""
    assert case.autofill_values["cond_volume"] == ""


def test_workspace_provider_returns_mapping_keys_and_row_specific_options():
    _app()
    session = _session_with_case()
    case = session.case_store.get_case_at(0)
    case.input_values["odu"] = "ODU-A"
    workspace = PredictWorkspace(
        session=session,
        mapping_repository=FakeMappingRepository(SAMPLE_MAPPING),
    )
    try:
        workspace.input_edit_controller.handle_cell_edited(case.case_id, "odu")

        idu_index = workspace.case_model.index(0, _column_index(workspace, "idu"))
        fin_index = workspace.case_model.index(0, _column_index(workspace, "fin_type"))

        assert workspace._dropdown_options_for_index(idu_index) == ("IDU-A", "IDU-B")
        assert workspace._dropdown_options_for_index(fin_index) == ("F&T",)
    finally:
        _dispose_workspace(workspace)


def test_dropdown_delegate_creates_editable_combobox_with_completer():
    _app()
    workspace = PredictWorkspace(
        session=_session_with_case(),
        mapping_repository=FakeMappingRepository(SAMPLE_MAPPING),
    )
    try:
        idu_index = workspace.case_model.index(0, _column_index(workspace, "idu"))
        editor = workspace.case_table.itemDelegate().createEditor(
            workspace.case_table,
            QStyleOptionViewItem(),
            idu_index,
        )

        assert isinstance(editor, QComboBox)
        assert editor.isEditable()
        assert editor.completer() is not None
        assert editor.completer().caseSensitivity() == Qt.CaseInsensitive
    finally:
        _dispose_workspace(workspace)


def test_typed_dropdown_value_commits_and_triggers_autofill_options():
    _app()
    session = _session_with_case()
    workspace = PredictWorkspace(
        session=session,
        mapping_repository=FakeMappingRepository(SAMPLE_MAPPING),
    )
    try:
        odu_index = workspace.case_model.index(0, _column_index(workspace, "odu"))
        editor = workspace.case_table.itemDelegate().createEditor(
            workspace.case_table,
            QStyleOptionViewItem(),
            odu_index,
        )
        assert isinstance(editor, QComboBox)
        editor.setEditText("ODU-A")

        workspace.case_table.itemDelegate().setModelData(
            editor,
            workspace.case_model,
            odu_index,
        )

        case_id = session.case_order[0]
        case = session.case_store.get_case(case_id)
        fin_index = workspace.case_model.index(0, _column_index(workspace, "fin_type"))
        assert case.input_values["odu"] == "ODU-A"
        assert workspace._dropdown_options_for_index(fin_index) == ("F&T",)
    finally:
        _dispose_workspace(workspace)


def test_missing_mapping_keeps_controlled_status_and_empty_mapping_options(tmp_path: Path):
    _app()
    repo = PredictMappingRepository(mapping_file=str(tmp_path / "missing.json"))
    workspace = PredictWorkspace(mapping_repository=repo)
    try:
        ref_index = workspace.case_model.index(0, _column_index(workspace, "ref_type"))
        idu_index = workspace.case_model.index(0, _column_index(workspace, "idu"))

        assert workspace.dropdown_option_adapter.mapping_status().status == "missing"
        assert workspace._dropdown_options_for_index(ref_index) == ()
        assert workspace._dropdown_options_for_index(idu_index) == ()
    finally:
        _dispose_workspace(workspace)


def test_missing_odu_cascade_keeps_dependent_options_empty():
    session = _session_with_case()
    case = session.case_store.get_case_at(0)
    case.input_values["odu"] = "ODU-A"
    mapping = {key: value for key, value in SAMPLE_MAPPING.items() if key != "odu_cascade"}
    controller = InputEditController(session, FakeMappingRepository(mapping))
    adapter = DropdownOptionAdapter(
        FakeMappingRepository(mapping),
        build_case_table_column_schema(),
    )

    controller.handle_cell_edited(case.case_id, "odu")

    assert controller.dropdown_options_for_case(case.case_id, "fin_type") == ()
    assert adapter.options_for_key(
        "fin_type",
        controller.dropdown_options_for_case(case.case_id, "fin_type"),
    ) == ()


def test_invalid_odu_cascade_shape_does_not_crash():
    session = _session_with_case()
    case = session.case_store.get_case_at(0)
    case.input_values["odu"] = "ODU-A"
    controller = InputEditController(
        session,
        FakeMappingRepository({**SAMPLE_MAPPING, "odu_cascade": []}),
    )

    controller.handle_cell_edited(case.case_id, "odu")

    assert controller.dropdown_options_for_case(case.case_id, "fin_type") == ()


def test_invalid_cond_specs_shape_does_not_crash_or_autofill():
    session = _session_with_case()
    case = session.case_store.get_case_at(0)
    case.input_values.update(
        {
            "odu": "ODU-A",
            "fin_type": "F&T",
            "pi": "7",
            "row": "1",
        }
    )
    controller = InputEditController(
        session,
        FakeMappingRepository({**SAMPLE_MAPPING, "cond_specs": []}),
    )

    controller.handle_cell_edited(case.case_id, "row")

    assert case.autofill_values["cond_area"] == ""
    assert case.autofill_values["cond_volume"] == ""
