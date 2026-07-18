"""Persisted Mapping vocabulary snapshot adapter for Data Definition."""

from __future__ import annotations

import hashlib
from pathlib import Path

from core.data_definition.one_hot.model import VocabularyCategory, VocabularySnapshot
from core.mapping.paths import MAPPING_JSON_FILE
from core.mapping.repository import load_mapping_data


def load_persisted_mapping_vocabulary_snapshots(
    mapping_file: str | Path = MAPPING_JSON_FILE,
) -> tuple[VocabularySnapshot, ...]:
    """Read persisted Mapping once and return immutable option-only evidence."""
    path = Path(mapping_file)
    if not path.exists():
        return ()
    payload = load_mapping_data(str(path))
    revision = hashlib.sha256(path.read_bytes()).hexdigest()
    snapshots = []
    for binding, section in sorted(payload.items()):
        if not isinstance(section, dict):
            continue
        categories = tuple(
            VocabularyCategory(
                identity=f"mapping:{binding}:{value}",
                value=str(value),
                label=str(value),
            )
            for value in section
            if str(value).strip()
        )
        snapshots.append(VocabularySnapshot(
            source_mode="mapping_backed",
            source_binding=str(binding),
            categories=categories,
            source_revision=revision,
        ))
    return tuple(snapshots)
