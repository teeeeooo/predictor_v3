# 168 Tkinter ISO Hong Kong Layout Correction

## Work Contract

- Goal: 사용자 확인 피드백에 맞춰 Tkinter ISO Hong Kong CSPF/HSPF visible layout을 correction한다.
- Scope: `ui_tk` ISO section/tab/result/input surface, 해당 widget-structure tests, 최소 UX docs와 `WORK_PLAN`.
- Non-goals: Excel-like behavior, graph/detail, standard/region 확장, PyQt 변경/retirement, core/profile/dispatcher/fixture/golden 변경, packaging, lifecycle maintenance.
- Verification: structure guard, `py_compile`, targeted Tkinter UI/helper tests, full pytest suite.

## Project Memory Recall Gate

`result_reports/memory/project_memory_seed.md`는 전문을 읽지 않고 요청 keyword에 대한 `rg -n` 제한 검색으로만 확인했다. 확인된 evidence는 다음과 같다.

- Tkinter ISO Hong Kong CSPF/HSPF는 matrix input, auto-calc, compact result surface를 유지해야 한다.
- 기존 smoke 값은 CSPF `4.939`, HSPF `3.643`이다.
- graph/detail과 PyQt retirement는 후속 판단으로 hold되어 있다.
- table behavior의 Excel-like contract는 별도 후속 구현 범위다.

이 evidence는 현재 prompt와 active UX/design docs를 대체하지 않으며, `project_memory_seed.md`는 수정하지 않았다.

## Task 1: Input Layout Correction

`ui_tk/sections/iso_cspf_section.py`와 `ui_tk/sections/iso_hspf_section.py`를 수정했다.

- 각 metric에 별도 `rated_table` surface를 두고 row label을 `정격 표기치`로 표시한다.
- `정격 표기치` surface는 `능력 [W]` 입력 하나만 가지며 `전력 [W]` row/cell을 만들지 않는다.
- CSPF 시험 입력 matrix는 `35 Full`, `35 Half` columns와 `능력 [W]`, `전력 [W]` rows만 가진다.
- HSPF 시험 입력 matrix는 `7 Full`, `7 Half` columns와 `능력 [W]`, `전력 [W]` rows만 가진다.
- `ui_tk/metric_input_table.py`의 numeric `Entry` 정렬을 가운데로 변경했다.
- 정격 값과 시험 값은 기존 calculator input key로 다시 병합하므로 계산 의미와 defaults는 바뀌지 않는다.

## Task 2: Result Placement And Error Surface

`ui_tk/tabs/iso16358_tab.py`와 `ui_tk/result_panel.py`를 수정했다.

- 각 metric section이 자신의 compact `ResultPanel`을 입력 바로 아래 렌더링한다.
- visible composition은 `CSPF 입력 → CSPF 결과 → HSPF 입력 → HSPF 결과` 순서다.
- tab 하단의 공통 result surface는 렌더링하지 않는다. 기존 단순 panel-availability caller를 깨지 않도록 `tab.result_panel`은 첫 section result panel에 대한 compatibility alias만 유지한다.
- visible `결과 복사`, `결과 지우기` 버튼은 제거했다. `ResultPanel.copy()`, `clear()`, `append()`, `set_text()` compatibility API는 삭제하지 않았다.
- valid result는 기존 compact header/value/status summary table을 유지한다.
- invalid/missing status처럼 field가 없는 summary는 gray title/header/value cell을 만들지 않는 `status_surface` 하나로 표시한다. 따라서 입력 오류 시 정상 result table 일부처럼 보이는 gray block이 생기지 않는다.
- 자동 재계산은 metric별 latest result를 교체하므로 결과 이력을 누적하지 않는다.

## Feedback Mapping

- Feedback 2~4: `정격`/`정격 난방`을 시험 matrix에서 제거하고 capacity-only `정격 표기치` surface로 분리했다.
- Feedback 5: 각 section 내부 결과 panel로 composition을 재배치해 CSPF input/result 다음 HSPF input/result 순서를 만든다.
- Feedback 6: 하단 공통 result button surface와 visible copy/clear buttons를 제거했다.
- Feedback 7: numeric entries를 가운데 정렬한다.
- Feedback 8: invalid result는 status-only role로 렌더링하고 summary header/value roles를 만들지 않는다.

## Task 3: Test Coverage

`tests/test_ui_tk_iso_table_autocalc.py`를 갱신했다.

- 별도 `rated_table` 존재, `정격 표기치` label, rated surface 내 power cell 부재를 검증한다.
- CSPF/HSPF 시험 matrix columns와 editable role 수를 검증한다.
- section/result title과 widget grid 순서로 입력/결과 composition을 검증한다.
- visible copy/clear/calculate button 부재와 numeric center alignment를 검증한다.
- default auto-calc 결과 CSPF `4.939`, HSPF `3.643` 및 section-local non-accumulating results를 검증한다.
- invalid input이 `status_surface`만 표시하고 `summary_title`, header/value roles, `None`, long raw float, traceback을 표시하지 않음을 검증한다.

Screenshot/pixel/geometry exact-match test, fixture/golden 변경, PyQt test 변경은 하지 않았다.

## Task 4: Docs And Plan

- `docs/guides/lightweight_calculator_tk_manual_smoke.md`: 168 화면 구조, section-local results, centered numeric inputs, status-only invalid feedback, copy/clear button 부재를 manual 확인 항목으로 반영했다. 이번 작업에서 manual smoke 자체는 수행하지 않았다.
- `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md`: task 168 layout correction completion을 짧게 추가했다.
- `docs/WORK_PLAN.md`: task 168 완료 항목과 다음 recommended action 순서를 기록했다.

Next recommended action order:

1. Tkinter Excel-like table behavior.
2. Tkinter graph/detail surface design.
3. Tkinter standard/region expansion plan.
4. Windows PyInstaller size measurement, Windows host available 시.
5. PyQt calculator source retirement 재검토, Tkinter UX/기능 migration/packaging 판단 이후.

## Boundaries Maintained

- Core calculator, profile, dispatcher, expected/golden, fixture는 수정하지 않았다.
- Excel-like behavior, graph/detail, large dependency, visual-token full wiring은 구현하지 않았다.
- PyQt source/Predict/Train과 packaging은 건드리지 않았다.
- `ACTIVE_DOCUMENTS.md`, `project_log.md`, `project_memory_seed.md`는 수정하지 않았다.
- 현재 active report는 165 lifecycle summary 이후 진행되는 새 implementation report이므로 lifecycle archive/summary maintenance는 수행하지 않았다.

## Verification

| Command | Result |
| --- | --- |
| `python3 -B tools/check_code_structure.py` | PASS: `code structure guard: OK (no findings)` |
| `python3 -B -m py_compile ui_tk/metric_input_table.py ui_tk/result_panel.py ui_tk/tabs/iso16358_tab.py ui_tk/sections/iso_cspf_section.py ui_tk/sections/iso_hspf_section.py tests/test_ui_tk_iso_table_autocalc.py` | PASS |
| `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_iso16358_helpers.py -q -rxXs` | PASS: `14 passed` |
| `python3 -B -m pytest -q -rxXs` | PASS: `630 passed, 32 skipped, 19 xfailed` |

- Full suite baseline delta versus the provided recent baseline (`630 passed, 32 skipped, 19 xfailed`): none.
- Remaining xfail count: `19`, unchanged.
- Native abort: not observed.
- Manual macOS UX smoke: not performed; it remains a subsequent user-visible verification activity after this implementation.

## Project Memory Delta

- type: decision
  topic: tkinter-iso-hong-kong-layout-correction
  content: "Tkinter ISO Hong Kong now separates capacity-only `정격 표기치` surfaces from full/half trial matrices, places each compact result directly below its metric input, omits visible bottom copy/clear controls, centers numeric editors, and renders invalid feedback as a status-only surface while preserving auto-calc and default results."
  keywords:
    - Tkinter
    - Hong Kong
    - CSPF
    - HSPF
    - input matrix
    - result surface
  assertionStatus: observed
  source: result_reports/active/168_tkinter-iso-hk-layout-correction.md
