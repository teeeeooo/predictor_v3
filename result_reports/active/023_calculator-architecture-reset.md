# 023_calculator-architecture-reset

## Goal
- predictor_v3 계산기 아키텍처를 ISO 16358 / KS C 9306 / AS/NZS workbook oracle 3개 모듈로 분리하기로 결정하고, 그 boundary와 다음 구현 순서를 docs/architecture/refactor/work plan/project_log에 고정한다.

## Scope
- `docs/architecture/project_architecture.md`의 calculator profile resolver 섹션에 ISO / KS / ASNZS calculator module boundary를 추가했다.
- `docs/REFACTOR_PLAN.md`의 active refactor candidate 1번을 ISO/KS/ASNZS 3-module 분리 reset으로 갱신하고 next work order, reference branch 정책, KS C 9306 분리 트리거를 정리했다.
- `docs/WORK_PLAN.md`의 near-term execution order를 KS 분리 → ISO16358 정리/재작성 → profile/UI 연결 → ML 복귀, Z phase AS/NZS workbook oracle 순서로 갱신했다.
- `project_log.md`에 2026-05-17 calculator architecture reset 결정을 짧게 기록했다.
- `result_reports/active/023_calculator-architecture-reset.md`를 생성했다.

## Non-goals
- 계산기 code 수정 금지.
- tests / fixture / workbook reference_files 수정 금지.
- UI / profile resolver code / `core/calculator_profiles.py` 수정 금지.
- 새 calculator 모듈(`core/calculator_ks_c9306.py`, `core/calculator_asnzs_hspf_excel.py`)을 실제로 생성하거나 기존 ISO 모듈을 재작성하지 않는다.
- `work/iso-hspf-refactor-ui-followup` 브랜치 merge / cherry-pick / diff 가져오기 금지.

## Verification
- `git branch --show-current` → `main` 확인 후 작업을 시작했다.
- `result_reports/{active,archive,summaries}` 전체 report 번호의 최대값(022)을 확인하고 다음 번호 023을 사용했다.
- 문서 4종(`docs/architecture/project_architecture.md`, `docs/REFACTOR_PLAN.md`, `docs/WORK_PLAN.md`, `project_log.md`)만 수정되었고 code/tests/fixture는 staged 대상에 포함되지 않았음을 commit 전 `git status` / `git diff --stat`로 확인했다.

## Task Results
### task 1 결과
- `docs/architecture/project_architecture.md`의 calculator profile resolver 섹션에 “Calculator module boundary (ISO / KS / ASNZS)” 하위 섹션을 추가했다.
- `core/calculator_iso16358.py` (ISO 16358 + region config 전용), `core/calculator_ks_c9306.py` (KS C 9306 special calculator), `core/calculator_asnzs_hspf_excel.py` (AS/NZS workbook oracle compatibility, Z-phase 후보)의 책임 경계를 명시했다.
- profile resolver는 `calculator_id` 값(`iso16358`, `ks_c9306`, `asnzs_excel_hspf`)으로 세 모듈을 명시적으로 라우팅하고, region/standard metadata만으로 KS 또는 ASNZS compatibility를 자동 활성화하지 않는다는 contract를 추가했다.
- 문서 전체 재작성 또는 ML / UI / COLUMNS 섹션 변경은 수행하지 않았다.

### task 2 결과
- `docs/REFACTOR_PLAN.md`의 active refactor candidate 1번을 “Calculator architecture reset: ISO / KS / ASNZS 3-module 분리”로 갱신했다.
- next work order를 다음 순서로 정리했다.
  1. `core/calculator_ks_c9306.py` 생성 및 KS CSPF/HSPF 분리
  2. `core/calculator_iso16358.py`를 ISO16358 CSPF/HSPF 전용으로 정리/재작성
  3. AS/NZS workbook oracle은 `core/calculator_asnzs_hspf_excel.py` Z-phase compatibility calculator로 보류
  4. profile resolver / Calculator UI 연결은 calculator boundary 안정화 후 별도 작업
- `work/iso-hspf-refactor-ui-followup` 브랜치는 merge 대상이 아니라 reference/spike로만 둔다고 기록했다.
- KS C 9306 helper separation 항목의 분리 트리거를 “ISO 계열 boundary 정리 직후 첫 단계”로 갱신했다.
- `docs/WORK_PLAN.md`의 near-term execution order를 동일한 순서로 갱신하고, reference 브랜치 정책을 명시했다.
- 구현 세부 수식 / 테스트 expected / UI redesign 계획은 이번 문서에 포함하지 않았다.

### task 3 결과
- `project_log.md`에 `## 2026-05-17 — Calculator architecture reset: ISO / KS / ASNZS boundary` 로그를 append했다.
- ISO16358 / KS C 9306 / ASNZS workbook oracle calculator 분리 결정, region config는 ISO16358 계열에만 붙여 쓴다는 원칙, KS C 9306을 AHRI/EN14825처럼 special calculator로 분리한다는 결정, AS/NZS workbook oracle은 Z-phase로 보류한다는 결정, next work order, reference branch 정책을 짧게 기록했다.
- 사건 재구성, code diff 설명, 가짜 테스트 결과는 포함하지 않았다.

### task 4 결과
- `result_reports/active/023_calculator-architecture-reset.md`를 생성하고 두 단계 commit + push를 수행했다.

## Changed Files
- `docs/architecture/project_architecture.md`
- `docs/REFACTOR_PLAN.md`
- `docs/WORK_PLAN.md`
- `project_log.md`
- `result_reports/active/023_calculator-architecture-reset.md`

## Known Failures / Risks
- 이번 작업은 docs-only 결정 고정이며, KS / ISO / ASNZS calculator 모듈 분리 실제 구현은 다음 작업에서 수행한다.
- profile resolver와 UI가 새 `calculator_id` 값(`ks_c9306`, `asnzs_excel_hspf`)을 실제로 라우팅하도록 구현되기 전까지는 문서상 contract와 코드 상태가 일시적으로 불일치한다.
- `work/iso-hspf-refactor-ui-followup` 브랜치는 reference로만 두는 정책이므로, 추후 작업 시 실수로 merge / cherry-pick되지 않도록 주의가 필요하다.
- `core/calculator_iso16358.py`는 현재까지의 책임이 섞여 있는 상태로 남아 있으므로, 다음 step (KS 분리)이 완료되기 전에는 ISO16358 전용으로 간주하지 않는다.

## Next Suggested Action
- `core/calculator_ks_c9306.py` 생성 및 KS C 9306 CSPF/HSPF 로직을 `core/calculator_iso16358.py`에서 분리하는 구현 작업.

## Scope Compliance
- code: 수정하지 않았음
- tests: 수정하지 않았음
- fixtures: 수정하지 않았음
- workbook/reference_files: 수정하지 않았음
- UI: 수정하지 않았음
- profile resolver code: 수정하지 않았음 (`core/calculator_profiles.py` 포함)
- git pull/merge/rebase: 수행하지 않았음

## Commit / Push
- source/docs commit: `7e819f3 docs: define calculator architecture boundary`
- report commit: `report: record calculator architecture reset`
- pushed branch: `origin/main`
