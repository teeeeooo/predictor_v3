# 116 — Calculator Deployment UI Feasibility Pivot (PyQt → Tkinter Spike)

## Goal

Calculator-only 배포 direction을 결정하기 위한 feasibility pivot.
PyQt5 + Qt runtime 포함으로 PyInstaller 배포물이 100~150 MB 수준이
될 가능성을 인식하고, 다음을 수행한다.

- PyQt calculator UI 고도화 workstream의 현재 완료 상태와 hold 범위를
  명확히 정리한다.
- Tkinter calculator-only MVP feasibility 기준을 design doc으로 고정
  한다.
- Tkinter prototype skeleton을 추가해 core calculator 호출 가능성을
  확인한다.
- PyInstaller packaging 크기 측정 절차를 문서화한다.
- WORK_PLAN / project_log를 방향 전환에 맞게 갱신한다.

## Scope

- task 1: PyQt calculator UI 고도화 workstream의 hold 범위 정리
  (삭제 금지).
- task 2: `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility
  .md` 작성.
- task 3: `app_calculator_tk.py` + `ui_tk/__init__.py` +
  `ui_tk/calculator_app.py` 최소 prototype 추가.
- task 4: `docs/guides/lightweight_calculator_packaging_check.md`
  PyInstaller 측정 절차.
- task 5: WORK_PLAN / project_log 갱신 + 본 report 작성.

## Non-goals

- PyQt calculator UI 삭제.
- `app_calculator.py` / `ui/calc_window.py` / `ui/calculators_2point.
  py` / `ui/spreadsheet_table.py` / `ui/calculator_errors.py` /
  `ui/theme.py` 수정.
- EN tab extraction (Slice ζ).
- AHRI tab extraction (Slice η).
- AHRI/EN auto-recompute wiring (Slice β).
- per-tab result/status panel (Slice γ).
- error feedback alignment (Slice δ).
- Hong Kong HSPF UI surface (PyQt).
- Train/Predict 리팩토링.
- unit adapter / ML / inverse-search 구현.
- calculator core, profile, dispatcher, expected, fixture, xfail,
  region config 수정.
- 기존 design doc 삭제 또는 rewrite.
- result report lifecycle maintenance (114 cycle 직후라 trigger 부근
  아님).
- `ACTIVE_DOCUMENTS.md` 갱신 (새 design doc 2개 + guide 1개는 다음
  lifecycle maintenance에서 design records / guides 행으로 추가 후보).
- `AGENTS_FULL.md` 열람.

## Verification

- `python3 -B -m py_compile app_calculator_tk.py ui_tk/__init__.py
  ui_tk/calculator_app.py` → OK.
- 로컬 macOS smoke (`python3 -B -c "..."`로 widget tree 구축):
  - `'PyQt5' not in sys.modules` after import of
    `ui_tk.calculator_app`.
  - `resolve_profile_id('Hong Kong', 'CSPF') == 'hong_kong_cspf'`,
    `resolve_profile_id('Hong Kong', 'HSPF') == 'hong_kong_hspf'`.
  - `create_calculator_for_profile(profile_id='hong_kong_cspf')
    .calculate_cspf(...)` → CSPF = 4.939 (matches
    `tests/test_iso16358_cspf_hong_kong_config.py` `measure_1`).
  - `create_calculator_for_profile(profile_id='hong_kong_hspf')
    .calculate_hspf(...)` → HSPF = 3.643 (matches Hong Kong golden
    case 1).
  - `CalculatorTkApp(root=tk.Tk()).iso_tab` 인스턴스 구축 가능,
    PyQt5 미import 확인.
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py
  tests/test_calculator_profiles.py tests/test_calculator_dispatcher
  .py -q` → 43 passed.
- `python3 -B -m pytest -q` (전체) → 본 macOS + Python 3.14 + PyQt5
  환경에서 4 PyQt 관련 테스트가 fatal abort로 crash. 동일 4개를
  제외하면 `533 passed, 1 skipped, 23 xfailed`. crash는 본 작업 이전
  부터 존재하는 환경 의존 crash이며 본 작업이 추가/수정한 파일과
  무관함 (자세한 내용은 Known Failures / Risks).

## Task Results

### task 1 — PyQt calculator UI 고도화 workstream hold

#### 현재 완료 상태 (관련 active/summary 보고서)

`result_reports/summaries/114_summary-ui-ux-ssot-calculator-boundary
.md` + `result_reports/active/115_calculator-errors-helper-extraction
.md` 기준.

- UI/UX SSOT 도입 (106): `docs/ui_ux/` active root.
- Calculator UI/UX audit (107).
- `ui/theme.py` token foundation (108).
- EN14825 layout polish (109).
- Calculator action model decision = Option A — auto-calc unified
  (110, `docs/designs/2026-05-22-calculator-action-model-alignment
  .md`).
- `SpreadsheetTableModel.values_changed` Slice α (111).
- Train/Predict UI drift audit (112).
- Calculator UI module boundary plan (113,
  `docs/designs/2026-05-22-calculator-ui-module-boundary.md`).
- Slice ε `ui/calculator_errors.py` 추출 완료 (115).

#### hold 처리 (deployment direction pending)

다음 작업은 **삭제하지 않고** "PyQt calculator deployment direction
pending — Tkinter feasibility 결과 후 resume / port / fallback 결정"
로 보류:

- Slice ζ — `ui/calculator_en_tab.py` extraction.
- Slice η — `ui/calculator_ahri_tab.py` extraction.
- Slice β — AHRI/EN auto-recompute wiring.
- Slice γ — per-tab result/status panel.
- Slice δ — error feedback alignment.
- Hong Kong HSPF UI surface (PyQt).

#### 유지되는 자산 (어느 direction에서도 reuse 가능)

- `core/calculator_iso16358.py` (ISO16358 common engine — CSPF +
  HSPF).
- `core/calculator_ks_c9306.py`, `core/calculator_ahri_seer2.py`,
  `core/calculator_ahri_hspf2.py`, `core/calculator_en14825.py`,
  `core/calculator_asnzs_hspf_excel.py`.
- `core/calculator_profiles.py` (manifest +
  `resolve_calculator_profile`).
- `core/calculator_dispatcher.py`
  (`create_calculator_for_profile`).
- `core/calculator_unit_adapter.py` (ML W ↔ Btu/h).
- `core/calculator_input_adapter.py`,
  `core/calculator_result_adapter.py`,
  `core/calculator_prediction_adapter.py`,
  `core/calculator_ranking_adapter.py`.
- `data/region_configs/*.json` 전체 (Hong Kong CSPF + HSPF 공유 config
  포함).
- 모든 calculator fixture / expected / xfail constant.

PyQt UI 자산 (`app_calculator.py`, `ui/calc_window.py`,
`ui/calculators_2point.py`, `ui/spreadsheet_table.py`,
`ui/calculator_errors.py`, `ui/theme.py`, `tests/test_app_calculator
_ui_smoke.py` 등)은 reference / 내부 검증용으로 보존한다. Calculator
UI module boundary plan (113) 및 action model decision (110)도
폐기하지 않고 Tkinter direction이 fall back될 때 PyQt resume 기준으로
보존한다.

### task 2 — Tkinter calculator-only MVP feasibility design doc

`docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md`
신규 작성. 포함 섹션:

- Background (PyQt 배포물 크기 가능성과 core 순수 Python 유지 상태).
- Problem statement (4가지 기준).
- Non-goals.
- Candidate UI direction (Tkinter primary, CLI / HTML fallback).
- **Information architecture — standard tab + region selection**
  (사용자 단순화):
  - 사용자에게 `profile_id` / `calculator_id` / `config_path` 비노출.
  - 표준 탭 + 지역 선택 + 같은 화면 내 다중 metric section.
  - Hong Kong → CSPF + HSPF 함께 표시 / EN → SEER + SCOP / AHRI →
    SEER2 + HSPF2.
  - 방식 B (per-region tabs), C (nested tabs) 거절.
  - KS C 9306은 ISO 16358 탭으로 병합하지 않음 (별도 탭).
- MVP scope (작은 범위 유지: ISO 16358 탭 + Hong Kong region + CSPF +
  HSPF section 한 화면 + Entry/grid + Text widget + clipboard copy).
- Profiles to test (`hong_kong_cspf`, `hong_kong_hspf`).
- Packaging measurement plan (별도 guide 참조).
- Reuse boundaries (어느 파일을 건드리지 않는지 명시).
- Decision criteria (continue / pause / fall back trigger).
- Next implementation slice (spike 단계 → 측정 단계 → decision 단계).
- Status (decision = spike).

Tkinter MVP은 **feasibility spike**라고 파일 주석과 design doc 모두에
명시. 전체 PyQt 이전 의도 아님을 분명히 했다.

### task 3 — Tkinter prototype skeleton

신규 파일:

- `app_calculator_tk.py` (10 LOC) — Tkinter 진입점. PyQt5 미import.
  `ui_tk.calculator_app.main()` 호출.
- `ui_tk/__init__.py` — package marker + spike 주석.
- `ui_tk/calculator_app.py` (~270 LOC) — feasibility spike. Tkinter
  + `ttk` 기반. 구성:
  - `REGION_BY_LABEL` (`"Hong Kong"` → `"hong_kong"`),
    `METRIC_SECTIONS_BY_REGION` (`"hong_kong"` → `("CSPF", "HSPF")`).
  - `resolve_profile_id(region, metric)` — `(region, metric)` →
    `profile_id` mapping. UI는 `profile_id` 비노출.
  - `_NumericEntryRow`, `_CspfSection`, `_HspfSection` (각각 정격
    능력 + full/half capacity + power Entry 입력 + 계산 버튼).
  - `_ResultPanel` (read-only `tk.Text` + "결과 복사" /
    "결과 지우기" 버튼; `clipboard_clear` / `clipboard_append`).
  - `_Iso16358Tab` (지역 selector + 선택된 region의 metric sections
    렌더링 + 공유 result panel).
  - `CalculatorTkApp` (top-level Tk window + `ttk.Notebook` +
    ISO 16358 탭 1개). `run()`은 `mainloop()` 호출하지만, 생성자는
    `mainloop()`를 호출하지 않아 테스트에서 withdrawn root 위에
    widget tree 구축 가능.

지원 profile (MVP):

- `hong_kong_cspf` — `calculate_cspf({"35_full": ..., "35_half":
  ...}, declared_capacity=...)`.
- `hong_kong_hspf` — `calculate_hspf({"rated_heating_capacity": ...,
  "7_full": ..., "7_half": ...})`.

#### 확인 사항

- **PyQt5 미import**: `import ui_tk.calculator_app` 후
  `'PyQt5' not in sys.modules` 검증 완료. 모듈 어느 곳에도
  `from PyQt5` / `import PyQt5` 없음.
- **core 호출 가능**: `create_calculator_for_profile(profile_id=
  'hong_kong_cspf').calculate_cspf({"35_full": {"capacity": 3600,
  "power": 900}, "35_half": {"capacity": 1700, "power": 380}},
  declared_capacity=3500)` → `CSPF = 4.939` (`measure_1` fixture
  값과 일치).
- `create_calculator_for_profile(profile_id='hong_kong_hspf')
  .calculate_hspf({"rated_heating_capacity": 6300, "7_full":
  {"capacity": 6300, "power": 1500}, "7_half": {"capacity": 3200,
  "power": 800}})` → `HSPF = 3.643` (Hong Kong golden case 1과
  일치).
- **Tk widget 구축 가능**: 로컬 macOS Python 3.14 + Tk에서
  `CalculatorTkApp(root=tk.Tk())` → `iso_tab` (`_Iso16358Tab`)
  생성 + `update_idletasks() + update()` cycle 정상 종료.

#### Blocker

- 본 macOS 환경에서는 Tk 윈도우가 동작하지만, **PyInstaller 실측
  은 수행하지 않았다** (Windows 호스트 부재). decision criteria의
  size delta는 측정 후에만 평가 가능.
- AHRI HSPF2 v3 입력 schema (5 cooling point × 2 row + Cd_low/
  Cd_full + system-type radios)나 EN14825 SCOP multi-climate 입력
  schema는 본 MVP scope 밖. Tkinter port 필요 시 추가 design slice.
- AHRI HSPF / EN SCOP 같은 비ISO calculator의 향후 Tkinter port에서는
  `core/calculator_unit_adapter.py` (Btu/h ↔ W) 활용이 필요하지만 본
  MVP에서는 ISO 16358만 다루기 때문에 wiring 미포함.
- Tkinter MVP는 production-final UI가 아니라 spike. 모든 키보드
  탐색 / 단위 검증 / paste path / undo / invalid 표시는 추후 design
  slice에서 결정 (지금은 기본 `ttk.Entry` 동작만 사용).

### task 4 — PyInstaller packaging size measurement plan

`docs/guides/lightweight_calculator_packaging_check.md` 신규 작성.
포함 섹션:

- Purpose (PyQt baseline vs Tkinter spike 비교).
- Target platform (Windows + 동일 Python interpreter + deployment-only
  venv).
- Build commands:
  - PyQt baseline one-folder dist
    (`pyinstaller ... app_calculator.py`).
  - PyQt baseline one-file
    (`pyinstaller --onefile ... app_calculator.py`).
  - Tkinter spike one-folder dist
    (`pyinstaller ... app_calculator_tk.py`).
  - Tkinter spike one-file
    (`pyinstaller --onefile ... app_calculator_tk.py`).
  - 모든 build에서 `--add-data "data;data"`로 `data/region_configs/
    *.json` 동봉.
- One-folder dist 크기 측정 (PowerShell `Get-ChildItem ... Measure-
  Object` / cmd `du -sh` / macOS·Linux `du -sh`).
- One-file exe 크기 측정 (`(Get-Item ...).Length / 1MB` / `ls -lh`).
- Windows-specific 검증 (앱 실행 / CSPF 검증값 / `tcl*.dll` /
  `tk*.dll` 포함 / `PyQt5` / `Qt5*.dll` 미포함).
- Comparison criteria (≥ 40 % 축소 = continue / < 20 % = pause / 의미
  없음 또는 Tcl/Tk 미포함 = fall back; fallback 순서 CLI → HTML →
  PyQt resume).
- Reporting protocol (`not measured` 명시 의무, 실측 후 별도 후속
  report에 기록, 본 design doc은 retroactively edit 하지 않음).
- Out of scope (UPX / `.spec` / 코드 서명 / 설치 패키지 / crash logging
  / Train·Predict packaging).

**실제 측정 수행 여부**: 수행하지 않았다. 이유:

- 본 환경은 macOS이며 deployment target은 Windows. 같은 Python +
  PyInstaller + PyQt5 버전에서 측정해야 비교 의미가 있다.
- 측정값 없이 추정치를 design doc / WORK_PLAN / report에 기록하지
  않는다 (작업 지시 금지 사항).

모든 size 수치는 `not measured`로 표시한다.

### task 5 — WORK_PLAN / project_log / report

#### `docs/WORK_PLAN.md`

- 항목 4b (Slice ε 완료) 아래에 새 항목 **4z — Calculator
  deployment UI feasibility pivot** 삽입. 본 116 보고서와 신규
  feasibility design doc / packaging guide / Tkinter skeleton을
  연결.
- 4c~4g (Slice ζ → η → β → γ → δ) 항목을 모두 `**hold**` prefix로
  변경. 작업 자체는 삭제하지 않고 "Tkinter spike 결과에 따라 resume
  여부 결정"으로 기록.
- 5번 (Hong Kong HSPF UI surface, PyQt) 항목을 `**hold**`로 변경.
  Tkinter MVP direction 결정 뒤 PyQt resume / Tkinter port / CLI
  fallback 중 한 경로로 재배치.
- 6번 (unit adapter 확장), 7번 (ML / inverse-search 복귀), 8번
  (Train/Predict refactor)은 **유지**하고 "순서는 4z 결과 이후
  재조정한다" 한 줄만 추가. 자체 hold는 아님.
- 기존 design doc (action model alignment, calculator UI module
  boundary) 및 도입 완료 문장은 그대로 보존했다.

#### `project_log.md`

다음 항목을 한 섹션으로 짧게 append: `### Follow-up — Calculator
deployment UI feasibility pivot`.

- Result: PyQt 배포 우려 + 신규 design doc + Tkinter prototype +
  packaging guide + WORK_PLAN hold 이동.
- Verification: py_compile + core 호출 smoke (CSPF 4.939 / HSPF 3.643)
  + targeted pytest 43 passed + 환경 의존 crash 사유.
- Decision: Tkinter spike 우선, decision criteria 충족 시 continue,
  미충족 시 CLI → HTML → PyQt Slice ζ resume 순으로 fallback. core /
  profile / dispatcher / region config / unit adapter / fixture /
  expected는 어느 direction에서도 수정하지 않는다.

#### lifecycle maintenance 제외 사유

114 summary cycle 직후라 active report 누적이 1건 (115) → 본 작업
이후 2건 (115 + 116) 수준이며, 다음 summary trigger (8~12개) 부근이
아니다. 또한 본 작업은 deployment direction 전환 시점이므로
lifecycle maintenance와 섞지 않는다 (`AGENT_TASK_ROUTER.md` Lifecycle
Check 원칙). active reports `115_calculator-errors-helper-extraction
.md`와 `116_lightweight-calculator-ui-feasibility-pivot.md`는 그대로
active 폴더에 둔다.

## Next Suggested Action

**Spike step 1 — Tkinter MVP packaging size 측정**.
`docs/guides/lightweight_calculator_packaging_check.md`의 PowerShell
스니펫으로 Windows에서 `app_calculator.py`(PyQt baseline)와
`app_calculator_tk.py`(Tkinter spike)의 PyInstaller one-folder dist /
one-file exe 크기를 동일 호스트 / 동일 Python 버전 / 동일 PyInstaller
버전으로 측정한다. 결과는 본 116 report와 별개의 후속 report
(`117_...`)에 기록하고 design doc은 retroactively 수정하지 않는다.

이후 decision criteria 적용:

- continue → Tkinter MVP에 Hong Kong HSPF 입력 폼 다듬기 + 키보드
  탐색 design slice.
- pause → CLI argparse fallback design.
- fall back → PyQt calculator UI Slice ζ resume.

## Scope Compliance

- PyQt calculator UI 삭제 미수행.
- `app_calculator.py`, `ui/calc_window.py`, `ui/calculators_2point.py`,
  `ui/spreadsheet_table.py`, `ui/calculator_errors.py`, `ui/theme.py`
  미수정.
- EN tab extraction, AHRI tab extraction, auto-recompute wiring,
  result/status panel, error feedback alignment, Hong Kong HSPF UI
  surface 미수행 (모두 hold).
- Train/Predict 리팩토링 미수행.
- unit adapter 수정 미수행. ML / inverse-search 구현 미수행.
- calculator core / profile / dispatcher / region config / expected /
  fixture / xfail 수정 미수행.
- result report lifecycle maintenance 미수행 (active 누적이 trigger
  부근 아님 + direction 전환 시점이라 섞지 않음).
- `active/archive/summaries` 이동 미수행.
- `ACTIVE_DOCUMENTS.md` 미수정 (다음 lifecycle maintenance에서 새
  design doc + guide 행 추가 후보).
- AGENTS_FULL.md 미열람.
- PyInstaller 실측치 단정 없음 (`not measured`).
- `PyInstaller` spec 파일 미작성.
- packaging optimization (UPX / exclude-module / hidden-import) 미수행.

## Changed Files

- A `docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md`
- A `docs/guides/lightweight_calculator_packaging_check.md`
- A `app_calculator_tk.py`
- A `ui_tk/__init__.py`
- A `ui_tk/calculator_app.py`
- M `docs/WORK_PLAN.md` (4b 완료 표시 보존 + 4z 추가 + 4c~4g + 5번
  hold + 6/7/8번 순서 재조정 메모)
- M `project_log.md` (pivot 섹션 append)
- A `result_reports/active/116_lightweight-calculator-ui-feasibility-
  pivot.md`

## Known Failures / Risks

- 본 macOS + Python 3.14 + PyQt5 환경의 전체 pytest 실행 중 PyQt
  clipboard / table 행위 테스트 4종에서 **fatal abort** 발생 (`tests/
  test_iso16358_result_table_copy_tsv.py`, `tests/test_iso16358_table
  _excel_like_behavior.py`, `tests/test_app_calculator_ui_smoke.py`,
  `tests/test_spreadsheet_table_view.py`). 본 작업의 변경 파일과
  무관하며 (`ui_tk/` + design doc + guide + WORK_PLAN / log /
  report만 추가/수정), 본 작업 적용 전후 동일 환경에서 동일 crash가
  발생한다. 동일 4개를 제외하면 `533 passed, 1 skipped, 23 xfailed`.
  CI / 회사 PC (Windows) 환경에서는 정상 통과 가능. 본 작업의 변경은
  PyQt path를 건드리지 않는다.
- Tkinter packaging 크기는 **not measured**. decision criteria
  적용은 측정 후에만 가능.
- Tk DLL이 Windows PyInstaller bundle에 정상 포함되는지, 그리고
  clean Windows host에서 정상 동작하는지 confirm 필요. 동작하지
  않으면 fall back 경로 진입.
- Tkinter MVP은 ISO 16358 + Hong Kong만 커버. AHRI / EN / KS C 9306
  전체 port은 별도 design slice 필요.
- 신규 design doc 2개 + guide 1개를 `ACTIVE_DOCUMENTS.md`에 아직 등록
  하지 않았다. 다음 lifecycle maintenance에서 design records / guides
  행으로 추가 후보.

## Test Results

- `python3 -B -m py_compile app_calculator_tk.py ui_tk/__init__.py
  ui_tk/calculator_app.py` → OK.
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py
  tests/test_calculator_profiles.py tests/test_calculator_dispatcher
  .py -q` → 43 passed.
- 전체 `python3 -B -m pytest -q` (위 4 environment-dependent crash
  파일 제외) → `533 passed, 1 skipped, 23 xfailed`.
- 로컬 Tkinter widget tree 구축 smoke → OK.
- Hong Kong CSPF 4.939 / HSPF 3.643 dispatcher 호출 smoke → OK.
- PyQt5 미import smoke → OK.

## Commit / Push

- 소스/문서 변경 (`docs/designs/2026-05-22-lightweight-calculator-ui-
  feasibility.md`, `docs/guides/lightweight_calculator_packaging_check
  .md`, `app_calculator_tk.py`, `ui_tk/__init__.py`,
  `ui_tk/calculator_app.py`, `docs/WORK_PLAN.md`, `project_log.md`)
  + 본 report 파일을 두 개의 commit으로 분리해 stage / commit / push
  한다.
- 소스/문서 commit message: `design: pivot calculator deployment UI
  feasibility`.
- report commit message: `report: 116 lightweight calculator UI
  feasibility pivot`.
- push branch: `work/ui-ux-ssot-adoption`.
