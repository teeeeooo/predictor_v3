"""Immutable deployment export derived only from one guarded Active revision."""

from __future__ import annotations

import traceback
from pathlib import Path

from .deployment_export_outcomes import (
    DeploymentExportResult,
    deployment_export_failure,
)
from .deployment_export_publication import publish_deployment_export
from .durability_errors import LifecycleRecoveryRequiredError
from .errors import (
    ActiveReferenceCorruptionError,
    CandidateCorruptionError,
    ModelLifecycleError,
    StaleActiveRevisionError,
)
from .promotion import ModelPromotionService
from .repository import ModelLifecycleRepository

class _DeploymentExportFailure(RuntimeError):
    def __init__(self, reason_code: str, diagnostic: str) -> None:
        super().__init__(diagnostic)
        self.reason_code = reason_code
        self.diagnostic = diagnostic


class DeploymentExportService:
    """Validate, stage, verify, and publish one immutable Active export."""

    def __init__(
        self,
        repository: ModelLifecycleRepository,
        promotion: ModelPromotionService,
    ) -> None:
        self._repository = repository
        self._promotion = promotion

    def export_active(
        self,
        destination_parent: str | Path,
        *,
        expected_revision: int,
    ) -> DeploymentExportResult:
        requested_parent = Path(destination_parent)
        parent = requested_parent.resolve()
        try:
            if requested_parent.is_symlink() or not parent.is_dir():
                raise _DeploymentExportFailure(
                    "publication_filesystem_failure",
                    "Export destination must be an existing regular directory",
                )
            try:
                active = self._repository.read_active()
            except FileNotFoundError as exc:
                raise _DeploymentExportFailure(
                    "missing_active",
                    str(exc),
                ) from exc
            except LifecycleRecoveryRequiredError as exc:
                raise _DeploymentExportFailure(
                    "recovery_required",
                    str(exc),
                ) from exc
            except (ActiveReferenceCorruptionError, OSError, ModelLifecycleError) as exc:
                raise _DeploymentExportFailure(
                    "corrupt_active",
                    str(exc),
                ) from exc
            if active.revision != expected_revision:
                raise _DeploymentExportFailure(
                    "stale_active_revision",
                    "Active revision changed before export",
                )
            export_id = f"predictor-v3-{active.candidate_id}-r{active.revision}"
            target = parent / export_id
            if target.exists() or target.is_symlink():
                raise _DeploymentExportFailure(
                    "destination_conflict",
                    f"immutable export already exists: {export_id}",
                )
            with self._repository.guard_active(active.candidate_id, active.revision):
                try:
                    candidate = self._repository.read_candidate(active.candidate_id)
                except LifecycleRecoveryRequiredError as exc:
                    raise _DeploymentExportFailure(
                        "recovery_required",
                        str(exc),
                    ) from exc
                except (
                    CandidateCorruptionError,
                    FileNotFoundError,
                    OSError,
                    ModelLifecycleError,
                ) as exc:
                    raise _DeploymentExportFailure(
                        "corrupt_active",
                        str(exc),
                    ) from exc
                compatibility = self._promotion.inspect_compatibility(
                    active.candidate_id
                )
                if compatibility.status != "compatible":
                    reason_code = {
                        "recovery-required": "recovery_required",
                        "corrupt": "corrupt_active",
                        "non-promotable": "partial_non_promotable_active",
                        "incompatible": "incompatible_active",
                    }.get(compatibility.status, "internal_failure")
                    raise _DeploymentExportFailure(
                        reason_code,
                        compatibility.diagnostic_message
                        or "Active Candidate is not currently compatible",
                    )
                publish_deployment_export(
                    parent,
                    target,
                    export_id,
                    active=active,
                    candidate=candidate,
                )
            return DeploymentExportResult(
                "exported",
                export_id,
                str(target),
                active.candidate_id,
                active.revision,
                "현재 사용 모델의 immutable deployment export를 생성했습니다.",
            )
        except _DeploymentExportFailure as exc:
            return deployment_export_failure(
                exc.reason_code,
                diagnostic=exc.diagnostic,
                diagnostic_traceback=traceback.format_exc(),
            )
        except StaleActiveRevisionError as exc:
            return deployment_export_failure(
                "stale_active_revision",
                diagnostic=str(exc),
                diagnostic_traceback=traceback.format_exc(),
            )
        except LifecycleRecoveryRequiredError as exc:
            return deployment_export_failure(
                "recovery_required",
                diagnostic=str(exc),
                diagnostic_traceback=traceback.format_exc(),
            )
        except FileExistsError as exc:
            return deployment_export_failure(
                "destination_conflict",
                diagnostic=str(exc),
                diagnostic_traceback=traceback.format_exc(),
            )
        except (CandidateCorruptionError, ActiveReferenceCorruptionError) as exc:
            return deployment_export_failure(
                "corrupt_active",
                diagnostic=str(exc),
                diagnostic_traceback=traceback.format_exc(),
            )
        except OSError as exc:
            return deployment_export_failure(
                "publication_filesystem_failure",
                diagnostic=str(exc),
                diagnostic_traceback=traceback.format_exc(),
            )
        except Exception as exc:
            return deployment_export_failure(
                "internal_failure",
                diagnostic=f"{type(exc).__name__}: {str(exc)}",
                diagnostic_traceback=traceback.format_exc(),
            )
