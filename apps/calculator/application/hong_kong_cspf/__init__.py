"""Hong Kong CSPF calculator application boundary."""

from apps.calculator.application.hong_kong_cspf.models import HongKongCspfUseCaseResult
from apps.calculator.application.hong_kong_cspf.usecase import HongKongCspfUseCase

__all__ = ["HongKongCspfUseCase", "HongKongCspfUseCaseResult"]
