"""Operation-specific, runtime-neutral standard calculation requests."""

from dataclasses import dataclass, field
from typing import Mapping

MeasuredPoints = Mapping[str, object]
BRAZIL_CSPF_COMPLIANCE_PROFILE_ID = "brazil_cspf_compliance"


@dataclass(frozen=True)
class Iso16358CspfRequest:
    profile_id: str
    measured_points: MeasuredPoints
    declared_capacity: float | None = None
    test_selection: str | None = None


@dataclass(frozen=True)
class BrazilCspfComplianceRequest:
    measured_points: MeasuredPoints
    profile_id: str = BRAZIL_CSPF_COMPLIANCE_PROFILE_ID


@dataclass(frozen=True)
class Iso16358HspfRequest:
    profile_id: str
    measured_points: MeasuredPoints


@dataclass(frozen=True)
class KsC9306CspfRequest:
    profile_id: str
    measured_points: MeasuredPoints
    declared_capacity: float | None = None


@dataclass(frozen=True)
class KsC9306HspfRequest:
    profile_id: str
    measured_points: MeasuredPoints


@dataclass(frozen=True)
class En14825SeerRequest:
    profile_id: str = "en14825_seer"
    parameters: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class En14825ScopRequest:
    profile_id: str = "en14825_scop"
    parameters: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class AhriSeer2Request:
    test_points: MeasuredPoints
    system_type: str = "HP"
    p_w_off: float = 0.0
    cd_low: float | None = None
    profile_id: str = "ahri_usa_seer2"


@dataclass(frozen=True)
class AhriHspf2Request:
    test_points: MeasuredPoints
    parameters: Mapping[str, object] = field(default_factory=dict)
    profile_id: str = "ahri_usa_hspf2"
