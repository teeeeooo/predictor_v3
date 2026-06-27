# core/ml/registry.py

MODEL_REGISTRY = {
    "power_model": {
        "name": "소비전력 예측 모델",
        "targets": ["Cooling Power", "Heating Power"],
        "use_rfe": True,
        "target_rules": {
            "Cooling Power": {
                "exclude": [
                    "Heating Capa", "Heating Hz",
                    "Heat_Capa_per_EER", "Heat_Capa_per_EvapArea",
                    "Heat_Capa_per_CondArea", "Heat_Capa_per_cc"
                ]
            },
            "Heating Power": {
                "exclude": [
                    "Cooling Capa", "Cooling Hz",
                    "Cool_Capa_per_EER", "Cool_Capa_per_CondArea",
                    "Cool_Capa_per_EvapArea", "Cool_Capa_per_cc"
                ]
            }
        }
    },
    "hz_model": {
        "name": "운전 주파수 예측 모델",
        "targets": ["Cooling Hz", "Heating Hz"],
        "use_rfe": True,
        "target_rules": {
            "Cooling Hz": {
                "exclude": [
                    "Heating Capa", "Heating Power",
                    "Heat_Capa_per_EER", "Heat_Capa_per_EvapArea",
                    "Heat_Capa_per_CondArea", "Heat_Capa_per_cc"
                ]
            },
            "Heating Hz": {
                "exclude": [
                    "Cooling Capa", "Cooling Power",
                    "Cool_Capa_per_EER", "Cool_Capa_per_CondArea",
                    "Cool_Capa_per_EvapArea", "Cool_Capa_per_cc"
                ]
            }
        }
    },
    "ref_model": {
        "name": "냉매량 예측 모델",
        "targets": ["Ref Qty"],
        "use_rfe": False,
        "target_rules": {
            "Ref Qty": {
                # [화이트리스트] 실제 데이터 컬럼명(R410A 등)과 일치하도록 수정 완료
                "allowed": [
                    "OD Volume", "ID Volume", "Evap Volume", "Cond Volume",
                    "R410A", "R32", "R290"
                ]
            }
        }
    }
}

def get_model_config(model_key):
    """
    지정된 모델 키의 설정값을 MODEL_REGISTRY에서 꺼내서 반환합니다.
    """
    if model_key not in MODEL_REGISTRY:
        raise KeyError(f"등록되지 않은 모델 키입니다: {model_key}")
    return MODEL_REGISTRY[model_key]
