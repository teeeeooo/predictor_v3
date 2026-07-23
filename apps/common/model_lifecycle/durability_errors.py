"""Controlled failures for lifecycle durability and recovery transitions."""

from .errors import LifecycleFilesystemError


class LifecycleDurabilityError(LifecycleFilesystemError):
    """A lifecycle mutation was rolled back after its durability step failed."""


class LifecycleRecoveryRequiredError(LifecycleFilesystemError):
    """A lifecycle mutation could not be reconciled without a later recovery."""


class PostRenameDurabilityError(LifecycleFilesystemError):
    """A rename completed but the containing directory was not made durable."""
