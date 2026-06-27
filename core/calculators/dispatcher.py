# core/calculator_dispatcher.py

"""Thin dispatcher that turns a resolved ``CalculatorProfile`` into a calculator
instance.

This module is a behavior-preserving foundation layer between profile lookup
and calculator instantiation. It does NOT execute any seasonal calculation;
it only constructs calculator instances using each calculator module's
existing public constructor.

Boundary:

- ``core/calculator_profiles.py`` (manifest/selector) is kept untouched.
- Calculator modules are imported lazily inside the dispatcher to avoid
  pulling unrelated modules at import time and to keep this layer thin.
- Unsupported ``calculator_id`` values fail fast with ``ValueError``.
- UI / ML schema dependencies are not introduced here.
"""

from typing import Optional

from core.calculators.profiles import (
    CalculatorProfile,
    resolve_calculator_profile,
)


def create_calculator_for_profile(
    profile_id: Optional[str] = None,
    standard: Optional[str] = None,
    region: Optional[str] = None,
    metric: Optional[str] = None,
    mode: Optional[str] = None,
):
    """Resolve a calculator profile and return a calculator instance.

    Either ``profile_id`` or the ``standard / region / metric / mode``
    selector tuple must select exactly one enabled profile. Selection logic
    is delegated to ``resolve_calculator_profile``; this function only adds
    the ``calculator_id`` → calculator-class mapping.

    Supported ``calculator_id`` values:

    - ``ks_c9306`` → ``core.calculator_ks_c9306.KSC9306Calculator.from_config_path(profile.config_path)``
    - ``iso16358`` → ``core.calculator_iso16358.ISO16358Calculator(profile.config_path)``
    - ``ahri_seer2`` → ``core.calculator_ahri_seer2.AHRICalculator(profile.config_path)``
    - ``ahri_hspf2`` → ``core.calculator_ahri_hspf2.AHRIHSPF2Calculator(profile.config_path)``
    - ``en14825`` → ``core.calculator_en14825.EN14825Calculator(profile.config_path)``
    - ``asnzs_excel_hspf`` → ``core.calculator_asnzs_hspf_excel.ASNZSExcelHSPFCompatibilityCalculator()``

    Any other ``calculator_id`` raises ``ValueError``.
    """
    profile: CalculatorProfile = resolve_calculator_profile(
        profile_id=profile_id,
        standard=standard,
        region=region,
        metric=metric,
        mode=mode,
    )

    calculator_id = profile.calculator_id
    config_path = profile.config_path

    if calculator_id == "ks_c9306":
        from core.calculator_ks_c9306 import KSC9306Calculator

        return KSC9306Calculator.from_config_path(config_path)

    if calculator_id == "iso16358":
        from core.calculator_iso16358 import ISO16358Calculator

        return ISO16358Calculator(config_path)

    if calculator_id == "ahri_seer2":
        from core.calculator_ahri_seer2 import AHRICalculator

        return AHRICalculator(config_path)

    if calculator_id == "ahri_hspf2":
        from core.calculator_ahri_hspf2 import AHRIHSPF2Calculator

        return AHRIHSPF2Calculator(config_path)

    if calculator_id == "en14825":
        from core.calculator_en14825 import EN14825Calculator

        return EN14825Calculator(config_path)

    if calculator_id == "asnzs_excel_hspf":
        from core.calculator_asnzs_hspf_excel import ASNZSExcelHSPFCompatibilityCalculator

        return ASNZSExcelHSPFCompatibilityCalculator()

    raise ValueError(
        f"Unsupported calculator_id for dispatcher: {calculator_id!r} "
        f"(profile_id={profile.profile_id!r})."
    )
