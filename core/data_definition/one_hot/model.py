"""Immutable vocabulary evidence supplied by application adapters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VocabularyCategory:
    """One provider-owned category identity/value pair."""

    identity: str
    value: str
    label: str = ""


@dataclass(frozen=True)
class VocabularySnapshot:
    """One immutable persisted/provider vocabulary observation."""

    source_mode: str
    source_binding: str
    categories: tuple[VocabularyCategory, ...]
    available: bool = True
    unavailable_reason: str = ""
    source_revision: str = ""

    def category_by_identity(self, identity: str) -> VocabularyCategory | None:
        return next((item for item in self.categories if item.identity == identity), None)

    def category_by_value(self, value: str) -> VocabularyCategory | None:
        return next((item for item in self.categories if item.value == value), None)


@dataclass(frozen=True)
class OneHotDriftEvidence:
    """Actionable mismatch between canonical rules and an observed vocabulary."""

    code: str
    source_binding: str
    source_value: str
    category_identity: str = ""
    emitted_feature_identity: str = ""
    emitted_ml_name: str = ""
    provider_category_identity: str = ""
    blocking: bool = False
    resolution: str = ""


def vocabulary_snapshot_for(
    snapshots: tuple[VocabularySnapshot, ...],
    source_mode: str,
    source_binding: str,
) -> VocabularySnapshot | None:
    """Resolve one exact immutable source observation."""
    matches = tuple(
        item for item in snapshots
        if item.source_mode == source_mode and item.source_binding == source_binding
    )
    return matches[0] if len(matches) == 1 else None
