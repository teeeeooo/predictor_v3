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

## 2026-06-07 — Section-level result formatting helper extraction

### Tried
- `_bin_details`, `_metric_value`, `_kwh_value`를 3개/2개 section 파일에서
  `result_formatting.py`로 추출.
- behavior change 없는 pure helper extraction.
- 10개 focused test 추가.

### Decision
- `result_formatting.py`가 section-level detail/summary formatting helper의
  canonical owner다.
- public names: `bin_details`, `metric_value`, `kwh_value`.
- `_kwh_value` (keyword-only `kwh_aliases` / `wh_aliases` 버전)은 summary
  function 내부용으로 유지.
- 다음 slice 후보: `BinDetailPanel` cleanup preflight 또는 controller switch
  design preflight.

---

## 2026-06-07 — BinDetailPanel cleanup preflight

### Tried
- `BinDetailPanel.__init__`(115 LOC)와 `BinDetailGraph._draw`(87 LOC)의
  long-function 원인 분석.
- `__init__`는 selector/summary/graph/table/button widget construction sequence.
- `_draw`는 canvas clear, axis, label, line, dot drawing sequence.
- `set_sources`, `set_status`, `copy_table`, `export_csv` public contract 확인.

### Decision
- `__init__`는 private setup helper로 나누기에 안전하고 regression risk가 낮다.
  (widget construction order만 보존하면 됨)
- `_draw`는 canvas side-effect sequence이므로 split은 유효하나 Windows GUI
  smoke가 필요하므로 별도 slice로 deferred.
- public contract (`set_sources`, `set_status`, `copy_table`, `export_csv`)는
  어떤 cleanup에서도 signature/behavior를 유지해야 한다.

### Decision
- 첫 implementation slice는 `BinDetailPanel.__init__` setup helper split으로
  결정.

---

## 2026-06-07 — BinDetailPanel.__init__ setup helper split

### Tried
- `BinDetailPanel.__init__`의 widget construction sequence를 6개 private
  setup helper로 분리.
- `_build_selector_row`, `_build_summary_label`, `_build_graph_row`,
  `_build_graph_canvas`, `_build_table`, `_build_action_buttons`.

### Result
- `__init__`는 state init + helper calls + `_refresh_current_source()`로 정리.
- behavior change 없음. widget hierarchy, attribute names, callback binding
  모두 유지.
- code map에서 `__init__`의 long-function hotspot 표시가 사라짐.
- `_draw`는 이번 작업에서 수정하지 않음.

### Decision
- public contract는 그대로 유지.
- 다음 slice 후보: `BinDetailGraph._draw` helper split 또는 controller switch
  design preflight.

---

## 2026-06-07 — Controller switch design preflight

### Tried
- `ExcelLikeTableController`와 `TkTableController` + `interaction_core`의
  behavior contract를 비교 분석.
- `MetricInputTable`의 `TkTableSurface` adapter compatibility 확인.
- paste, undo, selection, invalid field marking, callback, keyboard
  navigation parity assessment.

### Result
- `TkTableController`의 paste는 role-filtered (`editable_paste_targets_by_role`)
  로 265 policy와 더 잘 정렬됨.
- invalid field visual state는 `default_cell_background`를 통해 이미
  compatible (`MetricInputTable`이 이미 구현함).
- callback chain은 `set_positions_batch` -> `set_values_batch` 경로로
  compatible.
- `MetricInputTable`는 `ttk.Frame`을 상속하므로 `clipboard_clear`,
  `clipboard_append`, `clipboard_get`, `winfo_containing`을 이미 포함함.
  controller switch의 hard blocker는 없음.

### Decision
- controller switch의 hard blocker는 없음. `MetricInputTable`는 이미
  `TkTableSurface` protocol을 완전히 만족함.
- 다음 slice는 parity test foundation: `MetricInputTable` + `TkTableController`
  behavior parity 확인.
- binding strategy 차이(widget-level vs entry-level)는 parity test로 검증.
- parity test 통과 후 pilot section switch.

---

## 2026-06-07 — MetricInputTable clipboard protocol compatibility check

### Tried
- `MetricInputTable`가 `ttk.Frame`을 상속하므로 `clipboard_clear`,
  `clipboard_append`, `clipboard_get`을 이미 제공하는지 runtime 확인.
- `TkTableController._copy` / `._paste` 호출 방식과 signature 호환성 확인.
- focused roundtrip test 추가.

### Result
- `MetricInputTable`는 `ttk.Frame`에서 clipboard methods를 상속받음.
- signatures가 `TkTableController`의 호출 방식과 100% 호환.
- production code 수정 불필요.
- 279의 "clipboard methods missing" 판단은 잘못되었음.
- 279의 recursive wrapper 예시는 버그임.

### Decision
- controller switch의 hard blocker는 없음.
- 다음 slice는 controller switch parity test foundation.

---

## 2026-06-07 — Controller switch parity test foundation

### Tried
- `MetricInputTable + TkTableController` parity test 15개 작성.
- attach/select, copy/paste, clear/undo, invalid visual state, replace-on-type
  behavior를 검증.

### Result
- 15개 테스트 모두 headless 환경에서 skip (Tk unavailable).
- 0 failures. 테스트 구조는 정확함.
- production code 수정 불필요.

### Decision
- parity test foundation이 준비되었음.
- 다음 gate: Windows/iMac GUI 환경에서 동일한 focused test를 실행하여
  실제 pass 확인.
- GUI pass 확인 후 controller switch pilot implementation 진행.

---

## 2026-06-07 — Windows parity test closeout

### Tried
- Windows Python 3.14.5 환경에서 focused parity test 2회 실행.
- command: `python -m pytest tests/test_ui_tk_metric_input_table_controller_parity.py -rs -vv`

### Result
- 13 passed, 2 skipped, 0 failures (2회 동일 결과, flaky 아님).
- skip reason: local Tcl/Tk install/path issue (`Can't find a usable tk.tcl`, `init.tcl`).
- assertion failure 없음.

### Decision
- controller switch pilot implementation 조건부 진행 허용.
- 조건: pilot 구현 후 Windows manual smoke 필수.

---

## 2026-06-07 — Fix controller parity readonly paste test

### Tried
- `test_paste_ignores_readonly_target`가 실제 paste behavior를 검증하지 않음을 확인.
- 2x2 mixed editable/readonly fixture 추가 (왼쪽 열 editable, 오른쪽 열 readonly).
- readonly paste test를 실제 behavior 검증으로 교체:
  - 2x2 TSV clipboard paste 수행
  - editable cell은 값 변경, readonly cell은 변화 없음 확인
  - underlying snapshot에 readonly field key가 생성되지 않음 확인.

### Result
- test-only correction, production code 수정 없음.
- 15 tests collected, 15 skipped, 0 failures.

### Decision
- controller parity test suite 이제 "Paste role-filtering ignores readonly cells"를
  실제 mixed-role fixture로 검증함.
- 다음 gate는 동일: Windows/iMac GUI focused parity test confirmation.

---

## 2026-06-07 — Controller switch pilot implementation

### Tried
- `HongKongCspfSection`의 `rated_controller` / `input_controller`를
  `ExcelLikeTableController`에서 `TkTableController`로 전환.
- Xvfb 환경에서 pilot test 5개 및 parity test 15개 실행.

### Result
- 5 pilot tests: 5 passed, 0 skipped, 0 failures.
- 15 parity tests: 15 passed, 0 skipped, 0 failures.
- Xvfb 환경에서 전체 통과.
- production code 수정: import 1개, controller 생성 2줄.

### Decision
- controller switch pilot 구현 완료.
- 다음 gate: Windows manual smoke (app 실행, table interaction, paste, undo, clear, recalculate 확인).
- Windows smoke 통과 후 다른 section 전환 고려.

---

## 2026-06-07 — TkTableController type-replace flicker diagnosis

### Tried
- CSPF(TkTableController)와 HSPF(ExcelLikeTableController)의 callback/render count를
  diagnostic test로 비교.
- ResultPanel rebuild behavior 확인.
- controller type-replace flow 차이 분석.

### Result
- schedule count, set_summaries count, native edit count 모두 CSPF/HSPF 동일.
- ResultPanel은 양쪽 모두 full rebuild.
- 유일한 discriminating difference: TkTableController._type_replace가
  이미 focus를 가진 entry에 불필요한 focus_set()을 호출함.
- ExcelLikeTableController._type_replace에는 focus_set() 없음.

### Decision
- flicker root cause: TkTableController._type_replace의 redundant focus_set().
- 다음 slice: focus_set() 제거 후 Windows smoke 재확인.
- controller switch expansion은 flicker fix 확인 후 진행.

---

## 2026-06-07 — Remove redundant focus_set from TkTableController._type_replace

### Tried
- `TkTableController._type_replace()`의 redundant `focus_set()` 호출 제거.
- regression test 추가: `_type_replace` 중 `focus_set` 호출 0회 확인.

### Result
- production code 수정 1줄 (focus_set() 제거).
- 9 diagnostic tests passed, 15 parity tests passed, 5 pilot tests passed.
- Xvfb 환경에서 전체 통과.

### Decision
- flicker fix 적용 완료.
- 다음 gate: Windows manual smoke로 flicker 사라짐 확인.
- Windows smoke 통과 후 controller switch expansion 고려.

---

## 2026-06-07 — Stable ResultPanel summary update

### Tried
- `ResultPanel.set_summaries()`의 full destroy/recreate 구조를 stable update로 개선.
- same-shape summary는 기존 widget identity 유지, value label text와 status text만 갱신.
- shape 변경 시 기존 full rebuild fallback 유지.

### Result
- production code 수정: `ui_tk/result_panel.py`에 stable update logic 추가.
- 9 new tests + 10 diagnostic + 15 parity + 5 pilot = 39 tests passed under Xvfb.
- public API 변경 없음.

### Decision
- ResultPanel stable update 구현 완료.
- 다음 gate: Windows manual smoke로 flicker 해소 확인.
- flicker 해소 확인 후 controller switch expansion 진행.
- invalid text undo는 별도 후속 slice로 분리.

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

## 2026-06-09 — Narrow ResultPanel focus helper exception handling

### Tried
- `_is_descendant_of_panel()`와 `_restore_focus_if_alive()`의 broad `except Exception`를 `except tk.TclError`로 좁힘.
- 동작 변경 없이 code quality guardrail 반영.

### Result
- 13 stable update tests passed, 10 diagnostic tests passed.
- py_compile OK, check_code_structure no new violations.

### Decision
- ResultPanel focus helper 예외 처리를 Tkinter 경계 오류로 한정.
- 다음 gate는 288과 동일: Windows manual smoke.

---

## 2026-06-09 — Post-focus-preservation GUI smoke closeout

### Tried
- iMac GUI smoke for 288 focus-preservation fix.

### Result
- calculator_tk 실행 OK.
- Hong Kong CSPF profile OK.
- 숫자 입력 시 ResultPanel flicker 없음.
- invalid text 입력 후 오류 summary 표시 OK.
- Ctrl+Z undo가 원래 값으로 복원됨.
- undo 후 같은 셀에 계속 입력 가능.
- paste / clear / numeric undo 유지.
- detail open/close 이상 없음.
- 다른 profile 전환 후 이상 없음.

### Decision
- Post-focus-preservation GUI smoke passed.
- invalid text undo 문제 해결됨.
- controller switch expansion blocker 해소됨.
- 다음 action: active report lifecycle cleanup follow-up 또는 controller switch expansion readiness.

---

## 2026-06-09 — Active report lifecycle cleanup

### Tried
- 28 completed active reports를 4개 summary로 묶어 archive로 이동.
- 3개 report(262, 274, 275)는 다음 action 관련 preflight/결과로 active에 유지.

### Result
- active report count: 31 → 3.
- summaries: 292(paste policy), 293(reference map), 294(result formatting/bin detail), 295(controller switch/ResultPanel focus).
- archived: 28 reports.

### Decision
- active report lifecycle cleanup 완료.
- 다음 action: controller switch expansion readiness.

---

## 2026-06-09 — Controller switch expansion readiness preflight

### Tried
- 남은 section별 controller switch(TkTableController) 전환 타당성 및 blocker 검토.

### Result
- HongKongHspfSection, IsoIseer2PointSection, IsoSasoT3Section 모두 Blocker 없음.
- MetricInputTable은 이미 TkTableSurface 프로토콜을 만족함.
- IsoIseer2PointSection / IsoSasoT3Section의 custom result table은 Treeview 기반으로, ResultPanel stable update의 직접 영향이 없고 flicker 위험이 낮음.

### Decision
- 전환 순서를 HongKongHspfSection -> IsoIseer2PointSection -> IsoSasoT3Section 순으로 권장.
- 다음 action: HongKongHspfSection controller switch implementation.

---

## 2026-06-09 — Implement HongKongHspfSection controller switch

### Tried
- `HongKongHspfSection`을 `ExcelLikeTableController`에서 `TkTableController`로 전환.
- 6개의 focused test 추가 및 검증.

### Result
- `ui_tk/sections/hong_kong_hspf_section.py` 수정 완료.
- `tests/test_ui_tk_hong_kong_hspf_controller_switch.py` 신설 완료 (6 pass).
- CSPF, stable update, metric input table parity 테스트 등 39개 테스트 통과.
- py_compile OK, check_code_structure.py 신규 위반 없음.

### Decision
- HongKongHspfSection의 controller switch migration 완료.
- 다음 action: Post-HSPF controller switch GUI smoke.

---

## 2026-06-09 — Fix TkTableController type-replace selection carryover

### Tried
- macOS/Tk에서 셀 클릭 후 첫 글자 입력 후 다음 keystroke 입력 시 첫 글자가 덮어쓰여지는 selection carryover 문제 해결.
- `_type_replace`에서 programmatic replace 성공 후 `widget.select_clear()` 추가.
- type-replace multi-key append 동작 검증용 regression test 추가.

### Result
- `ui_tk/table/controller.py` 수정 완료.
- `tests/test_ui_tk_metric_input_table_controller_parity.py`에 regression test 추가 (`test_type_replace_clears_selection_for_multi_key_append` 통과).
- focused pytest 39개 통과, py_compile 및 구조 진단 경고 없음.

### Decision
- TkTableController type-replace selection carryover 버그 수정 완료.
- 다음 action: Post-type-replace selection fix GUI smoke.

---

## 2026-06-09 — Close out post-type-replace selection fix GUI smoke

### Tried
- 300 selection carryover 버그 수정 후 iMac 실기에서 GUI smoke 테스트 수행 및 closeout.

### Result
- `calculator_tk` 정상 실행 및 Hong Kong HSPF/CSPF type-replace(`1`, `10`, `100` 입력) 정상 확인.
- 기존 값 replace 및 후속 입력 append 확인 완료.
- Ctrl+Z undo, valid/invalid paste, clear, ResultPanel flicker-free, profile switch 정상 유지 확인.

### Decision
- type-replace selection carryover fix 검증 통과 및 blocker 해소.
- 다음 action: IsoIseer2PointSection controller switch implementation.

---

## 2026-06-09 — Implement IsoIseer2PointSection controller switch

### Tried
- `IsoIseer2PointSection`을 `ExcelLikeTableController`에서 `TkTableController`로 전환.
- 6개의 focused test 추가 및 검증.

### Result
- `ui_tk/sections/iso_iseer_2point_section.py` 수정 완료.
- `tests/test_ui_tk_iso_iseer_2point_controller_switch.py` 신설 완료 (6 pass).
- CSPF, HSPF, stable update, metric input table parity 테스트 등 45개 테스트 통과.
- py_compile OK, check_code_structure.py 신규 위반 없음.

### Decision
- IsoIseer2PointSection의 controller switch migration 완료.
- 다음 action: Post-2-point controller switch GUI smoke.

---

## 2026-06-09 — Close out post-2-point controller switch GUI smoke

### Tried
- 302 IsoIseer2PointSection controller switch 이후 iMac 실기에서 GUI smoke 테스트 수행 및 closeout.

### Result
- `calculator_tk` 정상 실행 및 ISO / ISEER 2-point profile type-replace (`1`, `10`, `100` 입력) 정상 확인.
- 기존 값 replace 및 후속 입력 append 확인 완료.
- valid paste 후 custom Treeview result table 정상 갱신 확인.
- invalid input/paste 시 validation block 및 오류 표시, Ctrl+Z undo 복원 확인.
- clear/delete 및 detail panel, profile transition 정상 작동 확인.

### Decision
- IsoIseer2PointSection의 controller switch 검증 통과 및 blocker 해소.
- 다음 action: IsoSasoT3Section controller switch implementation.

---

## 2026-06-10 — Implement IsoSasoT3Section controller switch

### Tried
- 마지막 controller switch 대상인 `IsoSasoT3Section`을 `ExcelLikeTableController`에서 `TkTableController`로 전환.
- 7개의 focused test 추가 및 검증.

### Result
- `ui_tk/sections/iso_saso_t3_section.py` 수정 완료.
- `tests/test_ui_tk_iso_saso_t3_controller_switch.py` 신설 완료 (7 pass).
- CSPF/HSPF/2-point controller switch 및 metric input table parity 테스트 등 40개 테스트 전체 통과.
- py_compile OK, check_code_structure.py 신규 위반 없음.

### Decision
- IsoSasoT3Section의 controller switch migration 완료.
- 다음 action: Post-SASO T3 controller switch GUI smoke.
- active report count exceeds lifecycle threshold; cleanup pending.

---

## 2026-06-10 — Code checker and reference map gate audit

### Tried
- tools/code_checker 및 CODEBASE_REFERENCE_MAP의 게이트로서의 동작 상태와 freshness trigger audit 진행.
- Reference Evidence Gate의 워크플로우 내 실효성 및 project-wide gap 분석.

### Result
- `result_reports/active/305_code_checker_and_reference_map_gate_audit.md` 작성 완료.
- Map Freshness, Workflow Trigger, Semantic Owner-Bypass, Duplicate Responsibility, Hotspot Expansion 등 6대 gap 분류 완료.
- 5개 후속 작업 slice 제안 및 우선순위 수립.

### Decision
- Reference map freshness 및 semantic gate 강화 계획 수립 완료.
- 다음 action: Post-SASO T3 controller switch GUI smoke. (이후 Slice 1: reference map 재생성/커밋으로 연계)
- active report count exceeds lifecycle threshold; cleanup pending.

---

## 2026-06-10 — Align 305 code checker audit with original 270-272 reference map intent

### Tried
- 305 audit 결과를 270~272 original code_checker/reference map intent와 비교 검토하여 보정.
- code_checker를 semantic hard gate로 과확장하지 않도록 follow-up 순서와 표현 정리.

### Result
- `result_reports/active/305_code_checker_and_reference_map_gate_audit.md` 보정 완료 (`semantic analysis tool` -> `reference/structure evidence map` 등으로 수정).
- follow-up slice 순서를 재정의 (SASO T3 validation alignment 우선 적용하도록 구성).

### Decision
- code_checker는 reference/structure evidence map으로 유지하고, hard-fail 검사는 `tools/check_code_structure.py`에 위임함.
- 다음 action: SASO T3 Section Input Validation Alignment (Slice 1).
- active report count exceeds lifecycle threshold; cleanup pending.

---

## 2026-06-10 — SASO T3 Section Input Validation Alignment

### Tried
- `IsoSasoT3Section`의 validation 로직을 `MetricInputTable`의 invalid visual marking 표준 API와 정렬.
- `MetricInputTable.get_numeric_values()`가 field subset 단위로 validation할 수 있도록 backward-compatible하게 확장.

### Result
- `ui_tk/metric_input_table.py` 및 `ui_tk/sections/iso_saso_t3_section.py` 수정 완료.
- `tests/test_ui_tk_metric_input_table_validation.py`에 subset validation focused test 추가 완료.
- `tests/test_ui_tk_iso_saso_t3_controller_switch.py`에 required/optional invalid & positivity & correction focused test 추가 및 검증 완료.
- `result_reports/active/305_code_checker_and_reference_map_gate_audit.md` 내 `semantic and structure overview` 문구 1줄 보정 완료.

### Decision
- `MetricInputTable`은 numeric parsing 및 invalid visual marking을 소유하며, `IsoSasoT3Section`은 required/optional 그룹 분류 및 positivity 도메인 정책을 소유함.
- 다음 action: Post-SASO T3 controller switch & validation GUI smoke.
- active report count exceeds lifecycle threshold; cleanup pending.

---

## 2026-06-10 — Post-SASO T3 controller switch & validation GUI smoke closeout

### Tried
- 304 SASO T3 controller switch 및 307 SASO T3 validation alignment 이후 iMac 실기에서 GUI smoke 테스트 수행 및 closeout.
- `ui_tk/sections/iso_saso_t3_section.py` 내 미사용 parsing 관련 import/함수 정리.

### Result
- required/optional invalid input visual marking, 35 Min partial required row 유지, valid correction 복원 정상 확인.
- paste, undo, clear 및 profile transition 정상 확인.
- tests 35 pass, py_compile OK, check_code_structure.py 신규 위반 없음.

### Decision
- SASO T3 controller switch 및 validation alignment manual GUI blocker 해제 및 closeout 완료.
- 다음 action: Reference Evidence Gate warning-first workflow patch.
- active report count exceeds lifecycle threshold; cleanup pending.

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

## 2026-06-10 — Improve code_checker metadata & freshness checking

### Tried
- tools/code_checker의 reference map 생성 흐름에 git commit short hash, dirty status, schema version 등의 compact metadata 추가.
- 기존 CODEBASE_REFERENCE_MAP.md를 훼손하지 않는 read-only freshness check CLI 옵션(--check) 및 출력 경로 재지정 옵션(--output) 구현.
- fake metadata 및 temp file을 사용하여 git 의존성을 회피하는 2개의 focused test 추가 및 검증.

### Result
- `tools/code_checker/metadata.py` 신설 완료.
- `tools/code_checker/renderer.py` 및 `tools/code_checker/build_reference_map.py` 수정 완료.
- `tests/test_code_checker_reference_map.py` 내 focused test 2개 추가 완료 및 pass (전체 11개 통과).
- `docs/WORK_PLAN.md` 및 `project_log.md` 갱신 완료.

### Decision
- code_checker는 reference evidence tool로서 HEAD와의 정렬 상태(freshness)를 warning-first 경고로 제공하며, hard structure guard는 check_code_structure.py에만 위임함.
- 다음 action: CODEBASE_REFERENCE_MAP 재생성.
- active report count exceeds lifecycle threshold; cleanup pending.

---

## 2026-06-10 — Regenerate codebase reference map

### Tried
- metadata 및 task-number label decoupling 패치가 완료된 tools/code_checker를 이용해 CODEBASE_REFERENCE_MAP.md를 실제로 재생성.
- 생성 결과물 내 metadata HTML comment 및 중립적인 헤더가 정상적으로 포함되어 렌더링되는지 검증.

### Result
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` 재생성 완료 (230 lines).
- generated metadata 주석 주입 및 Generated by... 부분에서 task number 괄호 제거 확인 완료.
- commit 전 상태에서 `--check` 실행하여 `Freshness status: FRESH` 출력 및 uncommitted changes warning 정상 리포트됨을 확인.
- `docs/WORK_PLAN.md` 및 `project_log.md` 갱신 완료.

### Decision
- codebase reference map을 최신 snapshot 상태로 동기화 완료. Git metadata 정렬이 유효하며, commit 후 short hash 불일치(stale warning)는 다음 implementation 작업 개시 전 regeneration을 권장하는 evidence로 삼음. (추가 commit loop 차단)
- 다음 action: Controller switch arc 최종 summary / closeout.
- active report count exceeds lifecycle threshold; cleanup pending.

---

## 2026-06-10 — Controller switch arc final summary / closeout

### Tried
- ui_tk controller switch arc(Hong Kong HSPF/CSPF, ISO/ISEER 2-Point, SASO T3 마이그레이션 및 SASO validation alignment) 전체 완료 상태 최종 정리.
- MVC/SoC 정렬 관점의 의사결정 기록 및 향후 active report 아카이빙을 위한 preflight closeout 리포트 작성.

### Result
- `result_reports/active/313_controller_switch_arc_final_summary_closeout.md` 작성 완료.
- `docs/WORK_PLAN.md` 및 `project_log.md` 갱신 완료.

### Decision
- ui_tk controller switch 대수술(legacy ExcelLikeTableController에서 공통 TkTableController 전환)이 성공적으로 종결되어 안정적으로 작동하고 있음을 최종 승인 및 마감.
- 다음 action: Active report lifecycle cleanup.
- active report count exceeds lifecycle threshold; cleanup pending.

---

## 2026-06-10 — Active report lifecycle cleanup after controller switch arc closeout

### Tried
- 313에서 closeout된 controller switch arc 관련 active report들(298~313, 총 16개)을 summaries/314번 요약본으로 묶고, covered active reports를 archive로 이동 완료.
- active folder에는 다음 의사결정 및 open blocker 성격의 리포트들(262, 274, 275 등)만 남겨둠.

### Result
- `result_reports/summaries/314_summary-tkinter-table-controller-switch-arc-closeout.md` 생성 완료.
- 16개 active reports (298~313)를 `result_reports/archive/` 로 이동 완료.
- `docs/WORK_PLAN.md`, `project_log.md` 갱신 및 `result_reports/active/315_active_report_lifecycle_cleanup_after_controller_switch.md` 리포트 작성 완료.

### Decision
- active report 갯수를 임계치 이하(criteria 충족 상태)로 정리하여 마일스톤 위생상태 복구 완료.
- 다음 action: Main table migration check.
- active report count meets lifecycle threshold criteria.

---

## 2026-06-10 — Active report lifecycle cleanup correction

### Tried
- 직전 lifecycle cleanup 이후 active 폴더에 남은 leftover active reports(275, 296, 297)를 재검토하여 추가 아카이빙 처리.
- 297 리포트 내의 Pending final execution 및 exact count 문구를 completed/threshold wording으로 교정 후 archive로 이동.
- 314 summary 내 로컬 절대경로 링크(file:///Users/...)들을 repo-relative 상대경로로 보정.
- 315 리포트 내의 remaining active 리스트를 최종 상태에 맞게 갱신.

### Result
- 3개 active reports (275, 296, 297)를 `result_reports/archive/` 로 추가 이동 완료.
- `result_reports/summaries/314_summary-tkinter-table-controller-switch-arc-closeout.md` 의 절대경로 링크를 relative path로 변환 완료.
- `result_reports/active/315_active_report_lifecycle_cleanup_after_controller_switch.md` 및 `docs/WORK_PLAN.md`, `project_log.md` 보정 완료.
- `result_reports/active/316_active_report_lifecycle_cleanup_correction.md` 작성 완료.

### Decision
- active folder에는 오직 preflight 목적의 active 의사결정 리포트들(262, 274) 및 최근 결과 리포트(315)만 남겨두고 위생 상태 복구를 최종 완결함.
- 다음 action: Main table migration check.
- active report count meets lifecycle threshold criteria.

---

## 2026-06-10 — Main table migration check after controller switch arc closeout

### Tried
- 기존 active report 262 및 274 preflight 내용을 최신 controller switch 완료(313) 상태와 비교 분석하여 메인 테이블 마이그레이션 가능성을 재평가함.
- MetricInputTable, TkTableSurface, TkTableController, interaction_core, ExcelLikeTableController의 책임과 migration boundary를 audit함.
- docs/WORK_PLAN.md 및 315 active report 내의 사소한 문구 mismatch(archive 개수 및 lifecycle cleanup 설명)를 보정함.

### Result
- `docs/WORK_PLAN.md` 315 설명 교정 및 `result_reports/active/315_active_report_lifecycle_cleanup_after_controller_switch.md` 의 archive 갯수/rename mismatch 보정 완료.
- `result_reports/active/317_main_table_migration_check_after_controller_switch.md` 리포트 작성 완료.

### Decision
- 4개 main section에 대한 `TkTableController`로의 마이그레이션이 이미 완료되어 안정화되었으므로, 더 이상의 추가 메인 테이블 마이그레이션 작업은 불필요(보류)한 것으로 판단함.
- 다음 핵심 action은 legacy ExcelLikeTableController 퇴출 및 테스트 갭 해소를 위한 `ui_tk folder cleanup`으로 결정함.
- active report count meets lifecycle threshold criteria.

---

## 2026-06-10 — Retire legacy ExcelLikeTableController and correct test gaps

### Tried
- production main table path에서 더 이상 사용되지 않는 legacy `ExcelLikeTableController`를 안전하게 제거 (`git rm ui_tk/excel_like_table_controller.py`).
- legacy controller 전용 테스트가 검증하던 paste / undo / clear / type-replace 등의 behavior가 `TkTableController`에서 정상 동작하는지 inventory를 대조함.
- `tests/test_ui_tk_excel_like_table_controller.py` 삭제 (`git rm`) 전, 부족한 controller interactive behavior(F2, Escape, Arrow Navigation, Shift Click 등)에 대한 focused unit test를 `tests/test_ui_tk_metric_input_table_controller_parity.py`에 보강함.
- `tests/test_ui_tk_iso_table_autocalc.py`와 `tests/test_ui_tk_table_controller.py`에 남아있던 `ExcelLikeTableController` import 및 type assertion을 `TkTableController` 기준으로 정정 및 behavior assertion으로 교정함.

### Result
- `ui_tk/excel_like_table_controller.py` 및 `tests/test_ui_tk_excel_like_table_controller.py` 제거 완료.
- `tests/test_ui_tk_iso_table_autocalc.py` 및 `tests/test_ui_tk_table_controller.py` 내 legacy assertion 교정 완료.
- `tests/test_ui_tk_metric_input_table_controller_parity.py`에 interactive behavior test 추가 완료.
- `result_reports/active/318_retire_excel_like_table_controller.md` 리포트 생성 및 `317` 리포트에 closeout note 반영 완료.

### Decision
- legacy controller가 성공적으로 퇴출되고 테스트 갭 교정이 마감되었으므로 `ui_tk folder cleanup` 단계를 종결함.
- 다음 핵심 action은 `EN14825 / AHRI 210/240 / KS profile expansion` 단계로 진입하는 것으로 결정함.
- active report count meets lifecycle threshold criteria.

---

## 2026-06-10 — ui_tk batch dialog folder boundary audit before profile batch expansion

### Tried
- ISO 2-point 및 SASO T3 batch dialog 확장 전 `ui_tk` 내부의 batch dialog 관련 파일들(`hong_kong_cspf_batch_section.py`, `batch_matrix_table.py` 등)의 폴더 boundary와 MVC/SoC 책임을 audit함.
- `HongKongCspfBatchDialog`가 dialog shell로서의 책임을 갖고 `HongKongCspfBatchSection`이 section widget의 책임을 가짐을 확인하고, 폴더링 후보(A. batch_dialogs, B. dialogs/batch, C. batch)를 비교 평가함.
- dynamic toggle(SASO T3), 비교 result surface(ISO 2-point) 차이에 따른 공통화 타당성을 평가하고, profile-specific dialog 배치의 안전성을 분석함.

### Result
- `result_reports/active/319_ui_tk_batch_dialog_folder_boundary_audit.md` 리포트 생성 완료.
- `docs/WORK_PLAN.md`에 task 319 완료 상태를 반영하고, 제안된 Next Actions 흐름으로 업데이트 완료.

### Decision
- batch dialog 확장 시의 import churn 및 file pollution을 방지하기 위해 `ui_tk/batch_dialogs/` 폴더 boundary를 도입하고, `HongKongCspfBatchDialog`를 이주하는 작업(`Move HongKongCspfBatchDialog to batch_dialogs`)을 다음 implementation slice로 정함.
- active report count meets lifecycle threshold criteria.

---

## 2026-06-10 — Correct batch dialog folder boundary decision to shell + profiles composition

### Tried
- 319의 flat `ui_tk/batch_dialogs/` 폴더 결정을 재검토하고, 다수 프로필 확장 시 발생하는 Toplevel 윈도우/lifecycle 제어 코드 복사-붙여넣기 방지를 위한 `shell + profiles` composition 구조 설계를 구상 및 확정함.
- `PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` 및 `07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` 문서를 대조하여, Toplevel window lifecycle, focus, close callback, hidden-first geometry settle/show, snapshot handoff 책임을 `shell.py`로 격리하고 profile-specific 구성은 얇은 어댑터 프레임으로 제한하도록 규칙을 세움.

### Result
- `result_reports/active/319_ui_tk_batch_dialog_folder_boundary_audit.md` 리포트 보정 및 `result_reports/active/320_batch_dialog_shell_profiles_boundary_correction.md` 신규 리포트 작성 완료.
- `docs/WORK_PLAN.md`에 task 320 완료 상태 반영 및 Next Actions(shell + profiles skeleton 및 CSPF 이주) 업데이트 완료.

### Decision
- 다형성 상속 남용 없이 Composition 기반으로 `batch_dialogs/shell.py` 컨테이너와 `batch_dialogs/profiles/` 하위 어댑터 간의 책임을 양분하도록 최종 승인함.
- 다음 핵심 action은 `Batch dialog shell + profiles skeleton and Hong Kong CSPF relocation` 구현 단계로 진입하는 것으로 결정함.
- active report count meets lifecycle threshold criteria.

---

## 2026-06-10 — Build batch dialog shell + profiles skeleton and relocate Hong Kong CSPF

### Tried
- 320 설계 보정에 따라 flat batch_dialogs 구조가 아닌 `ui_tk/batch_dialogs/shell.py` (공통 Toplevel container, geometry settle, close callback, snapshot handoff 담당)와 `ui_tk/batch_dialogs/profiles/hong_kong_cspf.py` (프로필별 matrix table layout, controller 연동 담당) 구조를 실제 코드로 구현 및 이주 완료.
- `ui_tk/sections/hong_kong_cspf_section.py` 및 관련 테스트의 import 경로와 API 호출부를 최신 구조에 맞춰 정상 갱신.
- `ui_tk/sections/hong_kong_cspf_batch_section.py` 파일을 삭제 처리.
- `tests/test_ui_tk_iso_table_autocalc.py`의 `test_hong_kong_cspf_batch_opens_dialog_not_metric_tab` 테스트 및 `tests/test_ui_tk_hong_kong_cspf_matrix_migration.py` 테스트가 신규 API에 대응하도록 테스트 코드 assertion 및 mock을 교정.

### Result
- `ui_tk/batch_dialogs/shell.py` 및 `ui_tk/batch_dialogs/profiles/hong_kong_cspf.py` 생성 완료.
- `ui_tk/sections/hong_kong_cspf_batch_section.py` 파일 제거 완료.
- 관련 import 경로 갱신 및 `pytest` 검증 완료.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` 재생성 완료.
- `result_reports/active/321_batch_dialog_shell_profiles_skeleton_hk_cspf_relocation.md` 신규 리포트 생성 및 `320` 리포트 마감 note 보정 완료.

### Decision
- 공통 Toplevel lifecycle/geometry/snapshot 관리와 프로필별 뷰 구성 어댑터 간의 Composition 설계가 정상 동작함을 최종 승인 및 마감.
- 다음 핵심 action은 `ISO 2-point batch dialog implementation`으로 결정함.

---

## 2026-06-10 — Batch dialog relocation smoke closeout and private access correction

### Tried
- 321 relocation 작업 후 사용자가 수행한 manual GUI smoke 결과(Multi 입력 오픈, snapshot 복원, 추가/삭제/복사/Export CSV, debounced auto calculation 및 상태 메시지 갱신, 안착 위치/크기 등 동작 이상 없음)를 closeout 처리.
- `HongKongCspfBatchDialog.snapshot()`에서 `BatchDialogShell`의 private attribute(`_adapter`)에 직접 접근하던 구현을 보정하여, `BatchDialogShell`에 public `snapshot()` 메서드를 추가하고 `close()`와 `HongKongCspfBatchDialog.snapshot()` 모두 이 public 메서드를 사용하도록 변경.
- `result_reports/active/321_batch_dialog_shell_profiles_skeleton_hk_cspf_relocation.md` 내에 남아 있던 로컬 절대경로(`file:///Users/...`) 링크들을 repo-relative path 또는 plain path로 교정.

### Result
- `ui_tk/batch_dialogs/shell.py` 및 `ui_tk/batch_dialogs/profiles/hong_kong_cspf.py` 소스 코드 수정 완료.
- `tests/test_ui_tk_iso_table_autocalc.py`에 public snapshot method 검증 assertion 보강 완료.
- `result_reports/active/321_batch_dialog_shell_profiles_skeleton_hk_cspf_relocation.md` 파일 링크 교정 및 closeout note 반영 완료.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` 재생성 완료.
- `result_reports/active/322_batch_dialog_relocation_smoke_closeout_private_access.md` 신규 리포트 생성 완료.

### Decision
- batch dialog의 private access 제거와 사용자 manual smoke closeout을 완료함으로써 profile 확장 전 batch dialog relocation 단계를 최종 완결함.
- 다음 핵심 action은 `ISO 2-point batch dialog implementation`으로 결정함.
- active report count meets lifecycle threshold criteria.
