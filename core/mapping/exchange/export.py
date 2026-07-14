"""Atomic exchange-package export for the Data Mapping draft."""

from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from core.mapping.editor_model import MappingEditorDraft, MappingEditorGroup
from core.mapping.entity_model import MappingValidationError
from core.mapping.exchange.contract import (
    CANONICAL_GROUP_FILENAMES,
    CANONICAL_GROUP_KEYS,
    serialize_bundle_csv,
    serialize_group_csv,
)


@dataclass(frozen=True)
class MappingExchangeExportPlan:
    """Read-only destination and validation plan for one exchange export."""

    success: bool
    bundle_path: Path
    group_paths: tuple[Path, ...] = ()
    existing_paths: tuple[Path, ...] = ()
    issues: tuple[MappingValidationError, ...] = ()
    message: str = ""


@dataclass(frozen=True)
class MappingExchangeExportResult:
    """Outcome of one atomic exchange-package export."""

    success: bool
    bundle_path: Path
    group_paths: tuple[Path, ...] = ()
    existing_paths: tuple[Path, ...] = ()
    issues: tuple[MappingValidationError, ...] = ()
    message: str = ""


@dataclass(frozen=True)
class _ExchangeTarget:
    final_path: Path
    existing_path: Path | None


def plan_mapping_exchange_export(
    draft: MappingEditorDraft,
    destination: str | Path,
    validation_errors: tuple[MappingValidationError, ...] = (),
) -> MappingExchangeExportPlan:
    """Validate a draft and calculate all eight output targets without writing."""
    bundle_path = _normalized_bundle_path(destination)
    groups, structural_issues = _validated_groups(draft)
    issues = [issue for issue in validation_errors if issue.severity == "error"]
    issues.extend(structural_issues)
    if bundle_path.name.casefold() in {name.casefold() for name in CANONICAL_GROUP_FILENAMES}:
        issues.append(
            _exchange_issue(
                "exchange_bundle_name_reserved",
                "Bundle filename conflicts with a canonical group CSV filename.",
                field=bundle_path.name,
            )
        )

    group_paths = tuple(bundle_path.parent / filename for filename in CANONICAL_GROUP_FILENAMES)
    targets = tuple(
        _target_for_path(path)
        for path in (*group_paths, bundle_path)
    )
    existing_paths = tuple(
        target.existing_path
        for target in targets
        if target.existing_path is not None
    )
    if any(target.existing_path is not None and target.existing_path.is_dir() for target in targets):
        issues.append(
            _exchange_issue(
                "exchange_target_not_file",
                "An exchange output target is an existing directory and cannot be replaced.",
                field="destination",
            )
        )
    if any(
        len(_casefold_matches(target.final_path.parent, target.final_path.name)) > 1
        for target in targets
    ):
        issues.append(
            _exchange_issue(
                "exchange_existing_collision",
                "Multiple existing files match an exchange target without case sensitivity.",
                field="destination",
            )
        )
    if _has_casefold_duplicate_targets(targets):
        issues.append(
            _exchange_issue(
                "exchange_target_collision",
                "Exchange output targets collide on a case-insensitive filesystem.",
                field="destination",
            )
        )
    message = "" if issues else "Exchange package targets are ready."
    return MappingExchangeExportPlan(
        success=not issues,
        bundle_path=bundle_path,
        group_paths=group_paths,
        existing_paths=existing_paths,
        issues=tuple(issues),
        message=message,
    )


def exchange_draft_structure_issues(
    draft: MappingEditorDraft,
) -> tuple[MappingValidationError, ...]:
    """Return exchange-specific structure blockers without destination checks."""
    _groups, issues = _validated_groups(draft)
    return issues


def export_mapping_exchange(
    draft: MappingEditorDraft,
    destination: str | Path,
    validation_errors: tuple[MappingValidationError, ...] = (),
) -> MappingExchangeExportResult:
    """Write and publish the seven group CSVs plus one bundle atomically."""
    plan = plan_mapping_exchange_export(draft, destination, validation_errors)
    if not plan.success:
        return MappingExchangeExportResult(
            success=False,
            bundle_path=plan.bundle_path,
            group_paths=plan.group_paths,
            existing_paths=plan.existing_paths,
            issues=plan.issues,
            message="Exchange export blocked: resolve the listed issues first.",
        )

    groups = {group.group_key: group for group in draft.groups}
    targets = tuple(
        _target_for_path(path)
        for path in (*plan.group_paths, plan.bundle_path)
    )
    staging_dir: Path | None = None
    try:
        plan.bundle_path.parent.mkdir(parents=True, exist_ok=True)
        staging_dir = Path(
            tempfile.mkdtemp(
                prefix=f".{plan.bundle_path.stem}.exchange-",
                dir=str(plan.bundle_path.parent),
            )
        )
        staged_payloads = [
            (group_key, serialize_group_csv(groups[group_key]))
            for group_key in CANONICAL_GROUP_KEYS
        ]
        staged_payloads.append(("bundle", serialize_bundle_csv(draft)))
        staged_paths: list[Path] = []
        for index, (_label, payload) in enumerate(staged_payloads):
            staged_path = staging_dir / f"{index}.csv"
            _write_staged_file(staged_path, payload)
            if staged_path.read_bytes() != payload:
                raise OSError(f"staged exchange file verification failed: {staged_path.name}")
            staged_paths.append(staged_path)
        _publish_package(staged_paths, targets, staging_dir / "backups")
    except Exception as exc:
        return MappingExchangeExportResult(
            success=False,
            bundle_path=plan.bundle_path,
            group_paths=plan.group_paths,
            existing_paths=plan.existing_paths,
            message=f"Exchange export failed: {exc}",
        )
    finally:
        if staging_dir is not None:
            shutil.rmtree(staging_dir, ignore_errors=True)
    return MappingExchangeExportResult(
        success=True,
        bundle_path=plan.bundle_path,
        group_paths=plan.group_paths,
        existing_paths=plan.existing_paths,
        message=(
            f"Exported mapping exchange package to {plan.bundle_path.parent} "
            f"with {len(plan.group_paths)} group CSV files and bundle {plan.bundle_path.name}."
        ),
    )


def _validated_groups(
    draft: MappingEditorDraft,
) -> tuple[dict[str, MappingEditorGroup], tuple[MappingValidationError, ...]]:
    groups: dict[str, MappingEditorGroup] = {}
    issues: list[MappingValidationError] = []
    for group in draft.groups:
        if group.group_key in groups:
            issues.append(
                _exchange_issue(
                    "exchange_duplicate_group",
                    f"Exchange draft contains duplicate group '{group.group_key}'.",
                    group=group.group_key,
                )
            )
        groups[group.group_key] = group
        if len(set(group.columns)) != len(group.columns):
            issues.append(
                _exchange_issue(
                    "exchange_duplicate_header",
                    "Exchange group contains duplicate visible columns.",
                    group=group.group_key,
                )
            )
    for group_key in CANONICAL_GROUP_KEYS:
        if group_key not in groups:
            issues.append(
                _exchange_issue(
                    "exchange_group_missing",
                    f"Required exchange group '{group_key}' is missing.",
                    group=group_key,
                )
            )
    for group_key in groups:
        if group_key not in CANONICAL_GROUP_KEYS:
            issues.append(
                _exchange_issue(
                    "exchange_group_unknown",
                    f"Unknown exchange group '{group_key}'.",
                    group=group_key,
                )
            )
    return groups, tuple(issues)


def _normalized_bundle_path(destination: str | Path) -> Path:
    path = Path(destination).expanduser()
    if not path.suffix:
        path = path.with_name(f"{path.name}.csv")
    return path


def _target_for_path(path: Path) -> _ExchangeTarget:
    matches = _casefold_matches(path.parent, path.name)
    if len(matches) > 1:
        return _ExchangeTarget(path, matches[0])
    return _ExchangeTarget(path, matches[0] if matches else None)


def _casefold_matches(parent: Path, name: str) -> tuple[Path, ...]:
    if not parent.is_dir():
        return ()
    try:
        return tuple(entry for entry in parent.iterdir() if entry.name.casefold() == name.casefold())
    except OSError:
        return ()


def _has_casefold_duplicate_targets(targets: tuple[_ExchangeTarget, ...]) -> bool:
    names = [str(target.final_path).casefold() for target in targets]
    return len(set(names)) != len(names)


def _write_staged_file(path: Path, payload: bytes) -> None:
    with path.open("wb") as output:
        output.write(payload)
        output.flush()
        os.fsync(output.fileno())


def _publish_package(
    staged_paths: list[Path],
    targets: tuple[_ExchangeTarget, ...],
    backup_dir: Path,
) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    backups: dict[int, Path] = {}
    for index, target in enumerate(targets):
        if target.existing_path is None:
            continue
        backup = backup_dir / f"{index}.bak"
        shutil.copy2(target.existing_path, backup, follow_symlinks=False)
        backups[index] = backup
    try:
        for staged, target in zip(staged_paths, targets):
            os.replace(staged, target.final_path)
        for target in targets:
            if (
                target.existing_path is not None
                and target.existing_path != target.final_path
                and not _paths_refer_to_same_file(target.existing_path, target.final_path)
            ):
                target.existing_path.unlink()
    except Exception:
        _rollback_package(targets, backups)
        raise


def _rollback_package(
    targets: tuple[_ExchangeTarget, ...],
    backups: dict[int, Path],
) -> None:
    for index, target in enumerate(targets):
        backup = backups.get(index)
        try:
            if backup is not None and backup.is_file():
                _unlink_file(target.final_path)
                if target.existing_path is not None:
                    os.replace(backup, target.existing_path)
            elif target.existing_path is None:
                _unlink_file(target.final_path)
        except OSError:
            continue


def _unlink_file(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()


def _paths_refer_to_same_file(left: Path, right: Path) -> bool:
    try:
        return os.path.samefile(left, right)
    except OSError:
        return False


def _exchange_issue(
    code: str,
    message: str,
    *,
    group: str = "",
    field: str = "",
) -> MappingValidationError:
    return MappingValidationError(
        code=code,
        message=message,
        entity_key=group,
        attribute_key=field,
        field=field,
    )
