# Project Log

이 문서는 작업 과정의 시도, 실패, 성공, 중요 결정사항 및 반복 방지를 위한 기록용입니다.

## Project Log Policy

- `project_log.md`는 milestone급 decision, failure, lesson, process-rule change만 기록한다.
- task별 상세 결과, 검증 상세, 체크리스트, 파일 변경 목록은 result report에 기록한다.
- granular memory candidate는 `Project Memory Delta`와 `result_reports/memory/project_memory_seed.md`에서 관리한다.
- report 본문이나 seed entry 전문을 `project_log.md`에 반복 복사하지 않는다.
- 기존 과거 로그는 보존하며, policy 추가 작업에서 기존 날짜별 항목을 재작성, 축약, 삭제하지 않는다.
- 새 로그를 추가하기 전 최근 2~3개 로그와 merge 가능한지 먼저 확인하고, 유사한 내용이면 중복 section을 만들지 않는다.
- 과거 로그는 `docs/archive/project_log/YYYY-MM/` capped segment archive 파일에서 heading 검색 후 필요한 범위만 확인한다.

## Historical Log Archives

- `docs/archive/project_log/2026-05/project_log_2026-05_part01_2026-05-18_to_2026-05-10.md`
- `docs/archive/project_log/2026-05/project_log_2026-05_part02_2026-05-04_to_2026-05-05.md`
- `docs/archive/project_log/2026-05/project_log_2026-05_part03_2026-05-06_to_2026-05-07.md`
- `docs/archive/project_log/2026-05/project_log_2026-05_part04_2026-05-11_to_2026-05-17.md`
- `docs/archive/project_log/2026-06/project_log_2026-06_part01_2026-06-10_to_2026-06-07.md`

> **Ordering note:** `partNN` 순서는 original `project_log.md` entry order를 보존한다. `project_log.md`는 최신 항목이 위에 오는 reverse chronological order이므로, segment filename의 date range도 reverse chronological일 수 있다. 과거 로그를 찾을 때는 파일명만 보지 말고 `rg -n "^## 2026-" docs/archive/project_log/YYYY-MM/*.md`로 heading을 검색한다.

## 2026-06-28 — Arc 9.5 second correction automated closeout

### Decision

- Arc 9.5 second correction implementation is complete for focused automated
  coverage after the manual-smoke rejection.
- The corrected scope covers the source-confirmed failure classes: table-linked
  group header geometry, editable dropdown/autocomplete commit path, mapping
  option adapter boundary, Train embedded Predict header ownership, Trainer
  `QTableView + QAbstractTableModel` compliance, workspace row command
  controller boundary, and reset undo clearing.
- Arc 10 Prediction Worker / Progress remains on hold until the user manually
  accepts the corrected Arc 9.5 surface.

### Reference

- `result_reports/active/581_arc95-second-correction-closeout.md`

## 2026-06-28 — Arc 9.5 final closeout superseded by manual smoke

### Decision

- The previous Arc 9.5 final closeout is not accepted for project-state
  purposes because user manual smoke found source-confirmed baseline failures.
- Arc 9.5 remains active for second correction; Arc 10 Prediction Worker /
  Progress is on hold until the correction slices pass.
- The correction scope is limited to the manual-smoke audit findings: unified
  table group header geometry, editable dropdown/autocomplete behavior,
  mapping option boundary, Train/Predict embedded header ownership, Trainer
  table MVC compliance, workspace command/state boundary cleanup, and focused
  regression coverage.

### Reference

- `result_reports/active/574_arc95-full-audit-after-manual-smoke.md`

## 2026-06-28 — Arc 9.5 unified case table parity closeout

### Decision

- Arc 9.5 Reopen is accepted for current scope with a B-option unified Predict
  case table: one visible row per prediction case, grouped input/auto/result/
  status columns, hidden `case_id`, and selectable/copyable read-only
  result/status cells.
- Spreadsheet UX baseline items from the reopen review are no longer deferred:
  rectangular selection, TSV copy/paste, selected-range fill, clear,
  grouped undo, Tab/Enter navigation, click/type replace-on-type, and
  read-only mutation prevention are covered by focused tests.
- Mapping-backed per-row dropdown option updates are complete without changing
  the mapping JSON schema.
- Trainer visual hierarchy is corrected while Trainer execution remains
  intentionally deferred to Arc 11.
- Arc 10 Prediction Worker / Progress is the next active arc; real-model
  prediction success smoke still requires a valid `model/model.pkl` artifact.

### Reference

- `result_reports/active/573_arc95-final-acceptance-closeout.md`

## 2026-06-21 — EN14825/AHRI detail and profile lifecycle closeout

### Decision

- EN14825 SCOP/SEER and AHRI HSPF2/SEER2 bin-detail surfaces are complete on the
  shared schema-driven detail panel.
- ISO, EN14825, and AHRI profile tabs now delegate visible-content lifecycle
  assembly to `ProfileVisibleContentLifecycleController`; a structure gate
  prevents direct primitive assembly in production profile tabs.
- Detail/profile/nested refits use named controller triggers with injected
  profile predicates and settle policy rather than local geometry patches.
- The completed reports are covered by summary 461; the next action is product
  performance sample removal under the empty-state policy.

### Reference

- `result_reports/summaries/461_summary-en14825-ahri-detail-lifecycle-closeout.md`

## 2026-06-21 — AHRI calculator UI/batch lifecycle closeout

### Decision

- AHRI 210/240 SEER2/HSPF2 main UI and two-row batch workflows are complete;
  user visual smoke confirms the final HSPF2 batch readability/sizing state.
- HSPF2 A2 is capacity-only at the UI boundary, optional heating points retain
  draft/active/superset snapshot behavior, and batch output is HSPF2-only.
- Shared BatchMatrix leading-column tokens and natural-content dialog fitting
  are the durable sizing policy; fixed geometry and profile min-size inflation
  are not the correction mechanism.
- Calculator launch policy keeps standard/option defaults but removes product
  performance demo values only after the required diagnostic surface exists.
- EN14825 SEER/SCOP and AHRI SEER2/HSPF2 detail-view design/implementation must
  precede their sample-removal slices; Hong Kong detail ownership is reference
  evidence rather than a schema to copy.
- The next action is EN14825/AHRI detail view design.

### Reference

- `result_reports/summaries/445_summary-ahri-calculator-ui-batch-lifecycle-closeout.md`

## 2026-06-20 — Project brief arc/milestone ownership correction

### Decision

- `project_brief.md` owns the Phase / Arc / Milestone map, not task-specific
  handoff pointers.
- `docs/WORK_PLAN.md` owns the current slice, next action, and explicit
  `Session Handoff` pointers.
- The duplicated next-session read list and Next Action were removed from the
  brief; this corrects the earlier broad handoff ownership split.

### Lesson

- Arc and milestone must remain larger than implementation slices; otherwise
  the brief becomes a second work plan.

## 2026-06-20 — Current execution board and session handoff ownership

### Decision

- `docs/WORK_PLAN.md` is the current execution board; completed history belongs
  in result summaries/archive and `project_log.md`.
- `project_brief.md` owns the stable current-state session handoff, while
  `ACTIVE_DOCUMENTS.md` remains the active document owner map.
- Only an explicit user handoff request updates `project_brief.md` for handoff
  and creates or fully replaces `WORK_PLAN.md`'s `Session Handoff`. Ordinary
  work plan maintenance does not update that section.

### Lesson

- Keep stable state, active execution, temporary handoff pointers, and history
  in separate owner documents; do not rebuild a report index inside the work
  plan.

## 2026-06-18 — EN14825 unified config and SCOP point contract milestone

### Decision
- `data/region_configs/en14825.json` is the single active EN14825 config owner
  with namespaced `seer` and `scop` sections; legacy config/fallback ownership
  was removed and the calculator constructor uses `config_path`.
- EN14825 SEER calculation and UI defaults read through config/adapter ownership
  rather than core module constants.
- `scop.point_contract` owns required, mapped, inactive, and threshold-only
  logical point behavior. Core resolution is propagated through adapter/table
  model/UI boundaries so unavailable SCOP inputs are not independent inputs.
- Existing golden expectations remain unchanged. EN14825 SCOP point-availability
  manual smoke is user-confirmed complete, so batch integration preflight is now
  unblocked.

### Reference
- `result_reports/summaries/404_summary-en14825-config-point-contract-ui-workflow-closeout.md`

## 2026-06-07 — Reference parity / standardization gate added

### Decision
- A new reference parity / standardization gate is added to common process
  documents to prevent repeated rediscovery of already-solved behavior bugs,
  lifecycle handling, and interaction patterns.
- When creating a new UI surface, script, helper, adapter, workflow path, or
  reusable component, the implementer must first check whether an existing stable
  implementation or workflow already covers the same concerns.
- Reuse is not forced; the implementer records why an existing reference was
  or was not reused, and leaves parity evidence in the result report.
- Affected documents: `AGENTS.md`, `AGENT_TASK_ROUTER.md`,
  `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`,
  `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`,
  `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`.
- Trigger: 242 Hong Kong CSPF matrix migration reproduced paste tiling, repeated
  undo, and restore flicker issues that had already been solved in the existing
  row-per-case `BatchCaseTable` surface.

## 2026-06-07 — Hong Kong CSPF matrix migration adapter pattern

### Decision
- Profile-specific batch matrix migration uses a thin adapter (`HongKongCspfMatrixController`) that bridges `BatchMatrixTable` with the existing row-per-case handler.
- No profile-specific knowledge enters `BatchMatrixTable` or `TkTableController`.
- Row-per-case code (`BatchCaseTable`, `BatchCalculationController`, `HONG_KONG_CSPF_BATCH_SPEC`) is preserved as importable fallback, not deleted.
- Snapshot compatibility uses dual-format acceptance (tuple/list) in `restore_snapshot()`.

## 2026-06-06 — Project-wide Clean Architecture boundary policy

### Decision
- The repeated Tkinter window-sizing issue is a project-wide responsibility
  boundary lesson, not only a UI geometry issue.
- Model / Controller(or Service) / Shell(or Adapter) / View / Policy boundaries
  are now owned by `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`.
- 230B refined the owner wording so concrete project/interface names are treated
  as examples/evidence, not scope boundaries.
- 230C applies the same audit lens to portable UI/UX docs before rewriting
  them, with adapter documents kept toolkit-specific by design.
- 230D applies the first UI/UX neutralization slice and adds a folder README so
  portable principles, adapters, and historical sources are easier to tell apart.
- 231 summarizes and archives the completed architecture/UI-UX boundary and
  window-refit arc, leaving 229 active as direct evidence for the next visible
  content measurement adapter extraction.
- 233A finds that measurement-owner extraction alone is not enough; profile
  switch needs a mapped-surface lifecycle that measures preferred size and
  overflow from one settled snapshot.
- 233B Windows smoke confirms the Hong Kong lower blank space is resolved and
  the refit loop remains gone; flicker is still visible enough that the next
  window task is lifecycle orchestration unification, not more blank-space
  debugging.
- Batch dialog sizing belongs under the window shell lifecycle arc, while batch
  copy/export belongs under the table/export arc. Batch export should reuse the
  existing clipboard/CSV helper direction; xlsx export stays deferred.
- Future batch layout should first evaluate a unified case-level two-row matrix
  shape instead of maintaining flat row-per-case and matrix layouts in parallel.
  Status is not a default output column; result columns are profile metrics
  such as Hong Kong CSPF/CSEC, with blank/error state handled outside the core
  output columns.
- 237 accepts the two-row matrix direction with constraints: model logical
  cases separately from physical rows, expose per-cell role/applicability for
  controller semantics, keep result columns metric-only, and implement
  model/spec mapping before Tk UI migration.
- 238 implements the headless matrix mapping foundation with no merged or
  fake-merged cells: Case/result values appear only on the first physical row,
  second-row positions are real blank read-only cells, and mutation targets are
  editable input cells only.
- 239 extends the common Tk table controller with optional per-cell
  `cell_role(position)` resolution while preserving the existing
  `cell_roles()[column]` fallback, so future matrix surfaces can guard
  paste/clear/copy by physical cell without forking the controller.
- HSPF/EN/AHRI/KS expansion should wait until result/detail/export contracts,
  two-row batch foundation, main table migration candidates, and ui_tk cleanup
  direction are checked.
- 233C/233C-2 reduced visible mutation by unifying lifecycle refit requests and
  reusing the valid Hong Kong metric surface. The remaining soft flicker is
  accepted for this arc because further reduction would require hidden-first
  first-show or stable-container lifecycle work beyond a micro-slice.
- Future window/dialog/profile/page surfaces should apply hidden-first
  first-show or stable-container lifecycle rules from
  `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`; the task router now
  points UI window/dialog/profile/page work at that policy.
- UI, calculator, ML/Predictor, and packaging workflow details were moved out
  of `AGENT_TASK_ROUTER.md` into `docs/agent_workflows/*`, bringing the router
  down to a compact route/gate map while preserving owner-specific detail.
- 233E fixed batch dialog close/reopen state loss by keeping session-local
  input snapshots outside the dialog shell. Stateful input dialog lifecycle is
  now documented in `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
  and the UI workflow gate: close is not reset, and reset/clear must be an
  explicit user action.
- 233F added batch viewport containment. 235 fixed the mouse-wheel parity gap by
  reusing the main scroll source-of-truth pattern, and Windows smoke accepted
  batch dialog wheel scrolling over canvas, cell/frame, entry, label, header,
  and row-header targets as OK.
- 236 summarizes and archives the completed 229/232/233/234/235
  window/dialog/table/batch viewport arc; the active report folder is cleared
  for the next batch two-row matrix layout preflight.
- UI soft LOC limits are now treated as preflight triggers, not hard failures:
  helper/adapter extraction follows owner-boundary and reuse/parity judgment,
  not line-count compliance alone.

### Lesson
- Repeated smoke failures of the same class are a signal to stop adding local
  patches and decide the owner boundary first.
- Passing one geometry bug does not close the shell arc if lifecycle flicker or
  batch dialog sizing still share the same root owner.
- Hidden-first preparation before first show is different from repeatedly
  hiding and showing an already-visible shell; new surfaces should be designed
  with the former instead of patched with the latter.
- Stateful input shell lifecycle and user input state lifecycle must be
  separated; destroying a widget shell must not silently discard structured
  user input.
- A new UI helper that looks structurally similar is not sufficient; it must
  match existing user-visible behavior such as wheel routing, selection,
  paste/copy, export, and viewport containment when a working surface already
  exists.
- When a route keeps accumulating detailed checklist text, move the workflow to
  an owner document and leave only the owner-routing gate in the router.

---

## 2026-06-21 — Profile visible-content lifecycle controller boundary

### Decision
- Repeated calculator profile measurement/scheduler/shell assembly will move to
  `apps/calculator/ui/lifecycle/ProfileVisibleContentLifecycleController`.
- Profile tabs remain widget-composition views and provide nested notebooks,
  active predicates, and evidence-based settle-cycle configuration.
- Migration order is EN14825, AHRI210240, ISO16358; a structure hard gate is
  enabled only after all production tabs migrate.
- Existing measurement, refit scheduler, content-hugging shell, and geometry
  primitive owners remain unchanged and are composed rather than merged.

---

## 2026-06-05 — Content-hugging shell/form contract direction

### Decision
- Content-hugging sizing should be handled as a toolkit-neutral shell/form
  contract, not as per-screen local sizing patches.
- SPOT is evidence that build, measure requested content, clamp, center, and
  apply geometry once is feasible; it is not a source of truth or dependency.

### Lesson
- Refit scheduling alone cannot guarantee content-hugging UX when shell/form
  ownership is missing.

---

## 2026-06-05 — Content-hugging window sizing direction

### Decision
- More settle-cycle patches are not the right long-term fix for Hong Kong
  lower blank space and profile-switch flicker.
- The next slice should measure the final visible content state and apply
  window geometry once, while keeping hidden content out of height decisions.

### Lesson
- Repeated post-render fitting can stabilize stale requested sizes, but it also
  makes flicker visible and does not guarantee content-hugging height.

---

## 2026-06-05 — Common dynamic refit owner decision

### Decision
- Dynamic content refit scheduling should move out of individual tabs into a
  common owner before nested tab-change refit is reintroduced.
- `ui_tk/window_geometry.py` should remain the geometry calculation/application
  helper; the new owner should coordinate triggers, suppress guards, and
  reentrant scheduling.

### Lesson
- Local tab-level scheduling mixed measurement, trigger binding, and mutation
  closely enough to create a Windows resize loop.

---

## 2026-06-05 — Nested notebook window refit policy

### Tried
- 220 Windows smoke checked the common-foundation batch table and main
  calculator sizing.

### Result
- Selected-range fill paste was resolved, but the Hong Kong metric notebook
  still left lower blank space until a detail toggle forced a later refit.

### Decision
- Nested notebook / dynamic sub-tab refit rules belong in
  `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`.
- Hong Kong implementation correction is split into a follow-up instead of
  mixing policy and code.

### Lesson
- Single-section fit rules are not enough for nested notebook surfaces.
- A detail-toggle recovery is a signal that layout settling needs a scheduled
  refit after the visible sub-tab stabilizes.

---

## 2026-06-05 — Table UX target and common Tk foundation direction

### Decision
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` remains the source of
  truth for table interaction UX across toolkits.
- SPOT is concrete example/evidence for the desired table feel, not a source
  of truth, dependency, vendor target, or copy target.
- `predictor_v3` should build its own common Tk table foundation before adding
  more independent Tk table controllers.

### Lesson
- A written table contract alone did not prevent paste, undo, focus, and
  navigation drift in a new controller.
- Desired interaction examples plus a shared foundation are needed so new
  table-shaped UI does not rely on Windows smoke to discover core gaps.

---

## 2026-06-05 — Agent workflow owner split

### Tried
- Audited `AGENTS.md`, `AGENT_TASK_ROUTER.md`, and `ACTIVE_DOCUMENTS.md`
  after repeated read-budget drift and table-rule harness corrections.

### Result
- Split detailed agent workflows out of `AGENT_TASK_ROUTER.md` into
  `docs/agent_workflows/` owner docs for result reports, diff/read budget,
  project log and memory, smoke-loop mode, and documentation lifecycle.
- Kept `AGENT_TASK_ROUTER.md` as a routing gate map instead of a long workflow
  manual.

### Decision
- `AGENTS.md` remains the lite entrypoint.
- `AGENT_TASK_ROUTER.md` should route to owner docs and keep only short gates.

### Lesson
- Adding more rules to the router made "read only needed ranges" harder to
  follow. Long procedure bodies need separate owners so the router can stay
  operationally cheap to inspect.

---

## 2026-06-04 — Scoped first-search harness rule

### Tried
- Reviewed recent task overhead from broad initial searches across tests and legacy files.

### Result
- Added an AGENTS.md rule to keep first searches within specified/allowed files when the task scope is file-bounded.

### Decision
- Expand to legacy/archive/tests-wide searches only when the initial bounded search hits a blocker.

## 2026-06-04 — WPF spike closeout and UI contract guardrail

### Tried
- A `spike/wpf-calculator-shell` branch tested a C# WPF calculator shell,
  reusable grid, and local Python worker bridge.

### Result
- WPF showed some table UX potential, but it added .NET runtime/SDK,
  GUI exe + worker exe, region config packaging, and worker resolver concerns.

### Failed / Risk
- The spike drifted toward component-demo UI instead of preserving the
  existing calculator_tk section order and immediate-calculation flow.

### Decision
- Do not merge C# WPF code to `main`. Return to `calculator_tk` and strengthen
  UI/UX contract guardrails before the next batch/detail-schema work.

### Lesson
- The root issue was not language choice alone; the UX contract must be
  enforced against the default user-facing screen, not only against reusable
  component behavior.

---

## 2026-05-24 — Tkinter calculator matrix UI direction + project-wide surface rules

### Decision
- PyQt calculator-only source retirement는 계속 hold한다. direct calculator tests는 retire했지만 shared PyQt utility와 guarded widget support는 별도 판단 전까지 retained/hold 자산이다 (154~156).
- Tkinter calculator final UX는 table/grid + auto-calc이며, Hong Kong CSPF/HSPF는 matrix input과 summary result surface까지 도달했다. core/profile/dispatcher 경로와 기본 smoke 값은 유지한다 (157, 161~163).
- `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md`와 `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`는 Calculator, Predict/Train, 후속 ML/inverse-search UI의 project-wide visual/surface-shaping SSOT다 (158~160, 164).
- 163 visible surface는 추가 refinement가 필요하다는 사용자 확인에 따라, lifecycle 이후에는 manual smoke보다 Tkinter matrix/result visual surface refinement implementation을 먼저 수행한다. Graph/detail과 큰 graph dependency는 별도 후속 단계로 유지한다.

### Lesson
- Table behavior contract만으로 반복 데이터의 화면 shape를 결정할 수 없다. 반복 입력은 matrix rule이, primary result는 summary surface rule이 필요하며 visible UX 검증은 구조 구현 이후 별도로 이어져야 한다.

---

## 2026-05-23 — Project Memory Delta workflow + seed staging

### Decision
- Result report는 backend-neutral `Project Memory Delta`로 장기 기억 후보를
  남길 수 있으며, 새 `keywords`는 YAML list로 작성한다. 기존 report 원문은
  이 형식 도입을 이유로 retroactive 수정하지 않는다.
- `result_reports/memory/project_memory_seed.md`는 summary 기반 기억 후보를
  source 추적 가능하게 유지하는 repo-local staging 문서로 두며, 특정 memory
  backend 전용 저장소나 기존 report 원문 대체물로 사용하지 않는다.
- agent workflow token leakage를 줄이기 위해 `wc -l`/`du -sh` pre-check, `rg`
  heading navigation, Quick Route Index, group summary `modified:` 규칙을
  `AGENT_TASK_ROUTER.md`에 추가했다.
- `project_log.md`를 active milestone log + `docs/archive/project_log/YYYY-MM/`
  capped segment archive로 분리하고, exact move 원칙으로 보존했다.
- `docs/archive/AGENTS_FULL.md`를 active workflow 문서에서 완전히 제거하고,
  상세 배경 확인은 active owner docs와 `ACTIVE_DOCUMENTS.md`로 유도했다.

### Lesson
- 세부 report delta를 `project_log.md`에 반복 복사하지 않고, milestone급
  process-rule 변화만 log에 남기며 summary-level seed entry로 장기 기억을
  연결한다.

---

## 2026-05-19 — ISO16358-2 HSPF -7_ext fix + golden update

### Tried
- 099에서 `_iso_hspf_extended_minus7_default()`의 -7_ext default factor 적용
  대상을 정정 (2°C frost → 2°C non-frost ×1.12/×1.06 → -7°C ×0.734/×0.877
  2-step).
- 100에서 ISO16358-2 HSPF official exact 16-case fixture expected를 원문
  audit + 099 기준값으로 갱신하고 `XFAIL_CASE_IDS`를 빈 frozenset으로 정리.

### Result
- case 3/4/9/10/11이 099 fix만으로 자연 pass.
- case 8/12/13/14/15/16의 expected를 원문 audit 기준값으로 갱신해 16/16 case
  모두 pass.
- frost trace / boundary COP / extended default focused test 그대로 pass.
- full suite: 425 passed, 4 skipped, 23 xfailed (XPASS strict 실패 0).

### Failed-Risk
- 091 시점에서는 case 12/15/16 large Δ를 external reference script의 frost/
  non-frost 동일 주입 해석 오류로 추정했으나, 원문 audit 결과 repo 구현이
  frost endpoint 정책 / -7 multi-measured / Formula 50 적용 / saturated 모두
  원문 준수임이 확인됐고, 실제 원인은 -7_ext default factor 적용 대상 오류
  (099) 였음.

### Decision
- ISO16358-2 HSPF 16-case mismatch hold 상태는 종료.
- official exact fixture expected는 원문 audit + 099 fix 기준값을 single
  source of truth로 둔다.
- 잔여 follow-up은 ISO table UI / TSV / unit adapter / ML 복귀 순으로 진행.

### Lesson
- factor 자체의 출처가 맞아도 적용 대상 (frost vs non-frost) 이 어긋나면
  대표적인 case에서 큰 mismatch가 발생한다. 0.734/0.877 같은 derived factor를
  볼 때는 derivation 시점의 baseline (여기서는 2°C non-frost) 을 항상 함께
  점검한다.

---

## 2026-06-07 — Side-effect-free visible content measurement policy repair

### Tried
- 256 이후 Windows smoke에서 확인된 Hong Kong profile flicker/refit loop 문제를
  shared measurement policy 문제로 다룸.
- `TkVisibleContentMeasurement._measure_nested_notebook()`이 hidden tab을
  `notebook.select(tab_id)`로 측정하여 `<<NotebookTabChanged>>` event를 발생시키고,
  이것이 refit을 다시 요청하는 measurement → select → event → refit loop를 유발함.
- 측정을 side-effect-free로 전환: current selected tab만 측정하고 hidden tab을
  select하지 않음.
- width 안정성을 위해 instance-level `_observed_max_tab_width` cache를 추가.
- batch dialog의 hidden-first lifecycle과 main visible refit lifecycle은 서로 다른
  표준임을 문서화.

### Result
- `_measure_nested_notebook()`에서 programmatic tab selection 완전 제거.
- current tab height만 사용, observed width cache는 current visible tab에서만 갱신.
- flicker loop 제거.
- 기존 ISO/ISEER/SASO/CSPF/HSPF regression은 변화 없음.
- core calculator, golden, fixture, batch matrix, detail panel schema 변경 없음.

### Decision
- visible main content measurement는 반드시 side-effect-free여야 한다.
- hidden tab size를 알기 위해 programmatic tab select를 사용하는 것은 금지한다.
- width 안정성은 observed cache로 달성한다.
- batch dialog의 hidden-first lifecycle과 main visible refit lifecycle은 별도 표준이다.

### Lesson
- measurement가 visible UI state를 바꾸면 event loop가 생긴다.
- side-effect-free measurement는 visible main refit의 필수 precondition이다.
- batch의 안정성 원인(hidden-first build)을 main에 무리하게 적용하지 말고,
  각 lifecycle에 맞는 표준을 분리해 적용해야 한다.

---

## 2026-06-07 — Main paste policy alignment to raw text paste + visible validation

### Tried
- `ExcelLikeTableController._paste()`의 atomic numeric pre-validation reject를 제거.
- `MetricInputTable.get_numeric_values()`가 invalid fields를 자동으로 visible
  marking하고 `ValueError`를 raise하도록 수정.
- `ExcelLikeTableController._paint_selection()`이 invalid field background를
  표시하도록 수정.

### Result
- main paste는 이제 invalid value를 cell에 raw text로 적용한다.
- invalid field는 빨간색 배경으로 표시된다.
- `get_numeric_values()` 호출 시 invalid fields가 표시되고 계산은 실행되지 않는다.
- undo는 paste 전체를 한 번에 되돌린다.
- batch/common paste behavior는 변경되지 않았다.
- controller switch는 아직 수행되지 않았다.

### Decision
- calculator main table paste policy는 common UX contract 방향으로 정렬된다.
- paste layer는 value validation을 이유로 reject하지 않는다.
- validation은 paste 이후 field-level에서 수행되고 visible marking으로 표시된다.
- execution은 invalid state에서 block된다.
- `get_numeric_values()`는 validation + execution blocking의 owner이다.

### Lesson
- atomic paste rejection은 사용자가 무엇이 잘못됐는지 알 수 없는 silent failure를
  만들 수 있다.
- paste → validate → execute 3-layer 분리가 사용자 의도와 일치한다.

---

## 2026-06-07 — Code checker reference map foundation design

### Tried
- predictor_v3에 lightweight code checker / repo reference map을 도입하는 설계.
- existing `tools/check_code_structure.py`와의 관계 정리.
- tracked compact map vs ignored detailed cache 경계 확정.
- MVP scope와 workflow hook policy 정의.

### Result
- `tools/code_checker/`가 권장 소유자 폴더.
- compact map은 `docs/code_map/CODEBASE_REFERENCE_MAP.md`로 tracked.
- detailed cache는 `.code_checker/`로 ignored.
- MVP는 Python symbol inventory, LOC/class/function count, import edges,
  duplicate candidates, soft-limit hotspots, Markdown rendering.

### Decision
- map은 evidence이며 source of truth가 아니다. AGENTS.md와 architecture docs가
  canonical rule을 유지한다.
- `check_code_structure.py`(structural guard)와 `code_checker/`(semantic map
  generator)는 complementary 관계다.
- 다음 slice는 MVP implementation: `tools/code_checker/build_reference_map.py` +
  `docs/code_map/CODEBASE_REFERENCE_MAP.md` 초기 생성.

### Lesson
- 반복되는 reference parity audit와 helper 재발견 문제는 static analysis 기반
  map으로 부분적으로 해결 가능하다.
- map staleness는 workflow hook policy와 explicit update header로 완화한다.

---

## 2026-06-07 — Reference Evidence Gate workflow integration

### Tried
- code_checker reference map을 agent workflow에 연결하는 integration slice.
- DIFF_READ_BUDGET.md에 Reference Evidence Gate 섹션 추가.
- AGENT_TASK_ROUTER.md의 관련 route에 최소 cross-reference 추가.

### Decision
- code_checker는 기본값 OFF이며, 구조 영향 작업에서만 조건부 ON이다.
- map 사용 시 broad read 금지, `rg`/small `sed` range로 제한적 읽기.
- map 재생성은 structural code change 후에만, commit은 significant
  architecture/surface change 후에만.
- DIFF_READ_BUDGET.md가 Reference Evidence Gate의 owner 문서다.
- AGENT_TASK_ROUTER.md의 Shared Guardrails와 Coding/UI route에서 cross-reference.

### Lesson
- token/read budget 문서가 code checker trigger policy의 자연스러운 owner다.
- router에 긴 trigger 목록을 복붙하지 않고 workflow owner 문서를 참조하는 것이
  유지보수에 유리하다.

---

## 2026-06-07 — Code quality guardrail backlog milestone registration

### Tried
- 270~274 흐름에서 확인된 code_checker/문서 하네스로 방어 가능한 영역과
  아직 미비한 guardrail 후보를 정리.
- 미비 항목을 REFACTOR_PLAN.md backlog로 등록하고 WORK_PLAN.md에
  잊지 않기 위한 reminder/checkpoint를 추가.

### Decision
- REFACTOR_PLAN.md가 상세 guardrail backlog를 소유한다.
- WORK_PLAN.md가 실행 보드로서 짧은 checkpoint를 유지한다.
- guardrail은 incremental, warning-first로 도입하며 당장 hard gate로 만들지 않는다.
- owner: semantic check는 `tools/code_checker/`, structural check는
  `tools/check_code_structure.py`.
- revisit 시점: ui_tk cleanup과 controller switch 완료 후.

---

## 2026-06-09 — Preserve external focus during ResultPanel shape-change rebuild

### Tried
- ResultPanel.set_summaries() shape-change path에 external focus capture/restore helper 추가.
- _capture_external_focus(), _is_descendant_of_panel(), _restore_focus_if_alive().
- same-shape stable update path는 변경 없음.
- focus preservation focused test 4개 추가.

### Result
- 13 stable update tests passed, 10 diagnostic tests passed, 15 parity tests passed, 5 pilot tests passed.
- py_compile OK, check_code_structure no new violations.
- headless macOS: focus 테스트는 deiconify+focus_force 필요; focus unavailable 환경에서는 skip 처리.

### Decision
- ResultPanel shape-change rebuild 시 external focus 보존하도록 구현 완료.
- 다음 gate: Windows manual smoke로 invalid text undo 개선 여부 확인.
- Windows smoke 후 undo 문제가 지속되면 next slice는 TkTableController edit-session undo policy fix.
- controller switch expansion은 Windows smoke 통과 전까지 계속 보류.

---

## 2026-06-10 — Reference Evidence Gate warning-first workflow patch & wording policy

### Tried
- Reference Evidence Gate를 warning-first 워크플로우로 보정하여 코드 수정 전 preflight 자문 checklist(책임/surface 추가, 중복, 우회, 핫스팟 확장 여부) 도입.
- 영구 문서(durable docs)에는 exact active report count를 기재하지 않고 threshold wording만 표기하도록 RESULT_REPORT_WORKFLOW.md 정책 갱신.
- `docs/WORK_PLAN.md`, `project_log.md`, `308_post_saso_t3_controller_switch_validation_gui_smoke_closeout.md` 등 기존 문서의 exact count 기록을 threshold wording으로 수정.

### Result
- `docs/agent_workflows/DIFF_READ_BUDGET.md` 및 `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md` 수정 완료.
- `AGENT_TASK_ROUTER.md` 라우팅 문구 최소 보정 완료.
- `docs/WORK_PLAN.md` 갱신 완료.
- `project_log.md` 내 exact count 기록 제거 및 threshold wording으로의 보정 완료.
- `result_reports/active/308_post_saso_t3_controller_switch_validation_gui_smoke_closeout.md` 보정 완료.

### Decision
- code_checker 및 codebase reference map은 semantic linter가 아닌 구조/참조 evidence로만 사용하며, exact count는 final agent output에만 보고하여 불일치 방지.
- 다음 action: code_checker metadata & freshness check improvement.
- active report count exceeds lifecycle threshold; cleanup pending.

---

## 2026-06-10 — Batch dialog shell/profile architecture decision

### Decision
- ISO 2-point 및 SASO T3 batch dialog 확장 전 `ui_tk` batch dialog 폴더 boundary를 audit한 결과, flat `batch_dialogs/` 구조보다 `shell.py` + `profiles/` composition 구조가 적합하다고 확정함 (319→320 재결정).
- `batch_dialogs/shell.py`가 Toplevel lifecycle, focus, close callback, hidden-first geometry settle, snapshot handoff를 단독 소유하고, 프로필별 파일은 matrix table layout + controller 연동만 담당하는 thin adapter로 제한하는 원칙을 수립함.
- 다형성 상속 없이 Composition 기반으로 책임을 양분하는 구조를 최종 승인함.
- 참조: reports 319, 320.

---

## 2026-06-10 — Batch dialog shell implementation and cleanup

### Decision
- `BatchDialogShell` + `profiles/hong_kong_cspf.py` 구현 및 이주를 완료하고, `hong_kong_cspf_batch_section.py` 제거 후 사용자 manual GUI smoke 이상 없음을 확인함 (321→322 closeout).
- `HongKongCspfBatchDialog.snapshot()`이 `BatchDialogShell`의 private attribute에 직접 접근하던 구현을 `BatchDialogShell.snapshot()` public 메서드로 전환하여 캡슐화를 완결함 (322→323 correction).
- 테스트 내 private access(`_shell.snapshot()`)를 제거하고, shell-level snapshot 검증은 `test_ui_tk_batch_dialog_shell.py` 전용 unit test로 이관함.
- 현재 검증 범위 내 마감.
- 참조: reports 321, 322, 323.

---

## 2026-06-10 — ISO and SASO batch profile expansion

### Decision
- ISO/India ISEER 2-point batch dialog를 `profiles/iso_iseer_2point.py`로, SASO T3 batch dialog를 `profiles/saso_t3.py`로 각각 구현 완료 (324, 326).
- SASO T3의 optional 35 Min partial 입력 처리 불일치 보정 및 header/column 순서(4pt first, 3pt second) 보정을 완료함 (327).
- ISO 2-point 리포트 내 로컬 절대경로 링크 교정 및 manual smoke 검증 기록 운영 원칙 수립 (325).
- 향후 prompt에서 수동 GUI 확인 세부 항목을 생략하고 결과만 반영한다는 운영 원칙 명시.
- 다음 핵심 action은 `Batch foundation foldering audit`.
- 참조: reports 324, 325, 326, 327.

---

## 2026-06-20 — Agent change gate owner and routing contract

### Decision
- 구조 영향 source 작업의 pre-write boundary, Read Ledger, staged report association, no-report exemption, future hook/CI 정책을 `docs/agent_workflows/AGENT_CHANGE_GATES.md`로 단일 owner화함.
- `AGENTS.md`, `AGENT_TASK_ROUTER.md`, `ACTIVE_DOCUMENTS.md`는 owner로 이동하는 최소 link만 유지하고 세부 정책을 복제하지 않음.
- `tools/check_agent_change_gate.py --cached`가 index blob, staged active report association, literal-path manifest, source/hotspot/code-map gate를 검증하도록 구현됨.
- 다음 workflow slice는 cached checker를 pre-commit/commit-msg hook에 연결하는 작업으로 제한함.

---

## 2026-06-20 — EN14825 calculator completion and AHRI readiness transition

### Decision
- EN14825 main SEER/SCOP UI, config/point contracts, SEER/SCOP batch workflows,
  SCOP parent access, snapshot handoff, and parent/dialog cleanup lifecycle을
  현재 범위에서 완료로 판정함.
- 실제 Tk/Toplevel lifecycle smoke에서 SEER/SCOP batch open, duplicate-dialog
  prevention, close snapshot, reopen restore, clean shutdown을 확인하고 EN14825
  focused superset 81 tests가 통과함.
- Computer Use의 Tk accessibility 한계로 pointer-click 시각 spot-check는
  weaker-verified로 남지만 제품 blocker로 분류하지 않음.
- 다음 Arc는 AHRI 210/240 readiness audit로 시작하며, audit 전에
  implementation이나 batch requirement를 임의로 확정하지 않음.
- 참조: Summary 404, Summary 416, report 422, report 424.

---

## 2026-06-28 — Arc 9.5 accepted and Arc 10 started

### Decision
- Arc 9.5 unified case table second correction is accepted after focused
  automated coverage and user manual-smoke acceptance.
- Completed Arc 9.5 visual parity, reopen, manual-smoke audit, and second
  correction reports were summarized into
  `result_reports/summaries/582_summary-arc95-unified-table-manual-smoke-closeout.md`
  and moved to archive.
- Arc 10 Prediction Worker / Progress is active. The next implementation action
  is Slice 1 - Worker/Progress Boundary Design Alignment.
- Real-model prediction success smoke remains blocked by absent
  `model/model.pkl`; Arc 11 Trainer execution remains deferred.

---

## 2026-06-28 — Arc 10 prediction worker progress implementation closeout

### Decision
- Arc 10 Prediction Worker / Progress implementation is complete for automated
  coverage: batch prediction execution now runs through worker/progress/cancel
  boundaries, row-level progress/results are reported, cancellation marks
  not-yet-run rows, and Predict model/mapping status ownership no longer lives
  in direct workspace file checks.
- Focused and final validation passed for Predict/Train/table/mapping/schema/
  worker/progress coverage, py_compile, structure guard, code-map freshness,
  and whitespace checks.
- Manual GUI smoke remains the next action. Real-model success smoke remains
  blocked until a valid `model/model.pkl` artifact exists.
- Arc 11 Trainer execution remains deferred and was not started in this arc.

---

## 2026-06-28 — Arc 10.5 DEV-only mock smoke foundation

### Decision
- A DEV-only mock smoke package under `tools/dev/mock_smoke/` can generate an
  inference-compatible mock prediction artifact and synthetic training CSV
  without requiring real data or a real `model/model.pkl`.
- Generated mock CSV/PKL/log/output files are isolated outside the repo by
  default, with repo-local fallback limited to ignored directories.
- The mock foundation is workflow-smoke evidence only; it does not validate
  prediction accuracy, physical trends, feature importance, or production model
  quality.
- Next action remains Arc 10 manual smoke with mock artifact, followed by the
  Arc 11 decision.

---

## 2026-06-28 — Arc 10.5b isolated mock bundle smoke verification

### Decision
- The DEV-only mock smoke tooling now creates a full isolated bundle:
  prediction artifact, mapping JSON, paste-ready case TSV, training CSV, and
  manifest.
- Offscreen Predict smoke verifies paste/autofill, prediction completion,
  slow-model cancel behavior, result/copy basics, and cleanup without modifying
  production app code.
- Offscreen Train smoke verifies shell/status/tab construction and disabled
  Train/Data Mapping execution controls only; Trainer execution remains
  deferred to Arc 11.
- Next action is Arc 11 Trainer execution boundary design using the same mock
  bundle.

---

## 2026-06-28 — Arc 11 Trainer execution foundation closeout

### Decision
- Arc 11 Trainer execution foundation is complete for automated coverage:
  Train execution now flows through Qt-free service/state contracts,
  `TrainWorker`, `TrainController`, and Train / Model UI callbacks.
- The production default service wraps `core.ml.training.train_all_models`
  without changing core ML algorithms, preprocessing, registry, artifact
  schema, calculator behavior, or Data Mapping execution.
- DEV-only Train execution E2E uses the Arc 10.5b mock bundle and fast backend,
  creates an inference-compatible local model artifact, then runs Predict smoke
  against that Train output with cleanup.
- Production real-core training smoke remains optional because it is expensive
  and mock-data metrics are meaningless. Manual GUI smoke remains the next
  action.

## 2026-06-28 — Arc 11 hexagonal boundary acceptance reopened

### Decision
- Arc 11 final architecture acceptance is reopened after hexagonal boundary
  review.
- Train/Predict correction remains in Arc 11 slices: Train production execution
  must move behind a killable process adapter, and Predict execution must move
  behind a UI/runtime-neutral usecase/port.
- Calculator correction is routed to Arc 12 without Arc 11 implementation.
- Former Arc 12 ML Pipeline Stabilization is moved to Arc 13 and held until Arc
  11 and Arc 12 architecture corrections complete.

## 2026-06-28 — Arc 11 hexagonal boundary correction closeout

### Decision
- Arc 11 Predict/Train hexagonal boundary correction is complete for automated
  closeout scope.
- Train production UI execution now runs through an execution port and
  killable process runner adapter; cancel terminates/kills the child process and
  avoids partial final model artifacts.
- Predict execution now has a UI/runtime-neutral usecase/port, with QThread
  lifecycle isolated in the PySide runner adapter.
- Calculator usecase boundary correction is the next architecture correction in
  Arc 12; Arc 13 ML Pipeline Stabilization remains on hold.

## 2026-06-28 — Arc 11 final Train/Predict boundary cleanup

### Decision
- `PredictionController` no longer imports or creates the concrete
  `PySidePredictionRunner`; PySide runner creation is owned by the PySide
  workspace composition layer.
- The legacy direct `TrainWorker` path was deleted, and default direct
  `TrainingService.train()` production execution was disabled.
- Optional real-core Train smoke now uses the QProcess train job path.
- Arc 12 Calculator UI/Application Boundary Audit remains the next action.

## 2026-06-28 — TrainingService validation-only cleanup

### Decision
- `TrainingService` is reduced to Train resource status and request validation
  only.
- DEV/test backend execution moved to `tools/dev/mock_smoke/dev_training_runner.py`.
- Production UI Train execution remains owned by `QProcessTrainingRunner` and
  `apps/train/jobs/train_job.py`.
- Arc 12 Calculator UI/Application Boundary Audit remains the next action.

## 2026-06-28 — Arc 12 calculator usecase boundary audit formalized

### Decision
- Arc 12 is a narrow Calculator UI/Application Boundary Correction, not a full
  calculator rewrite.
- The first implementation target is ISO/ISEER 2-point single application
  usecase extraction, followed by matching batch handler reuse.
- SASO T3, Hong Kong CSPF/HSPF, EN14825, and AHRI remain candidates
  after the first ISO/ISEER pattern lands.
- Calculator formulas, config semantics, profile IDs, fixtures/golden expected,
  and public result dict contracts remain protected.

## 2026-06-28 — Arc 12 ISO/ISEER usecase boundary closeout

### Decision
- `apps.calculator.application` and `apps.calculator.adapters` now own the
  calculator application resolver and app-side dispatcher boundary.
- ISO/ISEER 2-point single UI no longer imports the core dispatcher or calls
  `calculate_cspf`; it renders `IsoIseer2PointUseCase` output.
- ISO/ISEER 2-point batch handler reuses the same usecase and preserves its
  existing result keys and pending/error behavior.
- No calculator formulas, config semantics, profile IDs, fixtures/golden
  expected, or public result dict contracts changed.
- Recommended next calculator target is SASO T3 usecase extraction; Arc 13
  remains on hold unless the user explicitly accepts deferring remaining
  calculator debt.

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

## 2026-06-29 — Arc 12 Slice 12 calculator outbound adapter hardening

### Decision
- Remaining calculator outbound construction/config concerns now live behind
  focused `apps/calculator/adapters/` gateways:
  AHRI calculator construction, EN14825 concrete calculator creation, and SASO
  T3 test-selection config override.
- Calculator application code no longer imports the core dispatcher, EN14825
  application adapters no longer import the concrete EN14825 core class, and
  `SasoT3UseCase` no longer mutates core calculator config shape directly.
- No calculator formulas, config semantics, profile IDs, fixtures/golden
  expected, public result dict contracts, Tk layout, batch table UX, or
  copy/export behavior changed.
- Arc 13 ML Pipeline Stabilization remains the next recommended arc.

## 2026-06-30 — Arc 13 Slice 0 ML feature manifest design gate

### Decision
- Arc 13 starts with ML Feature Manifest SSOT Foundation rather than a broad
  ML Pipeline Stabilization implementation.
- Slice 0 is design/audit only: no production behavior changes, no runtime
  manifest connection, and no conversion of `core/ml/features.py`,
  `core/ml/registry.py`, or `core/predictor_schema/columns.py`.
- The initial manifest target is a single user-managed feature contract file,
  while UI presentation, model policy, derived formulas, and artifact schema
  remain code-owned.
- Broad `build_input_df()` zero-fill behavior is documented as compatibility
  behavior; the target policy allows mode-missing zero fill only for cooling
  and heating capacity/power features after separate tests and confirmation.

## 2026-06-30 — Arc 13 Slice 1 feature catalog loader and validator

### Decision
- `config/ml/features.csv` is introduced as a non-runtime catalog draft for the
  current ML feature contract.
- `core/ml/feature_catalog.py` can load, validate, and project catalog rows
  without import-time file I/O, while existing runtime exports remain unchanged.
- Focused tests verify parity with current `BASE_FEATURES`, `DERIVED_FEATURES`,
  `TARGETS`, predictor schema mappings, one-hot tuples, registry references,
  zero-fill policy, and the Train panel target tuple.
- Current `BASE_FEATURES` and `TARGETS` orders conflict for result-like names,
  so catalog `targets()` keeps an explicit compatibility order until projection
  migration resolves the ordering contract.

## 2026-06-30 — Arc 13 Slice 2 ML features projection from catalog

### Decision
- `core/ml/features.py` now exports `BASE_FEATURES`, `DERIVED_FEATURES`, and
  `TARGETS` from the validated feature catalog projection.
- `config/ml/features.csv` result rows were reordered to the canonical
  `TARGETS` order: Cooling Power, Heating Power, Ref Qty, Cooling Hz,
  Heating Hz.
- `TARGET_COMPAT_ORDER` was removed because result row order now owns target
  projection order.
- `BASE_FEATURES` still needs a separate legacy result-order projection because
  existing base-feature order places `Ref Qty` before power and frequency
  target-like names.

## 2026-06-30 — Arc 13 Slice 2.5 feature catalog contract cleanup

### Decision
- `ml_name` is the raw training data header and internal ML feature/target name.
  Training data must match the catalog; no train-header alias or mapping column
  is introduced.
- `BASE_FEATURES` and `TARGETS` are feature/target name exports, not UI column
  order contracts. Predictor UI order remains a later schema projection concern
  based on role group and catalog order.
- Feature catalog responsibilities are split into loader/data model,
  validation, and projection modules before the owner grows further.
- Training header validation helpers exist for guard tests but are not wired
  into the training runtime in this slice.

## 2026-06-30 — Arc 13 Slice 3 predictor schema projection from catalog

### Decision
- `core/predictor_schema/columns.py` now builds ML-visible input, auto, and
  result columns from catalog projection while preserving `COLUMNS`,
  `INPUT_COLS`, `AUTO_COLS`, and `RESULT_COLS` exports.
- Catalog projection orders UI-visible ML columns by role group
  (`input` -> `auto` -> `result`) and catalog `order` inside each group.
- Dropdown-only input columns and rule-only result columns remain code-owned
  compatibility inserts because they are not ML feature contract rows.
- Width/color remain code-derived through role defaults plus narrow
  compatibility width overrides needed to preserve the existing schema.

## 2026-06-30 — Arc 13 Slice 3.5 predictor UI-only column owner split

### Decision
- `core/predictor_schema/ui_columns.py` owns dropdown-only input columns,
  rule-only result columns, and their insertion rules for the predictor table.
- `core/predictor_schema/columns.py` remains the final schema assembly/export
  owner: it combines catalog-projected ML columns with UI-only compatibility
  inserts and preserves the existing schema constants.
- One-hot adapter projection and training runtime guards remain separate Arc 13
  work and were not mixed into this owner split.
