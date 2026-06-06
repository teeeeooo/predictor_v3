# 236 Summary - Window/Dialog/Batch Viewport Arc

## Covered Reports

Archived by this summary:

- `229_tk-content-hugging-shell-template.md`
- `231_result-report-lifecycle-cleanup-after-architecture-uiux-arc.md`
- `232_tk-visible-content-measurement-adapter.md`
- `233a_mapped-surface-sizing-flow-and-measurement-snapshot-preflight.md`
- `233b_visible-measurement-snapshot-contract.md`
- `233c_prep_work-plan-execution-order-update.md`
- `233c_profile-reselect-detail-lifecycle-orchestration.md`
- `233c2_hong-kong-profile-switch-reuse-cache.md`
- `233c_closeout_hidden-first-window-dialog-policy.md`
- `233d_batch-dialog-sizing-ux.md`
- `233e_batch-dialog-state-persistence.md`
- `233e_closeout_stateful-input-dialog-lifecycle.md`
- `233f_batch-table-viewport-scroll-containment.md`
- `233f_guard_ui-source-of-truth-and-soft-loc-preflight.md`
- `234_ui-surface-workflow-router-slimming.md`
- `235_batch-viewport-wheel-parity.md`

Reports intentionally kept active:

- none. The next batch two-row matrix layout preflight can use this summary,
  `docs/WORK_PLAN.md`, and the archived source reports if deeper evidence is
  needed.

## Completed Work

- Promoted the Tk content-hugging shell/form API into a reusable owner with
  provider registration and after-fit hooks.
- Extracted visible content measurement from `Iso16358Tab` into a Tk
  measurement adapter/provider consumed by the shell template.
- Established a visible measurement snapshot contract so preferred size and
  overflow delta are read from one settled snapshot before geometry apply.
- Unified profile switch, profile reselect, and detail toggle around one
  visible-surface lifecycle refit path.
- Reused the already-rendered Hong Kong metric surface when returning to Hong
  Kong from another profile with the same region.
- Documented hidden-first first-show and stable-container dynamic lifecycle
  policy for future windows, dialogs, Toplevels, and profile/page surfaces.
- Applied hidden-first content-measured first-show sizing to the Hong Kong CSPF
  batch dialog.
- Preserved Hong Kong CSPF batch row/input state across close/reopen by storing
  a session-local snapshot in the parent section.
- Contained the Hong Kong CSPF batch table in an internal vertical viewport.
- Corrected batch viewport mouse-wheel parity by reusing the main scroll
  source-of-truth pattern for Toplevel binding, containment routing,
  `mousewheel_units`, no-overflow break, and destroy cleanup.
- Moved route-specific workflow detail out of `AGENT_TASK_ROUTER.md` into
  `docs/agent_workflows/*` owner documents.

## Important Decisions

- Repeated window sizing and dynamic-surface smoke failures should trigger
  owner-boundary judgment before adding more local settle-cycle patches.
- Window/dialog first show should prefer hidden-first build, settle, measure,
  geometry apply, then show.
- Closing a stateful input dialog is not reset/clear; reset/clear must be an
  explicit user action.
- Batch layout should next evaluate a unified case-level two-row matrix shape:
  capacity/performance input row plus power input row.
- Batch result columns are actual profile output metrics, not a mandatory
  Status column. Hong Kong CSPF outputs remain CSPF and CSEC.
- Table/viewport work must check an existing working surface as
  source-of-truth evidence before introducing a new helper or adapter.
- Soft LOC limits are preflight triggers for owner-boundary and helper
  extraction judgment, not hard line-count-only rules.
- Completed reports should not try to self-record the commit hash of a commit
  that includes the same report; final pushed hash and push result belong in
  the final response when self-reference would create a hash/update loop.

## Windows / Manual Smoke Results

- Hong Kong lower blank space is resolved and the refit loop remains gone.
- Remaining profile/detail flicker is accepted for this arc unless future smoke
  identifies a specific visible mutation owner.
- Hong Kong CSPF batch dialog first-show sizing is accepted as not regressed
  after hidden-first sizing.
- Batch close/reopen state persistence is accepted for the current session
  scope.
- Batch Add Row viewport containment is accepted.
- Batch mouse-wheel scrolling is OK with the pointer over canvas empty area,
  table/cell frame, editable entry, read-only result label, header, and row
  header.

## Known Accepted Limitations

- Further flicker reduction would require a larger hidden/offscreen first-show
  or stable-container lifecycle slice and is not part of the next batch layout
  preflight.
- Batch export/copy-all and xlsx export were intentionally not implemented in
  this arc.
- The current Hong Kong batch table is still row-per-case; two-row matrix
  layout remains the next design/preflight task.
- HSPF detail/bin, EN14825, AHRI, KS profile expansion, main table migration,
  and ui_tk cleanup remain follow-up work after the batch foundation direction
  is decided.

## Remaining Next Actions

1. Batch two-row matrix layout preflight.
2. Common two-row batch table foundation if the preflight accepts the shape.
3. Batch copy-all / CSV export parity using existing clipboard/CSV helper
   direction; xlsx export stays deferred.
4. Result/detail/export common contract check before further profile expansion.
5. Main table migration candidate check and later ui_tk folder cleanup.

## Archived / Moved Reports

Moved to `result_reports/archive/`:

- `229_tk-content-hugging-shell-template.md`
- `231_result-report-lifecycle-cleanup-after-architecture-uiux-arc.md`
- `232_tk-visible-content-measurement-adapter.md`
- `233a_mapped-surface-sizing-flow-and-measurement-snapshot-preflight.md`
- `233b_visible-measurement-snapshot-contract.md`
- `233c_prep_work-plan-execution-order-update.md`
- `233c_profile-reselect-detail-lifecycle-orchestration.md`
- `233c2_hong-kong-profile-switch-reuse-cache.md`
- `233c_closeout_hidden-first-window-dialog-policy.md`
- `233d_batch-dialog-sizing-ux.md`
- `233e_batch-dialog-state-persistence.md`
- `233e_closeout_stateful-input-dialog-lifecycle.md`
- `233f_batch-table-viewport-scroll-containment.md`
- `233f_guard_ui-source-of-truth-and-soft-loc-preflight.md`
- `234_ui-surface-workflow-router-slimming.md`
- `235_batch-viewport-wheel-parity.md`

Kept active:

- none.

## Project Memory Seed Sync Judgment

- Update the source summary list with this summary.
- Mark the previous `Tk visible content measurement adapter extraction` open
  question as superseded/resolved by the 232-235 arc.
- Add one summary-level entry for the completed window/dialog/batch viewport
  arc and next batch two-row preflight boundary.
- Do not add per-report movement facts to memory seed.
