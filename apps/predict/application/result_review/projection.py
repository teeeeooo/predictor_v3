"""Canonical-session-backed Result Review projection."""

from __future__ import annotations

from collections.abc import Iterable

from apps.predict.application.result_enrichment import (
    COOLING_CAPACITY_FEATURE_ID,
    HEATING_CAPACITY_FEATURE_ID,
)
from apps.predict.application.runtime_columns import PredictRuntimeColumnDescriptor
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow

from .clipboard import ResultReviewClipboardDocument
from .contracts import ResultReviewIssue, ResultReviewRow, ReviewSourceValue


IDU_FEATURE_ID = "ufm_feature_641d0e930b015b799254735eee76aa28"
EVAP_FEATURE_ID = "ufm_feature_457be1be40cb5f65853c0e03a67417b2"
ODU_FEATURE_ID = "ufm_feature_e733a4911244508cad540f34f7d4aa36"
FIN_FEATURE_ID = "ufm_feature_25b5fc89cf7e5aa8ac3e9d142d9dce2b"
PI_FEATURE_ID = "ufm_feature_457baea2de595136a14283fc22ddb629"
ROW_FEATURE_ID = "ufm_feature_b9296ee2678057bfb28734e4cabb4f6b"
COMPRESSOR_FEATURE_ID = "ufm_feature_648806b49b8e56c6b337959409e25da4"
REFRIGERANT_FEATURE_ID = "ufm_feature_dd53e21576665050a1b5172fd869aa0f"
EXPANSION_FEATURE_ID = "ufm_feature_7a39f82756d9569e841ae17505fc816b"

REFRIGERANT_QUANTITY_TARGET_ID = "ufm_target_330e4539dc7e5bb583132943914a5df5"
COOLING_FREQUENCY_TARGET_ID = "ufm_target_4e8d07df9558577a94701a10cdeabf71"
HEATING_FREQUENCY_TARGET_ID = "ufm_target_e73ce9f258985ccf8ce1d3774cc108ce"

SUMMARY_GROUPS = (
    (IDU_FEATURE_ID, EVAP_FEATURE_ID),
    (ODU_FEATURE_ID, FIN_FEATURE_ID, PI_FEATURE_ID, ROW_FEATURE_ID),
    (COMPRESSOR_FEATURE_ID,),
    (REFRIGERANT_FEATURE_ID, EXPANSION_FEATURE_ID),
)


class ResultReviewProjection:
    """Project current case order without owning a mutable result collection."""

    def __init__(
        self,
        session: PredictSession,
        descriptors: tuple[PredictRuntimeColumnDescriptor, ...],
    ) -> None:
        self._session = session
        self._descriptors = tuple(descriptors)
        self._by_identity = {item.feature_identity: item for item in descriptors}
        required = {
            COOLING_CAPACITY_FEATURE_ID,
            HEATING_CAPACITY_FEATURE_ID,
            *(identity for group in SUMMARY_GROUPS for identity in group),
        }
        missing = required.difference(self._by_identity)
        if missing:
            raise ValueError("Result Review Feature identity projection is incomplete")

    @property
    def session(self) -> PredictSession:
        """Expose the canonical read owner, not a copied result table."""
        return self._session

    def rows(self) -> tuple[ResultReviewRow, ...]:
        return tuple(
            self._project_case(ordinal, case_id)
            for ordinal, case_id in enumerate(self._session.case_order, start=1)
        )

    def selected_rows(self, case_ids: Iterable[str]) -> tuple[ResultReviewRow, ...]:
        selected = set(case_ids)
        return tuple(row for row in self.rows() if row.case_id in selected)

    def clipboard_document(
        self, case_ids: Iterable[str]
    ) -> ResultReviewClipboardDocument:
        return ResultReviewClipboardDocument(self.selected_rows(case_ids))

    def _project_case(self, ordinal: int, case_id: str) -> ResultReviewRow:
        case = self._session.case_store.get_case(case_id)
        result = self._session.result_for_case(case_id)
        targets = {item.target_identity: item for item in result.target_outcomes}
        metrics = {item.metric_key: item for item in result.derived_metrics}
        return ResultReviewRow(
            case_ordinal=ordinal,
            case_id=case_id,
            status=result.status,
            freshness=result.freshness,
            message=result.message,
            stale_reason=result.stale_reason,
            cooling_capacity=self._capacity_value(
                case, result, COOLING_CAPACITY_FEATURE_ID
            ),
            heating_capacity=self._capacity_value(
                case, result, HEATING_CAPACITY_FEATURE_ID
            ),
            specification_summary=self._summary(case),
            eer=metrics.get("eer"),
            cop=metrics.get("cop"),
            cooling_frequency=targets.get(COOLING_FREQUENCY_TARGET_ID),
            heating_frequency=targets.get(HEATING_FREQUENCY_TARGET_ID),
            refrigerant_quantity=targets.get(REFRIGERANT_QUANTITY_TARGET_ID),
            target_outcomes=result.target_outcomes,
            derived_metrics=result.derived_metrics,
            execution_context=result.execution_context,
            issues=_issues(result),
        )

    def _capacity_value(self, case, result, identity: str) -> ReviewSourceValue:  # noqa: ANN001
        descriptor = self._by_identity[identity]
        if result.execution_context is not None:
            evidence = next(
                (
                    item
                    for item in result.execution_context.capacity_inputs
                    if item.feature_identity == identity
                ),
                None,
            )
            return ReviewSourceValue(
                identity,
                descriptor.key,
                descriptor.label,
                evidence.semantic_unit if evidence is not None else "W",
                "execution_evidence",
                evidence.raw_value if evidence is not None else None,
                evidence is not None,
            )
        value = _case_value(case, descriptor.key)
        return ReviewSourceValue(
            identity,
            descriptor.key,
            descriptor.label,
            "W",
            "current_case_input",
            value,
            value is not None and str(value) != "",
        )

    def _summary(self, case) -> str:  # noqa: ANN001
        groups = []
        for identities in SUMMARY_GROUPS:
            parts = []
            for identity in identities:
                descriptor = self._by_identity[identity]
                value = _case_value(case, descriptor.key)
                rendered = "—" if value is None or str(value) == "" else str(value)
                parts.append(f"{descriptor.label}: {rendered}")
            groups.append(" + ".join(parts))
        return " · ".join(groups)


def _case_value(case, key: str):  # noqa: ANN001, ANN202
    if key in case.input_values:
        return case.input_values[key]
    return case.autofill_values.get(key)


def _issues(result: ResultRow) -> tuple[ResultReviewIssue, ...]:
    issues = []
    if result.message:
        issues.append(ResultReviewIssue("row", "", result.message))
    if result.stale_reason:
        issues.append(ResultReviewIssue("freshness", result.stale_reason, ""))
    issues.extend(
        ResultReviewIssue(
            f"target:{item.target_identity}", item.reason_code, item.message
        )
        for item in result.target_outcomes
        if item.status != "available"
    )
    issues.extend(
        ResultReviewIssue(
            f"metric:{item.metric_key}", item.reason_code, item.message
        )
        for item in result.derived_metrics
        if item.status != "available"
    )
    return tuple(issues)
