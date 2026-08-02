"""Shared construction for Case-scoped Predict Target tests."""

from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter
from apps.predict.adapters.row_to_ml_input_adapter import RowToMlInputAdapter
from apps.predict.application.prediction_usecase import PredictionUseCase
from apps.predict.application.result_contract import (
    PredictionModelIdentity,
    execution_semantics_from_runtime,
)
from apps.predict.application.runtime_snapshot import (
    compatibility_predict_runtime_snapshot,
)
from apps.predict.schema.column_schema_adapter import (
    build_predict_column_schema,
    build_result_column_schema,
)
from apps.predict.state.predict_session import PredictSession


TARGET_MATRIX = (
    (3500, 4200, ("Cooling Power", "Heating Power", "Ref Qty", "Cooling Hz", "Heating Hz")),
    (3500, "", ("Cooling Power", "Ref Qty", "Cooling Hz")),
    ("", 4200, ("Heating Power", "Ref Qty", "Heating Hz")),
    ("", "", ("Ref Qty",)),
)


def build_stack(count: int = 1, *, request_validator=None):  # noqa: ANN001, ANN202
    runtime = compatibility_predict_runtime_snapshot()
    columns = build_predict_column_schema(runtime.column_descriptors)
    input_columns = tuple(item for item in columns if item.group in {"input", "auto"})
    session = PredictSession()
    session.case_store.append_empty_rows(count)
    input_mapper = RowToMlInputAdapter(
        columns=input_columns,
        one_hot_snapshot=runtime.one_hot,
        target_descriptors=runtime.target_descriptors,
    )
    result_mapper = PredictionResultAdapter(
        build_result_column_schema(runtime.column_descriptors),
        input_columns=input_columns,
        active_targets=runtime.active_targets,
        target_result_keys=runtime.target_result_keys,
        target_descriptors=runtime.target_descriptors,
        generation_id=runtime.generation_id,
    )
    model = PredictionModelIdentity("applicability-model", 1, runtime.generation_id)
    usecase = PredictionUseCase(
        session,
        input_mapper,
        result_mapper,
        execution_semantics_from_runtime(runtime),
        model,
        request_validator=request_validator,
    )
    return runtime, session, input_mapper, result_mapper, usecase, model


def fill_case(case, cooling, heating, *, ref_type="R32"):  # noqa: ANN001, ANN202
    if cooling != "":
        case.set_input_value("cooling_capa", cooling)
    if heating != "":
        case.set_input_value("heating_capa", heating)
    if ref_type:
        case.set_input_value("ref_type", ref_type)


def prediction_values(request, *, omit=()):  # noqa: ANN001, ANN202
    omitted = set(omit)
    return {
        descriptor.ml_name: float(index + 10)
        for index, descriptor in enumerate(request.requested_targets)
        if descriptor.ml_name not in omitted
    }
