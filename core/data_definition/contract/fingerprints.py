"""Scoped semantic fingerprints for Unified Feature compatibility."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

from core.data_definition.contract.codec import manifest_payload
from core.data_definition.contract.model import UnifiedFeatureManifest
from core.data_definition.contract.projections import generate_projections
from core.data_definition.contract.compatibility import (
    current_derived_definitions,
    current_one_hot_definitions,
    operand_ml_name,
)


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
    derived_semantics: str = ""

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
    group_identity_by_key = {
        item.group_key: item.identity for item in current_one_hot_definitions(manifest)
    }
    ml_payload = [
        {
            "ml_name": row.ml_name,
            "role": row.role,
            "one_hot_group": (
                group_identity_by_key.get(row.one_hot_group, "")
                if row.role == "one_hot" else row.one_hot_group
            ),
            "zero_fill_policy": row.zero_fill_policy,
        }
        for row in projections.ml if row.active
    ]
    all_derived_payload = _derived_semantic_payload(manifest)
    active_ids = {item.identity for item in current_derived_definitions(manifest) if item.active}
    derived_payload = [
        item for item in all_derived_payload if item["identity"] in active_ids
    ]
    one_hot_payload = _one_hot_semantic_payload(manifest)
    target_by_id = {item.identity: item for item in manifest.targets}
    target_payload = {
        "presentation": [
            asdict(target_by_id[identity]) for identity in manifest.ordering.targets
        ],
        "registry": list(projections.target_registry),
    }
    mapping_payload = [asdict(item) for item in projections.mapping_requirements]
    preprocessing_payload = {"version": manifest.preprocessing_version}
    return ScopedFingerprints(
        combined=semantic_manifest_fingerprint(manifest),
        predict=_hash(predict_payload),
        ordered_ml=_hash(ml_payload),
        derived=_hash(derived_payload),
        one_hot=_hash(one_hot_payload),
        target_registry=_hash(target_payload),
        mapping_requirements=_hash(mapping_payload),
        preprocessing=_hash(preprocessing_payload),
        derived_semantics=_hash(all_derived_payload),
    )


def _derived_semantic_payload(manifest: UnifiedFeatureManifest) -> list[dict[str, object]]:
    return [
        {
            "identity": item.identity,
            "ml_name": item.ml_name,
            "operation": item.operation,
            "numerator_ml_name": operand_ml_name(manifest, item.numerator_identity),
            "denominator_ml_name": operand_ml_name(manifest, item.denominator_identity),
            "zero_value": float(item.zero_value),
            "zero_fill_policy": item.zero_fill_policy,
            "active": item.active,
        }
        for item in current_derived_definitions(manifest)
    ]


def _one_hot_semantic_payload(manifest: UnifiedFeatureManifest) -> list[dict[str, object]]:
    feature_by_id = {item.identity: item for item in manifest.features}
    payload = []
    for group in current_one_hot_definitions(manifest):
        if not group.active:
            continue
        payload.append({
            "group_identity": group.identity,
            "selector_feature_identity": group.selector_feature_identity,
            "source_mode": group.category_source,
            "source_binding": group.source_binding,
            "unknown_policy": group.unknown_policy,
            "missing_policy": group.missing_policy,
            "categories": [
                {
                    "source_value": item.source_value,
                    "emitted_feature_identity": item.emitted_feature_identity,
                    "emitted_ml_name": feature_by_id[item.emitted_feature_identity].ml_name,
                    "order": item.order,
                    "provider_category_identity": item.provider_category_identity,
                }
                for item in sorted(group.categories, key=lambda category: category.order)
                if item.active
            ],
        })
    return payload


def legacy_bundle_fingerprint_payload(manifest: UnifiedFeatureManifest) -> dict[str, str]:
    """Return pre-v3 hashes accepted only when verifying historical bundles."""
    current = scoped_fingerprints(manifest)
    projections = generate_projections(manifest)
    ml_payload = [
        {
            "ml_name": row.ml_name,
            "role": row.role,
            "one_hot_group": row.one_hot_group,
            "zero_fill_policy": row.zero_fill_policy,
        }
        for row in projections.ml if row.active
    ]
    payload = asdict(current)
    payload["ordered_ml"] = _hash(ml_payload)
    payload["one_hot"] = _hash([asdict(item) for item in projections.one_hot])
    return payload


def semantic_manifest_fingerprint(manifest: UnifiedFeatureManifest) -> str:
    """Hash the complete canonical semantic payload, excluding generation metadata."""
    semantic_manifest = manifest_payload(manifest)
    semantic_manifest.pop("generation")
    for group in semantic_manifest["one_hot_groups"]:
        if group.get("selector_restore") is None:
            group.pop("selector_restore", None)
    return _hash(semantic_manifest)


def semantic_generation_id(
    manifest: UnifiedFeatureManifest,
    *,
    prefix: str,
) -> str:
    """Return a deterministic generation name using the shared semantic hash."""
    return f"{prefix}-{semantic_manifest_fingerprint(manifest)[:20]}"


def _hash(payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
