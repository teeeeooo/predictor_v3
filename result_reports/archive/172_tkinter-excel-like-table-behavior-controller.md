# 172. Tkinter Excel-like Table Behavior Controller

## Goal

Tkinter ISO Hong Kong CSPF/HSPF 입력 matrix에 Excel-like selection,
clipboard, clear, undo, navigation, type-to-replace 동작을 추가하되,
`MetricInputTable` 안에 interaction 책임을 누적하지 않고 별도
controller가 metadata surface에 attach되는 구조로 구현한다.

## Scope

- `MetricInputTable`에 controller가 사용할 address lookup과
  notify-once batch mutation API만 추가한다.
- 신규 `ExcelLikeTableController`가 rated/trial 입력 table의
  interaction state와 binding을 소유한다.
- CSPF/HSPF section의 rated table과 trial table에 controller를
  attach한다.
- pure helper 및 Tk controller behavior tests를 추가하고 기존 ISO
  result regression tests를 보강한다.
- Tkinter adapter, manual smoke guide, `WORK_PLAN`을 현재 구현
  상태와 다음 phase에 맞게 갱신한다.

## Non-goals

- graph/detail 또는 Canvas chart 구현, `matplotlib` 도입
- standard/region 확장 또는 PyQt retirement
- core/profile/dispatcher, calculator mapping/default, expected/golden/
  fixture, result panel 구조 변경
- visual owner boundary 우회 또는 palette 전면 변경
- packaging, lifecycle summary/archive, `project_log.md`,
  `project_memory_seed.md` 수정

## Evidence And Design Gate

- 작업 시작 시 branch는 `work/ui-ux-ssot-adoption`이고 origin과
  sync된 clean 상태였다.
- `project_memory_seed.md`는 `Excel-like`, `Tkinter`, `input matrix`,
  `result surface`, `Hong Kong`, `CSPF`, `HSPF` keyword 범위만
  확인했다. Evidence는 Hong Kong matrix/auto-calc/summary surface와
  기존 smoke 값을 유지하고 PyQt retirement는 hold한다는 결정이다.
- `result_reports/active/170_tkinter-responsive-table-architecture-alignment.md`
  는 controller 등록을 위한 metadata가 준비되었고 interaction을
  후속 slice로 분리했다는 근거로 확인했다.
- `result_reports/active/171_ui-ux-portable-visual-value-ownership-cleanup.md`
  는 concrete visual values를 `ui_tk/layout_constants.py`가 소유하고
  components/controller는 소비만 해야 한다는 boundary 근거로
  확인했다.
- Design Gate 결론: `MetricInputTable`은 surface metadata와 grouped
  mutation만 제공하고, 별도 controller가 interaction을 소유한다.
  새 selection visuals는 owner tokens로만 추가한다.

## Task Results

### Task 1: Attachment API

- 기존 `columns`, `rows`, `editable_cells`, `cell_frames`,
  `editable_entries`, `field_order`, `layout_policy` metadata를
  그대로 유지했다.
- `editable_addresses`, `field_key_for_address()`,
  `text_at_address()`, `set_address_values_batch()`를 추가해 controller가
  private widget state를 재구성하지 않고 row/column 주소로 접근할
  수 있게 했다.
- `set_values_batch()`는 여러 variable trace 변경을 한 번의
  `values_changed` callback으로 합친다. selection, clipboard, undo
  logic은 table class에 추가하지 않았다.

### Task 2: Standalone Controller

- `ui_tk/excel_like_table_controller.py`를 신규 작성했다. 250 LOC의
  단일 interaction 책임 모듈이며 table cell을 생성하지 않는다.
- Tk 없는 pure helpers:
  - `parse_clipboard_matrix`
  - `encode_selection_to_clipboard`
  - `clip_paste_targets`
  - `validate_paste_matrix`
  - `resolve_selection_bounds`
  - `resolve_next_cell`
- Controller module import 자체는 `tkinter`를 load하지 않으며,
  clipboard exception type만 paste action 실행 시 지연 import한다.
- Controller behavior:
  - single-click selection, Shift-click/drag rectangular selection
  - Ctrl/Command+C TSV copy, Ctrl/Command+V TSV paste
  - Delete/Backspace grouped clear, Ctrl/Command+Z grouped undo
  - Tab/Shift+Tab and Enter/Shift+Enter navigation
  - click-then-type whole-value replacement
- Selected/active entry backgrounds are consumed from new
  `TABLE_SELECTED_BG` and `TABLE_ACTIVE_BG` tokens in
  `ui_tk/layout_constants.py`; the controller declares no raw visual
  values.
- Current numeric auto-calc binding validates a complete paste before
  mutation. Invalid numeric TSV is rejected without partial cell updates or
  scheduled recalculation. This prompt-specific atomic policy is documented
  in the Tkinter adapter; inline invalid edits continue through the existing
  status-only result behavior.

### Task 3: Section Wiring

- `IsoCspfSection` and `IsoHspfSection` attach one controller to each
  `rated_table` and `input_table`.
- Controllers are attached after default values are populated and before the
  existing auto-calc callbacks are used; default input mapping and
  calculation paths are unchanged.
- Existing regression tests continue to establish default CSPF `4.939`,
  HSPF `3.643`, section-local results, and invalid status-only rendering.

### Task 4: Tests

- New `tests/test_ui_tk_excel_like_table_controller.py` covers:
  - pure-helper module import가 `tkinter`를 load하지 않음;
  - TSV parse/encode, paste clipping, atomic invalid validation;
  - selection bounds and row/column navigation;
  - click, Shift-click, and drag rectangular selection;
  - TSV copy/paste, grouped clear and undo;
  - invalid paste no-partial-apply;
  - navigation and click-then-type replacement;
  - notify-once behavior through grouped table mutations.
- `tests/test_ui_tk_iso_table_autocalc.py` now checks that all four
  visible rated/trial tables have attached controllers while retaining its
  existing layout/default/invalid regression checks.
- No screenshot/pixel tests, PyQt tests, expected/golden, or fixtures were
  modified.

### Task 5: Docs And Work Plan

- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md` records the completed
  controller attachment and numeric atomic-paste binding.
- `docs/guides/lightweight_calculator_tk_manual_smoke.md` adds manual
  selection, TSV, atomic invalid paste, clear/undo, navigation, and
  type-to-replace checks. Manual smoke was not performed in this coding
  task.
- `docs/WORK_PLAN.md` records task 172 completion. Next recommended action:
  1. Tkinter Canvas graph/detail surface design
  2. Tkinter standard/region expansion plan
  3. Windows PyInstaller size measurement
  4. PyQt calculator source retirement 재검토

## Test Results

- Pure helper coverage confirms TSV parse/encode, clipping, selection
  bounds, navigation, invalid-paste rejection, and import without loading
  `tkinter`.
- Tk coverage confirms rectangular selection, copy/paste, grouped
  clear/undo, navigation, type-to-replace, and one callback per grouped
  update.
- Existing ISO widget tests continue to cover default CSPF/HSPF output,
  section-local summary rendering, responsive surface behavior, and
  invalid-input status-only display after controller attachment.

## Verification

| Command | Result |
| --- | --- |
| `python3 -B tools/check_code_structure.py` | PASS: `code structure guard: OK (no findings)` |
| `python3 -B -m py_compile ui_tk/layout_constants.py ui_tk/metric_input_table.py ui_tk/excel_like_table_controller.py ui_tk/sections/iso_cspf_section.py ui_tk/sections/iso_hspf_section.py tests/test_ui_tk_excel_like_table_controller.py tests/test_ui_tk_iso_table_autocalc.py` | PASS |
| `python3 -B -m pytest tests/test_ui_tk_excel_like_table_controller.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_iso16358_helpers.py -q -rxXs` | PASS: `22 passed` |
| `python3 -B -m pytest -q -rxXs` | PASS: `642 passed, 32 skipped, 19 xfailed` |
| `git diff --check` | PASS |
| modified-file check for `project_log.md` and `result_reports/memory/project_memory_seed.md` | PASS: unchanged |

Full suite baseline was `635 passed, 32 skipped, 19 xfailed`.
The `+7 passed` delta is the new controller test module; skipped and xfail
counts are unchanged. No native abort occurred.

## Changed Files

- `ui_tk/excel_like_table_controller.py` - standalone controller and pure
  interaction helpers.
- `ui_tk/metric_input_table.py` - minimal metadata and notify-once batch API.
- `ui_tk/layout_constants.py` - selected/active cell visual owner tokens.
- `ui_tk/sections/iso_cspf_section.py` - rated/trial controller attachment.
- `ui_tk/sections/iso_hspf_section.py` - rated/trial controller attachment.
- `tests/test_ui_tk_excel_like_table_controller.py` - new helper/controller
  behavior coverage.
- `tests/test_ui_tk_iso_table_autocalc.py` - section attachment regression.
- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md` - implemented adapter binding
  and atomic paste policy.
- `docs/guides/lightweight_calculator_tk_manual_smoke.md` - interaction smoke
  checklist.
- `docs/WORK_PLAN.md` - task completion and next actions.

## Known Failures / Risks

- Numeric paste is intentionally all-or-nothing for this automatic
  calculation surface; this differs from the common contract's generic
  invalid-cell landing rule and is explicitly recorded as the current
  Tkinter calculator binding.
- Manual macOS UX smoke remains pending as the next user-visible validation
  step before packaging judgment; automated widget coverage passed here.

## Next Suggested Action

Design the lightweight Tkinter Canvas graph/detail surface without adding
`matplotlib` before Windows packaging size judgment.

## Scope Compliance

- No graph/detail implementation, Canvas chart, region/standard expansion,
  PyQt code, retirement, core/profile/dispatcher, expected/golden/fixture,
  packaging, or unrelated refactor was performed.
- `project_log.md` and `result_reports/memory/project_memory_seed.md` were not
  modified.
- No result report lifecycle movement was performed.

## Commit / Push

- Source/docs/test commit: `de4719a` (`feat: add Tkinter Excel-like table controller`)
- Report commit: committed separately using a `report:` commit message.
- Push target: `origin/work/ui-ux-ssot-adoption`, after report commit.

## Project Memory Delta

```yaml
- type: decision
  topic: tkinter-excel-like-table-controller
  content: "predictor_v3 ISO Hong Kong Tkinter rated and trial matrix tables attach a standalone ExcelLikeTableController to MetricInputTable metadata; the table exposes grouped mutation hooks, visual values remain owned by ui_tk/layout_constants.py, and numeric TSV paste is applied atomically to prevent partial automatic-calculation updates."
  keywords:
    - Tkinter
    - Excel-like behavior
    - input matrix
    - Hong Kong
    - CSPF
    - HSPF
    - auto-calc
  assertionStatus: verified
  source: result_reports/active/172_tkinter-excel-like-table-behavior-controller.md
```
