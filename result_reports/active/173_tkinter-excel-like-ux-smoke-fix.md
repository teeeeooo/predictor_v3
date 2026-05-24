# Tkinter Excel-like table UX smoke fix

## Goal

Task 172에서 자동 테스트는 통과했으나 macOS 수동 UI smoke에서 `ExcelLikeTableController`의 Excel-like 동작이 기대와 다른 점이 확인되어 이를 보정한다. 구체적으로:

- 셀 클릭 시 Entry 편집 커서가 즉시 보이지 않고 Excel의 "셀 선택 상태"처럼 보이게 한다.
- 선택 상태에서 첫 printable key 입력 시 기존 값을 replace하고, 이후 연속 입력은 자연스럽게 편집되도록 한다.
- 선택 상태에서 화살표 키 이동과 keypad Enter를 Excel-like navigation으로 지원한다.
- 선택 취소 행동(Esc, 빈 공간 클릭, 다른 table 클릭)에서 active/selected visual state가 사라지도록 한다.
- macOS Command+C / Command+V / Command+Z shortcut 동작을 안정화한다.

## Scope

- `ui_tk/excel_like_table_controller.py` — controller logic 수정
- `tests/test_ui_tk_excel_like_table_controller.py` — regression / 새 동작 테스트 추가
- `docs/guides/lightweight_calculator_tk_manual_smoke.md` — manual smoke checklist 갱신
- `docs/WORK_PLAN.md` — task 173 완료 후 다음 recommended action 갱신

## Non-goals

- MetricInputTable에 selection/copy/paste/undo 책임을 누적하지 않는다.
- 새 widget framework 또는 PyQt 코드를 건드리지 않는다.
- core/profile/dispatcher/calculator result logic을 수정하지 않는다.
- `project_log.md`, `project_memory_seed.md`를 직접 수정하지 않는다.
- Canvas graph/detail 구현, standard/region 확장, packaging, PyQt retirement는 본 작업 범위가 아니다.

## Verification

- `python3 -B tools/check_code_structure.py` → `code structure guard: OK (no findings)`
- `python3 -B -m py_compile ui_tk/excel_like_table_controller.py ui_tk/metric_input_table.py tests/test_ui_tk_excel_like_table_controller.py tests/test_ui_tk_iso_table_autocalc.py` → silent success
- `python3 -B -m pytest tests/test_ui_tk_excel_like_table_controller.py tests/test_ui_tk_iso_table_autocalc.py -q -rxXs` → **24 passed**
- `python3 -B -m pytest -q -rxXs` → **651 passed, 32 skipped, 19 xfailed**
- `git diff --check` → no output

## Task Results

### Task 1 — Click selection mode (no caret, replace on first key)

- `_click`에서 `entry.focus_set()` + `insertontime=0` + `selection_clear()` + `icursor(0)`을 설정하여 셀 클릭 직후 caret이 보이지 않도록 했다.
- `_type_replace`에서 첫 printable key 입력 후 `insertontime=600`으로 복구하여 이후 연속 입력에서 caret이 보이도록 했다.
- `_click`이 `"break"`를 반환하여 Tk 기본 entry click 동작(cursor 위치 변경)이 막히도록 했다.
- Tab/Enter 이동 후 첫 입력 replace 동작은 유지하고 regression test로 보호했다.

### Task 2 — Arrow key and keypad Enter navigation

- `_arrow(left/right/up/down)` 메서드를 추가하고, `_replace_pending`가 True일 때만 active cell을 이동시킨다.
- Arrow key는 `self._editable_positions` 경계 밖으로 이동하지 않는다.
- `<KP_Enter>`와 `<Shift-KP_Enter>`를 `_navigate`에 바인딩하여 Return과 동일하게 처리한다.
- `_replace_pending`가 False일 때(이미 편집 중)는 화살표를 entry 기본 동작으로 fall-through한다.

### Task 3 — Selection clear on Esc/blank click/other table click

- `<Escape>` 바인딩으로 `_clear_selection`을 호출한다.
- `header_cells`, `row_header_cells`, `static_cell_frames`에 `<Button-1>` 바인딩으로 `_clear_selection`을 호출한다.
- `<FocusOut>` 바인딩 + `self._internal_focus_move` flag로, controller 내부 이동(`_click`, `_navigate`, `_arrow`) 중에는 clear하지 않고, 외부로 focus가 나갈 때만 clear한다.
- `_clear_selection` 후 `_paint_selection`이 `TABLE_EDITABLE_BG`로 복구한다.
- `_on_focus_out`에서 `self.table.winfo_exists()`를 방어하여 destroy/re-render 후 stale binding 예외를 막는다.

### Task 4 — macOS Command+C/V/Z shortcut stabilization

- `entry.bind()`에 `<Command-C>`, `<Command-V>`, `<Command-Z>`, `<Control-C>`, `<Control-V>`, `<Control-Z>`를 추가하여 대소문자/keysym 차이를 방어했다.
- `table.table_frame`에도 동일한 Command/Control shortcut을 바인딩하여 focus가 entry가 아닌 table frame에 있을 때도 동작하도록 했다.
- paste의 atomic numeric validation 정책은 그대로 유지했다.

### Task 5 — Docs and report update

- `docs/guides/lightweight_calculator_tk_manual_smoke.md`에 click selection caret, arrow key, keypad Enter, Esc/blank click/other table click clear, macOS Command+C/V/Z 확인 항목을 반영했다.
- `docs/WORK_PLAN.md`에 task 173(4g-e) 항목을 추가하고 다음 recommended action을 갱신했다.
- 본 report를 작성했다.

## Test Results

- `tests/test_ui_tk_excel_like_table_controller.py`에 다음 테스트를 추가/갱신했다:
  - `test_click_does_not_show_typing_caret_until_first_key`
  - `test_arrow_keys_move_active_cell_when_in_selection_mode`
  - `test_kp_enter_bindings_exist_and_navigate_like_return`
  - `test_escape_clears_selection_and_restores_default_background`
  - `test_focus_out_clears_selection_when_not_internal_move`
  - `test_focus_out_ignored_during_internal_navigation`
  - `test_static_and_header_click_clears_selection`
  - `test_command_and_control_shortcuts_bound_on_entry_and_frame`
  - `test_paste_atomic_reject_on_invalid_value`
- 기존 `test_navigation_and_click_then_type_replace`를 갱신하여 `insertontime` 상태를 검증했다.
- 전체 suite 결과: 651 passed, 32 skipped, 19 xfailed.

## Changed Files

- `ui_tk/excel_like_table_controller.py`
- `tests/test_ui_tk_excel_like_table_controller.py`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/173_tkinter-excel-like-ux-smoke-fix.md`

## Known Failures / Risks

- `table.table_frame`에 shortcut 바인딩을 추가했지만, 현재 구조에서는 focus가 항상 entry에 있으므로 frame shortcut이 실제로 트리거될 일은 드물다. 이 바인딩은 나중에 focus를 frame으로 옮길 때를 대비한 방어적 wiring이다.
- macOS Tk에서 `<Command-c>`는 내부적으로 `<Mod1-Key-c>`로 등록되므로, 다른 OS에서는 `bind()` 문자열 검증이 다를 수 있다. 테스트는 `sys.platform == "darwin"` 분기로 이를 처리했다.
- `<KP_Enter>`는 OS/Tk 버전에 따라 `<Key-KP_Enter>` 또는 다른 keysym으로 등록될 수 있다. 테스트는 `"KP_Enter" in bind()` 결과 문자열로 검증했다.

## Next Suggested Action

1. **macOS Tkinter manual UX smoke** — controller patch 이후 다시 실행.
2. **Tkinter Canvas graph/detail surface design** — lightweight Canvas 방향으로 설계; `matplotlib`은 packaging size 판단 전 도입하지 않는다.
3. **Tkinter standard/region expansion plan** — ISO/ISEER 2점식, SASO T3, EN 14825, AHRI 210/240 순서를 판단.
4. **Windows PyInstaller size measurement** — Windows host available 시.
5. **PyQt calculator source retirement 재검토** — Tkinter UX, 기능 migration, packaging 판단 이후.

## Scope Compliance

- core/profile/dispatcher/calculator logic 수정 없음: confirmed (git diff --name-only 범위 내 없음)
- `project_log.md`, `project_memory_seed.md` 수정 없음: confirmed
- MetricInputTable에 interaction logic 누적 없음: confirmed (책임은 controller에 유지)
- PyQt 코드 수정 없음: confirmed
- `QTableWidget` / `setCellWidget` 도입 없음: confirmed

## Commit / Push

- Source change commit: `ui_tk/excel_like_table_controller.py`, `tests/test_ui_tk_excel_like_table_controller.py`
- Docs change commit: `docs/guides/lightweight_calculator_tk_manual_smoke.md`, `docs/WORK_PLAN.md`
- Report commit: `result_reports/active/173_tkinter-excel-like-ux-smoke-fix.md`
- Branch: `work/ui-ux-ssot-adoption`

## Project Memory Delta

- type: decision
  topic: Tkinter Excel-like table entry click UX
  content: 셀 클릭 시 Entry에 focus를 주되 insertontime=0과 icursor(0)으로 caret을 숨기고, 첫 printable key 입력 후 insertontime=600으로 복구하여 Excel-like selection mode를 흉내낸다.
  keywords:
    - tkinter
    - excel-like
    - insertontime
    - caret-hiding
    - selection-mode
  assertionStatus: verified
  source: result_reports/active/173_tkinter-excel-like-ux-smoke-fix.md, tests/test_ui_tk_excel_like_table_controller.py::test_click_does_not_show_typing_caret_until_first_key

- type: decision
  topic: Tkinter Excel-like table arrow key navigation boundary
  content: 화살표 키는 _replace_pending가 True인 selection mode에서만 active cell을 이동시키고, _replace_pending가 False(편집 중)일 때는 entry 기본 동작으로 fall-through한다. 경계 밖 이동은 _editable_positions 멤버십으로 방어한다.
  keywords:
    - tkinter
    - excel-like
    - arrow-key
    - navigation
    - selection-mode
  assertionStatus: verified
  source: result_reports/active/173_tkinter-excel-like-ux-smoke-fix.md, tests/test_ui_tk_excel_like_table_controller.py::test_arrow_keys_move_active_cell_when_in_selection_mode

- type: error
  topic: macOS Tk Command key bind string mapping
  content: macOS Tk에서 entry.bind("<Command-c>")는 bind() 결과에서 "<Mod1-Key-c>"로 노출된다. 플랫폼에 따라 keysym 문자열이 다르므로 bind() 문자열 직접 비교는 위험하며, 동작 테스트 또는 플랫폼 분기를 권장한다.
  keywords:
    - tkinter
    - macos
    - command-key
    - mod1
    - bind
  assertionStatus: observed
  source: result_reports/active/173_tkinter-excel-like-ux-smoke-fix.md, tests/test_ui_tk_excel_like_table_controller.py::test_command_and_control_shortcuts_bound_on_entry_and_frame
