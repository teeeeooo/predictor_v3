"""Pure dependency evidence for restricted Derived definitions."""

from __future__ import annotations

from core.data_definition.draft import DataDefinitionDraft


def derived_downstream_identities(
    draft: DataDefinitionDraft,
    source_identity: str,
) -> tuple[str, ...]:
    """Return direct and indirect downstream Derived identities in draft order."""
    derived = tuple(item for item in draft.rows if item.source_kind == "derived_policy")
    direct = {
        item.stable_identity
        for item in derived
        if source_identity in {item.numerator_identity, item.denominator_identity}
    }
    result: set[str] = set()
    pending = list(direct)
    while pending:
        identity = pending.pop(0)
        if identity in result:
            continue
        result.add(identity)
        pending.extend(
            item.stable_identity
            for item in derived
            if identity in {item.numerator_identity, item.denominator_identity}
        )
    return tuple(item.stable_identity for item in derived if item.stable_identity in result)
