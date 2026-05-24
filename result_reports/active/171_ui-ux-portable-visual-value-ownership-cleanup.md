# 171. UI/UX Portable Visual Value Ownership Cleanup

## Goal

Tkinter matrix/result UI에 남아 있던 component-local visual value를
명시적인 owner로 모으고, `docs/ui_ux`를 다른 프로젝트에 적용할 때
필요한 portable adoption kit와 최소 ownership guard를 정의한다.

## Scope

- `ui_tk/layout_constants.py`를 Tkinter table/result concrete visual
  value owner로 사용한다.
- `MetricInputTable`과 `ResultPanel`은 visual value를 import하여
  소비만 하도록 정리한다.
- portable UI/UX adoption guide와 active document 연결을 추가한다.
- `ui_tk` component 범위의 단일 visual-value ownership boundary
  guard 및 focused tests를 추가한다.
- `docs/WORK_PLAN.md`의 다음 실행 순서를 task 171 이후 상태로
  기록한다.

## Non-goals

- Excel-like selection/copy/paste/undo/drag 구현
- graph/detail 또는 Canvas chart 구현, `matplotlib` 도입
- UI layout 구조, responsive sizing policy, auto-calc, result
  formatting 또는 calculator mapping 변경
- core/profile/dispatcher, expected/golden/fixture, PyQt/Predict/Train,
  packaging 변경
- `project_log.md`, `result_reports/memory/project_memory_seed.md`
  수정 또는 lifecycle maintenance

## Evidence And Design Gate

- Branch는 작업 시작 시 `work/ui-ux-ssot-adoption`이며 origin과
  sync된 clean 상태였다.
- `project_memory_seed.md`는 `Tkinter`, `input matrix`, `result
  surface`, `visual design`, `Hong Kong`, `CSPF`, `HSPF`, `graph
  detail`, `PyQt retirement` keyword 결과 주변만 확인했다. 관련
  evidence는 matrix/result UI 유지, graph/detail 및 retirement
  deferred, active visual owners 유지였다.
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`,
  `04_VISUAL_DESIGN_ARCHITECTURE.md`,
  `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`,
  `adapters/TKINTER_TABLE_ADAPTER.md`의 관련 heading/owner 표현만
  확인했다.
- AGENTS Design Gate에 따라 공통 boundary를 먼저 확정했다.
  `ui_tk/layout_constants.py`가 Tkinter concrete visual value를
  소유하고 table/result components는 소비만 한다. Toolkit-neutral
  foundation의 전면 wiring, interaction, graph, calculator behavior는
  이 작업에서 변경하지 않는다.

## Task Results

### Task 1: Ownership State

- `ui_tk/metric_input_table.py`에는 grid/header/editable/static
  palette를 위한 raw hex local constants 6개가 남아 있었다.
- `ui_tk/result_panel.py`에는 grid/title/header/value/status
  palette를 위한 raw hex local constants 5개가 남아 있었다.
- `ui_tk` 전체 raw hex 스캔 결과 해당 두 component 외 추가
  palette literal은 없었다.
- 문제는 색상 값 하나의 선택이 아니라, concrete visual value를
  component가 직접 소유해 active docs의 token-owner 방향을
  강제할 boundary가 없었다는 점이었다.

### Task 2: Tkinter Visual Value Owner

- `ui_tk/layout_constants.py`에 `TABLE_*` 및 `RESULT_*` color/state
  tokens를 추가하고 기존 값 그대로 이전했다.
- `MetricInputTable`과 `ResultPanel`의 raw hex/local palette
  constants를 제거하고 owner token imports로 치환했다.
- 색상 값, responsive weight/metadata registry, table/result widget
  roles, parsing, auto-calc 및 result rendering 흐름은 변경하지
  않았다.
- `ui_common/visual_tokens.py`로 widget wiring을 강제하지 않았다.
  현재 변경은 기존 Tkinter surface에 필요한 concrete binding을
  local owner에 모으는 좁은 adoption 단계이기 때문이다.

### Task 3: Portable Adoption Kit

- `docs/ui_ux/06_PORTABLE_UI_UX_ADOPTION_GUIDE.md`를 추가했다.
  common docs, project binding document, token owner, toolkit adapter,
  component owner, optional interaction controller, optional
  Canvas/detail component, ownership guard를 함께 이식해야 하는 kit로
  정의한다.
- `docs/ui_ux/00_UI_UX_SYSTEM.md`와
  `02_DESIGN_TOKENS_AND_LAYOUT.md`에 portable guide 및 concrete owner
  boundary를 연결했다.
- `ACTIVE_DOCUMENTS.md`에 신규 guide를 active UI/UX owner
  document로 등록했다.
- 외부 선행 구현은 reference evidence일 뿐 architecture naming
  source나 owner가 아니라는 원칙을 기록했다.

### Task 4: Minimal Boundary Guard

- `tools/check_code_structure.py`에 하나의 configurable
  `check_ui_visual_value_ownership()` boundary check를 추가했다.
- 설정은 `UI_VISUAL_SCAN_ROOTS`, `UI_VISUAL_OWNER_PATHS`,
  `UI_VISUAL_ALLOWLIST_PATHS`로 분리했다. 현재 scan scope는
  `ui_tk`이고 owner는 `ui_tk/layout_constants.py` 및 기존
  toolkit-neutral foundation 경로다.
- component에서 raw hex literal 또는 module-level visual constants
  (`*_BG`, `*_FG`, `*_COLOR`, `*_FONT`, `*_PAD*`, `*_WIDTH`,
  `*_HEIGHT`)를 정의하면 error finding을 낸다.
- 숫자 literal 전체, docs, tests, legacy evidence, calculation
  modules를 검사하는 규칙은 추가하지 않았다. 이 guard는 style
  lint 묶음이 아니라 owner boundary 확인 하나다.

### Task 5: Tests And Work Plan

- `tests/test_code_structure_guard.py`에 raw hex component finding,
  component-local token finding, owner-file allowance, non-UI/core
  exclusion의 네 case를 추가했다.
- `docs/WORK_PLAN.md`에 task 171 owner cleanup을 기록하고 다음
  recommended action을 유지했다:
  1. Tkinter Excel-like table behavior controller
  2. Tkinter Canvas graph/detail surface design
  3. Tkinter standard/region expansion plan
  4. Windows PyInstaller size measurement
  5. PyQt calculator source retirement 재검토

## Verification

| Command | Result |
| --- | --- |
| `python3 -B tools/check_code_structure.py` | PASS: `code structure guard: OK (no findings)` |
| `python3 -B -m py_compile ui_tk/layout_constants.py ui_tk/metric_input_table.py ui_tk/result_panel.py tools/check_code_structure.py tests/test_code_structure_guard.py` | PASS |
| `python3 -B -m pytest tests/test_code_structure_guard.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_iso16358_helpers.py -q -rxXs` | PASS: `39 passed` |
| `python3 -B -m pytest -q -rxXs` | PASS: `635 passed, 32 skipped, 19 xfailed` |
| `git diff --check` | PASS |
| modified-file check for `project_log.md` and `result_reports/memory/project_memory_seed.md` | PASS: unchanged |

Full suite baseline was `631 passed, 32 skipped, 19 xfailed`.
The `+4 passed` delta is exactly the new guard coverage; skipped and
xfail counts are unchanged. No native abort occurred.

## Changed Files

- `ui_tk/layout_constants.py` - Tkinter table/result concrete visual
  value owner tokens.
- `ui_tk/metric_input_table.py` - consumes owner tokens instead of
  defining local palette values.
- `ui_tk/result_panel.py` - consumes owner tokens instead of defining
  local palette values.
- `tools/check_code_structure.py` - configurable UI visual-value
  ownership boundary check.
- `tests/test_code_structure_guard.py` - four boundary cases.
- `docs/ui_ux/06_PORTABLE_UI_UX_ADOPTION_GUIDE.md` - portable
  adoption kit owner guide.
- `docs/ui_ux/00_UI_UX_SYSTEM.md` - links portable guide from root.
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md` - clarifies concrete
  owner and adoption boundary.
- `ACTIVE_DOCUMENTS.md` - registers the new active guide.
- `docs/WORK_PLAN.md` - records completion and next actions.

## Known Failures / Risks

- The guard intentionally protects newly declared raw colors and
  module-level visual tokens in adopted `ui_tk` components. It is not a
  blanket audit of every existing widget geometry literal.
- No manual visual smoke was required because behavior and layout were
  not changed; the existing next implementation phase remains the
  Excel-like behavior controller.

## Next Suggested Action

Implement the Tkinter Excel-like table behavior controller against the
metadata registry retained by `MetricInputTable`, without moving visual
value ownership out of `ui_tk/layout_constants.py`.

## Scope Compliance

- No interaction, graph/detail, packaging, standard/region expansion,
  calculator logic, profile/dispatcher, golden/fixture, PyQt, or
  Predict/Train implementation was changed.
- `project_log.md` and `result_reports/memory/project_memory_seed.md`
  were not modified.
- No lifecycle summary/archive move was performed.

## Commit / Push

- Source/docs/test commit: `fe282fa` (`refactor: consolidate UI visual value ownership`)
- Report commit: this report is committed separately with a `report:`
  commit message.
- Push target: `origin/work/ui-ux-ssot-adoption`, after report commit.

## Project Memory Delta

```yaml
- type: decision
  topic: portable-ui-visual-value-ownership
  content: "predictor_v3 Tkinter table and result components consume concrete visual values from ui_tk/layout_constants.py, while a configurable ui_tk ownership boundary guard rejects component-local raw colors and visual token declarations; portable UI/UX adoption requires docs, token owner, component skeleton, adapter, and guard configuration together."
  keywords:
    - UI/UX
    - Tkinter
    - visual value ownership
    - portable adoption
    - table surface
    - result surface
  assertionStatus: verified
  source: result_reports/active/171_ui-ux-portable-visual-value-ownership-cleanup.md
```
