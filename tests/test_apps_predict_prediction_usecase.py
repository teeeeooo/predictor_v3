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


def test_prediction_usecase_keeps_multiple_row_errors_distinct_and_retries_after_edit():
    session = _session_with_cases("bad", "")
    usecase = _usecase(session)
    first, second = session.case_order

    initial = usecase.prepare_run([first, second])

    assert initial.job is None
    assert initial.summary.invalid == 2
    assert session.result_for_case(first).message == "냉방능력: 숫자로 입력해 주세요."
    assert session.result_for_case(second).message == "냉방능력: 필수 입력값입니다."
    assert "cooling_capa" not in session.result_for_case(first).message
    assert "cooling_capa" not in session.result_for_case(second).message

    session.case_store.get_case(first).set_input_value("cooling_capa", "3500")
    session.case_store.get_case(second).set_input_value("cooling_capa", "3600")
    retried = usecase.prepare_run([first, second])

    assert retried.job is not None
    assert retried.summary.invalid == 0
    assert len(retried.job.requests) == 2
    assert session.result_for_case(first).status == "running"
    assert session.result_for_case(second).status == "running"


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
                context=request.context,
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


def test_prediction_usecase_terminalizes_only_running_rows_after_infrastructure_failure():
    session = _session_with_cases("3500", "3600", "")
    usecase = _usecase(session)
    plan = usecase.prepare_run(list(session.case_order))
    assert plan.job is not None
    first, second, third = session.case_order
    usecase.apply_service_result(
        PredictionServiceResult(
            case_id=first,
            status="complete",
            predictions={target: 1200.0 for target in TARGETS},
            context=plan.job.requests[0].context,
        )
    )
    results = []

    summary = usecase.apply_infrastructure_failure(
        session.case_order,
        "Prediction worker failed: infrastructure exploded",
        results.append,
    )

    assert session.result_for_case(first).status == "complete"
    assert session.result_for_case(second).status == "error"
    assert session.result_for_case(third).status == "invalid"
    assert [result.case_id for result in results] == [second]
    assert (summary.total, summary.complete, summary.error, summary.invalid) == (3, 1, 1, 1)
