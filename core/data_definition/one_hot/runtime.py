"""Pure immutable One-hot runtime projection and encoding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any

from core.data_definition.contract.compatibility import current_one_hot_definitions
from core.data_definition.contract.model import UnifiedFeatureManifest


@dataclass(frozen=True)
class OneHotRuntimeCategory:
    category_identity: str
    source_value: str
    emitted_feature_identity: str
    emitted_ml_name: str
    order: int
    provider_category_identity: str = ""


@dataclass(frozen=True)
class OneHotRuntimeGroup:
    group_identity: str
    group_key: str
    selector_feature_identity: str
    selector_column_key: str
    source_mode: str
    source_binding: str
    categories: tuple[OneHotRuntimeCategory, ...]
    unknown_policy: str
    missing_policy: str


@dataclass(frozen=True)
class OneHotRuntimeSnapshot:
    generation_id: str
    groups: tuple[OneHotRuntimeGroup, ...]


@dataclass(frozen=True)
class OneHotEncodingResult:
    values: tuple[tuple[str, float], ...]
    warnings: tuple[str, ...] = ()


def one_hot_runtime_snapshot(manifest: UnifiedFeatureManifest) -> OneHotRuntimeSnapshot:
    """Project active runtime rules using stable selector/emitted identities."""
    feature_by_id = {item.identity: item for item in manifest.features}
    groups = []
    for group in current_one_hot_definitions(manifest):
        if not group.active:
            continue
        selector = feature_by_id.get(group.selector_feature_identity)
        if selector is None:
            raise ValueError(f"One-hot selector identity is missing: {group.selector_feature_identity}")
        categories = []
        for category in sorted(group.categories, key=lambda item: item.order):
            if not category.active:
                continue
            emitted = feature_by_id.get(category.emitted_feature_identity)
            if emitted is None or not emitted.ml_name:
                raise ValueError(
                    f"One-hot emitted Feature identity is missing: {category.emitted_feature_identity}"
                )
            categories.append(OneHotRuntimeCategory(
                category_identity=category.identity,
                source_value=category.source_value,
                emitted_feature_identity=emitted.identity,
                emitted_ml_name=emitted.ml_name,
                order=category.order,
                provider_category_identity=category.provider_category_identity,
            ))
        groups.append(OneHotRuntimeGroup(
            group_identity=group.identity,
            group_key=group.group_key,
            selector_feature_identity=selector.identity,
            selector_column_key=selector.column_key,
            source_mode=group.category_source,
            source_binding=group.source_binding,
            categories=tuple(categories),
            unknown_policy=group.unknown_policy,
            missing_policy=group.missing_policy,
        ))
    return OneHotRuntimeSnapshot(manifest.generation.generation_id, tuple(groups))


def encode_one_hot_values(
    snapshot: OneHotRuntimeSnapshot,
    selector_values: Mapping[str, Any],
) -> OneHotEncodingResult:
    """Encode selector values without mutating the input mapping."""
    encoded: list[tuple[str, float]] = []
    warnings: list[str] = []
    for group in snapshot.groups:
        positions: dict[str, int] = {}
        for category in group.categories:
            if category.source_value in positions:
                raise ValueError(
                    f"duplicate One-hot source value reached runtime: {group.group_key}"
                )
            positions[category.source_value] = len(encoded)
            encoded.append((category.emitted_ml_name, 0.0))
        raw_value = selector_values.get(group.selector_column_key)
        if _is_blank(raw_value):
            if group.missing_policy != "all_zero":
                raise ValueError(f"unsupported One-hot missing policy: {group.missing_policy}")
            continue
        selected = str(raw_value).strip()
        position = positions.get(selected)
        if position is not None:
            name, _value = encoded[position]
            encoded[position] = (name, 1.0)
            continue
        if group.unknown_policy != "warn_all_zero":
            raise ValueError(f"unsupported One-hot unknown policy: {group.unknown_policy}")
        warnings.append(f"Unsupported option ignored: {selected}")
    return OneHotEncodingResult(tuple(encoded), tuple(warnings))


def _is_blank(value: Any) -> bool:
    return value is None or str(value).strip() == ""
