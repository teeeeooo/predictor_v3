# 095 Excel-like Table Contract Clarification

## Goal
- 모든 PyQt table-shaped UI가 "Excel-like behavior"를 기본 UX 기준으로
  삼는다는 점을 active contract에 명시한다.
- agent가 UI 작업 시 이 기준을 놓치지 않도록 entry 문서 (AGENTS.md /
  AGENT_TASK_ROUTER.md) 와 calculator design doc에도 짧은 hook을 더
  한다.
- 코드 변경은 없다.

## Scope
- 수정: `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`, `AGENTS.md`,
  `AGENT_TASK_ROUTER.md`,
  `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`,
  `docs/WORK_PLAN.md`, 본 report.
- 변경하지 않음: `ui/**`, `core/**`, `tests/**`, `data/**`, AHRI/EN/ISO
  expected, xfail/fixture, ISO16358-2 HSPF mismatch (hold 유지).

## Non-goals
- ISO 테이블 코드 정렬 (코드 패치는 다음 slice).
- ISO16358-2 HSPF mismatch 후속 (외부 분석 대기 hold 유지).
- AHRI/EN/ISO calculator 또는 unit adapter 수정.

## Verification
| command | result |
| --- | --- |
| `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q` | 3 passed |
| `python3 -B -m pytest -q` | 464 passed, 34 xfailed (ISO16358-2 HSPF mismatch hold) |

## Task 1 — 전역 Excel-like 원칙 문서화
- 수정 파일: `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`.
- 추가 내용:
  - §1.1 "Excel-like UX is the project baseline" 절을 추가. 이 프로젝트의
    table UX 기준은 "Excel-like behavior"이며, 사용자는 매일 Excel /
    Google Sheets / Numbers를 다루는 spreadsheet muscle memory를
    가지고 있다는 전제를 명시. 기존 table이 이 동작과 다르면
    grandfathered exception 이 아니라 **contract alignment 대상**임을
    명시.
  - §3에 "Excel-like keyboard baseline (must-have)" 표를 추가:
    - `Ctrl+C`: 선택 영역 TSV 복사
    - `Ctrl+V`: TSV 붙여넣기 (top-left anchor)
    - `Delete` / `Backspace`: 선택 영역 clear
    - `Ctrl+Z`: undo
    - `Tab`: 오른쪽 셀
    - `Shift+Tab`: 왼쪽 셀
    - `Enter` / `Return`: 아래 셀
    - `Shift+Enter` / `Shift+Return`: 위 셀
  - 기존 §3의 본문은 그대로 유지하고 (§3.2로 묶어 보존) Excel-like
    baseline 표로 한 번 더 강조. wrap/clamp 세부 동작은 §10, copy /
    paste 상세는 §7, clear는 §8, undo는 §9에 위임.
- 기존 guardrail (§4 view/model/delegate 패턴, `QTableWidget` /
  `setCellWidget` 금지, paste path isolation, `blockSignals` try/finally,
  1-click editor, invalid 셀 시각 표시) 는 변경 없이 유지.

## Task 2 — AGENTS / Router hook 보강
- 수정 파일: `AGENTS.md`, `AGENT_TASK_ROUTER.md`.
- AGENTS.md (`Non-Negotiable Boundaries` 의 UI table 줄): 기존 문장에
  Excel-like baseline 한 줄을 이어 붙임 — "모든 table UX는
  Excel-like behavior를 기본으로 한다 (Ctrl+C TSV copy / Ctrl+V TSV
  paste / Delete·Backspace clear / Ctrl+Z undo / Tab→오른쪽 /
  Shift+Tab→왼쪽 / Enter→아래 / Shift+Enter→위). `QTableWidget` /
  `setCellWidget` 신규 도입 금지는 유지한다."
- AGENT_TASK_ROUTER.md (§8 UI 수정 절차 2번 줄): 기존 contract 확인
  지시 뒤에 Excel-like baseline을 명시하고, 기존 table이 어긋나면
  contract alignment 대상임을 적시. 기존 §4 / §13 checklist /
  `QTableWidget` 금지 / `setCellWidget` 금지 / signal blocking
  try/finally 룰은 변경 없이 유지.

## Task 3 — Calculator design doc 분리 명시
- 수정 파일:
  `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`.
- `Confirmed Decisions → Table input UI` 절 첫 bullet 앞에 한 bullet
  을 추가: "Calculator table surfaces (AHRI / EN14825 / future ISO
  migrations) inherit the global Excel-like table behavior from
  `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`. 이 design doc은 calculator
  별 table shape / unit / migration order 만 정의하고, navigation /
  copy / paste / clear / undo / invalid 세부 규칙은 전역 contract를
  따른다." 기존 bullets (AHRI/EN table shape, unit boundary 등) 은
  변경하지 않음.

## Task 4 — WORK_PLAN 갱신
- 수정 파일: `docs/WORK_PLAN.md`.
- "Near-term execution order" 3항을 다음 sequence로 갱신:
  1. ISO table Excel-like behavior patch — Ctrl+C copy, Delete/Backspace
     clear, invalid cell 시각화, Enter/Shift+Enter/Tab/Shift+Tab 방향
     정렬 (`ProfileInputGridModel` / `ProfileInputGridView`).
  2. ISO result/read-only table copy TSV — `TwoPointTableModel` /
     `RegionResultTableModel` / `TraceTableModel` /
     `RegionDetailTab.table` 에 TSV copy 추가.
  3. unit adapter 확장 — ISO / KS / EN profile.
  4. ML / inverse-search 복귀 준비.
- 4항에는 Excel-like baseline 문구가 contract / AGENTS / Router /
  calculator design doc에 명시 완료되었다는 사실과, 094 audit에서
  식별된 ISO16358-1 CSPF 입력표 (Copy / Clear / Invalid 시각 / Enter
  방향) 가 alignment 1번 대상임을 기록. ISO16358-2 HSPF mismatch는
  외부 분석 대기 hold 유지.

## 남은 위험
- 문서만 갱신했으므로 ISO 입력 표 사용자는 여전히 Excel과 다른
  동작 (Ctrl+C 미동작, Delete 무반응, invalid 셀 표시 없음,
  Enter→오른쪽)을 만난다. 첫 slice (Excel-like behavior patch) 가
  이 gap 을 닫는다.
- Enter / Shift+Enter 방향 변경은 기존 ISO 사용자에게 UX 변경이므로
  patch slice 진행 전 design gate / 사용자 확인이 필요할 수 있다.
- contract 본문이 길어지지 않도록 §3.2를 그대로 두고 §3.1에 한
  번 더 압축 표만 추가했다. 향후 §3.2 본문을 §3.1 표로 흡수하는
  cleanup은 별도 slice.
