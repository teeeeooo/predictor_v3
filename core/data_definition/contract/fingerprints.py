"""Scoped semantic fingerprints for Unified Feature compatibility."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

from core.data_definition.contract.codec import manifest_payload
from core.data_definition.contract.model import UnifiedFeatureManifest
from core.data_definition.contract.projections import generate_projections


@dataclass(frozen=True)
class ScopedFingerprints:
    combined: str
    predict: str
    ordered_ml: str
    derived: str
    one_hot: str
    target_registry: str
    mapping_requirements: str
    preprocessing: str

    @property
    def model_compatibility(self) -> tuple[str, str, str, str, str]:
        return (
            self.ordered_ml,
            self.derived,
            self.one_hot,
            self.target_registry,
            self.preprocessing,
        )


def scoped_fingerprints(manifest: UnifiedFeatureManifest) -> ScopedFingerprints:
    projections = generate_projections(manifest)
    predict_payload = [
        {key: value for key, value in asdict(row).items() if key != "line_number"}
        for row in projections.predict
    ]
    ml_payload = [
        {
            "ml_name": row.ml_name,
            "role": row.role,
            "one_hot_group": row.one_hot_group,
            "zero_fill_policy": row.zero_fill_policy,
        }
        for row in projections.ml if row.active
    ]
    derived_payload = [asdict(item) for item in projections.derived]
    one_hot_payload = [asdict(item) for item in projections.one_hot]
    target_payload = list(projections.target_registry)
    mapping_payload = [asdict(item) for item in projections.mapping_requirements]
    preprocessing_payload = {"version": manifest.preprocessing_version}
    semantic_manifest = manifest_payload(manifest)
    semantic_manifest.pop("generation")
    return ScopedFingerprints(
        combined=_hash(semantic_manifest),
        predict=_hash(predict_payload),
        ordered_ml=_hash(ml_payload),
        derived=_hash(derived_payload),
        one_hot=_hash(one_hot_payload),
        target_registry=_hash(target_payload),
        mapping_requirements=_hash(mapping_payload),
        preprocessing=_hash(preprocessing_payload),
    )


def _hash(payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
