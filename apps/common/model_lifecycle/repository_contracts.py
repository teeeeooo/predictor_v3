"""Repository read model for one published Candidate."""

from dataclasses import dataclass
from pathlib import Path

from .candidate_contracts import CandidateManifest, CandidateResult


@dataclass(frozen=True)
class CandidateSnapshot:
    manifest: CandidateManifest
    result: CandidateResult
    path: Path

    @property
    def model_path(self) -> Path:
        return self.path / "model.pkl"
