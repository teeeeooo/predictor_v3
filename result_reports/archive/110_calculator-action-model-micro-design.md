# 110 — Calculator Action Model Micro-Design

## Goal

Calculator UI 의 action model (auto-calc vs explicit) 을 새 UI/UX SSOT
기준으로 정리하기 위한 micro-design. 결정 + 구현 slice 분할까지 만
하고, UI 코드 / tests / calculator logic / unit adapter / ML 은 수정
하지 않음.

## Scope

- task 1: SSOT 문서에서 action model 판단 기준 추출.
- task 2: 현재 calculator UI 의 action flow inventory.
- task 3: Option A (auto-calc 통일) vs Option B (explicit 통일) 비교 +
  추천.
- task 4: 추천 option 기준 구현 slice 분할.
- task 5: design 문서 작성, WORK_PLAN 갱신, 본 report.

## Non-goals

- UI 코드 수정 / tests 수정 / 계산 로직 수정 / profile 수정 / unit
  adapter / ML / Hong Kong HSPF UI surface.
- 다음 구현 prompt 작성.
- result report lifecycle maintenance.

## Verification

- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → 3 passed
- `python3 -B -m pytest -q`
  → 462 passed, 6 skipped, 23 xfailed
- 코드 변경 없음. diff 는 본 report + design doc + WORK_PLAN 1줄.

## Task Results

### task 1 — SSOT 기준 추출

확인한 문서:
- `docs/ui_ux/00_UI_UX_SYSTEM.md`
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`
- `result_reports/active/107_calculator-ui-ux-audit-against-ssot.md`
- `result_reports/active/108_calculator-ui-design-token-foundation.md`
- `result_reports/active/109_en14825-layout-polish.md`
- `docs/WORK_PLAN.md`

Action model 결정에 직접 영향을 주는 기준:
- 00 §3 "Reduce required clicks for the primary task." → auto 쪽으로
  pull.
- 00 §4 "Disabled buttons must look disabled. Do not silently no-op a
  fully-styled active button." → 현재 ISO tab 의 `계산 실행` 버튼은
  active 상태로 보이지만 `calculate_iso()` 가 `pass`. SSOT 위반.
- 00 §5 / §6 progress + completion + error feedback. 현재 recompute
  는 ≪1s 이라 progress dialog 불필요. error 는 `QMessageBox.warning`
  / `critical` 사용 — `critical` 은 raw exception string 노출 위험
  (00 §10 "Stack traces shown directly to the end user" 잠재 위반).
- 00 §10 "Buttons that look like buttons but do nothing" — ISO tab
  에서 명확히 위반.
- 03 §10 keyboard-only workflow. auto-calc 든 explicit 든 keyboard
  만으로 가능해야 함. 둘 다 만족 가능.
- 03 / adapter 는 auto-calc vs explicit 결정에 침묵. 프로젝트 결정.
- 02 (design tokens) 는 action model 과 무관. 색 / spacing 만.
- 107 audit 의 gap 4 (interaction / action model gap) 가 본 작업의
  원인. 108 (token foundation) / 109 (EN layout polish) 는 이미
  완료이고 action model 결정을 의식적으로 미뤘다.

문서 간 충돌: 없음. SSOT 는 auto vs explicit 를 명시 강제하지 않고,
"smallest sufficient clicks" 와 "no dead button" 원칙 안에서 프로젝트
결정에 위임함. 본 design 이 그 결정을 명시한다.

### task 2 — 현재 Calculator UI action flow inventory

확인한 코드 / 테스트 (rg / 필요한 범위만 sed):
- `ui/calc_window.py`: `init_ui`, `on_calculate`, `calculate_iso`,
  `calculate_ahri`, `calculate_hspf2_v3`, `calculate_en`,
  `_read_*_table_points*`.
- `ui/calculators_2point.py`: `TwoPointTableModel` (debounce 300ms,
  `model_results_changed` / `row_updated` `pyqtSignal`),
  `ProfileInputGridModel.values_changed = pyqtSignal()`,
  `IsoCspfSingleWidget._install_input_grid` /  `_recalculate` /
  `_apply_profile`, `_build_hong_kong_inputs`, `_build_saso_inputs`.
- `ui/spreadsheet_table.py`: `SpreadsheetTableModel` (`dataChanged`
  emit 만, `values_changed` 등가 signal **없음**).
- `tests/test_app_calculator_ui_smoke.py`,
  `tests/test_iso16358_table_excel_like_behavior.py`,
  `tests/test_iso16358_result_table_copy_tsv.py`.

Tab 별 현재 action model:

| Tab | Trigger | 결과 surface | 오류 surface |
| --- | --- | --- | --- |
| ISO (`IsoCspfSingleWidget`) | auto-calc. `ProfileInputGridModel.values_changed`, `declared_capacity.textChanged`, `chk_saso_min.toggled`, profile combo. `TwoPointTableModel` 은 자체 debounce 300ms. | tab-local `RegionResultTableModel` + `status` `QLabel` + `RegionDetailTab` (`TwoPointTableView`, `TraceDetailPanel`, `BinGraphWidget`) | inline cell background / tooltip via `ProfileInputGridModel`. `QMessageBox` 없음. |
| AHRI SEER2 | explicit `계산 실행`. `on_calculate` → `calculate_ahri` (`test_points = _read_ahri_seer2_table_points`). | window-level `result_label` `QLabel` (한 줄 텍스트) | `InputValidationError` → `QMessageBox.warning` + red border. 기타 → `QMessageBox.critical(str(e))`. |
| AHRI HSPF2 v3 | `calculate_ahri` 안에서 system_type == HP 일 때 `calculate_hspf2_v3()` 체이닝. SEER2 결과 string 뒤에 concat. | 동일 `result_label`. | 동일. |
| EN SEER | `on_calculate` → `calculate_en` (`_read_en_table_points_kw` + W→kW). | `result_label`. | 동일. |
| EN SCOP (multi-climate) | 동일. 선택된 climate 마다 climate-dict 의 model 값을 W→kW 변환 후 `calculate_scop` 호출. | `result_label` (한 줄에 climate 들 concat). | 동일. |
| Hong Kong HSPF | profile/dispatcher 만 등록. **UI 진입점 없음.** | — | — |

핵심 비대칭 (audit 107 에서 식별):
- `계산 실행` 버튼은 window 하단에 항상 보이지만 ISO tab 에서
  `calculate_iso()` 가 `pass`. SSOT 00 §10 위반.
- 결과 surface 가 ISO (rich panel) vs AHRI/EN (single line label)
  로 비대칭.
- error surface 가 ISO (inline cell) vs AHRI/EN (QMessageBox) 로
  비대칭.
- `SpreadsheetTableModel` 에는 `values_changed` signal 이 없어서
  현재 그대로는 AHRI/EN 의 auto 트리거가 불가능 — 적용 시 신호
  추가 필요.

테스트 보호 범위:
- `tests/test_app_calculator_ui_smoke.py` 의 AHRI/EN smoke 는 **button
  click → result_label** 경로를 검증. ISO 의 auto 경로는 직접 smoke
  하지 않음 (model-level golden 으로 간접 보호).
- `tests/test_iso16358_*` 는 ISO 계산 결과를 model-level golden
  으로 보호. UI trigger 경로는 보호되지 않음.
- `tests/test_spreadsheet_table_*` 는 TSV / paste / clear / undo /
  navigation 같은 공통 contract 보호. 재계산 path 는 보호 범위 밖.

### task 3 — Option A / Option B 비교

`docs/designs/2026-05-22-calculator-action-model-alignment.md` 의
"Comparison" 표를 참고. 요지 요약:

- **사용자 입력 흐름**: A = 0 click, B = +1 click per change. A 우세.
- **오류 피드백**: A 는 inline + status banner 로 통일 가능. B 는
  현재 popup `QMessageBox.warning` 을 유지하는 흐름. A 우세.
- **result stale 위험**: A 는 debounce 로 항상 fresh. B 는 사용자
  잊기 가능. A 우세.
- **구현 surface**: A = `SpreadsheetTableModel` 에 `values_changed`
  추가 + AHRI/EN re-wire + tab-local result panel. B = ISO debounce /
  `values_changed` 분리 해제 + tab-local result panel 회수 + window-
  level result_label 일관화. 양쪽 surface 비슷한 크기. B 가 기존
  강점 (ISO panel) 을 깎는 방향이라 손해.
- **테스트 영향**: A = 기존 button click smoke 유지 + auto trigger
  smoke 추가. B = ISO 에 button click smoke 새로 작성 (현재 없음).
  A 가 호환성 더 좋음.
- **HK HSPF UI 와의 궁합**: HK HSPF UI 는 `IsoCspfSingleWidget` 의
  shared shell 에 붙는 게 자연. ISO 가 이미 auto-calc 이므로 A 와
  자연스럽게 맞물림. B 는 HK HSPF UI 도 explicit 으로 바꿔야 함.
  A 우세.
- **ML / unit adapter 독립성**: A 와 B 모두 calculator core / profile
  / unit adapter 미접근. 두 option 모두 ML / unit adapter slice 와
  독립.

**최종 추천: Option A — Auto-calc unified.**

근거:
1. 00 §3 (clicks 최소화) + 00 §10 (dead button 금지) 모두 A 에 우호적.
2. ISO 가 이미 보유한 우수한 result panel + inline error 패턴을
   AHRI/EN 으로 promote 하는 방향이 자연스러움.
3. 향후 HK HSPF UI 가 `IsoCspfSingleWidget` 쪽에 plug-in 될 가능성
   이 높음 — A 와 호환.
4. 구현 risk 가 `SpreadsheetTableModel` 한 곳의 signal 추가에 집중
   되어 contained.

Option B 제외 이유:
- 사용자에게 click 비용 증가.
- 기존 ISO panel UX 를 약화 (regression).
- error popup 흐름이 그대로 유지되어 00 §10 위반 가능성 (stack
  trace 노출) 이 해소되지 않음.

### task 4 — 다음 구현 slice 분할

전체 4 slice (α → β → γ → δ). 절대 섞이지 않을 항목 명시.

#### Slice α — `SpreadsheetTableModel.values_changed` signal
- 목적: AHRI/EN 공통 model 에 ISO grid 와 동일한 high-level
  `values_changed` signal 추가.
- 수정 대상 후보: `ui/spreadsheet_table.py`,
  `tests/test_spreadsheet_table_model.py`.
- 포함: `pyqtSignal()` 선언 + set/paste/clear/undo emit + 단위 test.
- 제외: AHRI / EN calc path, layout, button-click smoke, ISO 경로,
  result panel, error policy.
- 선행: 없음.
- 검증: `tests/test_spreadsheet_table_model.py`,
  `tests/test_spreadsheet_table_view.py`, full suite.

#### Slice β — AHRI / EN auto-recompute wiring
- 목적: Slice α 의 signal 을 AHRI SEER2 / HSPF2 / EN SEER / SCOP 에
  연결, debounced auto-recompute. window-level `계산 실행` 버튼은
  optional 'Recalculate now' 로 격하.
- 수정 대상 후보: `ui/calc_window.py`, smoke test.
- 포함: per-tab debounce slot (`_recalculate_ahri`/`_recalculate_en`),
  compute path 와 button click path 가 같은 helper 호출하도록 refactor,
  tab-local result text label.
- 제외: ISO 경로, result panel polish (γ), error policy (δ), HK HSPF
  UI, unit adapter, layout token 추가.
- 선행: Slice α.
- 검증: 기존 button smoke 유지 + edit→auto-recompute smoke 추가
  (signal 직접 호출 방식; debounce wall-clock 의존 회피).

#### Slice γ — Per-tab result / status surface unification
- 목적: 모든 tab 에 같은 result table / metric line + status label
  형태 부여. window-level `result_label` 단일 라인 제거 / fallback
  으로 격하.
- 수정 대상 후보: `ui/calc_window.py` (작은 helper `_CalculatorResult
  Panel` 도입 가능), 108 token spacing 활용.
- 포함: layout 수준 result surface 만. table contract 변경 없음.
  validation rewiring 없음.
- 제외: ISO `RegionResultTableModel` 내부 변경, AHRI/EN compute
  로직 (β 에서 끝남), error feedback (δ), HK HSPF UI.
- 선행: Slice β.
- 검증: objectName / 부모 layout index smoke (109 의
  `test_en_standby_group_is_positioned_above_*` 와 같은 스타일).

#### Slice δ — Error feedback alignment
- 목적: input validation 실패 시 popup `QMessageBox.warning` 제거,
  per-tab status banner + 기존 red-border (108 PoC) 만 사용. 기타
  exception 은 `QMessageBox.critical` 유지하되 메시지 truncation +
  trace logging.
- 수정 대상 후보: `ui/calc_window.py`.
- 포함: error routing + 메시지 표현만. validator 미수정.
- 제외: `_get_float_val` / `_read_*_table_points` 내부 validation
  규칙 변경, table coloring contract.
- 선행: Slice γ.
- 검증: `QMessageBox.warning` monkeypatch 로 호출 안 됨 확인 + status
  banner text smoke.

#### 추천 next action

**Slice α 1개.** 가장 작고 backward-compatible 한 변경 (model 에
signal 추가). β/γ/δ 모두 의존. 본 slice 가 안전하게 끝나면 후속
slice 가 한 번에 하나씩 풀린다.

### task 5 — design 문서 / WORK_PLAN / report

- 신규 design doc 작성: `docs/designs/2026-05-22-calculator-action-
  model-alignment.md` (Background / Current behavior / SSOT criteria /
  Option A / Option B / Decision / Implementation slices / Non-goals /
  Test strategy / Status 섹션 포함).
- `docs/WORK_PLAN.md` Near-term sequence 항목 3.4 (Calculator auto-
  calculate behavior alignment) 에 micro-design 완료 + 결정 (Option A)
  + 다음 구현 slice α 진입 명시. 다른 항목 (HK HSPF UI, unit adapter,
  ML) 순서 유지.
- `ACTIVE_DOCUMENTS.md`, `project_log.md` 미수정. 본 design doc 은
  새 active doc 이지만, 본 작업이 audit/design-only 라서 inventory
  업데이트는 구현 slice 가 끝난 뒤 함께 정리하는 편이 안전 (현재
  결정만 있고 후속 변경이 따라옴). 추후 lifecycle maintenance 에서
  반영.
- result report lifecycle maintenance 는 본 작업 범위가 아니며,
  `result_reports/active/` 누적이 trigger 부근까지 가 있지만 본
  작업이 design-only 라서 별도 lifecycle maintenance step 으로
  분리한다. Known Risks 에 pending 으로만 기록.

## Test Results

- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → 3 passed
- `python3 -B -m pytest -q`
  → 462 passed, 6 skipped, 23 xfailed

## Changed Files

- A `docs/designs/2026-05-22-calculator-action-model-alignment.md`
- M `docs/WORK_PLAN.md` (sequence 짧게 갱신)
- A `result_reports/active/110_calculator-action-model-micro-design.md`

## Known Failures / Risks

- result report lifecycle maintenance pending — `result_reports/
  active/` 누적이 trigger 부근. 본 design-only 작업에서는 처리하지
  않음.
- `ACTIVE_DOCUMENTS.md` 에 새 design doc 의 row 가 추가되지 않은
  상태. 구현 slice α/β 가 끝난 시점에 일괄 반영하는 편이 안전. 본
  report 의 Known Risks 로 명시.
- Slice β 의 result text 위치 (tab-local label) 와 Slice γ 의 result
  panel 디자인 사이 mismatch 가 나지 않게 β/γ 작업 시 design doc 의
  Implementation slices 섹션을 다시 확인할 것.

## Next Suggested Action

**Slice α — `SpreadsheetTableModel.values_changed` signal 추가.**
가장 작고 backward-compatible. β/γ/δ 의 진입점.

## Scope Compliance

- UI 코드 / tests / calculator logic / profile / dispatcher / expected
  / fixture / xfail 미수정.
- unit adapter / ML / Hong Kong HSPF UI surface 미수정.
- `ACTIVE_DOCUMENTS.md`, `project_log.md`, archive / summaries 미수정
  / 미이동.
- AGENTS_FULL.md 미열람.
- 구현 prompt 미작성.

## Commit / Push

- design doc + WORK_PLAN + 본 report 묶음.
- commit message: `design: decide calculator action model alignment`
- report commit message: `report: 110 calculator action model micro-design`
- push to `work/ui-ux-ssot-adoption`.
