"""Shared profile-to-capability compatibility validation."""

from __future__ import annotations

from core.calculators.capability.errors import CapabilityConfigurationError
from core.calculators.profiles import CalculatorProfile


def validate_profile_for_capability(
    profile: CalculatorProfile,
    capability_id: str,
    *,
    calculator_id: str,
    metrics: tuple[str, ...],
    mode: str,
    standard: str,
) -> None:
    """Fail fast when a profile cannot execute the requested capability."""
    allowed_capabilities = profile.capability_ids
    if allowed_capabilities is not None:
        if not allowed_capabilities:
            raise CapabilityConfigurationError(
                f"Profile {profile.profile_id!r} declares an empty capability allowlist"
            )
        if capability_id not in allowed_capabilities:
            raise CapabilityConfigurationError(
                f"Profile {profile.profile_id!r} does not allow capability "
                f"{capability_id!r}"
            )

    compatible = (
        profile.calculator_id == calculator_id
        and profile.metric.casefold() in {metric.casefold() for metric in metrics}
        and profile.mode.casefold() == mode.casefold()
        and profile.standard.casefold() == standard.casefold()
    )
    if not compatible:
        raise CapabilityConfigurationError(
            f"Profile {profile.profile_id!r} is not compatible with "
            f"capability {capability_id!r}"
        )
