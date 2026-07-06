"""Coordinate Predict input edits and mapping/autofill state updates."""

from core.mapping.autofill import build_autofill_updates

from apps.predict.mapping.mapping_repository import PredictMappingRepository
from apps.predict.schema.column_schema_adapter import column_by_key
from apps.predict.state.predict_session import PredictSession


class InputEditController:
    """Apply mapping/autofill side effects after input cell edits."""

    def __init__(
        self,
        session: PredictSession,
        mapping_repository: PredictMappingRepository | None = None,
    ) -> None:
        self._session = session
        self._mapping_repository = mapping_repository or PredictMappingRepository()
        self._dropdown_options: dict[str, tuple[str, ...]] = {}
        self._dropdown_options_by_case_id: dict[str, dict[str, tuple[str, ...]]] = {}

    @property
    def dropdown_options(self) -> dict[str, tuple[str, ...]]:
        """Return latest dependent dropdown option updates."""
        return self._dropdown_options

    def dropdown_options_for_case(self, case_id: str, key: str) -> tuple[str, ...] | None:
        """Return latest row-specific dropdown options for a column."""
        return self._dropdown_options_by_case_id.get(case_id, {}).get(key)

    def handle_cell_edited(self, case_id: str, changed_key: str) -> None:
        """Apply autofill updates after one case input cell changes."""
        case = self._session.case_store.get_case(case_id)
        mapping_data = self._mapping_repository.load()
        row_values = {**case.autofill_values, **case.input_values}
        result = build_autofill_updates(row_values, changed_key, mapping_data)

        for update in result.updates:
            target = column_by_key(update.key)
            if target.is_auto:
                case.autofill_values[update.key] = update.value
            elif target.is_input:
                case.input_values[update.key] = update.value
                case.dirty_fields.add(update.key)

        if result.updates:
            self._session.clear_result(case_id)
        self._dropdown_options.update(result.dropdown_options)
        if result.dropdown_options:
            row_options = self._dropdown_options_by_case_id.setdefault(case_id, {})
            row_options.update(result.dropdown_options)
