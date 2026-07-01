"""KOREA calculator application boundary."""

from apps.calculator.application.korea.models import KoreaCspfUseCaseResult
from apps.calculator.application.korea.usecase import KoreaCspfUseCase

__all__ = ["KoreaCspfUseCase", "KoreaCspfUseCaseResult"]
