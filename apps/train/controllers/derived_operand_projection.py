"""Application-owned presentation projection for Derived operand choices."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition.derived_operand_policy import derived_operand_eligibility
from core.data_definition.draft import DataDefinitionDraft


@dataclass(frozen=True)
class DerivedOperandOption:
    identity: str
    display_name: str
    ml_name: str
    source_kind: str
    selectable: bool
    blocked_code: str = ""
    blocked_reason: str = ""


def project_derived_operand_options(
    draft: DataDefinitionDraft,
    *,
    consumer_identity: str = "",
) -> tuple[DerivedOperandOption, ...]:
    """Project every canonical candidate without duplicating domain policy."""
    features = tuple(item for item in draft.rows if item.source_kind == "schema_row")
    derived = tuple(item for item in draft.rows if item.source_kind == "derived_policy")
    consumer = next(
        (item for item in derived if item.stable_identity == consumer_identity),
        None,
    )
    target_ids = {
        item.feature_identity
        for item in getattr(draft.base_manifest, "targets", ())
    }
    options = []
    for owner in (*features, *derived):
        identity = owner.stable_identity
        if not identity:
            continue
        eligibility = derived_operand_eligibility(
            features,
            derived,
            identity,
            target_feature_identities=target_ids,
            consumer_identity=consumer_identity,
            consumer_active=bool(consumer and consumer.active),
        )
        display_name = owner.label or owner.ml_name or owner.column_key or identity
        options.append(DerivedOperandOption(
            identity=identity,
            display_name=display_name,
            ml_name=eligibility.ml_name,
            source_kind=eligibility.source_kind,
            selectable=eligibility.eligible,
            blocked_code=eligibility.code,
            blocked_reason=eligibility.reason,
        ))
    return tuple(options)
