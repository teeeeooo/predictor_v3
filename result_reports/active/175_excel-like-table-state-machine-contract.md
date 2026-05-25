# Excel-like table selection/edit state machine contract

## Goal

Spreadsheet-like table의 `Selection mode`와 `Edit mode`를
toolkit-agnostic UX ground rule로 정의하고, Tkinter/PyQt adapter 및
Tkinter manual smoke guide가 동일한 state machine을 따르도록 연결한다.

## Scope

- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
- `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/175_excel-like-table-state-machine-contract.md`

## Non-goals

- Python source code 또는 test 수정 없음.
- visual token 변경 없음.
- Canvas graph/detail, standard/region 확장, packaging, PyQt calculator
  retirement 수행 없음.
- `project_log.md`, `result_reports/memory/project_memory_seed.md` 및
  lifecycle summary/archive maintenance 수정 없음.

## Verification

- `python3 -B tools/check_code_structure.py` -> `code structure guard: OK (no findings)`
- `git diff --check` -> no output
- 변경 파일 확인 -> 지정된 docs 5개와 본 report만 변경 대상으로 확인
- 공통 contract 확인 -> `insertontime`, `focus_set`, `tk.Entry` 등 Tkinter
  구현 표현을 추가하지 않았고 기존 widget-class 예시도 toolkit-neutral
  문구로 정리
- manual smoke 확인 -> edit mode 동작은 통과 결과로 기록하지 않고
  확인 항목으로만 추가

## Task Results

### Task 1 결과

- 수정 파일: `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- 수정 내용: `Selection mode`와 `Edit mode`를 정의하고, no-selection
  click부터 edit-mode focus leave까지 요청된 이벤트 전이표를 추가했다.
  First printable key는 whole-cell replace이고, same-cell second
  click/double click/`F2`는 기존 값을 보존한 edit entry임을 필수
  baseline으로 명시했다. Arrow/Delete/Backspace/Esc 및 commit 동작의
  mode별 차이도 clear/navigation 섹션과 일치시켰다.
- 검증 결과: transition 표에 요청 이벤트가 모두 포함되며 공통 문서에
  Tkinter 구현 세부가 포함되지 않음을 diff로 확인했다.

### Task 2 결과

- 수정 파일: `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
- 수정 내용: Entry-grid adapter가 공통 selection/edit state machine을
  따른다고 명시하고, caret hidden/visible, type-to-replace,
  same-cell/double-click/`F2` edit entry, mode별
  Delete/Backspace/Arrow/Esc mapping을 adapter 수준으로 정리했다.
  기존 predictor_v3 numeric atomic paste는 paste-specific deviation임을
  분명히 남겼다.
- 검증 결과: adapter 문구만 변경했고 Python source 및 visual token
  파일은 변경하지 않았다.

### Task 3 결과

- 수정 파일: `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`
- 수정 내용: PyQt table도 공통 state machine을 따르며,
  selection model과 editor delegate lifecycle을 이용해 이를 구현해야
  한다는 연결 문구만 추가했다.
- 검증 결과: PyQt source code 또는 calculator retirement 관련 문구는
  변경하지 않았다.

### Task 4 결과

- 수정 파일: `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- 수정 내용: 첫 click 후 whole-cell replace, same selected cell
  reclick/double click/`F2` edit entry, caret visible, mode별
  Arrow/Delete/Backspace/Esc 차이를 step 9 확인 항목과 OK/NG 기록
  template에 추가했다.
- 검증 결과: 해당 항목은 manual verification 대상으로만 추가했으며
  구현 완료 또는 smoke pass로 기록하지 않았다.

### Task 5 결과

- 수정 파일: `docs/WORK_PLAN.md`,
  `result_reports/active/175_excel-like-table-state-machine-contract.md`
- 수정 내용: WORK_PLAN에 task 175-a 계약 보정 완료 항목을 추가하고,
  다음 recommended action을 **Tkinter Excel-like edit mode
  implementation**으로 지정했다. 본 result report를 작성했다.
- 검증 결과: `project_log.md`, `result_reports/memory/project_memory_seed.md`
  및 lifecycle summary/archive 파일은 수정하지 않았다.

## Test Results

- 문서 전용 변경이므로 Python UI/test suite는 실행 대상이 아니다.
- 요청된 structure guard와 whitespace diff 검증은 통과했다.
- 새 manual smoke 항목은 후속 Tkinter edit mode 구현 이후 사람이
  실행할 확인 항목이며, 현재 pass 판정을 하지 않았다.

## Changed Files

- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
- `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`
- `docs/guides/lightweight_calculator_tk_manual_smoke.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/175_excel-like-table-state-machine-contract.md`

## Documentation Sync Judgment

- `ACTIVE_DOCUMENTS.md`: 불필요. 기존 contract/adapter/manual guide/WORK_PLAN
  owner 관계가 바뀌지 않았고 신규 active owner 문서를 만들지 않았다.
- `project_log.md`: 수정하지 않음. 사용자가 직접 수정 금지를 명시했고,
  결정 사항은 본 report의 `Project Memory Delta`로 추적한다.
- `docs/WORK_PLAN.md`: 필요. 다음 실행 순서를 edit mode implementation으로
  변경하라는 명시 요청을 반영했다.
- `docs/REFACTOR_PLAN.md`: 불필요. 구조 분리 후보 또는 guardrail 변경이 없다.
- `project_brief.md`: 불필요. session handoff 대표 상태 변경 요청이 없다.
- 규격별 notes/dev_notes: 불필요. 규격 해석 또는 계산 근거 변경이 없다.

## Known Failures / Risks

- 공통 UX contract가 요구하는 edit-mode entry와 mode별 text editing은
  이번 문서 작업에서 구현하지 않았다. 현재 Tkinter behavior의 충족
  여부는 후속 구현 및 manual smoke 대상이다.
- active report 수는 본 report 포함 10개가 되어 routine lifecycle
  trigger 범위에 해당한다. 사용자가 lifecycle summary/archive maintenance와
  memory seed 직접 수정을 금지했으므로 본 작업에서는 수행하지 않는다.

## Next Suggested Action

1. **Tkinter Excel-like edit mode implementation** - same-cell second click,
   double click, `F2`, caret-visible partial editing, mode별
   Arrow/Delete/Backspace/Esc behavior를 구현하고 검증한다.

## Scope Compliance

- Python source/test 변경 없음: confirmed by changed-file review.
- visual token 변경 없음: confirmed by changed-file review.
- core/profile/dispatcher/calculator/golden/fixture 변경 없음: confirmed by
  changed-file review.
- `project_log.md` / `result_reports/memory/project_memory_seed.md` 수정 없음:
  confirmed by changed-file review.
- lifecycle summary/archive maintenance 없음: confirmed by changed-file
  review and explicit user restriction.

## Commit / Push

- Docs commit: `7a60c5d` (`docs: define Excel-like table selection and edit modes`)
- Report commit: this report is committed separately after creation.
- Push target: `origin/work/ui-ux-ssot-adoption`; push result is reported in
  the final task summary after the report commit is pushed.

## Project Memory Delta

- type: decision
  topic: Spreadsheet-like table selection and edit state machine
  content: `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` requires selection mode to perform whole-cell replacement on first printable input and cell-level navigation or clear actions, while same-cell second click, double click, and F2 enter edit mode without clearing the existing value so caret-based partial editing can occur.
  keywords:
    - predictor_v3
    - spreadsheet-like table
    - Excel-like
    - selection mode
    - edit mode
    - UI UX SSOT
  assertionStatus: verified
  source: `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` (Selection and edit state machine); docs commit `7a60c5d`
