"""Read lifecycle-owned evidence for Phase 5G without redefining it."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps.common.model_lifecycle import ModelLifecycleRepository


class CampaignEvidenceReader:
    def __init__(self, lifecycle_root: str | Path) -> None:
        self.root = Path(lifecycle_root).resolve()
        self.repository = ModelLifecycleRepository(self.root)

    def active_reference(self) -> dict[str, Any] | None:
        active = self.repository.read_active(optional=True)
        if active is None:
            return None
        return {
            "candidate_id": active.candidate_id,
            "revision": active.revision,
        }

    def candidate_analysis(
        self, candidate_id: str
    ) -> tuple[dict[str, Any] | None, dict[str, Any]]:
        try:
            candidate = self.repository.read_candidate(candidate_id)
            analysis = self._read_json(candidate.path / "training_result.json")
        except Exception as exc:
            return None, {
                "valid": False,
                "code": "lifecycle_integrity_failure",
                "reason": str(exc).splitlines()[0],
                "evidence_reference": f"candidates/{candidate_id}/manifest.json",
            }
        return analysis, {
            "valid": True,
            "code": "candidate_integrity_valid",
            "reason": "",
            "evidence_reference": f"candidates/{candidate_id}/manifest.json",
            "manifest": candidate.manifest.to_payload(),
        }

    def run_analysis(
        self, run_record: dict[str, Any]
    ) -> tuple[dict[str, Any] | None, dict[str, Any]]:
        result = run_record.get("result") or {}
        candidate_id = result.get("candidate_reference")
        if candidate_id:
            return self.candidate_analysis(str(candidate_id))
        reference = result.get("evidence_reference")
        if not isinstance(reference, str) or not reference:
            return None, {
                "valid": False,
                "code": "incomplete_artifact",
                "reason": "Run has no structured evidence reference.",
                "evidence_reference": None,
            }
        try:
            path = (self.root / reference).resolve(strict=True)
            path.relative_to(self.root)
            return self._read_json(path), {
                "valid": False,
                "code": "incomplete_artifact",
                "reason": "Run evidence exists but no immutable Candidate was published.",
                "evidence_reference": reference,
            }
        except Exception as exc:
            return None, {
                "valid": False,
                "code": "incomplete_artifact",
                "reason": str(exc).splitlines()[0],
                "evidence_reference": reference,
            }

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("training analysis must be an object")
        return payload
