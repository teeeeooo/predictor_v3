"""Expected model lifecycle repository and artifact failures."""


class ModelLifecycleError(ValueError):
    """Base class for controlled lifecycle failures."""


class LifecycleFilesystemError(ModelLifecycleError):
    """A lifecycle path is outside its owner or has an unsafe object type."""


class CandidateCorruptionError(ModelLifecycleError):
    """A published Candidate cannot be read as its immutable contract."""


class ActiveReferenceCorruptionError(ModelLifecycleError):
    """The Active pointer cannot be read as its versioned contract."""


class StaleActiveRevisionError(ModelLifecycleError):
    """A guarded Active mutation was based on an obsolete revision."""


class LegacyArtifactError(ModelLifecycleError):
    """A legacy bundle cannot be imported or compatibility-checked."""
