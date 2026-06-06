# 233A — Mapped-Surface Sizing Flow and Measurement Snapshot Preflight

## Goal

Compare the working and failing Hong Kong sizing flows before implementation.
The objective is to define a reusable shell/form lifecycle slice rather than
copying a local behavior that happens to recover the window size.

## Checked Files / Ranges

- `result_reports/active/229_tk-content-hugging-shell-template.md`
- `result_reports/active/232_tk-visible-content-measurement-adapter.md`
- `result_reports/summaries/231_summary-architecture-uiux-boundary-and-window-refit-arc.md`
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`
- `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
- `ui_tk/tabs/iso16358_tab.py`
  - `_on_mode_changed`
  - `_render_mode`
  - `_render_region`
  - `_on_trace_visibility_changed`
  - `_schedule_toplevel_refit`
  - `_fit_toplevel_to_current_content`
- `ui_tk/window_measurement.py`
- `ui_tk/window_shell.py`
- `ui_tk/window_refit.py`
- `ui_tk/window_geometry.py`
- `ui_tk/scrollable_frame.py`
- `ui_tk/sections/hong_kong_cspf_section.py`
- `ui_tk/sections/hong_kong_hspf_section.py`
- `docs/WORK_PLAN.md`
- recent `project_log.md`

## Flow Comparison

| Flow | Lifecycle | Current fit trigger | Measurement state | Judgment |
|---|---|---|---|---|
| A. Other profile -> Hong Kong | `_on_mode_changed` -> `_render_mode` -> previous frames `pack_forget` -> `_render_region` destroys/recreates metric tabs and sections -> Hong Kong frame `pack` -> scheduler refit | `_schedule_toplevel_refit(settle_cycles=2)` after render | New metric tabs/sections can still be settling; canvas bbox, scrollregion, scrollbar visibility, and auto-calc result layout may not share one stable snapshot | Failing flow. It measures after render, but does not guarantee preferred size and overflow delta come from the same mapped/configured surface snapshot. |
| B. Hong Kong reselect while already on Hong Kong | `_on_mode_changed` -> `_render_mode` re-renders Hong Kong while the Hong Kong surface/root already has the same general mapped context -> scheduler refit | Same scheduler path | Root/canvas/notebook have already seen Hong Kong geometry and scroll state before re-render | Working recovery flow. This is useful evidence, but not safe as a source of truth because it relies on prior mapped state. |
| C. CSPF detail open/close | detail panel `grid`/`grid_remove` on already mapped CSPF surface -> callback -> scheduler refit | `_on_trace_visibility_changed` -> `_schedule_toplevel_refit()` | Surface is already mapped; configure/scrollregion events have a simpler delta from current content | Working flow. This is the cleaner lifecycle pattern: mapped surface, explicit user state change, settle, measure, fit. |

## Cause Judgment

The confirmed problem is not that the geometry primitive cannot shrink the
window. The problem is that profile switch-in can measure a newly mapped,
nested surface before all relevant layout owners have reached one consistent
snapshot.

The decisive difference is mapped state:

- detail toggle and Hong Kong reselect operate after the Hong Kong surface has
  already been mapped/configured at least once;
- other-profile-to-Hong-Kong creates/destroys metric tabs and sections, then
  packs the Hong Kong frame and schedules a refit from a newly mapped state.

Normal behavior should not be copied as "select Hong Kong twice" logic. It
should be translated into a reusable mapped-surface lifecycle:

1. render content;
2. mount/map the selected surface;
3. let layout settle;
4. measure one snapshot;
5. fit from that snapshot.

## Measurement Snapshot / Stale Overflow Judgment

Current `TkContentHuggingForm.fit()` calls:

1. `preferred_size_provider()`;
2. `overflow_provider()`;
3. shell geometry apply.

Those providers are separate calls. `TkVisibleContentMeasurement.preferred_size`
updates the content and temporarily selects hidden notebook tabs for width
protection. `vertical_overflow_delta` then reads `ScrollableFrame.canvas.bbox`
and `canvas.winfo_height()` independently.

This means preferred size and overflow delta are not guaranteed to come from
the same settled layout snapshot.

Specific risks:

- `ScrollableFrame._on_content_configured` updates `scrollregion` from canvas
  bbox, but profile switch-in can still be in configure churn when measurement
  runs.
- `vertical_overflow_delta()` can read a stale canvas height or bbox from the
  previous profile or an intermediate mapped state.
- `window_shell.visible_content_fit_geometry()` always adds positive overflow
  to target height. During shrink/profile-switch paths, stale overflow can
  preserve lower blank space instead of allowing the window to hug current
  content.
- 07 policy says overflow belongs inside the content viewport through
  scrolling. The current "preferred height + overflow" policy is acceptable
  only when overflow is known to reflect the same snapshot and is explicitly
  wanted for a fit path.

Conclusion: 233B should introduce a measurement snapshot contract. Preferred
size and overflow must be read together after one settled layout update, and
profile switch shrink fits should not blindly add stale overflow.

## MVC / Clean Architecture Boundary Evaluation

### View

`Iso16358Tab` is improved after 232 but still orchestrates too much lifecycle:

- render mode;
- destroy/create metric tab sections;
- pack the selected surface;
- choose settle cycles;
- request refit.

It no longer owns the measurement math, but it still implicitly owns
render/mount/settle/measure/fit ordering.

### Shell / Form

`window_shell.py` is a reusable content-hugging shell template, but its current
provider shape is split into preferred-size and overflow providers. It does not
own a single "measurement snapshot" concept and therefore cannot know whether
both values are from the same layout state.

### Adapter

`window_measurement.py` is the right owner for Tk-specific measurement:

- nested notebook hidden-width protection;
- visible tab height;
- canvas/scroll overflow;
- suppressing measurement-induced tab-change refits.

It should likely return a single snapshot object rather than separate preferred
size and overflow values.

### Controller / Orchestrator

The next missing owner is lifecycle orchestration:

- render;
- mount/map;
- settle;
- snapshot measure;
- fit.

This could be a small shell/form lifecycle method or helper rather than a large
new controller. The key is that profile switch, profile reselect, and detail
toggle use the same lifecycle semantics.

### Policy

No 07 policy change is needed before implementation. The current policy already
requires:

- hidden tabs affect width protection, not height reservation;
- profile switches, nested tab switches, and detail open/close use the same
  refit scheduling policy;
- measurement and mutation must not create configure loops;
- overflow belongs inside the content viewport through scrolling.

The implementation gap is snapshot/lifecycle ownership, not policy wording.

## Extensibility Risk Evaluation

| Scenario | Current flow risk | 233B handling |
|---|---|---|
| Another nested notebook is added | High. Current measurement knows one notebook. | Keep first slice to one nested notebook but design snapshot API so additional adapters can compose later. |
| Lazy-rendered panel in notebook | High. Preferred size may be read before lazy content is mapped. | Lifecycle must settle after mount before snapshot measure. |
| Dialog/popup trigger inside notebook | Medium. Dialog should not affect main window snapshot unless registered as content. | Exclude from 233B; document as future shell consumer boundary. |
| Very large detail panel | Medium. Overflow should scroll, not force unbounded height. | Snapshot should support overflow policy by fit mode. |
| Large height differences between tabs | High. Hidden height must not reserve visible height. | Preserve current visible tab height rule. |
| Scrollbar show/hide configure loop | High. Stale overflow and scrollbar visibility can feed geometry changes. | Snapshot measure should update idletasks once and read bbox/canvas height together. |
| Auto-calc/result update after render | Medium. CSPF/HSPF constructors flush auto-calc immediately, but delayed updates can still occur later. | 233B should test a delayed result/update candidate or leave explicit instrumentation. |
| Future GUI framework | Medium. Same lifecycle applies, but toolkit APIs differ. | Keep lifecycle contract toolkit-neutral; Tk adapter implements concrete measurement. |

## 233B Implementation Slice

Recommended task:

**233B — mapped-surface measurement snapshot lifecycle first slice**

Include:

- Add a measurement snapshot data shape, e.g. `VisibleContentSnapshot` with
  preferred size, overflow delta, and snapshot/source diagnostics.
- Make `TkVisibleContentMeasurement` expose a single snapshot method that
  updates the content/layout once, measures nested notebook width/current
  visible height, and reads scroll overflow in the same snapshot.
- Change `TkContentHuggingForm` / shell registration to accept a snapshot
  provider or equivalent while preserving compatibility where practical.
- Add a fit mode or policy so profile switch shrink paths do not blindly add
  positive overflow from stale/intermediate state. The conservative first slice
  should include overflow in initial/detail expand paths only when snapshot
  evidence says it is current.
- Route profile switch, Hong Kong reselect, and detail toggle through the same
  render/mount/settle/snapshot-measure/fit lifecycle helper.
- Add fake-surface tests for:
  - preferred size and overflow read from one snapshot;
  - hidden tab width but current visible tab height;
  - profile switch fit ignores stale prior overflow;
  - detail toggle still allows legitimate visible detail growth;
  - no direct metric tab-change refit loop.

Exclude:

- Hong Kong-only branches;
- direct metric tab-change refit reintroduction;
- settle-cycle-only changes;
- batch dialog sizing;
- main table migration;
- UI/UX or architecture policy rewrites.

If this is still too large, split:

- 233B: snapshot provider and shell fit API compatibility.
- 233C: lifecycle orchestration unification for profile switch/detail toggle.

## Excluded Scope

- No UI code changes.
- No tests changed.
- No settle cycles added.
- No Hong Kong-only branch.
- No direct metric tab-change refit.
- No adapter implementation changes.
- No policy document updates.
- No report lifecycle/archive work.

## Validation

- `git diff --check`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git status --short`: expected WORK_PLAN, project_log, and report changes
  only.

Not run:

- `pytest`: preflight/report-only task.
- GUI smoke: no UI code changes.

## Next Action

Mapped-surface measurement snapshot lifecycle first slice.
