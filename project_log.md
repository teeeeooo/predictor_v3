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

> **Ordering note:** `partNN` 순서는 original `project_log.md` entry order를 보존한다. `project_log.md`는 최신 항목이 위에 오는 reverse chronological order이므로, segment filename의 date range도 reverse chronological일 수 있다. 과거 로그를 찾을 때는 파일명만 보지 말고 `rg -n "^## 2026-" docs/archive/project_log/YYYY-MM/*.md`로 heading을 검색한다.

## 2026-07-17 — Train/Admin Unified Feature Manager phase insertion

### Decision

- Preserve completed Phases 1–3 and PR #16 history, but define the completed
  Phase 3 scope as the table-first Data Definition UX foundation.
- Make Phase 4 the proposed/current Unified Feature Manager workstream for
  complete Predict/ML Feature lifecycle and ordering, Derived/One-hot/Target
  authoring, transaction-safe multi-contract persistence, and live owner refresh.
- Move the unstarted Train/Model and Shell UX design to Phase 5; start it only
  after Phase 4 stabilization and a fresh dynamic Feature/Target contract audit.
- Keep Data Mapping as concrete value owner, Train as explicit training-execution
  owner, and Predict as saved-contract/compatible-model consumer. Exclude
  automatic retraining, automatic model activation, and Predict internal redesign
  from Phase 4.
- Keep current ML-projection-changing Save guards until Phase 4 approves and
  implements a persistence and compatibility migration/rollback boundary.
- Require one immutable persisted contract generation and coordinated consumer
  preflight/cutover; mixed-generation normal operation is forbidden and disk Save
  success remains distinct from runtime activation success.
- Bind every training run/result/artifact to its immutable start-generation
  Feature/Target/preprocessing snapshot. Definition Save does not retroactively
  alter an active run, and stale artifacts are not current-compatible by default.
- Preserve dirty Data Mapping drafts and expose pending requirement updates rather
  than silently reloading them. Separate static, mapping-backed, and external
  One-hot vocabulary owners.
- Keep initial Target CRUD limited to validated existing model-group association
  and target-level policies; new model groups and model-level training policy
  require a separately approved advanced contract.
- Separate run/generation-scoped candidate artifacts from the active model.
  Training completion cannot replace the active model; only validated explicit
  promotion by the artifact/model owner may do so, and failure preserves the
  previous compatible model.
- Limit atomic generation cutover to required owners inside one TrainShell
  process. Standalone Predict and other processes independently detect persisted-
  generation mismatch at startup/execution/reload boundaries and block new work
  when safe reload cannot succeed.

## 2026-07-16 — Train/Admin Phase 4 Train UX direction

### Decision

- Confirm Phase 3 is complete and merged through PR #16; remove the Phase 3 merge
  blocker from active planning.
- Make Phase 4 user-centered around `select training data → train → check
  progress → review results`.
- Run schema, feature, mapping, and compatibility checks automatically inside the
  workflow. Keep normal technical details out of the default surface; show an
  actionable user message first for errors and reserve details for Diagnostics or
  logs.
- Use the existing Train/ML safe defaults for ordinary training; optional or
  technical overrides remain behind Advanced settings and do not become required
  to start a supported default run.
- Separate authoritative training-start blockers from non-blocking warnings and
  post-training artifact/Predict blockers. Existing model, restart, mapping, and
  Predict readiness must not become Start prerequisites without an owner-contract
  basis.
- Center results on overall success, target-level R², optional MAE/RMSE, Optuna
  status and best trial/score when applicable, model-save status, elapsed time,
  and Predict availability.
- Treat the current-state audit and design finalization as the next Phase 4 work;
  preserve existing Data Definition, Data Mapping, Train, Predict, ML,
  persistence, and public-contract owners.

## 2026-07-16 — Train/Admin Data Definition UX Phase 3 closeout

### Decision

- Approve Phase 3 Slices 3A–3F and all audit corrections as one coherent Data
  Definition UX milestone; PR #16 was merged to `main`.
- Close the table-first Definition Inventory, controlled Add/Edit, guarded
  schema-only Save, impact/blocker workflow, saved-only Data Mapping handoff and
  coverage, keyboard/accessibility polish, and bounded native evidence while
  preserving their established owners.
- Keep `config/predict/schema.csv` as the canonical Data Definition write target
  and `config/ml/features.csv` as compatibility/parity-only. Projection-changing
  ML edits remain intentionally blocked without an approved projection writer.
- Accept visible-Cocoa/programmatic native evidence without claiming physical
  interaction; the known unsafe AppKit accessibility table-click path remains
  unused. Deferred Phase 2 native interaction remains separate.
- Keep production mapping completeness, training data, model quality, and
  production readiness company-local. No production config, mapping data,
  training data, protected fixture, or model artifact changed.
- Phase 3 closeout CI passed and the user merge completed; Phase 4 starts only
  from confirmed merged `main` on a separate branch and Draft PR after separate
  instruction.

## 2026-07-15 — Train/Admin Data Mapping UX Phase 2 closeout

### Decision

- Accept Phase 2 Slices 2A–2E and audit corrections at approved head
  `4fe580e1fa76a7af1f51c80e4cef163705ebe648`; PR #15 is the user merge target.
- Close code and repository automation with seven-group editing, spreadsheet
  CRUD/Undo, validation/dirty/Save/Reload, deterministic exchange export,
  exact-header canonical import, semantic row-order no-op, and best-effort
  rollback contracts intact.
- Treat incomplete Slice 2B+2C native interaction and Slice 2D+2E native visual
  evidence as deferred acceptance under the recorded AppKit and locked-desktop
  blockers. No new PNG or physical-interaction claim is made.
- Keep protected mapping data unchanged and do not infer real mapping
  completeness, model quality, or production readiness from fixtures/mock data.
- Mark PR #15 Ready for review after the closeout commit and CI succeed. The
  user performs merge; Phase 3 starts only from confirmed merged `main` on a
  separate branch and Draft PR after a current-state audit.

## 2026-07-14 — Train/Admin Mapping/Data Foundation Phase 1 closeout

### Decision

- Complete Slices 1A–1D and final corrections for repository-automated scope;
  final audit is approved and PR #14 was merged to `main`.
- Use the strict legacy bootstrap projection as a repository-only populated
  mapping fixture; never install it as production `data/mapping.json`.
- Keep Data Definition as dynamic mapping column/type/required owner and Data
  Mapping as value/persistence owner. Dynamic condenser payload attributes do
  not participate in conditional F&T/PFC identity.
- Apply that definition-backed payload contract to Refrigerant and Expansion
  without changing their key-based Predict options. Persist booleans as
  canonical JSON booleans, reject non-finite mapping numbers, and keep
  undeclared raw payload keys hidden from editor schema.
- Preserve undeclared runtime row payload from the current editor row backing
  data across unrelated Save/reload and key rename while overlaying only visible
  definition-backed values. Hidden payload is not review-exported and is
  removed with its row rather than recovered from historical source keys.
- Pair DEV selector metadata with unchanged ML numeric/one-hot training headers
  and fail fast when schema, mapping options/combinations, or resolved mock
  values diverge.
- Treat all fixture and mock success as structural workflow evidence only. Real
  mapping completeness, training data, model quality, and production readiness
  remain company-local validation work.
- Start Phase 2 only from merged `main` on a separate branch after separate
  instruction.

## 2026-07-13 — Active non-AHRI Calculator core refactor closeout

### Decision

- Preserve EN 14825, ISO 16358, and KS C 9306 public facade imports, methods,
  config attributes, routes, results, diagnostics, rounding, exceptions, and
  all official/golden expected values.
- Keep config, point resolution, performance curves, seasonal loops, and result
  assembly in standard-local private owners. ISO and KS CSPF/HSPF engines remain
  separate, and KS does not call the ISO public facade.
- Keep Brazil as capability-owned composite policy and AS/NZS as a disabled
  compatibility path. Resolve profile resources statically without repo-cwd
  dependence, scanning, or plugin discovery.
- Do not commonize cross-standard numeric helpers until formula, units,
  boundary, rounding, and exception semantics are all proven identical.

## 2026-07-12 — AHRI SEER2/HSPF2 core refactor closeout

### Decision

- Preserve `ahri_seer2.py` and `ahri_hspf2.py` as the stable public facades used by Calculator, capability, dispatcher, and ML envelope routes.
- Keep variable-capacity SEER2, variable-capacity HSPF2, and legacy HSPF2 v2 behind separate private owners; future two-stage/triple-capacity formulas must be sibling engines rather than branches added to the current formula bodies.
- Treat the existing user-confirmed expected results as official-calculator golden and the canonical deep-result fingerprints as structural characterization only. No formula, rounding, config, result/diagnostics schema, application scaling, or exception contract changed in this refactor.

## 2026-07-12 — Calculator table-family migration closeout

### Decision

- Completed the active Tk Calculator migration to three explicit table
  families: Editable Matrix, Compact Result Grid, and Scrollable Data Table.
- Shared visual policy and primitives now cover all active single, batch,
  compact-result, and detail tables while existing controllers, profile
  schemas, calculations, status meaning, lifecycle, and export contracts stay
  with their established owners.
- Small fixed results no longer use Treeview; the sole active Treeview remains
  the large `BinTraceTable` detail surface through the shared style adapter.
- EN14825 section hotspots remain unchanged ownership-wise; future new
  responsibilities require a split audit rather than reopening the table-family
  decision.
- Final correction keeps top/nested Notebook tab geometry fixed across
  selection, removes Python class-identity from AHRI/Korea visibility checks,
  and passes the full Tk Calculator suite without the prior order failure.
- Every active Single result surface now exposes Copy and Excel-friendly CSV
  actions while result owners retain their native payloads and detail/Batch
  export paths remain separate. SCOP composes export directly from active
  visible climate surfaces rather than its hidden compatibility text model.
- The user completed final GUI review and approved the feature branch for
  integration to `main`; the Calculator table architecture workstream is
  closed with no remaining merge blocker.

## 2026-07-11 — Clean/hexagonal desktop refactor

### Decision

- Preserve calculator and fixed-artifact ML numeric behavior while removing
  retired calculator code, stale legacy tests, dead Predict split-table UI, and
  the superseded Train Feature Catalog Manager UI.
- Keep `app_train.py` and `app_predict.py` separate and thin. Runtime-neutral
  ports, DTOs, and usecases are assembled in composition roots; PySide runners
  own toolkit/process lifecycle.
- Keep `config/ml/features.csv` and the core ML feature catalog as compatibility
  contracts without adding incomplete ML functionality. Arc 15 Data Definition
  remains the active Train/Admin schema surface.
- Use shared semantic visual tokens and screen-aware window policy, hidden-first
  calculator startup, multi-monitor-safe dialog placement, and two-axis batch
  table scrolling as the conservative desktop UX baseline.

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
- Stale generated reference-map/read-budget layers were retired; targeted
  owner/reuse search plus objective structure and staged gates remain.
- `ACTIVE_DOCUMENTS.md` is an owner-route map; child-document completeness
  belongs to local indexes and filesystem search.
- The active design root now contains only current/governing/future-unabsorbed
  decisions; 45 historical records are under an indexed legacy boundary.
- The audited harness branch was merged into `main` after pre-merge corrections.

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
