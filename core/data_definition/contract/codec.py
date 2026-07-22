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
    LegacyOneHotCategoryDefinition,
    LegacyOneHotGroupDefinition,
    OneHotCategoryDefinition,
    OneHotGroupDefinition,
    OneHotSelectorRestore,
    OrderingContract,
    TargetDefinition,
    UnifiedFeatureManifest,
    LegacyDerivedDefinition,
)
from core.data_definition.contract.compatibility import SUPPORTED_CONTRACT_VERSIONS


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
    if payload.get("contract_version") not in SUPPORTED_CONTRACT_VERSIONS:
        raise ValueError(f"unsupported contract_version: {payload.get('contract_version')!r}")
    return _manifest_from_payload(payload)


def _manifest_from_payload(raw: dict[str, Any]) -> UnifiedFeatureManifest:
    current_one_hot = raw["contract_version"].endswith(".v3") or any(
        "emitted_feature_identity" in category
        for group in raw["one_hot_groups"]
        for category in group["categories"]
    )
    groups = tuple(
        (OneHotGroupDefinition if current_one_hot else LegacyOneHotGroupDefinition)(
            **{
                key: value for key, value in group.items()
                if key not in {"categories", "selector_restore"}
            },
            categories=tuple(
                (OneHotCategoryDefinition if current_one_hot else LegacyOneHotCategoryDefinition)(**item)
                for item in group["categories"]
            ),
            **(
                {"selector_restore": OneHotSelectorRestore(**group["selector_restore"])
                 if group.get("selector_restore") else None}
                if current_one_hot else {}
            ),
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
        derived=tuple(
            (LegacyDerivedDefinition if raw["contract_version"].endswith(".v1") else DerivedDefinition)(**item)
            for item in raw["derived"]
        ),
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
