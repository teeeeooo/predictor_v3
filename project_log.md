# Project Log

이 문서는 milestone decision, durable failure/lesson, process rule를
보존하는 기록입니다.

## Project Log Policy

- `project_log.md`는 milestone decision, durable failure/lesson,
  process-rule change만 기록한다.
- ordinary 작업 상세는 Git diff/commit history, focused validation,
  terminal/final output에 남긴다. compact record는 conditional trigger에서만
  작성한다.
- 장기 기억 후보는 Memory Review Gate를 통해
  `result_reports/memory/project_memory_seed.md`에서 선별 관리한다.
- report 본문이나 seed entry 전문을 `project_log.md`에 반복 복사하지 않는다.
- 기존 과거 로그는 보존하며, policy 추가 작업에서 기존 날짜별 항목을 재작성, 축약, 삭제하지 않는다.
- 새 로그를 추가하기 전 최근 2~3개 로그와 merge 가능한지 먼저 확인하고, 유사한 내용이면 중복 section을 만들지 않는다.
- 과거 로그는 `docs/archive/project_log/YYYY-MM/` capped segment archive 파일에서 heading 검색 후 필요한 범위만 확인한다.

## Historical Log Archives

- `docs/archive/project_log/2026-05/project_log_2026-05_part01_2026-05-18_to_2026-05-10.md`
- `docs/archive/project_log/2026-05/project_log_2026-05_part02_2026-05-04_to_2026-05-05.md`
- `docs/archive/project_log/2026-05/project_log_2026-05_part03_2026-05-06_to_2026-05-07.md`
- `docs/archive/project_log/2026-05/project_log_2026-05_part04_2026-05-11_to_2026-05-17.md`
- `docs/archive/project_log/2026-05/project_log_2026-05_part05_2026-05-24_to_2026-05-19.md`
- `docs/archive/project_log/2026-06/project_log_2026-06_part01_2026-06-10_to_2026-06-07.md`
- `docs/archive/project_log/2026-06/project_log_2026-06_part02_2026-06-30_to_2026-06-04.md`
- `docs/archive/project_log/2026-06/project_log_2026-06_part03_2026-06-30_to_2026-06-29.md`
- `docs/archive/project_log/2026-07/project_log_2026-07_part01_2026-07-29_to_2026-07-26.md`
- `docs/archive/project_log/2026-07/project_log_2026-07_part02_2026-07-26_to_2026-07-18.md`
- `docs/archive/project_log/2026-07/project_log_2026-07_part03_2026-07-18_to_2026-07-01.md`

> **Ordering note:** `partNN` 순서는 original `project_log.md` entry order를 보존한다. `project_log.md`는 최신 항목이 위에 오는 reverse chronological order이므로, segment filename의 date range도 reverse chronological일 수 있다. 과거 로그를 찾을 때는 파일명만 보지 말고 `rg -n "^## 2026-" docs/archive/project_log/YYYY-MM/*.md`로 heading을 검색한다.

## 2026-07-31 — Predict input workflow broad overhaul activation

### Decision

- The user approved **Predict input workflow broad overhaul** as the next product
  workstream.
- Documentation lifecycle cleanup precedes source work so the current-state
  documents recover their owner boundaries before design or implementation.
- The overhaul changes shared case-table public behavior across several owners,
  so source work requires a Lane C Build handoff.
- A fresh current-state audit is required before detailed design. The expected
  audit areas are:
  - unified one-row-per-case table workflow;
  - row add, duplicate, delete, and reset;
  - spreadsheet selection, copy/paste, clear, undo, and keyboard navigation;
  - manual, mapping-backed, calculated, result, and status cell roles;
  - mapping cascade discoverability;
  - validation/warning and per-row/global issue placement; and
  - table width, internal scrolling, frozen identity candidates, and responsive
    viewport behavior.
- This documentation commit performs no source implementation.
