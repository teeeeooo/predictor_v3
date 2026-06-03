# 169 Tkinter Table/Card Width Alignment Refinement

## Work Contract

- Goal: task 168의 ISO Hong Kong 화면 구조를 유지하면서 rated/trial/result table의 폭, left edge, spacing을 한 section content-width contract로 정렬한다.
- Scope: Tkinter local layout constants, `MetricInputTable`, `ResultPanel`, CSPF/HSPF section composition, widget-contract tests, 최소 UX docs와 `WORK_PLAN`.
- Non-goals: Excel-like interaction, graph/detail 구현, Canvas chart 구현, `matplotlib`, standard/region 확장, PyQt 변경/retirement, core/profile/dispatcher/fixture/golden 변경, packaging.
- Verification: structure guard, `py_compile`, targeted Tkinter tests, full pytest suite.

## Project Memory Recall Gate

`result_reports/memory/project_memory_seed.md`는 요청 keyword에 대한 `rg -n` 제한 검색으로만 확인했다.

- Project-wide owners are `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md` and `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`.
- Tkinter ISO Hong Kong CSPF/HSPF retains matrix input, auto-calc, summary result surfaces, and smoke values.
- Graph/detail and PyQt calculator retirement remain held for later phases.

Memory seed는 evidence로만 사용했으며 수정하지 않았다.

## Task 1: Mismatch Cause And Scope

Task 168 이후 structure는 정격 표기치 분리 및 section-local result 배치를 이미 충족했다. Width mismatch 원인은 widget sizing이었다.

- `MetricInputTable`은 각 table의 현재 cell content/requested width에 의존했다. 따라서 1-column `정격 표기치` table과 2-column 시험 입력 table이 다른 폭으로 렌더링됐다.
- `ResultPanel`은 section에서 `sticky="ew"`로 배치되었고 summary field 구성에 따라 입력 table과 별도로 넓어질 수 있었다.
- 동일 section 내부에 공통 content width 및 horizontal padding owner가 없었다.

이번 작업은 visible layout alignment only이며 interaction, graph/detail, 계산/formatting route는 수정하지 않는다.

## Task 2: MetricInputTable Width Contract

신규 `ui_tk/layout_constants.py`에 Tkinter calculator surface용 local contract를 추가했다.

- `MATRIX_ROW_HEADER_WIDTH`
- `MATRIX_DATA_COLUMN_WIDTH`
- `ISO_SECTION_DATA_COLUMNS`
- `ISO_SECTION_CONTENT_WIDTH`
- `ISO_SECTION_PADX`
- `ISO_SECTION_BLOCK_GAP`

`MetricInputTable`은 optional `row_header_width`, `data_column_width`, `total_columns_hint`를 받으며 아래 public inspection attributes를 노출한다.

- `row_header_width`
- `data_column_width`
- `total_columns_hint`
- `content_width`
- `table_frame.content_width`

Column minsize는 contract로 계산한다. 정격 표기치 같은 1-column table은 `total_columns_hint=2`를 사용해 동일 section의 2-column 시험 input surface와 같은 visual width를 차지한다. 기존 cell roles, centered numeric editor, values-changed callback, get/set/numeric parsing behavior는 유지한다.

## Task 3: Result And Section Alignment

- CSPF/HSPF `rated_table`과 `input_table` 모두 같은 `ISO_SECTION_DATA_COLUMNS` policy를 적용한다.
- `ResultPanel`은 `content_width`를 받고, summary header/value columns 및 status-only surface에 같은 content width를 적용한다.
- `ResultPanel`의 외부 `LabelFrame` inset은 heading label + bordered summary table wrapper로 정리해 result table left edge가 input table과 직접 맞도록 했다.
- Result panel 배치는 `sticky="w"`와 공통 `ISO_SECTION_PADX`를 사용해 input table과 같은 left-edge policy를 따른다.
- Section vertical spacing은 local block-gap constant를 사용해 rated/trial/result surface rhythm을 맞춘다.
- Task 168 composition (`CSPF 입력 → CSPF 결과 → HSPF 입력 → HSPF 결과`), visible bottom-button absence, invalid status-only surface는 유지한다.

Local Tk geometry probe after implementation showed equal bordered surface widths:

| Metric | Left offsets: rated / trial / result | Widths: rated / trial / result |
| --- | --- | --- |
| CSPF | `12 / 12 / 12` | `414 / 414 / 414` |
| HSPF | `12 / 12 / 12` | `414 / 414 / 414` |

This probe is implementation evidence, not a screenshot/pixel regression test.

## Task 4: Layout Contract Tests

`tests/test_ui_tk_iso_table_autocalc.py`를 보강했다.

- Both rated/trial tables expose and share row-header/data-column/total-columns/content-width contract attributes.
- Both metric result panels expose the same `content_width` used by input tables.
- Rated/input/result placement uses common horizontal padding and result alignment policy.
- Numeric editor center alignment, defaults CSPF `4.939` / HSPF `3.643`, button absence, latest-result replacement, and invalid `status_surface` protection remain covered.

Screenshot/pixel expected tests, PyQt tests, fixture/golden changes는 하지 않았다.

## Task 5: Docs And Next Actions

- `docs/guides/lightweight_calculator_tk_manual_smoke.md`: rated/trial/result width equality, left-edge alignment, section spacing 항목을 추가했다.
- `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`: task 169 completion과 Canvas-oriented later graph/detail direction을 기록했다.
- `docs/WORK_PLAN.md`: task 169 완료와 다음 순서를 추가했다.

Next recommended action order:

1. Tkinter Excel-like table behavior.
2. Tkinter Canvas graph/detail surface design.
3. Tkinter standard/region expansion plan.
4. Windows PyInstaller size measurement, Windows host available 시.
5. PyQt calculator source retirement 재검토, Tkinter UX/기능 migration/packaging 판단 이후.

`matplotlib`은 packaging size 판단 전 도입하지 않는다.

## Boundaries Maintained

- Core calculator, profile, dispatcher, expected/golden, fixture는 수정하지 않았다.
- Excel-like behavior, graph/detail, Canvas chart, `matplotlib`, visual-token full wiring은 구현하지 않았다.
- PyQt source/Predict/Train과 packaging은 건드리지 않았다.
- `ACTIVE_DOCUMENTS.md`, `project_log.md`, `project_memory_seed.md`는 수정하지 않았다.
- Lifecycle summary/archive 이동은 수행하지 않았다.

## Verification

| Command | Result |
| --- | --- |
| `python3 -B tools/check_code_structure.py` | PASS: `code structure guard: OK (no findings)` |
| `python3 -B -m py_compile ui_tk/layout_constants.py ui_tk/metric_input_table.py ui_tk/result_panel.py ui_tk/tabs/iso16358_tab.py ui_tk/sections/iso_cspf_section.py ui_tk/sections/iso_hspf_section.py tests/test_ui_tk_iso_table_autocalc.py` | PASS |
| `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_iso16358_helpers.py -q -rxXs` | PASS: `14 passed` |
| `python3 -B -m pytest -q -rxXs` | PASS: `630 passed, 32 skipped, 19 xfailed` |

- Full suite baseline delta versus provided recent baseline: none.
- Remaining xfail count: `19`, unchanged.
- Native abort: not observed.
- Manual macOS UX smoke: not performed in this implementation task.

## Project Memory Delta

- type: decision
  topic: tkinter-table-card-width-alignment
  content: "Tkinter ISO Hong Kong rated, trial-input, and compact result surfaces now share a local content-width and spacing contract, aligning each CSPF/HSPF section without changing calculation, auto-calc, result formatting, or invalid status behavior."
  keywords:
    - Tkinter
    - Hong Kong
    - input matrix
    - result surface
    - layout alignment
  assertionStatus: observed
  source: result_reports/active/169_tkinter-table-card-width-alignment-refinement.md
