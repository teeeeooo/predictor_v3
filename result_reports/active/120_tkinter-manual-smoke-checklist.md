# 120 — macOS Tkinter Manual Smoke Checklist

## Goal

Windows PyInstaller 실측이 환경 부재로 불가능한 동안, 현재 macOS
환경에서 Tkinter calculator-only MVP의 GUI 동작을 수동 확인할 수
있는 체크리스트를 docs/guides에 고정한다. 코드 변경, 기능 추가,
PyInstaller 실행, PyQt calculator 재개는 본 작업 범위 밖이다.

## Scope

- task 1: 현재 Tkinter MVP의 수동 확인 대상과 기대 결과 정리.
- task 2: `docs/guides/lightweight_calculator_tk_manual_smoke.md`
  체크리스트 작성.
- task 3: 선택적 정적 command 문서화. 새 helper script 추가 없음.
- task 4: WORK_PLAN 업데이트 + 본 report.

## Non-goals

- Tkinter 기능 구현 / module 재분리.
- PyInstaller 실행 / size 추정값 확정.
- PyQt calculator UI 재개 / 삭제.
- `app_calculator.py`, `ui/calc_window.py`, `ui/calculators_2point.py`,
  PyQt tests 수정.
- Train/Predict 리팩토링, unit adapter, ML / inverse-search 구현.
- calculator core / profile / dispatcher / region config / expected /
  fixture / xfail 수정.
- legacy cleanup 실행.
- macOS PyQt fatal-abort 4 파일 crash 해결 시도.
- result report lifecycle maintenance, active/archive/summaries 이동.
- `project_log.md` / `ACTIVE_DOCUMENTS.md` / architecture 문서 수정.
- AGENTS_FULL.md 열람.

## Verification

- `python3 -B -m py_compile app_calculator_tk.py ui_tk/__init__.py
  ui_tk/calculator_app.py ui_tk/profile_resolver.py
  ui_tk/result_panel.py ui_tk/input_widgets.py ui_tk/tabs/__init__.py
  ui_tk/tabs/iso16358_tab.py ui_tk/sections/__init__.py
  ui_tk/sections/iso_cspf_section.py
  ui_tk/sections/iso_hspf_section.py` → OK.
- `python3 -B tools/check_code_structure.py` →
  `code structure guard: OK (no findings)`, exit 0.
- `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py
  tests/test_ui_tk_calculator_foundation.py
  tests/test_calculator_schema_boundaries.py
  tests/test_calculator_profiles.py
  tests/test_calculator_dispatcher.py -q` → **58 passed**.
- 전체 (위 4 PyQt 환경 의존 crash 파일 제외) → **568 passed, 1
  skipped, 23 xfailed**. 119 baseline 568 동일 (본 작업 docs only, test
  변경 없음).

## Task Results

### task 1 — Smoke 대상 + 기대 결과

#### 확인한 smoke 대상 (Tkinter MVP 진입 경로)

- Entrypoint: `app_calculator_tk.py` (16 LOC thin entrypoint, body
  변경 없음).
- Shell: `ui_tk/calculator_app.py` (54 LOC, `CalculatorTkApp` +
  `ttk.Notebook` + ISO 16358 tab 등록).
- Profile resolver: `ui_tk/profile_resolver.py` (pure Python,
  `REGION_BY_LABEL` / `METRIC_SECTIONS_BY_REGION` / `region_labels` /
  `supported_metrics_for` / `resolve_profile_id`).
- Tab: `ui_tk/tabs/iso16358_tab.py` (`Iso16358Tab(ttk.Frame)`, region
  combobox + section factories + result panel).
- Sections: `ui_tk/sections/iso_cspf_section.py` (Hong Kong CSPF —
  35_full/35_half + declared), `ui_tk/sections/iso_hspf_section.py`
  (Hong Kong HSPF — 7_full/7_half + rated heating).
- Result panel: `ui_tk/result_panel.py` (`ResultPanel.append` /
  `set_text` / `clear` / `copy`).
- Input primitive: `ui_tk/input_widgets.py` (`NumericEntryRow`,
  comma/strip/float, allow_empty).

#### 기대 결과 (체크리스트 산정 기준)

| 항목 | 기대값 |
| --- | --- |
| 윈도우 타이틀 | `Calculator (Tkinter)` |
| 표시되는 top-level 탭 수 | 1 (`ISO 16358`) |
| 지역 콤보 옵션 | `Hong Kong` (read-only) |
| Hong Kong 화면 metric sections | CSPF + HSPF 한 화면 |
| `profile_id` / `calculator_id` / `config_path` UI 노출 | 없음 |
| CSPF default 결과 | `4.939` (`tests/test_iso16358_cspf_hong_kong_config.py` `measure_1` 와 동일) |
| HSPF default 결과 | `3.643` (Hong Kong golden case 1) |
| `결과 복사` 동작 | 시스템 클립보드에 result text 복사 |
| `결과 지우기` 동작 | 결과 텍스트 비우기 |
| Region 재선택 | sections 재렌더링 + 결과 panel 보존 |
| PyQt5 미import | `sys.modules`에 `PyQt5.*` 없음 |

자동 테스트 (`tests/test_ui_tk_calculator_foundation.py`) 가 같은
4.939 / 3.643 / PyQt5 미import을 단위/smoke 수준에서 보호하고 있어,
manual checklist는 자동 테스트가 닿지 못하는 GUI 부분 (실제 윈도우
표시, 버튼 클릭 흐름, 클립보드 copy, region 재선택 후 panel 상태)
에 집중한다.

#### macOS / PyQt crash 분리 판단

본 manual checklist는 Tkinter MVP 전용 (`app_calculator_tk.py` →
`ui_tk/*`) 이며, macOS + Python 3.14 + PyQt5 환경의 4 PyQt clipboard
/ table 테스트 (`tests/test_iso16358_result_table_copy_tsv.py`,
`tests/test_iso16358_table_excel_like_behavior.py`, `tests/test_app_
calculator_ui_smoke.py`, `tests/test_spreadsheet_table_view.py`)
fatal-abort 와 **무관**하다. Tkinter MVP는 PyQt5를 import하지
않으며, 본 체크리스트도 PyQt path를 다루지 않는다. PyQt crash는
별도 항목으로 분리해 두고 본 작업에서 재현/해결하지 않는다.

### task 2 — Guide 작성

#### 경로

`docs/guides/lightweight_calculator_tk_manual_smoke.md` (신규).

#### 포함한 섹션

- Purpose
- Scope
- Non-goals
- Environment (macOS / Python 3.14.x / Tcl/Tk 확인 명령)
- Before you start (optional 정적 checks)
- Launch command (`python3 -B app_calculator_tk.py`)
- Manual checklist (14 항목)
- Expected values (CSPF 4.939 / HSPF 3.643 등 표)
- Pass / Fail recording format (OK/NG 한 줄씩 복사용 블록)
- Known macOS / PyQt issue separation
- Next step after passing

#### Manual checklist 14 항목

1. App launch (윈도우 + 타이틀)
2. Single ISO 16358 tab
3. Region selector ("Hong Kong" read-only)
4. CSPF + HSPF 한 화면
5. CSPF default 값 (5개 entry)
6. CSPF 계산 결과 `4.939`
7. HSPF default 값 (5개 entry)
8. HSPF 계산 결과 `3.643`
9. Result text 누적 (두 번째 계산이 첫 번째 덮어쓰지 않음)
10. Copy result (Cmd+V 외부 paste로 두 block 확인)
11. Clear result (panel 비움)
12. Region 재선택 시 sections 재렌더링 + panel 보존
13. PyQt5 미import (`sys.modules`에 PyQt5 없음, 별도 터미널 명령)
14. Clean shutdown (Cmd+W / 윈도우 close → 프로세스 정상 종료)

#### OK / NG 기록 형식

guide 안에 그대로 복사할 수 있는 markdown 블록을 둠. 14 항목 각각
`- <항목>: OK/NG` 한 줄 형식. 실패 시 한 줄 cause 추가 권장.

guide는 packaging guide (`docs/guides/lightweight_calculator_
packaging_check.md`) 와 중복 본문 없이 cross-link로 연결. Windows
PyInstaller 절차는 guide의 *주 내용이 아니라* "Next step after
passing"에서 한 줄로만 가리킨다.

### task 3 — Optional static commands

guide 내부 "Before you start" 섹션에 아래 3 command만 명시:

```bash
python3 -B -m py_compile <11 Tkinter MVP modules>
python3 -B tools/check_code_structure.py
python3 -B -m pytest -q tests/test_ui_tk_profile_resolver.py \
  tests/test_ui_tk_calculator_foundation.py \
  tests/test_calculator_schema_boundaries.py \
  tests/test_calculator_profiles.py \
  tests/test_calculator_dispatcher.py
```

각 command의 기대 출력 (`py_compile` silent OK / structure guard
`OK (no findings)` / pytest `58 passed`) 도 함께 기록.

#### 새 helper script를 만들지 않은 이유

- 작업 지시상 `tools/` 새 스크립트 추가 금지.
- 위 3 command는 모두 stdlib + 기존 repo asset (`tools/check_code_
  structure.py` 119에서 추가, pytest 기존 인프라) 으로 실행 가능.
- 자동 GUI / screenshot test 도 작업 지시상 금지. Tkinter screenshot
  자동화는 macOS 환경 의존성이 높고, manual checklist 자체로 충분히
  cover 가능.
- helper script를 한 번 만들면 유지 보수 대상이 늘어나는 반면, 본
  작업은 "현재 가능한 다음 작업을 체크리스트로 고정"이 목적이라
  rendering / executor가 필요 없다.

### task 4 — WORK_PLAN

`docs/WORK_PLAN.md` 4y (119 quality gate) 다음에 **4x 항목 추가**:

- 120 manual smoke checklist 작성 완료 기록.
- 14 항목 + OK/NG 형식 + 기대값 (CSPF 4.939 / HSPF 3.643) + PyQt5
  미import + macOS PyQt fatal-abort 분리 + 다음 단계 (Windows host
  확보 시 packaging guide로 진행, 아니면 pending 유지).
- Tkinter MVP는 코드 변경 없이 동일 (118 reset 유지).
- 다음 recommended action 3 후보:
  1. Windows host 확보 후 PyInstaller size 실측 (Slice T6).
  2. legacy / unused script cleanup audit.
  3. ISO section input dict / result formatter pure helper 분리.

추천: **(1) Windows host 확보 시 PyInstaller size 실측이 가장 큰
정보 이득**. 사용 불가 동안은 (2) 또는 (3) 중 사용자가 선택. 본
guide는 (1) 진행 시 비교 baseline으로 직접 활용된다.

4z (Tkinter feasibility pivot) / 4c~4g (PyQt UI hold) / 5번 (Hong Kong
HSPF PyQt UI surface hold) 항목은 그대로 유지. PyQt calculator UI
hold 상태는 유지.

#### lifecycle maintenance 제외 사유

- 114 summary cycle 이후 active 누적: 115 + 116 + 117 + 118 + 119 +
  120 = 6건. summary trigger 8~12개의 절반~midpoint 수준.
- 본 작업은 docs only (코드 변경 없음). lifecycle maintenance와
  섞지 않는다.
- `ACTIVE_DOCUMENTS.md` / `project_log.md` / architecture 문서 미수정.
- `result_reports/archive` / `result_reports/summaries` 미수정.

### task 5 — Report (본 파일)

본 `result_reports/active/120_tkinter-manual-smoke-checklist.md` 가
task 5 산출물.

## Next Suggested Action

(우선) **사용자 환경에 따라 두 갈래**:

- Windows host 확보 가능 → `docs/guides/lightweight_calculator_
  packaging_check.md` 절차로 PyInstaller 실측 (PyQt baseline vs
  Tkinter spike, one-folder dist + one-file exe). 실측 결과는 별도
  후속 report (예: `121_...`)에 기록하고 design doc은 retroactively
  수정하지 않는다.
- Windows host 확보 불가 (현 상태) → 두 후보 중 선택:
  - **(B) legacy / unused script cleanup audit** — `scripts/`,
    `tools/`, 기존 spike 잔재, PyQt hold 파일의 사용 여부를 audit하고
    이동/삭제 후보만 정리. 본 audit은 *판정* 단계만, 실제 cleanup은
    별도 phase. 코드 구조에 영향을 줄 수 있어 `python3 -B tools/check
    _code_structure.py` 결과를 함께 보고.
  - **(C) Tkinter ISO section cleanup** — `_read_inputs` / result
    text formatting을 pure helper로 분리. 본 작업 시 119 quality
    gate 적용 (소요 LOC 작아 분리 over-split 위험 낮음).

추천 1순위: **(A) Windows host 확보 시 PyInstaller 실측**. 본
checklist는 그때 비교 baseline으로 직접 사용된다.

## Scope Compliance

- Tkinter 기능 구현 / module 재분리 없음.
- PyInstaller 실행 / size 추정값 확정 없음.
- PyQt calculator UI 재개 / 삭제 / 수정 없음.
- `app_calculator.py`, `ui/calc_window.py`, `ui/calculators_2point.py`,
  PyQt tests 미수정.
- Train/Predict 리팩토링, unit adapter, ML / inverse-search 미수행.
- calculator core / profile / dispatcher / region config / expected /
  fixture / xfail 미수정.
- legacy cleanup 미실행.
- result report lifecycle maintenance 미수행.
- `project_log.md` / `ACTIVE_DOCUMENTS.md` / architecture 문서 미수정.
- active/archive/summaries 이동 없음.
- 새 helper script / automated GUI test 추가 없음.
- AGENTS_FULL.md 미열람.

## Changed Files

- A `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- M `docs/WORK_PLAN.md` (4x 항목 추가)
- A `result_reports/active/120_tkinter-manual-smoke-checklist.md`

## Known Failures / Risks

- 본 작업은 docs only. 동작 자체는 manual 단계에서 사람이 확인해야
  한다 — 본 report에는 manual 결과를 기록하지 않았다 (체크리스트
  자체를 산출물로 제공).
- macOS + Python 3.14 + PyQt5 환경의 4 PyQt clipboard / table fatal-
  abort 4건은 본 작업과 무관. checklist에서 명시적으로 분리.
- Windows PyInstaller size는 여전히 not measured.
- checklist 항목 중 "Region 재선택 시 sections 재렌더링"은 현 MVP에서
  region이 1개 (`Hong Kong`) 뿐이라 같은 region 재선택만 검증
  가능하다. 두 번째 region 추가 시 cross-region 전환 확인을 별도
  항목으로 보강해야 한다.

## Test Results

- `python3 -B -m py_compile` (11 Tkinter MVP modules) → OK.
- `python3 -B tools/check_code_structure.py` → `code structure guard:
  OK (no findings)`, exit 0.
- `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py
  tests/test_ui_tk_calculator_foundation.py
  tests/test_calculator_schema_boundaries.py
  tests/test_calculator_profiles.py
  tests/test_calculator_dispatcher.py -q` → 58 passed.
- 전체 (4 PyQt 환경 의존 crash 파일 제외) → 568 passed, 1 skipped,
  23 xfailed (119 baseline 동일, 본 작업 docs only).

## Commit / Push

- 소스/문서 변경 (`docs/guides/lightweight_calculator_tk_manual_
  smoke.md`, `docs/WORK_PLAN.md`) 와 본 report를 두 개 commit으로
  분리해 stage / commit / push.
- 소스/문서 commit message: `docs: add Tkinter calculator manual
  smoke checklist`.
- report commit message: `report: 120 tkinter manual smoke
  checklist`.
- push branch: `work/ui-ux-ssot-adoption`.
