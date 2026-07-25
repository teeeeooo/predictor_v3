"""Train application service boundaries."""

__all__ = ["CandidatePublisher", "TrainingLifecycleService"]


def __getattr__(name: str):
    """Keep public imports lazy so outbound adapters can consume contracts."""
    if name == "CandidatePublisher":
        from .candidate_publication import CandidatePublisher

        return CandidatePublisher
    if name == "TrainingLifecycleService":
        from .training_lifecycle import TrainingLifecycleService

        return TrainingLifecycleService
    raise AttributeError(name)
