"""Errors owned by the standard calculation capability boundary."""


class StandardCalculationCapabilityError(Exception):
    """Base error for contracts owned by the capability boundary."""


class CapabilityNotFoundError(StandardCalculationCapabilityError):
    pass


class CapabilityRequestTypeError(StandardCalculationCapabilityError, TypeError):
    pass


class CapabilityConfigurationError(StandardCalculationCapabilityError):
    pass
