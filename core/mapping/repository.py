"""Mapping data repository loading."""

import json
import os

from core.mapping.paths import MAPPING_JSON_FILE


def load_mapping_data(filepath: str | None = None) -> dict:
    """
    JSON 매핑 데이터를 안전하게 로드하여 반환합니다.
    UI 초기화 시점이나 업데이트가 필요할 때 명시적으로 호출하여 사용합니다.
    """
    filepath = filepath or MAPPING_JSON_FILE
    if not os.path.exists(filepath):
        print(f"⚠️ 매핑 파일이 없습니다. 기본 UI만 구성됩니다: {filepath}")
        return {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"❌ 오류: '{filepath}' 파일의 JSON 형식이 잘못되었습니다.")
        return {}
    except Exception as e:
        print(f"❌ 매핑 파일을 읽는 중 알 수 없는 오류 발생: {e}")
        return {}
