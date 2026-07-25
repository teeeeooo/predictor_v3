"""Controlled Candidate publication-stage failures."""

from .errors import ModelLifecycleError


class CandidatePublicationValidationError(ModelLifecycleError):
    """A staged Candidate failed lifecycle-owned validation."""
