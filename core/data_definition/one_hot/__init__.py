"""Canonical One-hot authoring and runtime contracts."""

from core.data_definition.one_hot.model import (
    OneHotDriftEvidence,
    VocabularyCategory,
    VocabularySnapshot,
)
from core.data_definition.one_hot.runtime import (
    OneHotEncodingResult,
    OneHotRuntimeCategory,
    OneHotRuntimeGroup,
    OneHotRuntimeSnapshot,
    encode_one_hot_values,
    one_hot_runtime_snapshot,
)

__all__ = [
    "OneHotDriftEvidence",
    "OneHotEncodingResult",
    "OneHotRuntimeCategory",
    "OneHotRuntimeGroup",
    "OneHotRuntimeSnapshot",
    "VocabularyCategory",
    "VocabularySnapshot",
    "encode_one_hot_values",
    "one_hot_runtime_snapshot",
]
