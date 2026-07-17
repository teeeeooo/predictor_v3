"""Canonical JSON encoding for Unified Feature manifests."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from core.data_definition.contract.model import (
    ContractGeneration,
    DerivedDefinition,
    FeatureDefinition,
    MappingRequirementDefinition,
    ModelGroupDefinition,
    OneHotCategoryDefinition,
    OneHotGroupDefinition,
    OrderingContract,
    TargetDefinition,
    UnifiedFeatureManifest,
)


def manifest_payload(manifest: UnifiedFeatureManifest) -> dict[str, Any]:
    """Return the versioned structured payload used for JSON persistence."""
    return asdict(manifest)


def dump_manifest(manifest: UnifiedFeatureManifest, path: str | Path) -> None:
    """Write deterministic UTF-8 JSON; publication atomicity belongs elsewhere."""
    Path(path).write_text(
        json.dumps(manifest_payload(manifest), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

def load_manifest(path: str | Path) -> UnifiedFeatureManifest:
    """Load a canonical manifest and reject unsupported top-level versions."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("contract_version") != "unified_feature_contract.v1":
        raise ValueError(f"unsupported contract_version: {payload.get('contract_version')!r}")
    return _manifest_from_payload(payload)


def _manifest_from_payload(raw: dict[str, Any]) -> UnifiedFeatureManifest:
    groups = tuple(
        OneHotGroupDefinition(
            **{key: value for key, value in group.items() if key != "categories"},
            categories=tuple(OneHotCategoryDefinition(**item) for item in group["categories"]),
        )
        for group in raw["one_hot_groups"]
    )
    model_groups = tuple(
        ModelGroupDefinition(
            **{key: value for key, value in group.items() if key not in {"target_identities", "target_rules"}},
            target_identities=tuple(group["target_identities"]),
            target_rules=tuple(
                (item[0], item[1], tuple(item[2])) for item in group["target_rules"]
            ),
        )
        for group in raw["model_groups"]
    )
    ordering = raw["ordering"]
    return UnifiedFeatureManifest(
        contract_version=raw["contract_version"],
        generation=ContractGeneration(**raw["generation"]),
        preprocessing_version=raw["preprocessing_version"],
        features=tuple(FeatureDefinition(**item) for item in raw["features"]),
        derived=tuple(DerivedDefinition(**item) for item in raw["derived"]),
        one_hot_groups=groups,
        targets=tuple(TargetDefinition(**item) for item in raw["targets"]),
        model_groups=model_groups,
        mapping_requirements=tuple(
            MappingRequirementDefinition(**item) for item in raw["mapping_requirements"]
        ),
        ordering=OrderingContract(
            predict=tuple(ordering["predict"]),
            ml=tuple(ordering["ml"]),
            derived=tuple(ordering["derived"]),
            targets=tuple(ordering["targets"]),
        ),
    )
