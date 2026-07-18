"""Current-composition adapter from canonical manifest to the shared evaluator."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from core.data_definition.contract import load_manifest
from core.data_definition.derived.evaluator import (
    DerivedEvaluationSnapshot,
    evaluation_snapshot,
)

_REPOSITORY_MANIFEST = (
    Path(__file__).resolve().parents[2] / "config" / "data_definition" / "manifest.json"
)


@lru_cache(maxsize=1)
def current_derived_evaluation_snapshot() -> DerivedEvaluationSnapshot:
    """Adapt the current repository composition until Phase 4H runtime cutover."""
    return evaluation_snapshot(load_manifest(_REPOSITORY_MANIFEST))
