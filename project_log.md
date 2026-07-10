# Project Log

이 문서는 작업 과정의 시도, 실패, 성공, 중요 결정사항 및 반복 방지를 위한 기록용입니다.

## Project Log Policy

- `project_log.md`는 milestone급 decision, failure, lesson, process-rule change만 기록한다.
- task별 상세 결과, 검증 상세, 체크리스트, 파일 변경 목록은 result report에 기록한다.
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

> **Ordering note:** `partNN` 순서는 original `project_log.md` entry order를 보존한다. `project_log.md`는 최신 항목이 위에 오는 reverse chronological order이므로, segment filename의 date range도 reverse chronological일 수 있다. 과거 로그를 찾을 때는 파일명만 보지 말고 `rg -n "^## 2026-" docs/archive/project_log/YYYY-MM/*.md`로 heading을 검색한다.

## 2026-07-10 — Agent harness report and memory lifecycle redesign

### Decision

- Ordinary tracked-file changes no longer require result reports.
- Durable compact records are limited to contract/policy/migration/manual
  evidence and non-obvious regression triggers, and are committed with their
  source changes.
- New records use date-based final paths plus `REPORT_INDEX.md`; terminal
  output owns commit hash and push status.
- Memory Review Gate replaces active-count/summary/archive cleanup as the
  memory-update checkpoint.
- Existing archive and summary reports now reside under read-only
  `result_reports/legacy/` while historical bodies remain unchanged.

## 2026-07-06 — Pre-Arc 15 config/mapping source audit decision

### Decision
- Do not proceed directly from Arc 14D-R into Arc 15 real dataset readiness or a
  `Unified Data Definition Manager` direction.
- First run a Pre-Arc 15 audit of `config/ml/features.csv`,
  `config/predict/schema.csv`, the existing legacy mapping fixture
  `tests/fixtures/mapping/mapping_tables_legacy_wide.csv`, and Data Mapping
  Manager output relationships.
- The user clarified that the legacy mapping CSV was already in the repo, while
  real training CSV data is still outside the repo on the user's local PC.
- Do not decide whether the current ML feature contract and Predict schema CSV
  split is final design or duplication debt until that audit is complete.

## 2026-07-03 — Arc 14/15 numbering sync

### Decision
- Renumbered Data Mapping Manager / Mapping Update Execution as Arc 14 because
  `app_train.py` Data Mapping is still a placeholder; moved ML catalog-aligned
  real dataset readiness audit to Arc 15.

## 2026-07-03 — Arc 13.5A feature catalog correction closeout

### Decision
- Completed Arc 13.5A Feature Catalog Manager correction: dropdown UX bugfix,
  user-confirmed GUI smoke, narrowed ML model compatibility fingerprint, and
  active payload dedup are closed out.
- Active report lifecycle cleanup is complete in
  `result_reports/legacy/summaries/673_summary-arc13-5a-feature-catalog-manager-closeout.md`.
- No Arc 13.5A blocker remains; next action is Arc 14 Data Mapping Manager /
  Mapping Update Execution after the Arc 14/15 numbering sync.

## 2026-07-02 — Arc 13.5 feature catalog editor closeout

### Decision
- Completed Arc 13.5 Feature Catalog Editor Bridge for automated scope.
- `app_train.py` now exposes a top-level `Feature Catalog` Train/Admin tab with
  catalog/project consistency validation, read-only review, Excel-safe
  UTF-8-SIG export, whitelisted edit fields, validation-gated save, and
  canonical UTF-8 without BOM safe-write.
- Direct `config/ml/features.csv` editing is no longer the default user
  workflow; it remains an advanced/developer fallback for row add/delete or
  recovery work.
- Arc 14 real dataset readiness audit is the next recommended arc.
- Real desktop GUI manual smoke remains pending; automated Qt validation used
  offscreen mode.

## 2026-07-01 — Calculator Sub-Arc KOREA notebook entry closeout

### Decision
- Completed the bounded KOREA calculator notebook sub-arc before Arc 13.5.
- KOREA is now a top-level calculator tab with CSPF/HSPF single calculation,
  midpoint guide tables, batch table dialogs, and official-result detail views.
- KS C 9306 core formula/config/profile/public result contracts and golden
  expected values were preserved.
- Next near-term action returns to Arc 13.5 Slice 0 Feature Catalog Editor
  Design Gate.

## 2026-07-01 — Arc 13.5 feature catalog editor direction

### Decision
- After Arc 13 closeout, practical review found that opening `features.csv` in
  Excel can display Korean labels incorrectly because Excel may not
  automatically detect UTF-8 CSV encoding.
- The preferred user workflow is not direct CSV editing in Excel or Numbers.
  Arc 13.5 should design the feature catalog workflow around an
  `app_train.py` Feature Catalog viewer/editor surface.
- CSV export remains useful for storage, sharing, and Excel/Numbers review, and
  the implementation design should evaluate an export encoding policy such as
  UTF-8-SIG.
- Arc 14, the real catalog-aligned dataset readiness audit, is deferred until
  after Arc 13.5 viewer/editor/export/save work.
- The Calculator Sub-Arc - KOREA Notebook Entry is the next action before Arc
  13.5 starts.

## 2026-06-30 — Arc 13 feature catalog closeout

### Decision
- Arc 13 is complete for automated scope. `config/ml/features.csv` is the ML
  feature contract; `ml_name` is the raw training header and internal ML name.
- ML feature exports, predictor ML-visible columns, one-hot lists, training
  header runtime guard, inference zero-fill policy, and registry/catalog
  consistency guards now share the catalog contract.
- Arc 13 reports 624-632 are covered by
  `result_reports/legacy/summaries/633_summary-arc13-feature-catalog-closeout.md` and
  archived.
- Next recommended work is an ML catalog-aligned real dataset readiness audit.

## 2026-06-29 — Arc 12 calculator application boundary closeout

### Decision
- Arc 12 Calculator UI/Application Boundary Correction is complete for
  automated scope.
- ISO/ISEER, SASO T3, Hong Kong CSPF/HSPF, EN14825 SEER/SCOP, and AHRI
  SEER2/HSPF2 now route calculation orchestration through
  `apps.calculator.application` / `apps.calculator.adapters` boundaries or thin
  UI shims.
- Matching batch paths reuse application usecases/adapters where applicable,
  and guard tests now prevent completed UI/batch surfaces from importing the
  core dispatcher or mutating calculator config.
- No calculator formulas, config semantics, profile IDs, fixtures/golden
  expected, or public result dict contracts changed.
- Arc 13 ML Pipeline Stabilization is unblocked as the next recommended arc.
