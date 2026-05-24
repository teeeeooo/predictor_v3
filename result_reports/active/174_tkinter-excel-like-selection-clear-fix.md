# Tkinter Excel-like table selection clear fix

## Goal

Task 173에서 Tkinter Excel-like table UX smoke fix를 적용했으나, macOS 수동 확인에서 selection visual clear 관련 문제가 남아 있었다. 본 작업에서는 다음을 보정한다:

- 다른 table/card의 셀을 클릭하면 이전 table의 active/selected visual state가 즉시 clear되도록 한다.
- table 내부의 non-editable area(header/row header/static cell/blank gap) 클릭 시 selection이 clear되는 영역을 넓힌다.
- `_internal_focus_move` flag가 외부 focus-out clear를 잘못 무시하지 않도록 안정화한다.
- task 173 테스트의 약한 부분(binding/경로 중심)을 보강한다.

## Scope

- `ui_tk/excel_like_table_controller.py` — controller logic 수정
- `tests/test_ui_tk_excel_like_table_controller.py` — regression / 새 동작 테스트 추가
- `docs/guides/lightweight_calculator_tk_manual_smoke.md` — manual smoke checklist 갱신
- `docs/WORK_PLAN.md` — task 174 완료 항목과 다음 recommended action 갱신

## Non-goals

- `MetricInputTable`에 selection lifecycle 책임을 추가하지 않는다.
- result panel, auto-calc, core/profile/dispatcher는 수정하지 않는다.
- 무분별한 app-global side effect를 만들지 않는다.
- `project_log.md`, `project_memory_seed.md`를 직접 수정하지 않는다.
- Canvas graph/detail 구현, standard/region 확장, packaging, PyQt retirement는 본 작업 범위가 아니다.

## Verification

- `python3 -B tools/check_code_structure.py` → `code structure guard: OK (no findings)`
- `python3 -B -m py_compile ui_tk/excel_like_table_controller.py tests/test_ui_tk_excel_like_table_controller.py tests/test_ui_tk_iso_table_autocalc.py` → silent success
- `python3 -B -m pytest tests/test_ui_tk_excel_like_table_controller.py tests/test_ui_tk_iso_table_autocalc.py -q -rxXs` → **29 passed**
- `python3 -B -m pytest -q -rxXs` → **656 passed, 32 skipped, 19 xfailed**
- `git diff --check` → no output

## Task Results

### Task 1 — Cross-table selection clear

- `ExcelLikeTableController`에 class-level `_active_controller` 속성을 추가했다.
- `select()`에서, 새로운 controller가 select를 받으면 이전 `_active_controller`의 `_clear_selection()`을 호출한다.
- 이전 controller가 destroyed되거나 `winfo_exists()`가 False이면 예외 없이 무시한다.
- `_clear_selection()`에서는 자신이 `_active_controller`면 class-level 속성을 None으로 해제한다.
- 같은 table 내부의 Shift-click / drag selection은 `prev is not self` 조건으로 영향을 받지 않는다.

### Task 2 — Expand blank-area click clear

- header/row_header/static cell의 Frame뿐 아니라 그 안의 Label(자손 widget)까지 `<Button-1>` binding이 걸리도록 `_bind_clear_recursive()` helper를 추가했다.
- `table_frame` 자체에도 `<Button-1>` binding(`_on_table_frame_click`)을 추가했다. `event.widget is self.table.table_frame`일 때만 clear하여, editable cell/entry 클릭은 기존 handler가 처리하도록 분기했다.
- 이로써 table 내부의 모든 non-editable 영역(header, row header, static cell, Label, table_frame gap)에서 클릭 시 selection이 clear된다.
- editable cell/entry의 기본 click/select 동작은 방해받지 않는다.

### Task 3 — `_internal_focus_move` flag stabilization

- `_mark_internal_focus_move()`와 `_reset_internal_focus_move()` helper를 추가했다.
- `_click`, `_navigate`, `_arrow`에서 `_internal_focus_move = True` 직접 대입 대신 `_mark_internal_focus_move()`를 호출한다.
- `_mark_internal_focus_move()`는 `self.table.after_idle(self._reset_internal_focus_move)`를 예약하여, 내부 이동이 끝난 후 flag가 반드시 False로 돌아가도록 한다.
- `_on_focus_out`에서는 flag가 True이면 return(내부 이동 중 FocusOut 억제). flag가 False이면 `_clear_selection()` 실행.
- `after_idle`이 처리된 후 외부 focus-out이 발생하면 flag는 이미 False이므로 정상적으로 clear된다.

### Task 4 — Test strengthening

- `two_controlled_tables` fixture를 추가하여 두 개의 독립 controller/table을 생성한다.
- `test_click_on_other_table_clears_previous_selection`: controller1을 select한 후 controller2의 `_click`을 호출하면 controller1이 clear되고 controller2가 active가 되는지 확인한다.
- `test_table_frame_click_on_blank_area_clears_selection`: `table_frame`에 `<Button-1>` binding이 존재하고, `event.widget is table_frame`인 simulate event로 `_clear_selection`이 호출되는지 확인한다.
- `test_header_label_click_clears_selection_via_recursive_binding`: header cell 내부 Label에 `<Button-1>` binding이 존재함을 확인하고, clear 후 background가 복구되는지 검증한다.
- `test_internal_focus_move_resets_via_after_idle`: `_navigate` 후 `tk_root.update_idletasks()`로 after_idle을 처리하면 `_internal_focus_move`가 False가 됨을 검증한다.
- `test_external_focus_out_after_internal_move_clears`: after_idle 처리 후 `_on_focus_out`이 호출되면 selection이 clear됨을 검증한다.
- `test_focus_out_during_internal_move_is_suppressed_then_clears_after_idle`: after_idle 처리 전 `_on_focus_out`은 clear를 막고, after_idle 처리 후 외부 `_on_focus_out`은 clear함을 검증한다.
- 기존 `test_static_and_header_click_clears_selection`은 `_clear_selection` 직접 호출 대신 실제 binding 확인과 경로 검증으로 보강했다.

### Task 5 — Docs and report update

- `docs/guides/lightweight_calculator_tk_manual_smoke.md`의 step 9에서:
  - "Press Esc"를 별도 항목으로 분리
  - "Click a blank area inside the table frame"에 header/row header/static cell/empty space를 명시하고 "entire table surface"로 표현
  - "Click another table/card cell"를 별도 항목으로 분리
- recording format에 `Esc clears selection visual`, `Blank area click clears selection`, `Other table/card cell click clears previous selection` 항목을 추가했다.
- `docs/WORK_PLAN.md`에 task 174(4g-f) 항목을 추가하고 다음 recommended action을 갱신했다.
- 본 report를 작성했다.

## Test Results

- `tests/test_ui_tk_excel_like_table_controller.py`에 추가/갱신된 테스트:
  - `test_table_frame_click_on_blank_area_clears_selection`
  - `test_header_label_click_clears_selection_via_recursive_binding`
  - `test_click_on_other_table_clears_previous_selection`
  - `test_internal_focus_move_resets_via_after_idle`
  - `test_external_focus_out_after_internal_move_clears`
  - `test_focus_out_during_internal_move_is_suppressed_then_clears_after_idle`
- 전체 suite 결과: 656 passed, 32 skipped, 19 xfailed.

## Changed Files

- `ui_tk/excel_like_table_controller.py`
- `tests/test_ui_tk_excel_like_table_controller.py`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/174_tkinter-excel-like-selection-clear-fix.md`

## Known Failures / Risks

- class-level `_active_controller`는 controller instance를 직접 참조하므로, table destroy 후에도 참조가 남을 수 있다. `select()`와 `_clear_selection()`에서 `winfo_exists()`와 `try/except`로 방어하고 있다.
- `table_frame.bind("<Button-1>")`은 `event.widget is self.table.table_frame`일 때만 처리하므로, editable cell/entry 클릭과 충돌하지 않는다. 하지만 `table_frame`의 다른 자손 widget(미래에 추가될 경우)은 `_on_table_frame_click`에서 `""`를 반환하여 fall-through되므로, 별도 handler가 필요할 수 있다.
- macOS Tk의 `after_idle` 처리 타이밍은 single-threaded event loop 내에서 안정적이나, `update_idletasks()`를 사용한 테스트는 production 동작과 동일한 순서를 보장한다.

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
- Report commit: `result_reports/active/174_tkinter-excel-like-selection-clear-fix.md`
- Branch: `work/ui-ux-ssot-adoption`

## Project Memory Delta

- type: decision
  topic: Tkinter Excel-like cross-table selection clear
  content: ExcelLikeTableController는 class-level `_active_controller`를 추적하여, 새 controller가 select를 받으면 이전 controller의 selection visual을 자동으로 clear한다. destroyed table에 대한 stale reference는 `winfo_exists()`로 방어한다.
  keywords:
    - tkinter
    - excel-like
    - cross-table
    - selection-clear
    - active-controller
  assertionStatus: verified
  source: result_reports/active/174_tkinter-excel-like-selection-clear-fix.md, tests/test_ui_tk_excel_like_table_controller.py::test_click_on_other_table_clears_previous_selection

- type: decision
  topic: Tkinter Excel-like blank area click clear
  content: table 내부의 non-editable 영역(header, row header, static cell, frame gap)에서 selection clear가 동작하도록, header/row_header/static cell 및 모든 자손 widget에 recursive `<Button-1>` binding을 추가하고, `table_frame` 자체에도 blank gap click handler를 추가한다. editable cell/entry 클릭은 기존 handler path가 보호한다.
  keywords:
    - tkinter
    - excel-like
    - blank-area
    - recursive-binding
    - selection-clear
  assertionStatus: verified
  source: result_reports/active/174_tkinter-excel-like-selection-clear-fix.md, tests/test_ui_tk_excel_like_table_controller.py::test_table_frame_click_on_blank_area_clears_selection

- type: decision
  topic: Tkinter Excel-like internal focus move flag stabilization
  content: 내부 navigation(click, Tab, Enter, arrow) 중에 발생하는 FocusOut으로 selection이 clear되지 않도록 `_internal_focus_move` flag를 사용하되, flag를 `after_idle`로 reset하여 내부 이동이 끝난 후 외부 focus-out에서는 정상적으로 clear되도록 한다.
  keywords:
    - tkinter
    - excel-like
    - focus-move
    - after-idle
    - flag-stabilization
  assertionStatus: verified
  source: result_reports/active/174_tkinter-excel-like-selection-clear-fix.md, tests/test_ui_tk_excel_like_table_controller.py::test_focus_out_during_internal_move_is_suppressed_then_clears_after_idle
