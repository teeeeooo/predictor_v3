"""Brazil CSPF compliance capability handler and domain policy."""

from __future__ import annotations

import math
from collections.abc import Mapping

from core.calculators.capability.compatibility import validate_profile_for_capability
from core.calculators.capability.errors import CapabilityConfigurationError
from core.calculators.capability.requests import (
    BRAZIL_CSPF_COMPLIANCE_PROFILE_ID,
    BrazilCspfComplianceRequest,
)
from core.calculators.capability.results import (
    BrazilCspfComplianceResult,
    BrazilRuleEvaluation,
)
from core.calculators.dispatcher import create_calculator_for_profile
from core.calculators.profiles import resolve_calculator_profile


BRAZIL_CSPF_COMPLIANCE_CAPABILITY_ID = "brazil.cspf_compliance"
RULE_1_MULTIPLIER = 1.4
_MEASURED_POINT_KEYS = ("35_full", "35_half", "29_half")
_CALCULATOR_POINT_KEYS = ("35_full", "35_half")


class BrazilCspfComplianceError(ValueError):
    """Brazil-owned input, diagnostic, or compliance invariant violation."""


class BrazilCspfComplianceHandler:
    capability_id = BRAZIL_CSPF_COMPLIANCE_CAPABILITY_ID
    request_type = BrazilCspfComplianceRequest

    def execute(self, request: BrazilCspfComplianceRequest) -> BrazilCspfComplianceResult:
        profile = _resolve_profile(request.profile_id)
        _validate_request_points(request.measured_points)
        normalized_points = _normalized_points(request.measured_points)
        three_point_inputs = _copy_points(normalized_points, _MEASURED_POINT_KEYS)
        two_point_inputs = _copy_points(normalized_points, _CALCULATOR_POINT_KEYS)

        three_point_calculator = create_calculator_for_profile(
            profile_id=profile.profile_id
        )
        two_point_calculator = create_calculator_for_profile(
            profile_id=profile.profile_id
        )
        three_point_result = three_point_calculator.calculate_cspf(three_point_inputs)
        two_point_result = two_point_calculator.calculate_cspf(two_point_inputs)

        three_point_exact_cspf, three_point_29_bin = _exact_cspf(
            three_point_result, "3-point", require_29_bin=True
        )
        two_point_exact_cspf, _ = _exact_cspf(
            two_point_result, "2-point", require_29_bin=False
        )
        measured_29_half_eer = normalized_points["29_half"]["capacity"] / normalized_points[
            "29_half"
        ]["power"]
        calculated_29_eer = _finite_positive(
            three_point_29_bin["eer"], "3-point 29°C bin eer"
        )

        rule_1_right = two_point_exact_cspf * RULE_1_MULTIPLIER
        rule_1 = BrazilRuleEvaluation(
            left_value=three_point_exact_cspf,
            right_value=rule_1_right,
            passed=three_point_exact_cspf <= rule_1_right,
        )
        rule_2 = BrazilRuleEvaluation(
            left_value=measured_29_half_eer,
            right_value=calculated_29_eer,
            passed=measured_29_half_eer > calculated_29_eer,
        )
        return BrazilCspfComplianceResult(
            three_point_result=three_point_result,
            two_point_result=two_point_result,
            three_point_exact_cspf=three_point_exact_cspf,
            two_point_exact_cspf=two_point_exact_cspf,
            rule_1_multiplier=RULE_1_MULTIPLIER,
            rule_1=rule_1,
            rule_2=rule_2,
            final_passed=rule_1.passed or rule_2.passed,
        )


def _resolve_profile(profile_id: object):
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise CapabilityConfigurationError(
            "Brazil CSPF compliance profile_id must be a non-empty string"
        )
    try:
        profile = resolve_calculator_profile(profile_id=profile_id)
    except ValueError as exc:
        raise CapabilityConfigurationError(
            f"Brazil CSPF compliance cannot resolve profile {profile_id!r}"
        ) from exc
    if profile.profile_id != BRAZIL_CSPF_COMPLIANCE_PROFILE_ID:
        raise CapabilityConfigurationError(
            f"Brazil CSPF compliance requires profile "
            f"{BRAZIL_CSPF_COMPLIANCE_PROFILE_ID!r}; received {profile.profile_id!r}"
        )
    validate_profile_for_capability(
        profile,
        BRAZIL_CSPF_COMPLIANCE_CAPABILITY_ID,
        calculator_id="iso16358",
        metrics=("CSPF",),
        mode="cooling",
        standard="ISO_16358",
    )
    return profile


def _validate_request_points(measured_points: object) -> None:
    if not isinstance(measured_points, Mapping):
        raise BrazilCspfComplianceError("measured_points must be a mapping")
    for point_key in _MEASURED_POINT_KEYS:
        if point_key not in measured_points:
            raise BrazilCspfComplianceError(
                f"Brazil CSPF compliance requires measured point {point_key!r}"
            )
        point = measured_points[point_key]
        if not isinstance(point, Mapping):
            raise BrazilCspfComplianceError(
                f"Measured point {point_key!r} must be a mapping"
            )
        for field in ("capacity", "power"):
            if field not in point:
                raise BrazilCspfComplianceError(
                    f"Measured point {point_key!r} is missing {field!r}"
                )
            _finite_positive(point[field], f"{point_key}.{field}")


def _normalized_points(measured_points: Mapping[str, object]) -> dict[str, dict[str, float]]:
    return {
        point_key: {
            field: _finite_positive(measured_points[point_key][field], f"{point_key}.{field}")
            for field in ("capacity", "power")
        }
        for point_key in _MEASURED_POINT_KEYS
    }


def _copy_points(
    measured_points: Mapping[str, Mapping[str, float]], point_keys: tuple[str, ...]
) -> dict[str, dict[str, float]]:
    return {point_key: dict(measured_points[point_key]) for point_key in point_keys}


def _exact_cspf(
    raw_result: object,
    scenario: str,
    *,
    require_29_bin: bool,
) -> tuple[float, Mapping[str, object] | None]:
    if not isinstance(raw_result, Mapping):
        raise BrazilCspfComplianceError(f"{scenario} raw result must be a mapping")
    for key in ("cspf", "annual_cooling_kwh", "annual_power_kwh"):
        _finite_number(raw_result.get(key), f"{scenario} raw result {key}")
    bin_details = raw_result.get("bin_details")
    if not isinstance(bin_details, (list, tuple)):
        raise BrazilCspfComplianceError(
            f"{scenario} raw result bin_details must be a list or tuple"
        )

    cooling_total = 0.0
    power_total = 0.0
    bins_at_29: list[Mapping[str, object]] = []
    for index, detail in enumerate(bin_details):
        if not isinstance(detail, Mapping):
            raise BrazilCspfComplianceError(
                f"{scenario} bin_details[{index}] must be a mapping"
            )
        temperature = _finite_number(detail.get("tj"), f"{scenario} bin {index} tj")
        cooling_bin = _finite_number(
            detail.get("cstl_bin"), f"{scenario} bin {index} cstl_bin"
        )
        power_bin = _finite_number(
            detail.get("csec_bin"), f"{scenario} bin {index} csec_bin"
        )
        if cooling_bin < 0 or power_bin < 0:
            raise BrazilCspfComplianceError(
                f"{scenario} bin {index} accumulated values must not be negative"
            )
        cooling_total += cooling_bin
        power_total += power_bin
        if temperature == 29.0:
            bins_at_29.append(detail)

    if power_total <= 0:
        raise BrazilCspfComplianceError(f"{scenario} cumulative CSEC must be positive")
    if require_29_bin and len(bins_at_29) != 1:
        raise BrazilCspfComplianceError(
            f"{scenario} raw result must contain exactly one 29°C bin; "
            f"found {len(bins_at_29)}"
        )
    return cooling_total / power_total, bins_at_29[0] if bins_at_29 else None


def _finite_positive(value: object, label: str) -> float:
    number = _finite_number(value, label)
    if number <= 0:
        raise BrazilCspfComplianceError(f"{label} must be positive")
    return number


def _finite_number(value: object, label: str) -> float:
    if isinstance(value, bool):
        raise BrazilCspfComplianceError(f"{label} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise BrazilCspfComplianceError(f"{label} must be numeric") from None
    if not math.isfinite(number):
        raise BrazilCspfComplianceError(f"{label} must be finite")
    return number
