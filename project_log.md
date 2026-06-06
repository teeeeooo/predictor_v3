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
- 233F added batch viewport containment, but Windows smoke found mouse-wheel
  parity missing over table/cell/entry content. The failure is not only missing
  wheel validation; the UI workflow now requires checking existing normal
  surfaces as source-of-truth evidence before creating new helpers/adapters.
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
