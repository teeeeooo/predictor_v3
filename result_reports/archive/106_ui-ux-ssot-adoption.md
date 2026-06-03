# 106 — UI/UX SSOT Adoption

## Goal

새 UI/UX 문서 세트를 `docs/ui_ux/` 아래 active SSOT로 도입하고, 기존
`docs/ui/SPREADSHEET_TABLE_CONTRACT.md` 단일 owner 참조를 새 SSOT 경로로 이관한다.
계산기 UI/계산 로직/unit adapter/ML 코드는 건드리지 않는다.

## Scope

- `docs/ui_ux/` 도입 (이미 직전 docs commit에 포함됨, task 1)
- `docs/ui/SPREADSHEET_TABLE_CONTRACT.md` 삭제 + `docs/ui/` 폴더 제거 (task 2)
- `AGENTS.md`, `AGENT_TASK_ROUTER.md` UI/table hook 갱신 (task 3)
- `ACTIVE_DOCUMENTS.md` UI/UX owner 관계 갱신 (task 4)
- `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`
  inheritance note 갱신 (task 5)
- `docs/WORK_PLAN.md` 상태 및 다음 순서 갱신 (task 6)
- 본 report 작성

## Non-goals

- 계산기 UI 코드 수정
- 계산 로직 수정
- unit adapter 작업
- ML / inverse-search 작업
- 새 UI/UX 문서 본문 재작성
- `_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md` 중복 추가
- `docs/architecture/project_architecture.md` 본문 재구성 (참조 경로만 갱신)
- result report lifecycle maintenance (active 8~12개 미달, summary 미생성)
- archive/summaries 과거 report 수정

## Verification

- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` → 3 passed
- `python3 -B -m pytest -q` → 430 passed, 6 skipped, 23 xfailed
- `grep -rln "docs/ui/SPREADSHEET_TABLE_CONTRACT.md" --include="*.md"` 의
  active doc 잔존 hit은 본 작업의 narrative 설명 라인 2건 뿐 (참조용 아닌
  변경 이력 설명) — `AGENT_TASK_ROUTER.md` shared guardrail의 legacy
  안내 라인, `docs/WORK_PLAN.md`의 도입 완료 라인.
- archive/summaries 의 historical hit은 의도적으로 보존.

## Task Results

### task 1 — `docs/ui_ux/` 도입
- 상태: 이미 직전 commit `docs : make new ui_ux folder and add files`
  (822b88e) 시점에 다음 파일이 모두 도입되어 있음.
  - `docs/ui_ux/00_UI_UX_SYSTEM.md`
  - `docs/ui_ux/01_TOOLKIT_SELECTION_POLICY.md`
  - `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
  - `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
  - `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`
  - `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
  - `docs/ui_ux/_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md`
- 새 UI/UX 문서 본문 수정 없음.
- `_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md`는 중복 추가하지
  않고 `docs/ui_ux/_source/`에만 history source로 유지. 동일 본문의
  legacy 파일이 두 곳에 존재하지 않게 task 2에서 `docs/ui/` 측을
  삭제하여 single-source 정리.
- 본 작업에서 task 1 영역의 추가 변경은 없음.

### task 2 — legacy 경로 삭제
- 사용자 선택에 따라 `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`는 redirect로
  남기지 않고 `git rm`으로 삭제.
- `docs/ui/` 폴더가 비어 `rmdir`로 제거. 이제 active SSOT는
  `docs/ui_ux/`로 단일화.
- active reference (active docs 한정):
  - table UX: `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
  - PyQt 구현: `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`
  - 전체 UI/UX root: `docs/ui_ux/00_UI_UX_SYSTEM.md`
- archive/summaries 의 historical 참조는 그대로 둠.

### task 3 — agent entry hooks
- `AGENTS.md` Non-Negotiable Boundaries UI/table 항목에서 기존
  `docs/ui/SPREADSHEET_TABLE_CONTRACT.md` 참조를 새 SSOT 경로(UI/UX
  root + table UX contract + PyQt 구현 adapter)로 교체. Excel-like
  baseline, QTableWidget / setCellWidget 금지, blockSignals try/finally
  guardrail은 그대로 유지.
- `AGENT_TASK_ROUTER.md`:
  - Shared Guardrails / UI 경계 항목을 새 SSOT 경로로 교체하고 Tkinter
    adapter 참조도 추가. legacy 삭제 사실을 한 줄 안내로 명시.
  - section 8 (UI 수정) 의 조건부 참조 및 절차 step 2 를 새 경로로 갱신.
  - section 7 (Notes 내용 정리 / 문서 리팩토링) 끝에 active SSOT
    (`docs/ui_ux/`) 와 legacy source (`docs/ui_ux/_source/`) 혼동
    방지 안내 1줄 추가.
- 기존 guardrail (QTableView+QAbstractTableModel+QStyledItemDelegate
  패턴, QTableWidget/setCellWidget 신규 도입 금지, Excel-like baseline,
  blockSignals try/finally) 은 약화 없이 유지.

### task 4 — ACTIVE_DOCUMENTS.md
- Core Project Docs 표의 기존 `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`
  row 하나를 다음 7개 row로 교체:
  - UI/UX SSOT root (`docs/ui_ux/00_UI_UX_SYSTEM.md`)
  - Toolkit policy (`docs/ui_ux/01_TOOLKIT_SELECTION_POLICY.md`)
  - Design tokens/layout (`docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`)
  - Table UX contract (`docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`)
  - PyQt adapter (`docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`)
  - Tkinter adapter (`docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`)
  - Legacy source (`docs/ui_ux/_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md`)
- Design Records 표의 calculator horizontal table input UI row의
  outbound 참조를 `docs/ui_ux/` 경로로 교체.
- 그 외 active doc 관계는 건드리지 않음 (대규모 재작성 회피).
- 사용자 선택에 따라 `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`는 삭제했
  으므로 "Legacy redirect" 행은 만들지 않고, legacy source 파일 자체만
  history pointer로 inventory에 남김.

### task 5 — calculator design doc
- `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`:
  - 상단 Scope note를 새 SSOT 경로 (UI/UX root + table UX contract +
    PyQt adapter)를 명시하는 형태로 교체하면서, 이 문서가 calculator-
    specific table shape / unit boundary / migration order 만 정의한
    다는 책임 경계를 다시 강조.
  - Confirmed Decisions / Table input UI 두 bullet 의 owner 참조를
    새 경로로 교체.
- AHRI/EN/ISO table shape, 능력/전력 row, unit label, profile-bound
  column set, ML W ↔ calculator-native unit boundary 본문은 변경하지
  않음.

### task 6 — WORK_PLAN
- Current milestone focus 의 "전역 PyQt spreadsheet-like table UI는
  `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`를 단일 owner" 문장을 새
  SSOT 경로 (`docs/ui_ux/00_UI_UX_SYSTEM.md` / `…/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
  / `…/adapters/PYQT_TABLE_IMPLEMENTATION.md`)로 교체하고 legacy 파일
  삭제 사실을 명시.
- Near-term execution order 항목 3 의 sequence를 다음으로 갱신:
  1. Calculator UI/UX audit against new SSOT
  2. unit adapter 확장 — ISO / KS / EN profile
  3. ML / inverse-search 복귀 준비
- 항목 4 의 "전역 table contract" 줄에서 `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`
  참조를 새 SSOT 경로로 교체.
- 계산기 UI code polish 는 이번 작업에 포함하지 않음 (audit phase로만 둠).
- result report lifecycle maintenance 는 이번 작업 scope 가 아니라서
  WORK_PLAN 에 별도 항목으로 추가하지 않음. Known Risks 에 pending 으로 기록.

## Test Results

- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → 3 passed in 0.13s
- `python3 -B -m pytest -q`
  → 430 passed, 6 skipped, 23 xfailed in 2.56s

## Changed Files

- D `docs/ui/SPREADSHEET_TABLE_CONTRACT.md` (legacy 삭제)
- D `docs/ui/` 폴더 (빈 폴더 제거)
- M `AGENTS.md`
- M `AGENT_TASK_ROUTER.md`
- M `ACTIVE_DOCUMENTS.md`
- M `docs/architecture/project_architecture.md`
- M `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`
- M `docs/WORK_PLAN.md`
- A `result_reports/active/106_ui-ux-ssot-adoption.md`

## Known Failures / Risks

- result report lifecycle maintenance pending — `result_reports/active/`
  에 누적된 보고서가 lifecycle gate trigger 부근까지 가 있지만, 본
  작업 scope는 docs SSOT adoption 으로 한정. 별도 lifecycle maintenance
  작업에서 정리.
- 계산기 UI 코드 자체는 아직 새 UI/UX SSOT 와 일치하는지 audit 되지
  않음 — WORK_PLAN 의 다음 step (Calculator UI/UX audit against new SSOT)
  에서 다룸. 본 작업에서는 코드/UI 변경 없음.
- 새 UI/UX 문서 본문에 repo 경로/링크가 정확히 일치하지 않는 항목이
  있다면 본문 대규모 수정 없이 보존. follow-up 으로 audit 단계에서
  확인 필요.

## Next Suggested Action

1. Calculator UI/UX audit against new SSOT — 계산기 각 tab (AHRI SEER2,
   AHRI HSPF2, EN14825 SEER/SCOP, ISO16358 CSPF/HSPF, KS, Hong Kong,
   India ISEER, SASO) 의 table 입력/결과 surface가
   `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` 와
   `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md` 와 정렬되는지
   audit.
2. unit adapter 확장 — ISO / KS / EN profile.
3. ML / inverse-search 복귀 준비.

## Scope Compliance

- 계산기 UI 코드, 계산 로직, unit adapter, ML 코드 미수정.
- 새 UI/UX 문서 본문 미수정.
- `_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md` 중복 추가 없음.
- archive/summaries 과거 report 미수정.
- expected / fixture / xfail / golden 미수정.
- AGENTS_FULL.md 미열람.
- result report lifecycle maintenance 미실행 (Known Risks에 명시).

## Commit / Push

- source/docs 변경 commit 후 report commit 분리.
- commit message: `docs: adopt UI UX SSOT`
- report commit message: `report: 106 UI UX SSOT adoption`
- push to `work/ui-ux-ssot-adoption` branch.
