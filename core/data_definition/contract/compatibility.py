"""Versioned Derived compatibility decoding without mutating history."""

from __future__ import annotations

from dataclasses import replace

from core.data_definition.contract.model import (
    DerivedDefinition,
    LegacyDerivedDefinition,
    UnifiedFeatureManifest,
)

CURRENT_CONTRACT_VERSION = "unified_feature_contract.v2"
LEGACY_CONTRACT_VERSION = "unified_feature_contract.v1"
SUPPORTED_CONTRACT_VERSIONS = frozenset({LEGACY_CONTRACT_VERSION, CURRENT_CONTRACT_VERSION})


def current_derived_definitions(
    manifest: UnifiedFeatureManifest,
) -> tuple[DerivedDefinition, ...]:
    """Return identity operands, rejecting missing or ambiguous legacy names."""
    if manifest.contract_version == CURRENT_CONTRACT_VERSION:
        return tuple(_require_current(item) for item in manifest.derived)
    if manifest.contract_version != LEGACY_CONTRACT_VERSION:
        raise ValueError(f"unsupported contract_version: {manifest.contract_version!r}")
    by_name: dict[str, list[str]] = {}
    for item in (*manifest.features, *manifest.derived):
        if item.ml_name:
            by_name.setdefault(item.ml_name, []).append(item.identity)
    resolved: list[DerivedDefinition] = []
    for item in manifest.derived:
        if not isinstance(item, LegacyDerivedDefinition):
            raise ValueError("v1 manifest contains a non-legacy Derived DTO")
        numerator = _resolve_legacy_name(item, "numerator", item.numerator_ml_name, by_name)
        denominator = _resolve_legacy_name(
            item, "denominator", item.denominator_ml_name, by_name
        )
        resolved.append(DerivedDefinition(
            identity=item.identity,
            ml_name=item.ml_name,
            operation=item.operation,
            numerator_identity=numerator,
            denominator_identity=denominator,
            zero_denominator_policy="constant",
            zero_value=float(item.zero_value),
            zero_fill_policy=item.zero_fill_policy,
            active=item.active,
        ))
    return tuple(resolved)


def migrate_manifest(manifest: UnifiedFeatureManifest) -> UnifiedFeatureManifest:
    """Return an in-memory v2 candidate; never writes the source generation."""
    if manifest.contract_version == CURRENT_CONTRACT_VERSION:
        current_derived_definitions(manifest)
        return manifest
    return replace(
        manifest,
        contract_version=CURRENT_CONTRACT_VERSION,
        derived=current_derived_definitions(manifest),
    )


def operand_ml_name(
    manifest: UnifiedFeatureManifest,
    identity: str,
) -> str:
    owners = [
        item.ml_name
        for item in (*manifest.features, *current_derived_definitions(manifest))
        if item.identity == identity
    ]
    if len(owners) != 1 or not owners[0]:
        raise ValueError(f"Derived operand identity must resolve exactly once: {identity}")
    return owners[0]


def _resolve_legacy_name(item, role: str, name: str, by_name) -> str:  # noqa: ANN001
    matches = by_name.get(name, ())
    if len(matches) != 1:
        reason = "missing" if not matches else "ambiguous"
        raise ValueError(
            f"legacy Derived {item.ml_name} {role} {name!r} is {reason}; "
            "resolve it to exactly one Feature or Derived identity"
        )
    return matches[0]


def _require_current(item) -> DerivedDefinition:  # noqa: ANN001
    if not isinstance(item, DerivedDefinition):
        raise ValueError("v2 manifest contains a legacy Derived DTO")
    return item
