# 024_refine-calculator-architecture-docs

## Goal
- 직전 calculator architecture reset(보고서 023) 이후 남은 문서 정합성 두 곳을 소폭 정리해, 다음 KS C 9306 분리 작업의 출발점이 흔들리지 않도록 한다.

## Scope
- `docs/WORK_PLAN.md`의 `Current milestone focus` 섹션을 calculator architecture reset 실행 / KS C 9306 분리 / `core/calculator_iso16358.py` ISO16358 전용 정리 선행 작업 중심으로 갱신했다.
- `docs/architecture/project_architecture.md` 상단 `## 1. 파일 구조 (File Structure)`의 `calculator_*.py` 예시를 ISO16358 / KS C 9306 / AHRI / EN14825 / AS/NZS compatibility 등을 포함하도록 넓혔다.
- `result_reports/active/024_refine-calculator-architecture-docs.md`를 생성했다.

## Non-goals
- code / tests / fixture / workbook / reference_files / UI / profile resolver / `core/calculator_profiles.py` 수정하지 않는다.
- `project_log.md`, `docs/REFACTOR_PLAN.md`는 수정하지 않는다 (이미 architecture reset 결정이 반영되어 있음).
- 새 calculator 모듈 생성 또는 기존 ISO 모듈 재작성은 이번 작업에서 수행하지 않는다.
- ML / UI / COLUMNS / calculator profile resolver contract 섹션은 건드리지 않는다.
- ISO 수식, 테스트, xfail 상세는 추가하지 않는다.

## Verification
- `git branch --show-current` → `main` 확인 후 작업을 시작했다.
- `result_reports/{active,archive,summaries}` 전체 report 번호 최대값(023)을 확인하고 다음 번호 024를 사용했다.
- commit 전 `git status` / `git diff --stat`로 `docs/WORK_PLAN.md`와 `docs/architecture/project_architecture.md`만 staged 대상으로 들어가고, `project_log.md` / `docs/REFACTOR_PLAN.md` / code / tests / fixture가 staged에 포함되지 않음을 확인했다.

## Task Results
### task 1 결과
- `docs/WORK_PLAN.md`의 `Current milestone focus`를 “Calculator architecture reset 실행 (ISO / KS / ASNZS 3-module boundary)”, “KS C 9306 CSPF/HSPF를 `core/calculator_ks_c9306.py`로 분리”, “`core/calculator_iso16358.py`를 ISO16358 CSPF/HSPF 전용으로 정리/재작성하기 위한 선행 작업”, 기존 production/Z-phase 정책 유지로 갱신했다.
- `Near-term execution order`는 이미 KS 분리 → ISO16358 정리/재작성 → profile/UI → ML, Z-phase ASNZS 순서로 정렬되어 있어 변경하지 않았다.

### task 2 결과
- `## 1. 파일 구조 (File Structure)`의 `core/calculator_*.py` bullet을 “규격별 효율 계산 엔진 (ISO16358, KS C 9306, AHRI, EN14825, AS/NZS compatibility 등)”으로 갱신했다.
- 하단 `Calculator module boundary (ISO / KS / ASNZS)` 섹션은 보고서 023에서 정리된 상태를 유지하고 변경하지 않았다.

### task 3 결과
- `result_reports/active/024_refine-calculator-architecture-docs.md`를 생성하고 두 단계 commit + push를 수행했다.

## Changed Files
- `docs/WORK_PLAN.md`
- `docs/architecture/project_architecture.md`
- `result_reports/active/024_refine-calculator-architecture-docs.md`

## Known Failures / Risks
- 이번 작업은 docs-only 정합성 보정이며 calculator code 동작은 변하지 않는다.
- 상단 파일 구조 요약과 하단 `Calculator module boundary` 섹션 사이의 표현은 일관되지만, KS / ASNZS 모듈이 실제 코드로 생성되기 전까지는 문서상 contract가 코드 상태보다 앞서 있다.

## Next Suggested Action
- `core/calculator_ks_c9306.py`를 생성하고 KS C 9306 CSPF/HSPF 로직을 `core/calculator_iso16358.py`에서 분리하는 구현 작업.

## Scope Compliance
- code: 수정하지 않았음
- tests: 수정하지 않았음
- fixtures: 수정하지 않았음
- workbook/reference_files: 수정하지 않았음
- UI: 수정하지 않았음
- profile resolver code: 수정하지 않았음 (`core/calculator_profiles.py` 포함)
- project_log: 수정하지 않았음
- REFACTOR_PLAN: 수정하지 않았음
- git pull/merge/rebase: 수행하지 않았음

## Commit / Push
- source/docs commit: `54d419a docs: refine calculator architecture docs`
- report commit: `report: record calculator architecture docs refinement`
- pushed branch: `origin/main`
