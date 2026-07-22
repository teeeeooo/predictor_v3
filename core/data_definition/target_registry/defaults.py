"""Frozen compatibility facts for the three validated trainer families."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidatedModelGroup:
    identity: str
    registry_key: str
    name: str
    use_rfe: bool
    targets: tuple[str, ...]
    rules: tuple[tuple[str, str, tuple[str, ...]], ...]


VALIDATED_MODEL_GROUPS = (
    ValidatedModelGroup(
        "ufm_model_group_9e71f4a75bd15c1e80688d21d2732208",
        "power_model", "소비전력 예측 모델", True,
        ("Cooling Power", "Heating Power"),
        (
            ("Cooling Power", "exclude", (
                "Heating Capa", "Heating Hz", "Heat_Capa_per_EER",
                "Heat_Capa_per_EvapArea", "Heat_Capa_per_CondArea", "Heat_Capa_per_cc",
            )),
            ("Heating Power", "exclude", (
                "Cooling Capa", "Cooling Hz", "Cool_Capa_per_EER",
                "Cool_Capa_per_CondArea", "Cool_Capa_per_EvapArea", "Cool_Capa_per_cc",
            )),
        ),
    ),
    ValidatedModelGroup(
        "ufm_model_group_2187461a19525b55aa639d0aa48b5332",
        "hz_model", "운전 주파수 예측 모델", True,
        ("Cooling Hz", "Heating Hz"),
        (
            ("Cooling Hz", "exclude", (
                "Heating Capa", "Heating Power", "Heat_Capa_per_EER",
                "Heat_Capa_per_EvapArea", "Heat_Capa_per_CondArea", "Heat_Capa_per_cc",
            )),
            ("Heating Hz", "exclude", (
                "Cooling Capa", "Cooling Power", "Cool_Capa_per_EER",
                "Cool_Capa_per_CondArea", "Cool_Capa_per_EvapArea", "Cool_Capa_per_cc",
            )),
        ),
    ),
    ValidatedModelGroup(
        "ufm_model_group_70a181ec4f605f3293554f59756c4607",
        "ref_model", "냉매량 예측 모델", False,
        ("Ref Qty",),
        (("Ref Qty", "allowed", (
            "OD Volume", "ID Volume", "Evap Volume", "Cond Volume", "R410A", "R32", "R290",
        )),),
    ),
)

VALIDATED_GROUP_BY_KEY = {item.registry_key: item for item in VALIDATED_MODEL_GROUPS}
VALIDATED_GROUP_BY_IDENTITY = {item.identity: item for item in VALIDATED_MODEL_GROUPS}
