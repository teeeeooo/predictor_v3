"""Coordinate Predict input edits and mapping/autofill state updates."""

from core.mapping.autofill import (
    build_autofill_updates,
    build_final_dropdown_options,
)

from apps.predict.mapping.mapping_repository import PredictMappingRepository
from apps.predict.schema.column_schema_adapter import PredictColumn, build_predict_column_schema
from apps.predict.state.predict_session import PredictSession


class InputEditController:
    """Apply mapping/autofill side effects after input cell edits."""

    def __init__(
        self,
        session: PredictSession,
        mapping_repository: PredictMappingRepository | None = None,
        columns: tuple[PredictColumn, ...] | None = None,
    ) -> None:
        self._session = session
        self._mapping_repository = mapping_repository or PredictMappingRepository()
        self._columns_by_key = {
            item.key: item for item in (columns or build_predict_column_schema())
        }
        self._dropdown_options: dict[str, tuple[str, ...]] = {}
        self._dropdown_options_by_case_id: dict[str, dict[str, tuple[str, ...]]] = {}

    @property
    def dropdown_options(self) -> dict[str, tuple[str, ...]]:
        """Return latest dependent dropdown option updates."""
        return self._dropdown_options

    def dropdown_options_for_case(self, case_id: str, key: str) -> tuple[str, ...] | None:
        """Return latest row-specific dropdown options for a column."""
        return self._dropdown_options_by_case_id.get(case_id, {}).get(key)

    def handle_cell_edited(self, case_id: str, changed_key: str) -> object:
        """Apply autofill updates after one case input cell changes."""
        case = self._session.case_store.get_case(case_id)
        mapping_data = self._mapping_repository.load()
        row_values = {**case.autofill_values, **case.input_values}
        result = build_autofill_updates(row_values, changed_key, mapping_data)

        for update in result.updates:
            target = self._columns_by_key.get(update.key)
            if target is None:
                continue
            if target.is_auto:
                self._session.set_autofill_value(case_id, update.key, update.value)
            elif target.is_input:
                case.set_input_value(update.key, update.value)

        final_values = {**case.autofill_values, **case.input_values}
        self.replace_dropdown_options_for_case(
            case_id, build_final_dropdown_options(final_values, mapping_data)
        )
        return mapping_data

    def replace_dropdown_options_for_case(
        self,
        case_id: str,
        options: dict[str, tuple[str, ...]],
    ) -> None:
        """Replace, rather than merge, one row's current dependent options."""
        normalized = dict(options)
        self._dropdown_options = normalized
        self._dropdown_options_by_case_id[case_id] = normalized

    def retain_case_ids(self, case_ids: tuple[str, ...]) -> None:
        """Drop row-option projections for rows no longer in the session."""
        live = set(case_ids)
        self._dropdown_options_by_case_id = {
            case_id: options
            for case_id, options in self._dropdown_options_by_case_id.items()
            if case_id in live
        }
