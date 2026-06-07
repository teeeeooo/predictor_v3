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

> **Ordering note:** `partNN` 순서는 original `project_log.md` entry order를 보존한다. `project_log.md`는 최신 항목이 위에 오는 reverse chronological order이므로, segment filename의 date range도 reverse chronological일 수 있다. 과거 로그를 찾을 때는 파일명만 보지 말고 `rg -n "^## 2026-" docs/archive/project_log/YYYY-MM/*.md`로 heading을 검색한다.

## 2026-06-07 — Batch two-row matrix and reference parity arc summary lifecycle cleanup

### Decision
- Reports 237-248 are summarized under `result_reports/summaries/249_summary-batch-two-row-matrix-and-reference-parity-arc.md` and moved to archive.
- No active reports remain for this arc.
- Next technical action is result/detail/export common contract check.
- `project_memory_seed.md` updated with two new durable entries and one superseded entry.

## 2026-06-07 — Main notebook legacy vs batch dialog lifecycle audit

### Decision
- Main notebook/tab path (`Iso16358Tab`) is a partially corrected legacy path with
  nested notebook, profile switch, dynamic refit scheduler, and visible measurement.
- Batch dialog/table path (`HongKongCspfBatchDialog`, `BatchMatrixTable`) is a newer
  stable path created after the 229–235 window/dialog/table arc, using hidden-first
  sizing, internal viewport, common table foundation, and explicit state persistence.
- Apparent duplication between `BatchCaseTable` and `BatchMatrixTable` is shape-specific
  construction (row-per-case vs two-row matrix), not generic boilerplate. A base class
  would be premature with only two concrete shapes.
- `BatchMatrixTable` is at 422 LOC (soft limit 400). The next responsibility addition
  must trigger helper extraction, not file growth. No immediate refactor is required.
- Extraction priority: result/export contract check first, then main table migration
  preflight, then ui_tk folder cleanup.

## 2026-06-07 — BatchMatrixTable interaction parity repair

### Decision
- 245 audit's "paste tiling is not common helper gap" judgment was incorrect.
- `editable_paste_targets_by_role()` else path pasted multi-row clipboard once
  only; this is a common helper gap, not a surface-level restore/rebuild issue.
- Fix: tile/repeat MxN clipboard across selection rectangle via modulo indexing.
- Single-cell anchor and 1x1/1-row special cases are preserved.
- Same-shape `restore_snapshot` now updates cases and StringVars in-place without
  rebuilding widgets, matching BatchCaseTable's proven pattern.
- BatchMatrixTable exceeds 400 LOC soft limit; helper extraction is deferred
  to a future cleanup slice.

## 2026-06-07 — BatchMatrixTable repair vs rebuild audit

### Decision
- Audit (245) applied the 244 reference parity gate to BatchCaseTable as the
  reference for BatchMatrixTable interaction parity.
- BatchMatrixTable's critical gap is localized: `restore_snapshot` always calls
  `_rebuild_table()` even on same-shape restores, causing focus loss, selection
  loss, and flicker on undo and paste.
- BatchCaseTable already solved this with a same-shape restore path that
  updates model rows and StringVars directly without destroying widgets.
- Recommendation: repair current skeleton (add same-shape restore path to
  `restore_snapshot`) rather than partial rewrite or rebuild.
- Public surface contract (`TkTableSurface`), migration section, adapter, and
  handler do not need to change.

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

## 2026-06-07 — Tk two-row matrix table skeleton completed

### Decision
- `ui_tk/batch_matrix_table.py` provides the first reusable Tk two-row matrix surface.
- Integration path is confirmed: `BatchMatrixSpec` → `cell_role(position)` → `TkTableController`.
- Existing `BatchTableViewport` is reused without modification.
- Next step is Hong Kong CSPF matrix migration, not parallel maintenance of row-per-case and matrix layouts.

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

## 2026-06-05 — Table/window refit report lifecycle cleanup

### Result
- Summarized and archived completed reports from the post-main table/window
  refit arc through 221-b.
- Kept 221-c active because it is the direct evidence for the common dynamic
  content refit owner preflight.

### Decision
- Active reports should now focus on the current blocker and next decision:
  common dynamic content refit owner preflight.

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

## 2026-05-30 — Tkinter detail panel, copy, and graph parity recovery

### Decision
- Tkinter ISO result detail parity now follows the PyQt reference IA: main result
  surfaces expose `상세 보기 ↓ / 상세 닫기 ↑`, while source selection, summary,
  graph, detail table, detail TSV copy, and detail CSV export live inside the
  detail panel.
- Result comparison tables are TSV-copy surfaces, not CSV export targets.
  Detail/bin tables keep TSV copy plus CSV export.
- Detail graph x-axis is outdoor temperature bin `tj` (`Outdoor Temp [°C]`);
  `Bin Hours [h]` is a selectable y-series backed by `nj`.

### Lesson
- Implementing small trace/export/copy slices without preserving the PyQt
  reference IA caused main-screen control drift. Future UI parity work should
  treat the reference IA as the first acceptance gate, then layer helper actions
  inside that structure.

### Open
- Dual-monitor geometry clipping remains a separate audit/hotfix.
- Hong Kong HSPF heating detail needs a separate schema decision.

---

## 2026-05-30 — Tkinter ISO profile expansion and UI stabilization

### Tried
- Tkinter ISO tab expansion was split into design, implementation, manual smoke, and lifecycle slices. The arc covered ISO / ISEER 2-point adoption, Hong Kong coexistence, result comparison, profile-switch geometry, Design First Gate usage, and SASO T3 design.

### Result
- `ISO / ISEER 2-point` is the default ISO profile and renders a section-local comparison table for `ISO 16358-1` and `India ISEER`.
- `Hong Kong` keeps CSPF/HSPF metric sub-tabs and existing result behavior.
- Profile switching uses rendered preferred-size exact-fit with one measured-overflow correction and scroll reset.
- SASO T3 is designed as a dedicated section with required-only 3-point vs optional-min 4-point comparison, but is not implemented yet.

### Failed / Risk
- Grow-only profile-switch fit avoided shrink but left awkward blank space when returning from Hong Kong to ISO/ISEER 2-point, so it was replaced by default exact-fit.
- Future dynamic surfaces such as graph/detail need their own preferred-size owner before geometry can be considered stable for those modes.

### Decision
- Keep specialized result comparison surfaces section-local. Do not change `ResultPanel` or extract a generic comparison framework until repeated needs justify it.
- Use Design First Gate for larger profile/result additions; keep hotfixes small and evidence-driven.

### Lesson
- Profile-specific UI polish needs manual smoke after focused tests because measured content height, scroll state, and preferred-size policy can look correct in isolation but awkward during profile switching.

---

## 2026-05-28 — Tkinter calculator UX implementation arc + metric sub-tab amendment

### Decision
- Tkinter calculator ISO Hong Kong CSPF/HSPF visible UX가 matrix input, auto-calc,
  summary result surface를 거쳐 Excel-like controller 및 state machine까지
  구현되었다 (166~177). core/profile/dispatcher 경로와 기본 smoke 값은 유지한다.
- `MetricInputTable`은 metadata/mutation API만 제공하고 interaction logic은
  별도 `ExcelLikeTableController`가 소유하는 구조로 정착했다 (172).
- Selection mode / Edit mode, type-to-replace, same-cell second click / double
  click / F2 edit mode, Esc/focus/cross-table commit semantics가
  `03_SPREADSHEET_TABLE_UX_CONTRACT.md`와 Tkinter adapter에 반영됨 (175~177).
- UI smoke-loop mode와 diff/read budget 규칙이 `AGENT_TASK_ROUTER.md`에 추가되어
  token-heavy micro-fix churn을 줄임 (179a).
- Window geometry policy 값은 toolkit-local layout owner (`ui_tk/layout_constants.py`)
  에 두고 app shell module에는 직접 넣지 않는 원칙을 확정함 (179a).
- macOS 수동 smoke에서 CSPF/HSPF same-view vertical stack이 창 높이/스크롤/geometry
  문제를 반복 일으킴. 이에 final UX contract를 amendment하여 content density가 높은
  경우 standard tab 낸부 metric sub-tab 또는 equivalent segmented metric navigation을
  허용하고, ISO Hong Kong CSPF/HSPF는 metric 분리를 권장하는 amendment로 변경 (179e).
- EN 14825 SEER/SCOP, AHRI 210/240 SEER2/HSPF2도 같은 metric-navigation 원칙 적용.
- PyQt calculator-only source retirement와 graph/detail surface는 여전히 hold/deferred.

### Lesson
- Table behavior contract와 visible surface refinement를 분리해 구현하면,
  interaction foundation을 먼저 안정화한 뒤 visible layout을 반복 smoke로
  정제할 수 있다.
- Same-view vertical stack은 content density가 높을 때 창 geometry/scroll 문제를
  반복하므로, design gate에서 metric-level navigation을 early rejection하지 말고
  content density를 기준으로 조걶적으로 허용하는 편이 유연하다.

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

## 2026-05-23 — Xfail cleanup + PyQt/Tkinter environment stabilization

### Decision
- ISO pure-route Formula 45/49/47/50 xfail 4개는 obsolete experiment로 판정해
  `tests/test_iso16358_hspf_pure_iso_track_a.py`에서 제거. full suite xfail
  count는 23 → 19로 정리됨 (124).
- 남은 19개 xfail의 성격을 명확히 분리: `tests/_legacy` 17개는 legacy
  workbook-oracle diagnostic/reference (125), AS/NZS case3 2개는 external
  workbook reference / full component row data prerequisite으로 Z-phase
  deferred (126). marker / count / expected / fixture / core 코드 변경 없음.
- macOS 15.7.3 arm64 + Python 3.14.4 + PyQt5 5.15.11 환경에서 일부
  `QTableView` subclass 생성이 native SIGABRT abort를 일으키는 것을 audit
  완료 (128). `tests/helpers/pyqt_env.py` + `tests/test_pyqt_environment_guard.py`
  로 known-bad 환경 사전 skip 가드를 도입해 manual PyQt ignore 없이 full suite
  실행 가능해졌다 (129). PyQt test는 삭제하지 않고 다른 host에서는 계속 실행.
- Tkinter ISO section input dict / result formatting을 pure helper
  (`ui_tk/sections/iso16358_helpers.py`) 로 분리. Hong Kong CSPF 4.939 / HSPF
  3.643 smoke 유지 (130).
- `docs/guides/pyqt_test_support_matrix.md`는 중간 안정화 문서로 유지하되,
  PyQt calculator-only UI를 계속 고도화하는 것은 더 이상 목표가 아니다 (131).
  다음 방향은 **PyQt calculator-only retirement audit** (read-only inventory)
  이며, PyQt Predict/Train 앱은 유지 후보로 둔다.

### Lesson
- xfail은 marker만 보고 일괄 retirement하지 말고, 각각이 (a) production guard,
  (b) historical diagnostic/reference, (c) external prerequisite 중 어디에
  속하는지 분리해야 안전하게 정리할 수 있다.
- 특정 host (macOS + Python 3.14 + PyQt5) 의 native abort는 test 삭제나 xfail
  변환이 아니라 known-bad 환경 사전 skip 가드로 해결한다 — PyQt를 지원하는
  다른 host 실행 가능성을 깨지 않는다.

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

## 2026-06-07 — Configurable bin-detail schema extraction

### Tried
- 252 preflight에서 확인한 Hong Kong HSPF `bin_details`를 기존 CSPF detail panel
  shell로 표시하기 위한 foundation extraction.
- cooling-only hardcode를 복제하지 않고, `BinDetailSchema` dataclass로
  column/key/graph series를 주입 가능하게 분리.
- `BinTraceTable`, `BinDetailPanel`, `BinDetailGraph`에 schema parameter를
  추가하고 기본값으로 cooling schema를 유지.

### Result
- 기존 CSPF/SASO/ISEER detail panel 동작은 변화 없음 (regression 1 passed,
  16 skipped in headless).
- heating schema (`HEATING_HSPF_BIN_DETAIL_SCHEMA`)를 정의하고 sample HSPF bin
  row가 expected table row로 변환되는 것을 확인.
- `table_export_data()` / copy / CSV export contract는 그대로 유지.
- core calculator, golden, fixture, ResultPanel, batch matrix는 변경 없음.

### Decision
- UI shell과 domain-specific schema는 `BinDetailSchema`로 분리한다.
- profile-specific detail surface는 schema 주입으로 동일한 shell을 재사용한다.
- heating-specific duplicate class는 schema 주입으로 대체 가능하다.

### Lesson
- hardcoded domain schema를 직접 복제하는 대신, 작은 dataclass 하나로
  table+graph+export contract를 parameterize하면 동일 shell로 multi-profile
  detail surface를 안전하게 확장할 수 있다.

---

## 2026-06-07 — Hong Kong HSPF single-case detail/bin panel wiring

### Tried
- 253/254에서 준비한 configurable schema-driven `BinDetailPanel` shell과
  `HEATING_HSPF_BIN_DETAIL_SCHEMA`를 사용해 Hong Kong HSPF section에 detail
  toggle + panel을 추가.
- core가 이미 반환하는 `result["bin_details"]`를 `BinDetailSource(rows=...)`로
  변환해 detail table/graph/summary에 연결.
- invalid input / calculation error 시 stale detail rows를 `_clear_trace()`로
  제거.

### Result
- Hong Kong HSPF section에 detail toggle + `BinDetailPanel` 추가 완료.
- Heating detail table은 10개 컬럼(Bin No, Temp, Hours, Load, Delivered, Power,
  Case, Heat Pump, Auxiliary, Total)을 표시.
- Heating graph combo는 7개 series(Bin Hours, Load, Delivered, Power, Heat Pump,
  Auxiliary, Total)를 제공.
- Detail summary는 HSPF / HSTL [kWh] / HSEC [kWh]를 표시.
- 상세 복사/CSV보내기는 기존 `table_clipboard` / `table_csv_export` helper를
  그대로 사용.
- 기존 CSPF/SASO/ISO detail regression은 변화 없음.
- core calculator, golden, fixture, batch matrix, ResultPanel 변경 없음.

### Decision
- Hong Kong HSPF single-case detail surface는 `HEATING_HSPF_BIN_DETAIL_SCHEMA`
  주입으로 동일 `BinDetailPanel` shell을 재사용한다.
- heating detail wiring pattern은 cooling detail wiring과 구조적으로 동일하며,
  차이는 schema와 section-specific summary formatter뿐이다.

### Lesson
- schema-driven shell이 준비된 상태에서 profile-specific detail wiring은
  section-level helper + schema 주입만으로 완성할 수 있다.
- shell 수정 없이 section wiring만으로 새 profile detail surface를 추가하는
  것이 clean architecture boundary를 지키는 방법이다.

---

## 2026-06-07 — Shared Tk content-hugging refit/minsize lifecycle repair

### Tried
- Hong Kong CSPF/HSPF에서 드러난 창 크기/상세보기/minsize 문제를 shared lifecycle
  문제로 다루어 공통 owner에서 수정.
- `fit_visible_content()`의 minsize update를 제거하여 detail open이 minsize를
  영구적으로 잠그지 않게 함.
- `_on_metric_tab_changed`를 scheduler-based refit로 활성화하여 tab switch 시
  current content 기준 refit이 동작하게 함.
- HSPF section에 `on_trace_visibility_changed` callback contract를 CSPF와 동일하게
  추가.

### Result
- `fit_visible_content()`는 geometry만 변경하고 minsize는 건드리지 않음.
- Metric notebook tab change 시 `DynamicContentRefitScheduler`가 refit을 요청.
- HSPF detail toggle 시 parent refit이 요청됨.
- 기존 ISO/ISEER/SASO/CSPF regression은 변화 없음.
- core calculator, golden, fixture, batch matrix, detail panel schema 변경 없음.

### Decision
- minsize는 init baseline/floor로 유지하고 content fit이 minsize를 override하지
  않는다.
- nested notebook tab switch refit은 direct synchronous call이 아니라
  `DynamicContentRefitScheduler`를 통해 loop-safe하게 요청한다.
- 모든 detail-panel section은 tab owner로부터 visibility callback을 받아야 한다.
  누락은 wiring bug로 취급한다.

### Lesson
- `root.minsize(target)`를 content fit마다 호출하면 detail open/close 후
  창이 다시 작아질 수 없다. minsize와 content fit target은 별도 policy로
  관리해야 한다.
- scheduler-based refit은 tab switch, detail toggle 등 여러 이벤트에서
  geometry loop를 방지하는 필수 infrastructure다.

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

## 2026-06-07 — Nested notebook current-state width/height replacement repair

### Tried
- 257 이후 남은 Hong Kong nested notebook 창 크기 refit 문제를 current-state
  replacement policy로 해결.
- `_observed_max_tab_width` sticky cache를 제거하고 `current_tab_width`를 사용.
- height correction formula가 no-op이 되던 문제를 chrome_estimate 기반으로 수정.

### Result
- `max_tab_width`는 current_tab_width로, 이전 expanded size를 고정하지 않음.
- height correction은 chrome_estimate(tab bar height) + current_tab_height로
  notebook sticky height를 실제 current visible height로 치환.
- 기존 ISO/ISEER/SASO/CSPF/HSPF regression은 변화 없음.
- core calculator, golden, fixture, batch matrix, detail panel schema 변경 없음.

### Decision
- nested notebook auto-fit의 width/height는 모두 current visible tab 기준이어야 한다.
- observed cache는 sticky target이 아니라 chrome estimate 같은 보조 용도로만 사용.
- height correction은 `max_tab_height` 대신 `chrome_estimate`를 사용해야 한다.

### Lesson
- sticky cache(`observed_max`)는 shrink가 필요할 때 창 크기를 고정한다.
- side-effect-free measurement와 current-state replacement는 별개 원칙이지만
  둘 다 충족해야 한다.

---

## 2026-06-07 — Nested notebook width replacement using chrome-width estimate

### Tried
- 258 이후 남은 width sticky 문제를 chrome-width estimate와 replacement formula로
  해결.
- `_chrome_estimate`를 `_chrome_height_estimate`와 `_chrome_width_estimate`로
  분리.
- `NestedNotebookMeasurement`에 `notebook_width` 추가.
- width replacement formula를 height formula와 동일한 구조로 적용.

### Result
- width도 height처럼 `content_reqwidth - notebook_width + chrome + current_tab`
  구조로 replacement되어 shrink 가능.
- `max(content_reqwidth, current_tab_width)`는 sticky notebook width가 있으면
  shrink를 막으므로 replacement formula가 필요.
- 기존 ISO/ISEER/SASO/CSPF/HSPF regression은 변화 없음.
- core calculator, golden, fixture, batch matrix, detail panel schema 변경 없음.

### Decision
- nested notebook auto-fit width/height는 모두 replacement formula를 사용.
- chrome estimate는 axis별로 분리(height/width)하여 추적.
- `content_reqwidth`가 sticky container width를 포함하면 `max()` fallback만으로는
  shrink가 불가능하다.

### Lesson
- width와 height의 measurement 정책은 대칭적으로 유지해야 한다.
- 한 축만 replacement하고 다른 축은 `max()` fallback을 남겨두면 asymmetric
  shrink/grow behavior가 생긴다.

---

## 2026-06-07 — HSPF detail/schema + window lifecycle arc closeout and archive

### Tried
- 250~259 active reports를 summary(260)로 묶고 archive로 이동.
- Windows smoke OK 상태로 window lifecycle arc를 closeout.
- project_memory_seed에 schema-driven bin detail shell과 side-effect-free
  measurement policy durable decisions를 추가.

### Result
- 250~259 active reports 모두 archive로 이동 완료.
- 260 summary 작성 완료.
- project_memory_seed에 2개 entry 추가 완료.
- Window lifecycle 관련 문제는 사용자 확인 하에 닫을 수 있는 상태.

### Decision
- 완료된 arc는 summary와 archive로 정리하여 active report folder를 정리한다.
- 다음 architectural assessment 전에 active report 수를 기준 이하로 유지한다.

### Lesson
- 연속된 micro-fix(256~259)는 개별 report를 남기되, 최종적으로 summary로 묶어
  archive하면 active folder 관리가 용이하다.

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

## 2026-06-07 — Main paste policy / validation arc Windows validation closeout

### Tried
- 265~268 arc를 Windows validation 결과 기준으로 closeout.
- excel_like_table_controller: 32 passed / 1 skipped.
- metric_input_table_validation: 19 passed / 2 skipped.
- metric_input_table_adapter: 23 passed / 1 skipped.

### Result
- assertion failure 없음.
- 남은 skip은 Python 3.14.5 Tcl/Tk environment issue로 code defect 아님.
- paste policy arc는 Windows validation closeout 가능.

### Decision
- 265~268 arc는 완료로 판단.
- 다음 작업은 AI-generated code risk checklist adoption audit.

### Lesson
- headless 환경에서 skipped된 GUI tests는 Windows 실제 실행에서 assertion
  failure가 발생할 수 있으므로, Windows validation closeout을 별도로 수행해야 한다.
- callback count와 같은 세부 contract는 headless가 아닌 실제 실행에서만
  드러날 수 있다.

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

## 2026-06-07 — ui_tk cleanup preflight using Reference Evidence Gate

### Tried
- Reference Evidence Gate를 실제 preflight에 처음 적용.
- code_checker map을 token-safe하게 사용해 ui_tk hotspot과 duplicate helper를
  감사.
- table/controller convergence boundary, detail/export duplication, window
  related 파일을 분류.

### Decision
- `_bin_details`, `_metric_value`, `_kwh_value`는 3개/2개 section 파일에서
  동일하게 복제되어 있어 `result_formatting.py`로 추출 가능하다.
- `ExcelLikeTableController`는 legacy controller이며 4개 section에서 사용 중.
  `TkTableController`로의 switch는 유효한 future slice이나 첫 slice로는
  regression risk가 높다.
- `MetricInputTable`과 `BatchMatrixTable`의 adapter method 추출은 controller
  switch 안정화 후가 적절하다.
- `BinDetailPanel`의 `__init__`/`_draw` split은 GUI smoke가 필요하므로
  별도 slice로 deferred.

### Decision
- 첫 implementation slice는 section-level result formatting helper 추출로
  결정. zero behavior change, Windows smoke 불필요.

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
