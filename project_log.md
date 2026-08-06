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
- `docs/archive/project_log/2026-07/project_log_2026-07_part04_2026-07-31_to_2026-07-31.md`
- `docs/archive/project_log/2026-08/project_log_2026-08_part01_2026-08-06_to_2026-08-02.md`

> **Ordering note:** `partNN` 순서는 original `project_log.md` entry order를 보존한다. `project_log.md`는 최신 항목이 위에 오는 reverse chronological order이므로, segment filename의 date range도 reverse chronological일 수 있다. 과거 로그를 찾을 때는 파일명만 보지 말고 `rg -n "^## 2026-" docs/archive/project_log/YYYY-MM/*.md`로 heading을 검색한다.

## 2026-08-06 — Native Windows acceptance defect follow-up sequencing

### Decision

- Native Windows 11 Enterprise source-runtime acceptance resumed after the
  independently audited Windows compatibility repairs through PR #56 and exposed
  two Predict Result Review defects plus Data Definition / Data Mapping onboarding
  gaps. Treat these as follow-up work, not as evidence that the closed Windows
  persistence/publication repairs regressed.
- Make **Predict Result Review bounded repair** the exact next source gate. Repair
  the narrow/pinned `Case + 상태` anchor versus right-side result-table header/first
  row alignment and the unavailable cooling/heating `ReviewSourceValue` tooltip
  path that assumes generic `reason_code/message` fields and raises
  `AttributeError`.
- After that repair receives its exact-head Gate, merge, and Close, resume native
  Windows acceptance. Preserve and inspect the previously affected runtime state
  first when available, then exercise clean-state Train, Predict, Experiment,
  Calculator, and Deployment Export; Train must complete real training through
  Candidate publication.
- Follow native acceptance with a bounded **Data Definition / Data Mapping
  onboarding workstream**: expose the current generation's actual Train-required
  `ml_name` headers as a user Training Header Template/reference workflow, and
  bootstrap missing `data/mapping.json` from the legacy wide mapping source only
  into a validated unsaved Data Mapping draft that is reviewed/exported/imported
  and explicitly Saved to create local runtime mapping. Keep
  `config/ml/features.csv` a compatibility projection rather than the canonical
  user owner; audit remaining static compatibility dependencies before source
  mutation.
- Keep the Standard Request Product/Owner Decision and Multi-point Predict →
  Calculate on hold until native Windows acceptance closes. Result Review XLSX
  implementation remains `DEFER`.

## 2026-08-05 — Engineering Workflow / repository authority boundary

### Decision

- Engineering Workflow owns generic role/lane authority, Build → Gate → Close,
  generic evidence reuse/re-proof, merge/synchronization/hygiene, and
  role-specific reporting when its role contract applies.
- `predictor_v3` separately owns project-specific hard boundaries, task routing,
  architecture/domain/UI contracts, conditional Result Record/Memory lifecycle,
  and repository-specific mechanical enforcement. Neither authority replaces the
  other's responsibility.
- `AGENT_TASK_ROUTER.md` remains task-to-owner navigation rather than a duplicate
  generic execution workflow. Repository Result Records remain conditional
  durable evidence and do not replace Engineering Workflow role reports.
- Durable source: `result_reports/records/2026-08/2026-08-05-active-documentation-contract-restoration-memory-correction.md`, which supersedes the original record's Memory Review disposition while preserving the original authority evidence.
  This entry records the process-rule decision only and does not assert PR merge,
  audit acceptance, synchronization, or Close.
