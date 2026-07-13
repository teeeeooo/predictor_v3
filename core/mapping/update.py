"""Pure mapping update conversion logic."""

import json
import os

import pandas as pd

from core.mapping.condenser_identity import condenser_requires_pi, condenser_spec_key
from core.mapping.paths import MAPPING_JSON_FILE


def update_mapping_to_json(excel_file):
    """선택받은 엑셀 파일을 읽어 투 트랙 JSON으로 변환하여 저장합니다."""
    if not excel_file or not os.path.exists(excel_file):
        print("⚠️ 작업이 취소되었거나 파일을 찾을 수 없습니다.")
        return

    mapping_data = {}

    try:
        print(f"📦 '{os.path.basename(excel_file)}' 읽는 중...")

        # 확장자에 따른 파일 읽기 분기
        _, ext = os.path.splitext(excel_file)
        ext = ext.lower()

        if ext == '.csv':
            try:
                df_single = pd.read_csv(excel_file, encoding='cp949')
            except UnicodeDecodeError:
                df_single = pd.read_csv(excel_file, encoding='utf-8')
            all_sheets = {"Sheet1": df_single}

        elif ext in ['.xlsx', '.xls']:
            all_sheets = pd.read_excel(excel_file, sheet_name=None)

        else:
            raise ValueError(f"지원하지 않는 파일 형식: {ext}")

        # 시트별 데이터 처리
        for sheet_name, df in all_sheets.items():
            df.columns = df.columns.str.strip()
            df = df.where(pd.notnull(df), None)

            # [특수 처리] ODU 시트는 '투 트랙(Two-Track)' 구조로 변환
            if sheet_name.lower() == "odu":
                odu_cascade = {}
                cond_specs = {}

                for _, row in df.iterrows():
                    odu = str(row.get("ODU", "")).strip()
                    fin = str(row.get("Fin type", "")).strip()
                    pi = str(row.get("Pi", "")).strip()
                    row_num = str(row.get("Row", "")).strip()

                    if not odu or odu == "None":
                        continue

                    if odu not in odu_cascade:
                        odu_cascade[odu] = {
                            "Available_Fins": set(),
                            "Available_Pis": set(),
                            "Available_Rows": set()
                        }

                    if fin and fin != "None": odu_cascade[odu]["Available_Fins"].add(fin)
                    if condenser_requires_pi(fin) and pi and pi != "None":
                        odu_cascade[odu]["Available_Pis"].add(pi)
                    if row_num and row_num != "None": odu_cascade[odu]["Available_Rows"].add(row_num)

                    if not condenser_requires_pi(fin):
                        pi = ""
                    cond_index_key = condenser_spec_key(odu, fin, pi, row_num)
                    cond_specs[cond_index_key] = {
                        "Cond Area": row.get("Cond Area"),
                        "Cond Volume": row.get("Cond Volume")
                    }

                for odu, specs in odu_cascade.items():
                    specs["Available_Fins"] = sorted(list(specs["Available_Fins"]))
                    specs["Available_Pis"] = sorted(list(specs["Available_Pis"]))
                    specs["Available_Rows"] = sorted(list(specs["Available_Rows"]))

                mapping_data["odu_cascade"] = odu_cascade
                mapping_data["cond_specs"] = cond_specs
                print(f"  ✔️ ODU 시트 '투 트랙' 변환 완료 (모델 {len(odu_cascade)}개)")

            # [일반 처리] IDU, Evap, Compressor 등 나머지 시트
            else:
                first_col = df.columns[0]

                # [안전장치] 결측치 및 중복 방지 방어 로직
                df = df.dropna(subset=[first_col])
                df = df.drop_duplicates(subset=[first_col], keep='last')

                mapping_data[sheet_name] = df.set_index(first_col).to_dict('index')
                print(f"  ✔️ {sheet_name} 시트 일반 변환 완료 (항목 {len(mapping_data[sheet_name])}개)")

        os.makedirs(os.path.dirname(MAPPING_JSON_FILE), exist_ok=True)
        with open(MAPPING_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(mapping_data, f, ensure_ascii=False, indent=4)

        print(f"\n✅ 매핑 데이터 업데이트 성공: {MAPPING_JSON_FILE}")

    except Exception as e:
        print(f"\n❌ 업데이트 중 오류 발생: {e}")
