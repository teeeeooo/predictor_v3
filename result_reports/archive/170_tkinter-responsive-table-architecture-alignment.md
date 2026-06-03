# 170 Tkinter Responsive Table Architecture Alignment

## Work Contract

- Goal: task 169에서 정렬한 ISO Hong Kong table/result surfaces를 fixed pixel sizing에서 project-wide responsive Excel-like matrix table architecture 방향으로 전환한다.
- Scope: Tkinter table/result layout policy, interaction-ready metadata, focused UI/UX owner-doc clarification, UI tests, smoke guide, `WORK_PLAN`.
- Non-goals: selection/copy/paste/undo/drag 구현, graph/detail 또는 Canvas chart 구현, `matplotlib`, standard/region 확장, PyQt 변경/retirement, core/profile/dispatcher/golden/fixture 변경, packaging.
- Verification: code structure guard, `py_compile`, targeted Tkinter tests, full pytest suite.

## Evidence And Memory Recall

`result_reports/memory/project_memory_seed.md`는 요청 keyword에 대해 `rg -n` 제한 검색으로만 확인했다.

- Active UI/UX owners는 `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md`와 `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`다.
- Tkinter ISO Hong Kong CSPF/HSPF는 matrix input, auto-calc, compact summary result와 기존 smoke 값을 유지해야 한다.
- Graph/detail 및 PyQt calculator retirement는 후속 판단으로 보류되어 있다.
- Excel-like interaction baseline은 table contract에 존재하지만 이번 구현 범위가 아니다.

사용자가 지정한 외부 reference URL `https://github.com/teeeeooo/SPOT`은 확인 시 404로 내용을 직접 검토할 수 없었다. 따라서 사용자 prompt에 제공된 개념 요약(frame-wrapped entry cells, character/font sizing, parent stretch, separate controller registration)만 evidence로 사용했으며, 해당 이름을 architecture 명칭으로 사용하지 않았다.

## Task 1: Fixed Layout Cause

Task 169는 동일 폭을 만드는 데 성공했지만 아래 fixed mechanism이 window resize 반응을 막았다.

- `ui_tk/layout_constants.py`의 `MATRIX_ROW_HEADER_WIDTH`, `MATRIX_DATA_COLUMN_WIDTH`, `ISO_SECTION_CONTENT_WIDTH`가 pixel width contract였다.
- `MetricInputTable`은 `columnconfigure(..., minsize=..., weight=0)`과 `content_width`를 적용해 table width를 고정했다.
- `ResultPanel`은 `content_width`를 summary/status cell minsize로 적용했다.
- Sections는 입력/결과 surfaces를 `sticky="w"`로 두어 parent가 넓어져도 table surface가 함께 확장되지 않았다.

이번 task는 responsive layout와 typography density alignment only이며 계산 또는 interaction feature 작업이 아니다.

## Task 2: Responsive MetricInputTable

`ui_tk/layout_constants.py`는 fixed pixel width values를 제거하고 다음 responsive defaults를 소유하도록 변경했다.

- `TABLE_FONT_SIZE`, `TABLE_BODY_FONT`, `TABLE_HEADER_FONT`
- `TABLE_ROW_HEADER_CHARS`, `TABLE_DATA_COLUMN_CHARS`
- `TABLE_ROW_HEADER_WEIGHT`, `TABLE_DATA_COLUMN_WEIGHT`
- compact `TABLE_CELL_PADX`, `TABLE_CELL_PADY`, `TABLE_HEADER_PADY`
- existing section padding/gap constants

`MetricInputTable` 변경:

- Initial cell size는 label/entry의 character-based width로 결정한다.
- Table wrapper와 internal columns는 `sticky="ew"` 및 positive grid weights로 parent width를 사용한다.
- Numeric entries remain centered and use the larger table font with compact padding.
- Header/body/static/editable surface roles, parsing, get/set, and values-changed callback remain unchanged.

Interaction-ready metadata exposed for the later controller slice:

- `layout_policy = "responsive"`
- `columns`, `rows`, `editable_cells`
- `cell_frames`, `editable_entries`
- visual `field_order`

`field_order`는 editable cells가 실제 화면에서 생성되는 순서로 기록되며, 후속 controller가 visual traversal order를 재구성하지 않아도 된다. Task 170은 해당 registry를 제공할 뿐 selection/clipboard/undo controller를 구현하지 않는다.

## Task 3: Responsive Result/Section Alignment

- `ResultPanel`에서 fixed `content_width` parameter와 summary/status minsize 계산을 제거했다.
- Result summary cells는 equal positive grid weights로 available parent width를 공유한다.
- CSPF/HSPF rated table, trial table, and result panel은 모두 section column에 `sticky="ew"`로 배치된다.
- Result header/value/status shape와 invalid `status_surface`는 유지한다.
- Visible bottom copy/clear buttons는 계속 없다.

Runtime geometry evidence:

| Window geometry | Metric | Rated / trial / result widths | Left offsets |
| --- | --- | --- | --- |
| `650x900` | CSPF | `610 / 610 / 610` | aligned |
| `650x900` | HSPF | `610 / 610 / 610` | aligned |
| `950x900` | CSPF | `910 / 910 / 910` | aligned |
| `950x900` | HSPF | `910 / 910 / 910` | aligned |

This is a runtime diagnostic supporting the responsive behavior; automated tests assert relative expansion/equality rather than fixed pixels.

## Task 4: UI/UX Owner Docs

- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`: existing architecture explanation now states that table surfaces expose metadata, expand responsively with related results, use character/font-based initial sizing where appropriate, and may receive behavior through a separate controller.
- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`: added responsive Entry-grid construction rules: frame-wrapped cells, metadata registry, parent-driven stretch, no fixed-pixel alignment lock, and compact typography density. Interaction behavior may attach through a later controller.
- `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`: recorded that task 170 supersedes the fixed-width mechanism while retaining task 169's alignment intent.

No new narrow UI/UX contract document was created.

## Task 5: Test Coverage

`tests/test_ui_tk_iso_table_autocalc.py` now verifies:

- removed fixed-width public contract/constants and active `responsive` layout policy;
- row/column/cell/editable-entry metadata for future controller registration;
- character-based sizing defaults, increased table font, and compact padding;
- rated/trial/result surfaces use `ew` stretch and expand together when the root width increases;
- after expansion, rated/trial/result widths remain equal per metric;
- centered numeric editors, default CSPF `4.939` / HSPF `3.643`, no visible copy/clear buttons, no accumulation, and invalid status-only rendering remain intact.

No screenshot/pixel test, PyQt test, expected/golden, or fixture was modified.

## Task 6: Guide And Work Plan

- `docs/guides/lightweight_calculator_tk_manual_smoke.md`: added resize responsiveness, readable larger text, compact row density, and maintained alignment observations.
- `docs/WORK_PLAN.md`: recorded task 170 and the next action sequence.

Next recommended action order:

1. Tkinter Excel-like table behavior controller.
2. Tkinter Canvas graph/detail surface design.
3. Tkinter standard/region expansion plan.
4. Windows PyInstaller size measurement, Windows host available 시.
5. PyQt calculator source retirement 재검토, Tkinter UX/기능 migration/packaging 판단 이후.

Excel-like behavior is separated into task 171 because this slice establishes responsive surface construction and controller registration metadata only; implementing interactions simultaneously would combine layout architecture changes with keyboard/clipboard/selection behavioral risk.

## Boundaries Maintained

- Core calculator, profile, dispatcher, expected/golden, fixture는 수정하지 않았다.
- Excel-like selection/copy/paste/undo/drag, graph/detail, Canvas chart, `matplotlib`, visual-token full rewrite는 구현하지 않았다.
- PyQt source/Predict/Train과 packaging은 건드리지 않았다.
- `ACTIVE_DOCUMENTS.md`, `project_log.md`, `project_memory_seed.md`는 사용자 금지 범위에 따라 수정하지 않았다.
- Lifecycle summary/archive 이동은 수행하지 않았다.

## Verification

| Command | Result |
| --- | --- |
| `python3 -B tools/check_code_structure.py` | PASS: `code structure guard: OK (no findings)` |
| `python3 -B -m py_compile ui_tk/layout_constants.py ui_tk/metric_input_table.py ui_tk/result_panel.py ui_tk/tabs/iso16358_tab.py ui_tk/sections/iso_cspf_section.py ui_tk/sections/iso_hspf_section.py tests/test_ui_tk_iso_table_autocalc.py` | PASS |
| `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_iso16358_helpers.py -q -rxXs` | PASS: `15 passed` |
| `python3 -B -m pytest -q -rxXs` | PASS: `631 passed, 32 skipped, 19 xfailed` |

- Full suite baseline delta versus provided recent baseline (`630 passed, 32 skipped, 19 xfailed`): `+1 passed` from the added responsive layout test; skipped/xfail unchanged.
- Native abort: not observed.
- Manual macOS UX smoke: not performed in this implementation task.

## Project Memory Delta

- type: decision
  topic: tkinter-responsive-matrix-table-architecture
  content: "Tkinter ISO Hong Kong matrix and summary surfaces now use character/font-based requested sizing with parent-driven responsive stretch and public cell metadata for a later interaction controller; fixed pixel content-width alignment was removed while auto-calc and result behavior remain unchanged."
  keywords:
    - Tkinter
    - input matrix
    - result surface
    - responsive layout
    - Excel-like
    - Hong Kong
  assertionStatus: observed
  source: result_reports/active/170_tkinter-responsive-table-architecture-alignment.md
