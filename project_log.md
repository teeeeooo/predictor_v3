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

## 2026-08-02 — Target applicability design reconciliation

### Decision

- Reject Partial-target Active model support as a product direction. Active
  artifacts must prove the full runtime Target capability; missing artifact
  capability is incompatible Active / FAIL. Preserve Candidate/Active promotion,
  explicit reload, fail-closed compatibility, reload-failure fallback, Active
  observation, and no-hot-swap semantics.
- Distinguish full Active compatibility from a Case-scoped requested execution
  subset. Actual failure for part of the requested subset on a compatible Active
  remains runtime `partial`; a not-requested Target retains N/A / not-applicable
  meaning rather than becoming a fabricated failure.
- Preserve existing ML mode-specific missing and target leakage policy. Record
  the current integration gap: the policy is established, but Predict execution
  does not yet fully consume it as a Case-scoped requested Target contract. This
  documentation decision implements no source behavior.
- Derive future applicability from canonical raw user input before zero-fill or
  preprocessing, distinguish blank from numeric `0`, negative, and non-numeric
  invalid values, keep mode-independent Targets common to runnable Cases, and
  determine EER/COP independently from requested mode and accepted power outcome.
- Leave the both-capacities-blank execution/validation UX unresolved for a small
  product decision before implementation.
- Set the authoritative order to documentation reconciliation → read-only
  Case-Scoped Target Applicability Owner Audit → separate Lane C source
  correction → fresh independent exact-head audit and Close → independent Narrow
  Viewport Result Review Pinning → separately approved deferred work. This
  decision supersedes the earlier close-time gate description.

## 2026-08-02 — Predict input workflow broad overhaul completion

### Decision

- Close Predict overhaul Slices 1–6 after independent exact-head Lane C audits
  and guarded merges. The delivered boundary now includes stable identity, typed
  result/execution provenance, EER/COP enrichment, Result Review, shared Layout B,
  and one canonical bulk-paste transaction.
- The repaired bulk transaction preserves final-combination Mapping/autofill,
  current row issue truth, atomic rollback, affected-only result invalidation,
  and fail-closed compound undo across ordinary authoring chronology.
- Preserve the audit lesson that a canonical transaction is not complete unless
  its adjacent authoring projections and undo authorization remain synchronized
  with current canonical state.
- This close authorized no immediate successor source slice. Target applicability
  is now reconciled by the decision above; narrow-viewport pinning, export, and
  future multi-point Predict-to-Calculate integration remain separately gated.

## 2026-07-31 — Predict overhaul product and integration boundary approval

### Decision

- Approve Layout B: Input Authoring and Result Review each use the full shared
  workspace while reading one canonical session and stable `case_id` selection
  in standalone and embedded Predict. Do not restore the legacy split table,
  add a persistent detail panel, or create a separate Full Context surface.
- Approve the default review sequence as Case → 상태 → 냉방능력 → 난방능력 →
  `사양 요약` → EER → COP → 냉방 주파수 → 난방 주파수 → 냉매량. Compose the
  single summary column by stable feature identity and active-generation
  labels/values; keep its grouping and presentation under Predict.
- Keep cooling/heating power as canonical hidden source results. Calculate
  EER/COP in a Qt-free Predict enrichment seam, not as ML targets or generic
  Feature formulas. Do not expose CSPF/HSPF2 until a future multi-point
  Predict-to-Calculate contract provides real capability.
- Reuse the existing Feature Manager, Data Mapping, Train/model lifecycle,
  prediction execution, and Calculate owners. Add separate Predict seams for
  stable identity, typed result/execution context, enrichment, Result Review
  projection, shared workspace state, and bulk input transaction.
- Sequence implementation as identity → typed result/context → EER/COP →
  Result Review → shared Layout B, with bulk paste as a separate slice and
  Calculate integration as a future workstream. Preserve target-set, stale-result,
  precision, summary formatting, hidden-source copy/export, and narrow-viewport
  pinning choices as open compatibility gates.
- This decision records an implementation boundary only. No source, schema,
  result-contract, UI, formula, or Lane C Build work starts in this documentation
  commit.

## 2026-07-31 — Predict overhaul product direction and mock baseline

### Decision

- Preserve expected input usage as approximately 70% Excel paste and 30%
  on-screen dropdown authoring, with both paths first-class and the initial paste
  contract limited to headerless value-only TSV in active Predict input order.
- Treat bulk paste as one staged transaction with final-combination cascade,
  validation, bounded refresh, and compound undo. Keep single-edit local feedback
  separate from aggregate bulk feedback.
- Reject the fixed six-column Result Review proposal because it cannot preserve
  case-configuration distinguishability across Evap index, FIN/PI/ROW, and
  expansion-device differences.
- Derive Result Review from the Feature Manager / Data Definition active
  generation while keeping Predict-specific compact review preference a Predict
  presentation concern unless a later owner decision changes that boundary.
- Keep Compact and Full Context, Result Review reveal behavior, and layout
  candidates open until comparable disposable PySide6 mock evidence exists.
- Sequence the work as documentation → mock comparison → user decision → explicit
  implementation boundary and Lane C Build handoff. This decision starts no
  prototype or production source implementation.

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
