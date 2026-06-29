"""Hong Kong HSPF calculator application boundary."""

from apps.calculator.application.hong_kong_hspf.models import HongKongHspfUseCaseResult
from apps.calculator.application.hong_kong_hspf.usecase import HongKongHspfUseCase

__all__ = ["HongKongHspfUseCase", "HongKongHspfUseCaseResult"]
