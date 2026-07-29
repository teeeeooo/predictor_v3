"""Versioned machine-readable headless Experiment interface."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from apps.common.model_lifecycle import (
    ModelLifecycleRepository,
    default_model_lifecycle_root,
)
from apps.train.application.experiments.campaign import CampaignApplicationService
from apps.train.application.experiments.agent_campaign import AgentCampaignApplicationService
from apps.train.application.experiments.agent_contracts import AGENT_CAMPAIGN_VERSION
from apps.train.application.experiments.contracts import (
    ExperimentContractError,
    load_specification,
    resolve_specification,
)
from apps.train.application.experiments.execution_lock import (
    execution_lock_is_held,
    read_lock_metadata,
)
from apps.train.application.experiments.store import ExperimentStore
from apps.train.composition.experiments import build_headless_experiment_service

from .command_contract import (
    EXIT_INTERNAL,
    EXIT_LOCK_CONFLICT,
    EXIT_SUCCESS,
    EXIT_TRAINING_FAILURE,
    EXIT_VALIDATION,
    campaign_exit,
    emit,
    json_diagnostics,
    parser,
    require_campaign_version,
    require_run_version,
    run_exit,
)
from .agent_commands import dispatch_agent_mutation, dispatch_agent_read
from .closeout_commands import dispatch_closeout


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return _dispatch(args)
    except ExperimentContractError as exc:
        emit(args.command, "validation_failure", str(exc), {"code": exc.code})
        return EXIT_VALIDATION
    except (FileNotFoundError, PermissionError, ValueError) as exc:
        emit(
            args.command,
            "validation_failure",
            "Requested owned record is unavailable or invalid.",
            {"type": type(exc).__name__, "detail": str(exc)},
        )
        return EXIT_VALIDATION
    except Exception as exc:
        emit(
            args.command,
            "internal_failure",
            "The headless interface failed internally.",
            {"type": type(exc).__name__, "detail": str(exc)},
        )
        return EXIT_INTERNAL


def _dispatch(args: argparse.Namespace) -> int:
    lifecycle_root = default_model_lifecycle_root()
    closeout = dispatch_closeout(args, lifecycle_root)
    if closeout is not None:
        return closeout
    agent_read = dispatch_agent_read(args, lifecycle_root)
    if agent_read is not None:
        return agent_read
    if args.command in {"run-status", "run-result", "run-logs", "run-artifacts"}:
        record = ExperimentStore(lifecycle_root).read_run(args.run_id)
        require_run_version(record)
        data = record
        if args.command == "run-logs":
            result = record.get("result") or {}
            data = {
                "run_id": record["run_id"],
                "log_reference": result.get("log_reference"),
                "evidence_reference": result.get("evidence_reference"),
                "events": list(
                    ExperimentStore(lifecycle_root).read_run_events(args.run_id)
                ),
            }
        elif args.command == "run-artifacts":
            data = _run_artifacts(lifecycle_root, record)
        emit(args.command, record["status"], "Run record loaded.", data=data)
        return EXIT_SUCCESS
    if args.command == "campaign-status":
        record = ExperimentStore(lifecycle_root).read_campaign(args.campaign_id)
        require_campaign_version(record)
        emit(args.command, record["status"], "Campaign record loaded.", data=record)
        return EXIT_SUCCESS
    if args.command in {"campaign-pause", "campaign-cancel"}:
        store = ExperimentStore(lifecycle_root)
        record = store.read_campaign(args.campaign_id)
        require_campaign_version(record)
        action = args.command.rsplit("-", 1)[1]
        store.request_control(args.campaign_id, action)
        emit(args.command, "accepted", f"Campaign {action} requested.", data=record)
        return EXIT_SUCCESS
    if args.command == "lock-status":
        lock_path = lifecycle_root / ".training-execution.lock"
        metadata = {
            **read_lock_metadata(lock_path),
            "held": execution_lock_is_held(lock_path),
        }
        emit(args.command, "success", "Execution lock diagnostics loaded.", data=metadata)
        return EXIT_SUCCESS
    if args.command == "models":
        return _models(args, lifecycle_root)

    specification = None
    resolved = None
    if args.command in {"validate", "resolve", "run", "campaign-start"}:
        specification = load_specification(args.specification)
        resolved = resolve_specification(specification)
    if args.command == "validate":
        assert resolved is not None
        emit(
            args.command,
            "success",
            "Experiment specification is valid.",
            data={
                "fingerprint": resolved.fingerprint,
                "resolved_specification": resolved.payload,
            },
        )
        return EXIT_SUCCESS

    campaign_id = getattr(args, "campaign_id", "") or ""
    service = build_headless_experiment_service(
        lifecycle_root=lifecycle_root,
        campaign_id=campaign_id,
    )
    agent_mutation = dispatch_agent_mutation(args, service)
    if agent_mutation is not None:
        return agent_mutation
    if args.command == "resolve":
        assert specification is not None
        resolved = service.resolve_current(specification)
        emit(
            args.command,
            "success",
            "Experiment specification is valid.",
            data={
                "fingerprint": resolved.fingerprint,
                "resolved_specification": resolved.payload,
            },
        )
        return EXIT_SUCCESS
    if args.command == "run":
        assert resolved is not None
        run_id = args.run_id or f"run-{uuid4().hex}"
        result = service.run(
            resolved,
            run_id=run_id,
            execution_owner="headless-single",
        )
        if result is not None and result.status == "lock_conflict":
            emit(
                args.command,
                "lock_conflict",
                result.message,
                diagnostics=json_diagnostics(result.summary),
                data={"run_id": run_id},
            )
            return EXIT_LOCK_CONFLICT
        if result is not None:
            emit(
                args.command,
                "training_failure",
                result.message or "Training preflight failed.",
                data={"run_id": run_id, "result_status": result.status},
            )
            return EXIT_TRAINING_FAILURE
        record = service.inspect_run(run_id)
        emit(args.command, record["status"], "Experiment run finished.", data=record)
        return run_exit(record["status"])
    if args.command == "campaign-start":
        assert specification is not None
        record = CampaignApplicationService(service).start(
            specification,
            campaign_id=args.campaign_id,
        )
        emit(args.command, record["status"], "Campaign execution returned.", data=record)
        return campaign_exit(record["status"])
    if args.command == "campaign-resume":
        stored = ExperimentStore(lifecycle_root).read_campaign(args.campaign_id)
        record = (
            AgentCampaignApplicationService(service).resume(args.campaign_id)
            if stored.get("schema_version") == AGENT_CAMPAIGN_VERSION
            else CampaignApplicationService(service).resume(args.campaign_id)
        )
        emit(args.command, record["status"], "Campaign resume returned.", data=record)
        return campaign_exit(record["status"])
    raise ExperimentContractError("command_unsupported", "Unsupported command.")


def _models(args: argparse.Namespace, lifecycle_root: Path) -> int:
    repository = ModelLifecycleRepository(lifecycle_root)
    active = repository.read_active(optional=True)
    candidates = repository.list_candidates()
    emit(
        args.command,
        "success",
        "Model lifecycle state loaded.",
        data={
            "active": (
                {"candidate_id": active.candidate_id, "revision": active.revision}
                if active else None
            ),
            "candidates": [
                {
                    "candidate_id": item.manifest.candidate_id,
                    "run_id": item.manifest.run_id,
                    "promotion_eligible": item.manifest.promotion_eligible,
                    "blocking_reasons": list(item.manifest.blocking_reasons),
                    "analysis_artifacts": [
                        {
                            "path": reference.path,
                            "category": reference.category,
                            "sha256": reference.sha256,
                        }
                        for reference in item.manifest.analysis_artifacts
                    ],
                }
                for item in candidates
            ],
        },
    )
    return EXIT_SUCCESS


def _run_artifacts(lifecycle_root: Path, record: dict) -> dict:
    result = record.get("result") or {}
    candidate_id = result.get("candidate_reference")
    artifacts = []
    if candidate_id and result.get("publication_outcome") == "published":
        candidate = ModelLifecycleRepository(lifecycle_root).read_candidate(
            candidate_id
        )
        artifacts = [
            {
                "path": reference.path,
                "category": reference.category,
                "sha256": reference.sha256,
                "required": reference.required,
            }
            for reference in candidate.manifest.analysis_artifacts
        ]
    return {
        "run_id": record["run_id"],
        "candidate_reference": candidate_id,
        "evidence_reference": result.get("evidence_reference"),
        "analysis_artifacts": artifacts,
    }


if __name__ == "__main__":
    raise SystemExit(main())
