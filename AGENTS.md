# predictor_v3 에이전트 규칙
작업 시작 전 이 파일을 반드시 읽을 것

## 프로젝트 정보
* 프로젝트명: predictor_v3
* 언어: Python
* GUI: PyQt5
* ML: XGBoost
* 개발 환경: VSCode + 에이전트 (Cline, Gemini CLI, CODEX, Claude Code)

---

## 🏗️ 아키텍처 절대 원칙 (어떤 이유로도 위반 금지)
* **Train / Predict 엄격 분리**: `app_train.py`와 `app_predict.py`는 절대 병합 금지.
* **import 제한**: `core/trainer.py`는 `app_train.py` 전용이며 `core/predictor.py`에서 import 절대 금지.
* **학습 라이브러리 격리**: `core/predictor.py`에 학습용 라이브러리(optuna, sklearn, shap, matplotlib) 추가 금지.
* **UI 구조 강제**: `QTableWidget` 사용 금지. 반드시 `QTableView` + `QAbstractTableModel` 구조만 허용.
* **단일 모델 파일**: ML 모델은 반드시 단일 파일(`model.pkl`)로 통합 저장하며, 예측 시 `preprocess_version` 검증(Lite 안전장치 v1.0) 필수.
* **단일 소스 원칙(SSOT)**: `COLUMNS` 정의는 `core/constants.py`에서만 중앙 관리하며, `MODEL_REGISTRY`는 `core/models.py` 단일 소스 유지.

---

## 🚫 절대 금지 규칙
* **명시적 지시 없이 기존 계산 경로(계산 로직) 수정 금지**
* `calculate_hspf2_v2()` 및 `calculate_hspf2()` 임의 수정 금지
* 기존 JSON 스키마 하위 호환성 유지 (데이터 필드 삭제 금지)
* v2와 v3 계산 경로 분리 유지
* 명시적 요청 없이 공개 함수명 또는 JSON 키 이름 변경 금지
* 테스트 기댓값 무단 변경 금지

---

## 🔒 수정 범위 제한 규칙 (Scoped Editing)

- 명시된 파일/함수 외의 코드는 절대 수정하지 말 것.
- 수정 범위가 주어지면 해당 범위 외 변경은 모두 금지.
- 리팩토링, 변수명 변경, 구조 변경은 명시적 요청 없으면 금지.

---

## 🎨 UI 및 뷰(View) 원칙
* **위젯 직접 삽입 금지**: 테이블 내 드롭다운 구현 시 `setCellWidget` 절대 금지. 반드시 `QStyledItemDelegate`의 `paint`와 `editorEvent`를 활용한 1-Click 콤보박스 방식으로 구현할 것.
* **배경색 상태 규칙**: 
  * 직접 입력(`input_cols`): 흰색 (`#FFFFFF`)
  * 자동 매핑(`auto_cols`): 회색 (`#F2F2F2`) - 사용자가 수동 수정 시 흰색으로 전환.
  * 결과 출력(`result_cols`): 연녹색 계열 (`#E6F3E6`)
* **블로킹 안전장치**: `blockSignals` 사용 시 반드시 `try/finally`로 감싸서 무한 루프(Recursion)를 방지할 것.

---

## 🧠 ML 및 데이터 연산 원칙
* **DataFrame 네이티브 학습**: `model.fit()`에 `.values` 변환 절대 금지 (피처명 `feature_names_in_` 보존 필수).
* **물리적 제약 조건 반영**: 통계적 수치보다 HVAC 물리 원칙 우선. 전력/주파수 등은 단조 제약 조건(Monotone Constraints)을 반드시 반영.
* **타겟별 완전 독립 분기**: 다중 타겟(MultiOutput) 학습 방식 금지. Cooling과 Heating은 각각 완전히 독립된 XGBoost 모델과 독립된 RFE 피처셋, Data Leakage 룰을 가질 것.
* **안전한 데이터 처리**: 파생 피처 계산 시 단위 루프(`apply`) 대신 Pandas 벡터 연산(`np.where`)을 사용하며, 필수 피처 누락 시 경고가 아닌 `raise ValueError`로 엄격히 중단(Fail-Fast)할 것.

---

## 📦 빌드 및 패키징 원칙
* **클린 빌드 환경**: 배포용 빌드(PyInstaller)는 반드시 `venv_deploy` 가상환경에서 수행할 것.
* **DLL 런타임 방어**: XGBoost 및 Numpy의 DLL 파일 누락을 막기 위해 `.spec` 파일의 `binaries` 항목에 명시적으로 매핑할 것.
* **글로벌 에러 로깅**: 실행 파일 최상단에 `sys.excepthook` 기반 글로벌 핸들러를 배치하여 강제 종료 시 `crash_log.txt`를 생성하도록 설계할 것.

---

## 📐 HSPF2 구현 범위
* 적용 규격: AHRI 210/240
* 우선 대상: non-ducted, single-split, variable-capacity, air-to-air heat pump
* 우선 지역: Region IV
* 아래 항목은 명시적 요청 없으면 구현 금지:
  * ducted ESP, multi-split, VRF, dual fuel, furnace, zoning, northern heat pump, two-compressor 특수 케이스

---

## 🗂️ 계산기 파일 구조
* `calculator.py` — ISO 16358 (한국 KC, 태국 EGAT 등)
* `calculator_en14825.py` — EN 14825 (EU SEER/SCOP)
* `calculator_ahri_seer2.py` — AHRI 210/240 SEER2
* `calculator_ahri_hspf2.py` — AHRI 210/240 HSPF2
* 지역별 파라미터는 `data/region_configs/*.json` 또는 `data/usa_hspf2.json`으로 분리.
* **calculator 계열 파일 제약**: numpy/pandas 금지, 순수 파이썬(Built-in)만 사용할 것.

---

## 📝 규격 및 공식 규칙
* **AHRI 공식 임의 작성 금지**
* 공식이 불완전하거나 불확실하면 `TODO`로 표시 — 절대 추측으로 구현하지 말 것.
* 표준 테이블 추가 시 JSON에 출처 메타데이터 유지.
* fractional bin hours와 absolute bin hours를 반드시 구분할 것.
  * `fractional bin hours × HLH = absolute bin hours`
  * 계절 부하/에너지 합산은 반드시 `absolute bin hours` 사용.
* `BL(t_j)` 계산은 반드시 Table 14의 `t_zl, t_OD, C_vs` 사용.

---

## 💻 코딩 규칙 및 보고 형식
* 작은 단위로 수정 — 한 번에 한 파일만 수정.
* 관련 없는 코드 리팩토링 금지.
* 계산기 작업 중 UI 파일(`ui/`) 수정 금지.
* 계산기 작업 중 ML predictor/trainer 코드 수정 금지.
* 계산 로직 변경 시 반드시 smoke test 또는 assert 추가.

**[작업 완료 보고 형식] (반드시 이 형식으로 보고할 것)**
* [수정 파일] 파일명
* [변경 내용]
   - 수정/추가/제거: 내용
* [테스트 결과]
   - 실행 명령: python3 -B ...
   - 주요 출력값
   - assert pass/fail
* [다음 작업] 확인 후 말씀해 주세요.