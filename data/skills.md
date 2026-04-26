1. pyqt5_dropdown_delegate.md
# PyQt5 1-Click 드롭다운 델리게이트 패턴

## 목적
QTableWidget에서 드롭다운(콤보박스)을 사용할 때
더블클릭해야 열리는 UX 불편함을 해결하고,
붙여넣기 시 발생하는 데이터 오염을 방지하는
커스텀 델리게이트 패턴.

## 핵심 구현 포인트
- 1-Click 전개: editorEvent 오버라이딩 +
  QTimer.singleShot으로 즉시 팝업
- 붙여넣기 방어: 유효하지 않은 값이면
  무시하거나 기본값으로 처리

## 코드 패턴
from PyQt5.QtWidgets import QStyledItemDelegate, QComboBox
from PyQt5.QtCore import QTimer, Qt, QEvent

class OneClickDropdownDelegate(QStyledItemDelegate):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.items = items

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.items)
        QTimer.singleShot(0, editor.showPopup)
        return editor

    def editorEvent(self, event, model, option, index):
        if (event.type() == QEvent.MouseButtonRelease
                and event.button() == Qt.LeftButton):
            return True
        return super().editorEvent(
            event, model, option, index
        )

## V2 시행착오 - 반드시 기억할 것
- time.sleep 타이밍 제어 절대 금지
  → 반드시 QTimer.singleShot 사용
- 붙여넣기는 on_paste_complete() 별도 처리 필요
  on_cell_changed와 다른 경로로 들어옴
- _apply_mapping() 대신 on_dropdown_changed() 사용
  메서드명 혼용으로 AttributeError 발생 경험
- QTableWidget 구조에서 붙여넣기/이벤트 꼬임이
  근본 원인 → V3에서 QTableView + QAbstractTableModel
  로 전환하여 원천 차단
2. xgboost_rfe_pipeline.md
# XGBoost + Pandas Native RFE 파이프라인

## 목적
XGBoost 학습 시 피처명(feature_names_in_)을
보존하고, RFE로 최적 피처를 선택하는 파이프라인.
데이터-모델 간 피처명 불일치로 인한
Silent Bug를 원천 차단.

## 핵심 규칙 (절대 원칙)
model.fit()에 .values 변환 없이
DataFrame을 그대로 전달할 것.
이를 어기면 feature_names_in_이 소실되어
predictor에서 피처명 역추적 불가.

## 코드 패턴
from xgboost import XGBRegressor
from sklearn.feature_selection import RFECV

def select_features_rfecv(
    df: pd.DataFrame,
    target: str,
    mandatory: list[str],
    excluded: list[str],
    leakage: list[str]
) -> list[str]:

    # 후보 피처 구성
    candidates = [
        f for f in df.columns
        if f != target
        and f not in excluded
        and f not in leakage
        and f not in mandatory
    ]

    # RFECV 적용 (.values 변환 없이 DataFrame 유지)
    X_candidates = df[candidates]
    y = df[target]

    selector = RFECV(
        XGBRegressor(n_estimators=100),
        cv=5
    )
    selector.fit(X_candidates, y)  # DataFrame 그대로

    selected = X_candidates.columns[
        selector.support_
    ].tolist()

    # mandatory는 항상 포함
    return mandatory + selected


def train_model(
    df: pd.DataFrame,
    target: str,
    features: list[str]
) -> XGBRegressor:

    X = df[features]   # .values 절대 금지
    y = df[target]

    model = XGBRegressor(
        n_estimators=500,
        max_depth=4,
        learning_rate=0.05
    )
    model.fit(X, y)    # feature_names_in_ 자동 보존
    return model

## V2 시행착오 - 반드시 기억할 것
- 초기에 .values 변환으로 학습
  → feature_names_in_ 소실
  → OptimalModel.features로 우회했으나 기술적 부채
  → DataFrame 직접 전달로 수정 후 해결
- RandomForest → XGBoost 전환 시
  .values 관성 코드가 남아있어 문제 발생
- RFECV 후보에서 mandatory/excluded/leakage
  3가지 모두 제거 후 진입할 것
  (leakage 누락 시 Data Leakage 발생)

3. dropdown_target_mapping.md
# SSOT 기반 드롭다운-자동입력 매핑 아키텍처

## 목적
UI 앱의 드롭다운과 자동입력 셀 간 관계를
constants.py 단일 진실 공급원(SSOT)으로 관리.
비즈니스 로직 하드코딩 제거.

## 핵심 구현 포인트
- DROPDOWN_TARGET을 Dict[int, List[int]]로 정의
- .get(col, []) 로 KeyError 원천 차단
- COLUMNS에 ml_feature 키 추가로
  UI 표시명과 모델 피처명 불일치 해결

## 코드 패턴

### constants.py (SSOT 정의)
DROPDOWN_TARGET = {
    COL_IDU:       [COL_ID_VOLUME],
    COL_EVAP_INDEX:[COL_EVAP_AREA, COL_EVAP_VOLUME],
    COL_ODU:       [COL_OD_VOLUME],
    COL_ROW:       [COL_COND_AREA, COL_COND_VOLUME],
    COL_COMPRESSOR:[COL_COMP_EER, COL_COMP_CC]
}

COLUMNS = [
    {
        'key':        'id_volume',
        'header':     'ID\nVol',      # UI 표시용
        'ml_feature': 'ID Volume',    # 모델 피처명
        'group':      'auto'
    },
    ...
]

### predictor.py (동적 매핑)
col_mapping = {
    c['key']: c.get('ml_feature', c['header'])
    for c in COLUMNS
}

### UI 검증 로직
def validate_direct_inputs(self, row_idx):
    for col in DROPDOWN_COLS:
        value = self._get_cell_value(row_idx, col)
        if value == '직접 입력':
            target_cols = DROPDOWN_TARGET.get(col, [])
            for target_col in target_cols:
                if not self._get_cell_value(
                    row_idx, target_col
                ):
                    raise ValueError(
                        f"{col}번 열이 직접 입력입니다. "
                        f"{target_col}번 열을 채워주세요."
                    )

## V2 시행착오 - 반드시 기억할 것
- header와 ml_feature 불일치 문제
  예: header='ID\nVol' vs 피처명='ID Volume'
  → predictor에 보정 딕셔너리 하드코딩은 안티패턴
  → COLUMNS에 ml_feature 키 추가로 해결
- .get(col, []) 없이 직접 인덱싱하면
  매핑 없는 열 진입 시 KeyError 발생

4. cascading_autofill_pattern.md
# 계층형 자동완성 및 UI 상태 잠금 패턴

## 목적
마스터 드롭다운 선택 시 하위 Auto Cols를
계층적으로 자동 입력하고, UI 상태(Read-only/
Editable)를 안전하게 제어하는 패턴.

## 로직 3단계 분리 (반드시 이 순서)
1단계: DB/매핑에서 데이터 가져오기
2단계: blockSignals(True) → 값 쓰기
        → blockSignals(False)
3단계: UI 배경색 및 잠금 상태 업데이트

## 코드 패턴
def apply_cascade_mapping(self, row, col, value):

    # 1단계: 매핑 데이터 조회
    mapped_values = self.mapping_tables.get(
        col, {}
    ).get(value, {})
    if not mapped_values:
        return

    # 2단계: 시그널 차단 후 값 쓰기
    self.table.blockSignals(True)
    try:
        for target_col, val in mapped_values.items():
            self._set_cell_value(row, target_col, val)
    finally:
        self.table.blockSignals(False)  # 반드시 해제

    # 3단계: UI 상태 업데이트
    self._update_auto_cols_state(row, col, value)

def _update_auto_cols_state(self, row, col, value):
    # UI 잠금은 반드시 마스터 드롭다운 값 기준으로만
    is_direct = (value == '직접 입력')
    target_cols = DROPDOWN_TARGET.get(col, [])
    for target_col in target_cols:
        self._set_cell_editable(
            row, target_col, editable=is_direct
        )

## V2 시행착오 - 반드시 기억할 것
- blockSignals 없이 값 세팅하면
  itemChanged 시그널 연쇄 폭발
  → 매핑 함수 무한 호출 발생
- blockSignals(True) 후 예외 발생 시
  False로 해제가 안 되는 문제
  → 반드시 try/finally 구조 사용
- Delete 키로 Auto Cols 삭제 시
  부모 상태 확인 없이 무조건 잠금 처리하는 버그
  → UI 상태 변경 전 반드시
    마스터 드롭다운 값 먼저 조회
- 단방향 원칙: UI 잠금/해제는
  오직 마스터 드롭다운 값에 의해서만 결정
  다른 곳에서 상태 변경 금지


5. ml_safety_patterns.md
# ML 안전장치 패턴 (Lite Safety v1.0)

## 목적
모델 학습/배포 시 조용한 버그(Silent Bug)를
막는 안전장치 패턴.
버전 불일치, 피처 오염, Data Leakage를
코드 레벨에서 원천 차단.

## 안전장치 3종

### 1. 전처리 버전 체크
# utils.py - OptimalModel 데이터클래스
@dataclass
class OptimalModel:
    target: str
    features: list[str]
    metrics: ModelMetrics
    model: Any
    preprocess_version: str = "v1.0"

# predictor.py - 로드 시 검증
for target, model_info in models.items():
    saved = getattr(
        model_info, 'preprocess_version', 'unknown'
    )
    if saved != CURRENT_PREPROCESS_VERSION:
        raise ValueError(
            f"[{target}] 전처리 버전 불일치. "
            f"재학습 필요."
        )

### 2. Feature Freeze 체크
# 모델이 요구하는 피처가 현재 데이터에 있는지
required = set(model_info.model.feature_names_in_)
available = set(df.columns)
missing = required - available
if missing:
    raise ValueError(f"누락 피처: {missing}")

### 3. Data Leakage Hard Gate
# 학습 진입 전 반드시 실행
# 통과 못하면 fit() 진입 자체 금지
LEAKAGE_FEATURES = {
    'Cooling Power': [
        'Heating Power', 'Cooling Hz',
        'Heating Hz', 'Ref Qty'
    ],
    'Ref Qty': [
        'Cooling Power', 'Heating Power',
        'Cooling Hz', 'Heating Hz'
    ],
    'Cooling Hz': [
        'Cooling Power', 'Heating Power',
        'Heating Hz', 'Ref Qty'
    ],
    'Heating Hz': [
        'Cooling Power', 'Heating Power',
        'Cooling Hz', 'Ref Qty'
    ]
}

## 스냅샷 테스트 구조
- features_power_candidates.json
  → RFE 입력 후보 풀 감시
- features_power_selected.json
  → RFE 최종 선택 결과 감시
- 둘 다 필요 (후보만 있으면 RFE 결과 변화 감지 불가)

## V2 시행착오 - 반드시 기억할 것
- preprocess_version을 XGBoost 객체에 직접 붙이면
  버전 업데이트 시 날아갈 위험
  → OptimalModel 데이터클래스 속성으로 관리
- CSPF, HSPF는 Rule-based 계산값이라
  피처 풀 자체에 없음 → Leakage 검증 대상 아님
- Ref Qty 누락이 가장 발견하기 어려운 Leakage
  (모델2 타겟인데 모델1 후보에 포함될 수 있음)

 6. model_registry_pattern.md
# MODEL_REGISTRY 패턴 (모델 확장성 설계)

## 목적
모델 추가 시 여러 파일을 동시에 수정해야 하는
구조적 문제를 해결.
MODEL_REGISTRY 하나만 수정하면
trainer, predictor, test 전체에 자동 반영.

## V2의 문제
모델 하나 추가 시 아래 파일 전부 수정 필요:
- constants.py  → TARGETS 추가
- trainer.py    → mandatory/excluded/leakage 추가
                   학습 분기 추가
- predictor.py  → target_to_key 매핑 추가
- predict_app.py→ 결과 출력 추가
- test_features → leakage 테스트 추가

## V3 목표 구조
# core/models.py
MODEL_REGISTRY = {
    "Cooling Power": ModelConfig(
        mandatory=["R410A", "R32", "R290"],
        excluded=["Cond Volume", "Evap Volume"],
        leakage=[
            "Heating Power", "Cooling Hz",
            "Heating Hz", "Ref Qty"
        ],
        use_rfe=True,
        result_key="cooling_power"
    ),
    "Ref Qty": ModelConfig(
        mandatory=[
            "Cond Volume", "Evap Volume",
            "R410A", "R32", "R290"
        ],
        excluded=[],
        leakage=[
            "Cooling Power", "Heating Power",
            "Cooling Hz", "Heating Hz"
        ],
        use_rfe=False,  # mandatory 고정
        result_key="ref_qty"
    ),
    # 새 모델 추가 = 여기만 수정
}

## 구현 효과
trainer.py:
  for target, config in MODEL_REGISTRY.items():
      # config에서 동적으로 읽어서 학습

predictor.py:
  for target, config in MODEL_REGISTRY.items():
      result[config.result_key] = model.predict(X)

test_features.py:
  for target, config in MODEL_REGISTRY.items():
      assert no_leakage(config.leakage)

## V2 시행착오 - 반드시 기억할 것
- 모델 파일을 power/refqty/hz 3개로 분리했다가
  버전 불일치 위험으로 model.pkl 1개로 통합
  → 처음부터 통합 구조로 설계할 것
- pkl 저장 구조를 딕셔너리로 바꾸면
  SHAP 등 외부 라이브러리 호환성 깨짐
  → OptimalModel 객체를 모델 딕셔너리 value로
    유지하고 save_data 루트에 메타만 추가

7. test_harness_pattern.md
# 테스트 하네스 설계 패턴 (V3 기준)

## 목적
기능 수정 시 기존 ML 모델의 물리적 타당성과
UI 로직이 깨지지 않도록 자동 검증하는 방어막.

## 4단계 Gating Strategy

### 1단계: Feature Harness (매번 실행, ~1초)
목적: 피처 오염 즉시 감지
- MODEL_REGISTRY vs 현재 코드 피처 목록 일치 확인
- Data Leakage 금지 피처 포함 여부 검출
- 스냅샷(candidates/selected) 일치 확인
- 실패 시 학습 진입 자체 금지 (Hard Gate)

### 2단계: UI Logic Harness (UI 수정 시 실행)
목적: UI 상태 제어 로직 검증
- Auto Cols 상태 전환 (Editable/Read-only)
- blockSignals 누락으로 인한 이벤트 루프 감지
- 마스터 드롭다운 변경 시 하위 셀 초기화 확인

### 3단계: ML Sanity Harness (모델 수정 시 실행)
목적: 물리적 타당성 검증
- 단조성 검증:
  capa * 1.1 증가 시
  Power_new >= Power_base * 0.98
  (2% tolerance, 최소 10개 샘플)
- 예측 안정성:
  동일 입력 2회 예측 결과 ±1e-6 이내

### 4단계: Optimization Harness (필요 시에만)
목적: 최적 파라미터 확보
- --run-optuna 옵션 시에만 실행
- Optuna 결과 갱신

## 실행 규칙 (.clinerules 연동)
- UI/데이터/피처 코드 수정 시:
  pytest -m "not slow" 통과 필수
- ML 모델/파라미터 수정 시:
  pytest 전체 통과 필수
- 통과 로그 없이 완료 보고 금지

## 스냅샷 관리 원칙
- candidates 스냅샷: RFE 입력 후보 풀 감시
- selected 스냅샷:  RFE 최종 선택 결과 감시
- 둘 다 필수. 후보만 있으면 RFE 결과 변화 감지 불가
- 의도적 피처 변경 시에만 사람이 직접 갱신
- 학습할 때마다 자동 갱신 금지

## V3 구현 시 주의사항
- conftest.py: QTableView 기반 픽스처로 새로 작성
- test_features.py: MODEL_REGISTRY 기반으로 재작성
  (V2처럼 타겟별 하드코딩 금지)
- UI 하네스: QTableWidget → QTableView 전환으로
  V2 코드 재사용 불가, 새로 작성 필요
- snapshots/: V2에서 그대로 가져와서
  재학습 후 갱신

## MODEL_REGISTRY 기반 자동 테스트 패턴
# V3 test_features.py 구조
from core.models import MODEL_REGISTRY

def test_leakage_all_models():
    for target, config in MODEL_REGISTRY.items():
        for leakage_feature in config.leakage:
            assert leakage_feature \
                not in config.mandatory, \
                f"[{target}] leakage 피처가 " \
                f"mandatory에 포함됨: {leakage_feature}"

def test_snapshot_all_models():
    for target, config in MODEL_REGISTRY.items():
        snapshot = load_snapshot(target)
        current = config.get_candidate_features()
        assert sorted(snapshot) == sorted(current), \
            f"[{target}] 피처 풀 변경 감지"

