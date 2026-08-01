"""Test-owned Predict result setup through the runtime projection boundary."""

from dataclasses import replace

from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow


def install_projection_results(
    session: PredictSession,
    *results: ResultRow,
) -> None:
    """Install display/migration fixtures without exposing a production backdoor."""
    projection = session.snapshot_runtime_projection()
    by_case = {result.case_id: result for result in projection.results}
    by_case.update((result.case_id, result) for result in results)
    session.restore_runtime_projection(
        replace(
            projection,
            results=tuple(
                by_case[case_id]
                for case_id in projection.case_order
                if case_id in by_case
            ),
        )
    )
