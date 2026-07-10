"""PredictionUseCase tests without PySide/QApplication."""

from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter
from apps.predict.adapters.row_to_ml_input_adapter import RowToMlInputAdapter
from apps.predict.application.models import PredictionServiceResult
from apps.predict.application.prediction_usecase import PredictionUseCase
from apps.predict.ports.prediction_execution_port import PredictionWorkerSummary
from apps.predict.state.predict_session import PredictSession
from core.ml.features import TARGETS


def _session_with_cases(*cooling_values: str) -> PredictSession:
    session = PredictSession()
    rows = session.case_store.append_empty_rows(len(cooling_values))
    for row, value in zip(rows, cooling_values, strict=True):
        if value:
            row.set_input_value("cooling_capa", value)
    return session


def _usecase(session: PredictSession) -> PredictionUseCase:
    return PredictionUseCase(
        session,
        input_mapper=RowToMlInputAdapter(),
        result_mapper=PredictionResultAdapter(),
    )


def test_prediction_usecase_prepares_invalid_and_valid_rows_without_qt():
    session = _session_with_cases("3500", "")
    usecase = _usecase(session)
    results = []

    plan = usecase.prepare_run(list(session.case_order), results.append)

    assert plan.job is not None
    assert plan.summary.invalid == 1
    assert len(plan.job.requests) == 1
    assert session.result_for_case(session.case_order[0]).status == "running"
    assert session.result_for_case(session.case_order[1]).status == "invalid"
    assert [result.status for result in results] == ["running", "invalid"]


def test_prediction_usecase_fake_runner_e2e_without_pyside():
    session = _session_with_cases("3500", "3600")
    usecase = _usecase(session)
    plan = usecase.prepare_run(list(session.case_order))
    assert plan.job is not None

    for request in plan.job.requests:
        usecase.apply_service_result(
            PredictionServiceResult(
                case_id=request.case_id,
                status="complete",
                predictions={target: 1200.0 for target in TARGETS},
            )
        )
    summary = usecase.summary_from_worker(
        PredictionWorkerSummary(
            run_id=plan.job.run_id,
            total=len(plan.job.requests),
            complete=len(plan.job.requests),
        ),
        invalid_count=plan.summary.invalid,
    )

    assert summary.complete == 2
    assert summary.invalid == 0
    for case_id in session.case_order:
        assert session.result_for_case(case_id).status == "complete"
