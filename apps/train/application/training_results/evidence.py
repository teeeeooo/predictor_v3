"""Application-owned outbound contracts for training evidence and artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from apps.common.model_lifecycle.candidate_contracts import CandidateArtifactReference
from apps.train.state.training_run_state import TrainingResult
from core.ml.training_results import CoreTrainingEvidence

from .contracts import TrainingAnalysisResult


class TrainingEvidencePort(Protocol):
    def load_active_baseline(
        self,
    ) -> tuple[TrainingAnalysisResult | None, str, str]: ...

    def load_candidate(
        self, staging: Path, targets: tuple[object, ...]
    ) -> CoreTrainingEvidence: ...

    def load_terminal(
        self, staging: Path, result: TrainingResult
    ) -> CoreTrainingEvidence: ...

    def prepare_terminal(
        self, staging: Path, candidate_id: str
    ) -> Path: ...


class TrainingResultArtifactPort(Protocol):
    def write(
        self, staging: Path, result: TrainingAnalysisResult
    ) -> tuple[CandidateArtifactReference, ...]: ...


class TrainingTerminalEvidencePort(Protocol):
    def write(self, staging: Path, result: TrainingAnalysisResult) -> None: ...
