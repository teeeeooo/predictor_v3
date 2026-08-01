"""Immutable artifacts and pure validation for canonical Predict result state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from apps.predict.application.result_contract import (
    PredictionExecutionContext,
    PredictionExecutionSemantics,
    PredictionModelIdentity,
)
from apps.predict.application.result_validation import (
    NON_EXECUTED_RESULT_STATUSES,
    canonical_stored_result_rejection_reason,
)
from apps.predict.application.target_outcome import PredictionTargetDescriptor
from apps.predict.state.result_row import ResultRow


@dataclass(frozen=True)
class AllowedExecution:
    context: PredictionExecutionContext
    expected_targets: tuple[PredictionTargetDescriptor, ...]


@dataclass(frozen=True)
class PredictSessionProjection:
    case_order: tuple[str, ...]
    cases: tuple[tuple[str, dict, dict, set, int], ...]
    results: tuple[ResultRow, ...]
    target_contract: tuple[PredictionTargetDescriptor, ...] = ()
    execution_semantics: PredictionExecutionSemantics | None = None
    model_identity: PredictionModelIdentity | None = None
    allowed_executions: tuple[tuple[str, AllowedExecution], ...] = ()
    session_revision: int = 0
    _authority: object | None = field(default=None, repr=False, compare=False)


@dataclass(frozen=True)
class _IssuedProjection:
    authority: object
    kind: str
    projection: PredictSessionProjection


class ResultProjectionAuthority:
    """Seal session snapshots/migrations and reject altered or foreign artifacts."""

    def __init__(self) -> None:
        self._issued: dict[int, _IssuedProjection] = {}

    def issue(
        self, projection: PredictSessionProjection, kind: str
    ) -> PredictSessionProjection:
        authority = object()
        issued = PredictSessionProjection(
            projection.case_order,
            projection.cases,
            projection.results,
            projection.target_contract,
            projection.execution_semantics,
            projection.model_identity,
            projection.allowed_executions,
            projection.session_revision,
            authority,
        )
        self._issued[id(authority)] = _IssuedProjection(
            authority, kind, copy_projection(issued)
        )
        return issued

    def validate(self, projection: PredictSessionProjection, kind: str) -> None:
        authority = projection._authority
        issued = self._issued.get(id(authority)) if authority is not None else None
        if (
            issued is None
            or issued.authority is not authority
            or issued.kind != kind
            or issued.projection != projection
        ):
            raise ValueError("runtime projection was not issued by this Predict session")

    def consume(self, projection: PredictSessionProjection) -> None:
        self._issued.pop(id(projection._authority), None)

    def release(self, projection: PredictSessionProjection, kind: str) -> bool:
        """Release an unconsumed artifact; already-consumed cleanup is idempotent."""
        authority = projection._authority
        if authority is None or id(authority) not in self._issued:
            return False
        self.validate(projection, kind)
        self.consume(projection)
        return True

    @property
    def count(self) -> int:
        return len(self._issued)


def validate_direct_result(result: ResultRow) -> None:
    if (
        result.status not in NON_EXECUTED_RESULT_STATUSES
        or result.execution_context is not None
        or result.target_outcomes
        or result._legacy_result_values
        or result.freshness != "current"
        or result.stale_reason
    ):
        raise ValueError("executed result requires canonical acceptance")


def validate_projected_results(
    projection: PredictSessionProjection,
    *,
    session_id: str,
) -> None:
    contract = tuple(projection.target_contract) or None
    case_revisions = {item[0]: item[4] for item in projection.cases}
    for result in projection.results:
        validate_stored_result(
            result,
            target_contract=contract,
            case_revisions=case_revisions,
            execution_semantics=projection.execution_semantics,
            model_identity=projection.model_identity,
            session_id=session_id,
        )
        if result.freshness == "stale" and contract is not None:
            keys_by_feature = {
                descriptor.result_feature_identity: descriptor.result_key
                for descriptor in contract
            }
            if any(
                outcome.result_feature_identity in keys_by_feature
                and outcome.result_key != keys_by_feature[outcome.result_feature_identity]
                for outcome in result.target_outcomes
            ):
                raise ValueError("invalid canonical Predict result: result_key_mismatch")


def validate_projection_structure(
    projection: PredictSessionProjection, case_order: tuple[str, ...]
) -> None:
    if projection.case_order != case_order:
        raise ValueError("Predict case structure changed after prepare")
    if tuple(item[0] for item in projection.cases) != projection.case_order:
        raise ValueError("Predict case projection order is invalid")
    result_ids = tuple(result.case_id for result in projection.results)
    if (
        len(result_ids) != len(set(result_ids))
        or not set(result_ids).issubset(projection.case_order)
    ):
        raise ValueError("Predict result projection identity is invalid")


def validate_canonical_results(
    results: Mapping[str, ResultRow],
    *,
    case_order: tuple[str, ...],
    case_revisions: Mapping[str, int],
    target_contract: tuple[PredictionTargetDescriptor, ...] | None,
    execution_semantics: PredictionExecutionSemantics | None,
    model_identity: PredictionModelIdentity | None,
    session_id: str,
) -> None:
    for case_id, result in results.items():
        if case_id != result.case_id or case_id not in case_order:
            raise ValueError("canonical Predict result identity is invalid")
        validate_stored_result(
            result,
            target_contract=target_contract,
            case_revisions=case_revisions,
            execution_semantics=execution_semantics,
            model_identity=model_identity,
            session_id=session_id,
        )


def without_case_dependencies(
    results: Mapping[str, ResultRow],
    allowed: Mapping[str, AllowedExecution],
    case_ids: tuple[str, ...],
) -> tuple[dict[str, ResultRow], dict[str, AllowedExecution]]:
    removed = set(case_ids)
    return (
        {key: value for key, value in results.items() if key not in removed},
        {key: value for key, value in allowed.items() if key not in removed},
    )


def validate_stored_result(
    result: ResultRow,
    *,
    target_contract: tuple[PredictionTargetDescriptor, ...] | None,
    case_revisions: Mapping[str, int],
    execution_semantics: PredictionExecutionSemantics | None,
    model_identity: PredictionModelIdentity | None,
    session_id: str,
) -> None:
    reason = canonical_stored_result_rejection_reason(result, target_contract)
    context = result.execution_context
    if not reason and context is not None:
        if context.session_id != session_id:
            reason = "session_mismatch"
        elif context.case_id != result.case_id:
            reason = "case_mismatch"
        elif result.freshness == "current" and (
            context.case_input_revision != case_revisions[result.case_id]
        ):
            reason = "input_revision_changed"
        elif result.freshness == "current" and (
            execution_semantics is None
            or context.semantics.currentness_key
            != execution_semantics.currentness_key
        ):
            reason = "execution_semantics_changed"
        elif result.freshness == "current" and context.model != model_identity:
            reason = "loaded_model_changed"
    if reason:
        raise ValueError(f"invalid canonical Predict result: {reason}")


def validate_migration_relation(
    source: Mapping[str, ResultRow],
    destination_results: tuple[ResultRow, ...],
) -> None:
    destination = {result.case_id: result for result in destination_results}
    if set(source) != set(destination):
        raise ValueError("Predict result migration cannot add or remove rows")
    for case_id, before in source.items():
        if not _is_valid_result_migration(before, destination[case_id]):
            raise ValueError("Predict result migration changed execution evidence")


def copy_result(result: ResultRow) -> ResultRow:
    return ResultRow(
        result.case_id,
        result.status,
        dict(result._legacy_result_values),
        result.message,
        target_outcomes=result.target_outcomes,
        execution_context=result.execution_context,
        freshness=result.freshness,
        stale_reason=result.stale_reason,
    )


def copy_projection(projection: PredictSessionProjection) -> PredictSessionProjection:
    return PredictSessionProjection(
        tuple(projection.case_order),
        tuple(
            (case_id, dict(inputs), dict(autofill), set(dirty), input_revision)
            for case_id, inputs, autofill, dirty, input_revision in projection.cases
        ),
        tuple(copy_result(result) for result in projection.results),
        tuple(projection.target_contract),
        projection.execution_semantics,
        projection.model_identity,
        tuple(projection.allowed_executions),
        projection.session_revision,
        projection._authority,
    )


def _is_valid_result_migration(before: ResultRow, after: ResultRow) -> bool:
    if (
        before.case_id != after.case_id
        or before.status != after.status
        or before.message != after.message
        or before.execution_context != after.execution_context
        or before._legacy_result_values != after._legacy_result_values
        or len(before.target_outcomes) != len(after.target_outcomes)
    ):
        return False
    if before.freshness == "stale" and after.freshness != "stale":
        return False
    if before.freshness == "current" and after.freshness == "stale":
        if after.stale_reason != "execution_semantics_changed":
            return False
    elif (before.freshness, before.stale_reason) != (
        after.freshness,
        after.stale_reason,
    ):
        return False
    return all(
        (
            source.target_identity,
            source.result_feature_identity,
            source.canonical_unit,
            source.status,
            source.value_source,
            source.raw_value,
            source.reason_code,
            source.message,
        )
        == (
            destination.target_identity,
            destination.result_feature_identity,
            destination.canonical_unit,
            destination.status,
            destination.value_source,
            destination.raw_value,
            destination.reason_code,
            destination.message,
        )
        for source, destination in zip(
            before.target_outcomes, after.target_outcomes, strict=True
        )
    )
