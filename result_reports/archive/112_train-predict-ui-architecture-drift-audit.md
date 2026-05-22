# 112 — Train/Predict UI Architecture Drift Audit

## Goal

Calculator UI 가 monolith 화 / token 미적용 / 책임 혼재 위험에
걸렸던 것과 같은 drift 가 `ui/predict_window.py`, `ui/train_window.py`,
`ui/base_model.py`, `ui/base_view.py` 에도 있는지 audit-only 로
확인하고, ML / inverse-search 복귀 시점의 작은 refactor phase 후보로
정리한다.

## Scope

- task 1: app entrypoint + Predict/Train window + base model/view
  responsibility inventory (rg / 필요한 함수 범위만).
- task 2: monolith / hardcoding / duplicate / interface boundary 위험
  분류.
- task 3: `docs/architecture/project_architecture.md` 수정 필요성
  판단.
- task 4: WORK_PLAN 에 ML-return refactor phase 후보 짧게 반영.
- task 5: 본 audit report.

## Non-goals

- `app_predict.py`, `app_train.py`, `ui/predict_window.py`,
  `ui/train_window.py`, `ui/base_model.py`, `ui/base_view.py` 코드
  수정.
- Calculator action model 후속 slice (β/γ/δ) 작업.
- AHRI/EN auto-recompute wiring / Hong Kong HSPF UI / unit adapter /
  ML / inverse-search 구현.
- calculator logic / profile / dispatcher / expected / fixture / xfail
  수정.
- result report lifecycle maintenance.
- `ACTIVE_DOCUMENTS.md`, `project_log.md` 수정.

## Verification

- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → 3 passed
- `python3 -B -m pytest -q`
  → 462 passed, 6 skipped, 23 xfailed
- 코드 변경 없음. diff 는 본 report + WORK_PLAN 1줄.

## Entrypoint inventory

| File | LOC | 책임 |
| --- | --- | --- |
| `app_predict.py` | 29 | `QApplication` 생성, `Fusion` style, `setup_global_exception_handler`, `PredictWindow()` 생성/표시, event loop. ML 로딩이나 UI wiring 직접 호출하지 않음 — thin entrypoint. |
| `app_train.py` | 26 | 위와 동형 + `TrainWindow()` 사용. Thin entrypoint. |

두 entrypoint 모두 thin (≤ 30 lines, business logic 없음). drift
징후 없음.

## Predict UI responsibility inventory

`ui/predict_window.py` (164 lines, 단일 class `PredictWindow`,
`QMainWindow`):

| 책임 영역 | 위치 | 메모 |
| --- | --- | --- |
| 의존성/모델 로드 | `__init__` (`load_mapping_data`, `load_model`) | ML model 로드 실패는 `print` 만 + `self.ml_model_data = None`. user-facing surface 는 `lbl_status` 만. |
| UI setup | `_setup_ui` | 상단 button row + `HVACTableModel` + `HVACTableView`. inline hex `#E6F3E6` on `btn_predict`. |
| signal wiring | `_connect_signals` | `btn_predict.clicked`, `btn_clear.clicked`, `table_model.dataChanged`. 단 한 곳에 집중. |
| ODU cascading | `_update_odu_cascading` | `self.mapping_data["odu_cascade"]` magic key 직접 조회. 결과는 view.update_dropdown_items() 로 전달. |
| Cond Index lookup | `_check_and_fill_cond_specs` | `"odu fin pi row"` literal join 으로 `cond_specs` key 생성. mapping miss 시 cells 비움. |
| Cascade-triggered cell clear | `_clear_cells` + on_data_changed | ODU 변경 시 dependent column 비움 (`COL_FIN_TYPE, COL_PI, COL_ROW, COL_COND_AREA, COL_COND_VOLUME`). 무한 루프 방지로 값 있을 때만 setData. |
| Predict execution | `on_predict_clicked` | `predict_row(self.ml_model_data, row_dict)` 호출 + 결과를 7개 result column 에 writeback (`COL_COOLING_POWER`, `COL_CSPF`(="TODO: 입력부족" literal), `COL_HEATING_POWER`, `COL_HSPF2`(="TODO: 입력부족" literal), `COL_REF_QTY`, `COL_COOLING_HZ`, `COL_HEATING_HZ`). magic string result key (`"Cooling Power"`, `"Heating Power"`, `"Ref Qty"`, `"Cooling Hz"`, `"Heating Hz"`) 가 controller 안에 박혀 있음. |
| Table clear (`on_clear_clicked`) | 동일 class | 모든 셀 순회 + setData("",...). 무한 루프 방지 주석 있음. |

cascading + 책임이 한 class 안에 모여 있지만 LOC 164 라 monolith 는
아직 아님. 다만 result key SSOT 없이 controller 가 magic string 으로
ML output 을 받는 부분은 ML 복귀 시 schema-aware adapter 로 이관할
후보.

## Train UI responsibility inventory

`ui/train_window.py` (149 lines, 두 class):

`TrainWorker(QThread)`:
- `__init__(data_path)`, `run` → `core.trainer.train_all_models(
  data_path=..., log_callback=self.log_signal.emit)`.
- `log_signal = pyqtSignal(str)` + `finished_signal = pyqtSignal(bool,
  str)` 두 signal 만 export. Worker boundary 자체는 깔끔.

`TrainWindow(QMainWindow)`:

| 책임 | 위치 | 메모 |
| --- | --- | --- |
| Window shell | `_setup_ui` | mapping update row + file picker row + start button + log textedit. inline hex `#FFF2CC` (`btn_update_mapping`), `#E6F3E6` (`btn_start_train`), `#F8F9FA` (log textedit, font `Consolas`). |
| signal wiring | `_connect_signals` | 단일 위치에 모임. |
| Mapping update | `on_update_mapping_clicked` → `select_excel_file` + `update_mapping_to_json` | scripts/update_mapping 의존. |
| File picker | `on_find_file_clicked` → `QFileDialog.getOpenFileName`. |
| Train start | `on_start_train_clicked` | 파일 존재 검증 → 버튼 비활성/문구 변경 → `TrainWorker` 인스턴스화 + signal 연결 + `start()`. 워커 dup 실행 방지. |
| Log routing | `append_log` | `txt_log.append` + 스크롤 bottom 유지. |
| Finish routing | `on_training_finished` | log append + `QMessageBox.information` / `critical` + 버튼 원복 + `self.worker = None`. |

UI ↔ worker boundary 가 비교적 잘 분리됨 (signal 만 cross). drift
징후 약함. inline hex / token 미적용 정도가 주요 시정 후보.

## Base model / view responsibility inventory

`ui/base_model.py` (`HVACTableModel`, 144 lines):
- `core/constants.COLUMNS` / `DROPDOWN_TARGET` 를 SSOT 로 사용.
- `setData` 가 INPUT + dropdown 경우 `on_dropdown_changed` 호출 →
  1-step cascading (IDU 등). ODU 4-step cascading 은 `PredictWindow`
  쪽에서 별도 처리 (architecture doc §3.2 와 일치).
- `get_row_as_ml_dict`: ML feature dict 변환. 여기서 `["R410A", "R32",
  "R290"]` / `["EEV", "Capi"]` literal 이 직접 박혀 있음.

`ui/base_view.py` (`HVACTableView` + `DropdownDelegate`, 132 lines):
- `DropdownDelegate` 가 paint / createEditor / setEditorData /
  setModelData / editorEvent 모두 구현. `QTimer.singleShot(0,
  cb.showPopup)` 사용 → 1-click editor UX 규칙 준수.
- `setup_delegates` 가 column dropdown items 를 mapping_data 와
  `ref_type` (`["R410A", "R32", "R290"]`) / `exp_type` (`["EEV",
  "Capi"]`) literal 로 빌드.
- `update_dropdown_items` 가 외부 (`PredictWindow._update_odu_cascading`)
  에서 호출 가능하도록 노출.

분리 자체는 이미 model/view/delegate 3분할 — 03/adapter 요구를 큰
틀에서 만족. 단, 위 literal 중복이 base_model/base_view 양쪽에 존재.

## Architecture drift findings

### Monolith / size

- 가장 큰 위험 후보였던 `ui/calc_window.py` (~822 LOC) 와 달리,
  Predict/Train window 는 ≤ 164 LOC 로 작다. Predict/Train 쪽은
  아직 monolith 가 아님.
- Calculator UI 와의 차이: Calculator 는 ISO/EN/AHRI 세 tab 의
  init + read + calculate 가 한 class 에 모여 있어 ~800 LOC. Train/
  Predict 는 각 window 가 단일 주 시나리오 (예측 1 화면, 학습 1
  화면) 이므로 자연스럽게 작다.

### Controller responsibility 누적

- Predict: cascading lookup + cond_specs lookup + result writeback 이
  한 controller 에 모여 있음. 작지만 cascading helper / result
  adapter 로 향후 분리 후보 (다만 ML 복귀 직전까지는 LOC 가 작아 즉시
  분리 필요는 없음).
- Train: worker / window boundary 가 잘 분리되어 있음. drift 미세.

### Business / data transformation 박힘

- `PredictWindow.on_predict_clicked` 에 ML result key magic string
  (`"Cooling Power"` 등) 이 직접 박혀 있다. `core/models.py` 의
  `MODEL_REGISTRY.result_key` SSOT 와 unbinding. ML 복귀 시 result
  adapter (예: `core/calculator_result_adapter.py` 와 같은 layer)
  의 predict 버전이 자연스러운 위치.
- `HVACTableModel.get_row_as_ml_dict` 에 `["R410A", "R32", "R290"]`,
  `["EEV", "Capi"]` 가 base_view.py 의 `setup_delegates` 와 **이중**
  으로 박혀 있음. core SSOT (예: `core/constants.py`) 에 single
  source 로 두는 편이 안전.

### Hardcoding / token 미적용

- inline hex: predict 1곳 (`#E6F3E6`), train 3곳 (`#FFF2CC`,
  `#E6F3E6`, `#F8F9FA`). `ui/theme.py` (108) 의 token (e.g.
  `color.accent`, `color.bg.app`) 으로 옮길 후보. 단 Calculator 처럼
  inline 일괄 치환은 본 audit scope 밖.
- string-as-status: predict 의 `"TODO: 입력부족"` literal 이 result
  cell 에 직접 쓰여짐. CSPF/HSPF2 자리. 향후 calculator 연동 (ML →
  unit adapter → calculator → result envelope) 시 자연스럽게 제거
  대상.

### `blockSignals` / signal / cascading 안전성

- `PredictWindow.on_data_changed` 는 ODU 변경 시 dependent column 을
  비우는데, `_clear_cells` 가 "값이 있을 때만 setData" 로 무한 루프
  방지. `try/finally blockSignals` 자체는 사용하지 않지만 idempotent
  guard 로 안전성 확보.
- `HVACTableModel.on_dropdown_changed` 는 model 내부 dict 에 직접
  write (`self._data[row][i] = ...`) 하고 마지막에 한 번
  `dataChanged.emit` 만 발생. setData 재진입 없음 → 안전.
- 다만 architecture doc §3.3 의 "blockSignals 는 반드시 try/finally"
  가이드라인을 future refactor 에서 cascading 경로에도 명시적으로
  적용할 후보 (현재 시점에는 setData 재진입이 없어 위반 아님).

### Worker / thread boundary

- `TrainWorker.run` 이 `train_all_models(data_path, log_callback=
  self.log_signal.emit)` 를 호출. `log_callback` 으로 stdout 식
  지속 보고. exception 은 `finished_signal.emit(False, ...)` 로
  surface. UI 와의 결합도 낮음 — 두 signal 만 cross.
- 개선 여지: worker module 을 `ui/train_window.py` 가 아니라 `ui/
  workers/` 또는 `core/runners/` 같은 layer 로 분리하는 안.
  현재 LOC 가 작아 시급성은 낮음.

### UI/UX SSOT 적용 대상 여부

- 03 (spreadsheet table UX) / adapter (PyQt) 적용 대상: Predict 의
  `HVACTableView` 는 single-selection + dropdown delegate 기반.
  copy/paste TSV 같은 spreadsheet UX 는 현재 미지원 (입력 1 cell ↔ 1
  ODU 1 spec 흐름). 03 contract 의 "spreadsheet-like editable table"
  정의에 정확히 부합하지는 않음 (multi-cell paste / TSV 가 UX 의
  primary 요구가 아님). 03 contract 의 §10 keyboard-only workflow,
  §6 navigation, §8 cell states 정도는 ML 복귀 시 점검 대상.
- 00 (common UX) 적용 대상: 두 window 의 button label, status
  feedback, error popup 모두 00 §4/§5/§6 의 약한 위반/모호 영역이
  존재 (예: predict 의 "✅ N개 행 예측 완료" 한 줄 status, train 의
  `QMessageBox` info/critical 두 모드). 즉시 fix 필요까지는 아님.
- 02 (design tokens): inline hex 가 토큰 외부에 있음. 108 token
  foundation 으로 단계적 흡수 가능.

### Calculator UI 와의 유사점 / 차이점

| 항목 | Calculator UI | Train/Predict UI |
| --- | --- | --- |
| Monolith 위험 | 큼 (822 LOC) | 낮음 (≤ 164 LOC) |
| token 미적용 inline hex | 다수 (108/109 에서 점진 정리 중) | 소수 (4 곳 정도) |
| 책임 혼재 | tab init + read + calc 가 한 class | controller 위주, worker 분리, helper 일부 |
| Spreadsheet table contract | 03+adapter 적용 (108~111) | 03 contract 의 일부만 해당 (dropdown table) |
| Action model | mixed (auto vs explicit) — 110 micro-design 으로 정리 중 | 단순 (button-driven) |
| ML 결과 schema 결합 | calculator envelope (`core/calculator_result_adapter.py`) | predict_window 가 magic string 직접 사용 |
| 우선순위 | 현재 active sequence | ML 복귀 시 작은 refactor phase |

같은 종류 위험 (책임 혼재, hardcoded literal, inline hex) 은 두 쪽에
모두 있지만, Train/Predict 쪽은 LOC 가 작고 사용 빈도 / 변경 빈도가
낮아 지금 손대는 비용-효익이 낮다. ML 복귀 시점에 함께 묶는 편이
자연.

## Architecture doc update judgment

- 현재 `docs/architecture/project_architecture.md` §3.2, §3.3 는 이미
  다음을 명시:
  - INPUT/AUTO/RESULT column 그룹 (`COLUMNS` SSOT)
  - IDU 단순 매핑은 `ui/base_model.py`, ODU 4-step cascading 은
    `ui/predict_window.py`
  - DROPDOWN_TARGET / ml_feature 매핑 SSOT 위치
  - QTableView + QAbstractTableModel + QStyledItemDelegate 패턴
  - QTableWidget / setCellWidget 신규 금지
  - INPUT/AUTO/RESULT bg color convention
  - `blockSignals` try/finally
  - 1-click editor lifecycle + `QTimer.singleShot`
  - Paste path isolation
  - Handler naming stability
  - Train/Predict UI 와 Calculator UI 의 분리 원칙
  - UI/UX SSOT (`docs/ui_ux/`) 위치
- 본 audit 에서 확인된 위험 (controller responsibility 누적, ML result
  key magic string, ref/exp literal 중복, inline hex) 은 위 guardrail
  의 **위반** 이 아니라 "guardrail 안에서 ML 복귀 시 정리해 두면 좋을
  follow-up" 수준.
- 따라서 architecture 문서 본문은 **수정하지 않는다**. 추가 guardrail
  은 가독성 손실 대비 가치가 낮고, ML 복귀 phase 에서 구체 계획이
  나오면 그때 dev_notes 또는 design doc 으로 기록하는 편이 안전.
- 이 결정 자체는 본 report 와 `docs/WORK_PLAN.md` 에 명시 → 다음
  refactor phase 에서 architecture 문서 갱신 여부를 재판단할 수
  있음.

## Future ML-return refactor plan

ML / inverse-search 복귀 phase 시작 직전 또는 직후의 작은 refactor
phase 후보. Calculator action model / unit adapter / ML 본 구현과는
**섞지 않는다.**

후보 (size order, 모두 small):
1. **app entrypoint thin invariant 유지** — `app_predict.py`,
   `app_train.py` 가 늘어나지 않도록 guard test 또는 LOC budget 같은
   소소한 보호. 본 audit 기준으로는 이미 thin.
2. **PredictWindow controller 책임 정리** — `_update_odu_cascading`,
   `_check_and_fill_cond_specs`, `on_predict_clicked` 의 result
   writeback 을 helper 모듈 또는 result adapter 로 분리. `cond_specs`
   key 빌드 (`f"{odu} {fin} {pi} {row}"`) 도 named helper 로 옮김.
3. **ODU cascading helper 분리 검토** — 4-step cascading 을
   `ui/cascade/odu_cascade.py` 같은 작은 helper module 로 빼서
   PredictWindow 의존성을 줄임. 아직 LOC 가 작아 즉시 분리 비용
   대비 효익 낮음 — refactor phase 에서만.
4. **TrainWorker / TrainWindow boundary 정리** — `TrainWorker` 를
   `ui/workers/train_worker.py` 또는 `core/runners/` 로 이동.
   `log_signal` / `finished_signal` schema 만 contract 로 명문화.
5. **inline style → token 적용 검토** — predict 의 `#E6F3E6`, train
   의 3 hex 를 `ui/theme.py` token 으로 단계적 교체 (108 의 PoC 와
   동일 방식). Calculator 와 같은 token registry 공유.
6. **ML result key SSOT 정렬** — `PredictWindow.on_predict_clicked`
   의 magic string (`"Cooling Power"` 등) 을 `core/models.py` 의
   `MODEL_REGISTRY.result_key` (또는 동등) 와 알 수 있게 매핑 helper
   로 옮김. `predict_row` 의 반환 dict schema 도 함께 확인.
7. **`ref_type` / `exp_type` literal SSOT 정렬** — `["R410A","R32",
   "R290"]`, `["EEV","Capi"]` 를 `core/constants.py` 의 single source
   에 두고 `base_model.py` / `base_view.py` 모두 import.
8. **base_model / base_view contract 재확인** — 03/adapter
   접근에서 본 view 가 single-selection + dropdown 위주임을 명문화.
   향후 spreadsheet UX (TSV paste, undo) 가 Predict 에 필요해지면
   `SpreadsheetTableModel` 으로 옮길지 여부 명시.

이들 후보는 ML / inverse-search 복귀가 시작될 때 별도 micro-design
한 page 로 묶어서 1~2 commit 분량의 작은 refactor 로 처리한다.
Calculator action model slice (β/γ/δ), unit adapter 확장, ML 본
구현과는 **mix 하지 않는다.**

## Recommended next action

본 audit 의 직접적인 next action 은 없음. 현재 immediate sequence
(Slice β AHRI/EN auto-recompute wiring) 그대로 진행한다. 본 audit
결과는 WORK_PLAN 의 future refactor phase 후보로만 반영된다.

## Known Failures / Risks

- result report lifecycle maintenance pending — `result_reports/
  active/` 누적이 trigger 부근. 별도 lifecycle maintenance step 에서
  처리.
- `ACTIVE_DOCUMENTS.md`, `project_log.md` 본 audit 에서 수정 안 함
  (audit-only).
- 본 audit 에서 확인한 위험은 모두 즉시 수정 대상이 아님. 미반영
  채로 시간이 지나면 위험이 커질 수 있어, ML / inverse-search 복귀
  phase 진입 시 본 report 를 다시 참조한다.
