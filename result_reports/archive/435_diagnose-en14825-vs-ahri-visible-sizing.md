# 435 Diagnose EN14825 vs AHRI Visible Sizing

## Goal

Compare EN14825 and AHRI visible-content measurements, reproduce the remaining
AHRI lower-white-space behavior after 434, and identify the correction owner
without changing production sizing.

## Scope

- Compare both tab sizing/refit/measurement/scroll flows.
- Add a focused diagnostic collector covering metric round trips and HSPF2
  Batch open/close.
- Record measured values, root cause, 434 disposition, and a correction
  proposal.

## Non-goals

- No production sizing, geometry/minsize, table dimensions/tokens, calculator,
  A2/source, batch label, core/config/fixture/golden, EN14825, or AHRI behavior
  change.

## Changed Files

- `tests/test_ui_tk_visible_sizing_diagnostics.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/435_diagnose-en14825-vs-ahri-visible-sizing.md`

## Sizing Flow Comparison

Both tabs use `preferred_initial_size -> TkVisibleContentMeasurement.snapshot`,
`fit_toplevel_to_current_content_once -> TkContentHuggingForm.fit`, the same
`ScrollableFrame`, and scheduler-backed metric refits. Both nested notebooks
build all metric children before the first measurement and therefore report a
requested size based on the largest child.

The relevant difference after 434 is only AHRI's top-level visibility gate and
two settle cycles. That correctly suppresses hidden/early refits, but it does
not change either the nested notebook requested size or the cached chrome
estimate. It therefore cannot remove white space already encoded in the
snapshot and notebook allocation.

## Collected Diagnostics

Values below were collected on macOS by the focused Tk diagnostic after each
explicit content fit. Sizes are width x height in pixels.

| State | Root | Snapshot | Content req | Current tab req | Nested notebook req | Chrome estimate | Overflow | Canvas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EN SEER | 803x973 | 803x973 | 1309x955 | 689x807 | 1301x947 | 54x140 | 44 | 734x911 |
| EN SCOP | 1389x1008 | 1389x1051 | 1309x955 | 1247x885 | 1301x947 | 54x140 | 9 | 1320x946 |
| EN SEER return | 803x973 | 803x973 | 1309x955 | 689x807 | 1301x947 | 54x140 | 44 | 734x911 |
| AHRI SEER2 | 999x723 | 999x723 | 1215x705 | 876x332 | 1207x697 | 54x365 | 44 | 930x661 |
| AHRI HSPF2 | 1290x1008 | 1290x1026 | 1215x705 | 1153x635 | 1207x697 | 54x365 | 0 | 1236x946 |
| AHRI SEER2 return | 999x723 | 999x723 | 1215x705 | 876x332 | 1207x697 | 54x365 | 44 | 930x661 |
| HSPF2 Batch open | 999x723 | 1290x1026 | 1215x705 | 1153x635 | 1207x697 | 54x365 | 44 | 930x661 |
| HSPF2 Batch close | 999x723 | 1290x1026 | 1215x705 | 1153x635 | 1207x697 | 54x365 | 44 | 930x661 |
| SEER2 after Batch | 999x723 | 999x723 | 1215x705 | 876x332 | 1207x697 | 54x365 | 44 | 930x661 |

The test also emits compact JSON with top-notebook size and scrollregion bbox
when run with `pytest -s`.

## Root Cause Judgment

- **Measurement value is oversized: yes.** On first AHRI measurement,
  `nested_notebook_height - current_tab_height` is `697 - 332 = 365`. The
  cached `chrome_height_estimate` therefore contains the 303px HSPF2-versus-
  SEER2 child-height difference in addition to real notebook chrome.
- **Nested notebook requested-height stickiness: primary cause.** The notebook
  stays at 697px for both AHRI metrics because both children already exist. A
  SEER2 frame with a 332px request expands inside that allocation, producing
  the visible lower blank area.
- **ScrollableFrame viewport feedback: secondary symptom, not cause.** Content
  requested height remains 705 in every AHRI state. After the smaller SEER2 fit
  the 661px canvas produces a stable 44px overflow; it does not increase the
  content/notebook request.
- **ResultPanel/section pack-grid: not supported as cause.** The selected child
  requests are stable and differ coherently by metric; no state-dependent
  section growth appears on return.
- **Batch open/close: not a cause.** Root geometry, content request, nested
  request, chrome estimate, and canvas size are identical before/after close.

EN14825 has the same estimator weakness (`947 - 807 = 140` for SEER), but its
visible-child height delta is much smaller and screen-height capping masks most
of the effect. Its successful appearance is therefore not evidence that the
estimator is correct.

## 434 Disposition

Keep 434. Its selected-surface gate prevents hidden construction events from
fitting the root and its settled request is the correct lifecycle boundary.
Reverting it would reintroduce stale/hidden fits while leaving the contaminated
chrome estimate and sticky notebook allocation unchanged.

## Correction Proposal (Not Implemented)

Use the 434 visible lifecycle to synchronize the AHRI notebook requested height
to the selected metric's settled requested height before taking the snapshot;
derive notebook chrome from settled mapped allocation/current child allocation,
not `max-child notebook reqheight - current child reqheight`. Keep this
profile-local first and prove SEER2 -> HSPF2 -> SEER2 replacement plus no-loop
behavior. If the same correction is later required elsewhere, extract it into
the existing measurement/lifecycle owner rather than adding fixed heights or
settle-cycle patches.

## Verification

- `python3 -B -m pytest -s tests/test_ui_tk_visible_sizing_diagnostics.py`
  — 1 passed; nine compact state records collected.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Manual Check

Computer Use opened and read the local calculator window, confirming the live
Tk application was available. Tk notebook tabs were not exposed in the
accessibility tree and pointer switching was not reliable, so metric visual
smoke remains required. The automated live-widget collector supplied all
requested geometry/snapshot/canvas values.

## Known Risks

- Pixel values vary by Tk theme, display scale, and screen cap; the diagnostic
  test asserts state relationships rather than exact pixels.
- A correction must address notebook allocation as well as snapshot arithmetic;
  changing only the root target could turn blank space into clipping/scrolling.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: not_required
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed this
  session; reason: applicable diagnostic/report gates.
- `result_reports/memory/project_memory_seed.md`: window-refit topics only;
  reason: 233B/233C superseding evidence.
- `result_reports/summaries/236_summary-window-dialog-batch-viewport-arc.md`:
  completed-work and decision sections; reason: snapshot/lifecycle policy.
- EN14825 and AHRI tab files: sizing/measurement/refit ranges only; reason:
  side-by-side flow comparison.
- `window_measurement.py`, `window_refit.py`, `window_shell.py`, and
  `scrollable_frame.py`: relevant measurement/scheduler/viewport ranges only;
  reason: causal boundary.
- focused existing sizing tests: matching snapshot/geometry ranges only;
  reason: diagnostic test style and invariant selection.
- `docs/WORK_PLAN.md`: current slice range; reason: next-action sync.
- broad read: none
- repeated read: none

## Next Action

AHRI sizing correction implementation.
