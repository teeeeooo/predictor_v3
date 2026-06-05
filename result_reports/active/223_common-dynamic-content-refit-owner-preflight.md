# 223 — Common Dynamic Content Refit Owner Preflight

## Goal

Decide whether dynamic/nested content refit should remain inside individual
tabs or move to a common owner, then define the next implementation slice.

## Checked Files And Documents

- `result_reports/active/221c_dynamic-content-refit-loop-stabilization.md`
- `result_reports/active/222_result-report-lifecycle-cleanup.md`
- `result_reports/summaries/221_summary-post-main-table-window-refit-arc.md`
- `result_reports/memory/project_memory_seed.md`
- `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`
- `docs/WORK_PLAN.md`
- `ui_tk/window_geometry.py`
- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/scrollable_frame.py`

## Current State

Resolved:

- 221C stopped the Hong Kong profile infinite resize/refit loop.
- Direct metric notebook tab-change refit is disabled.
- Selected-range fill paste remains resolved from 220.

Unresolved:

- Hong Kong CSPF lower blank space remains.
- Nested metric tab-change refit cannot be safely reintroduced as a local
  `Iso16358Tab` patch.
- Common table foundation exists, but calculator main table migration is not
  part of this decision.

Next decision target:

- whether a common dynamic content refit owner is required before further Hong
  Kong sizing fixes.

## Current Owner Boundary

`ui_tk/window_geometry.py` currently owns geometry calculation/application
helpers:

- parse/format geometry;
- content-based initial/fitted geometry;
- vertical-only visible-bounds clamp;
- one-shot `fit_window_to_preferred_content()`;
- one-shot overflow growth.

It does not own event scheduling, trigger registration, suppression, or running
guards.

`Iso16358Tab` currently owns too many dynamic refit responsibilities:

- profile switch trigger;
- detail visibility trigger;
- region change trigger;
- settled refit scheduling;
- pending guard;
- preferred-size measurement for hidden Hong Kong metric tabs;
- measurement suppress guard;
- overflow growth;
- scroll reset.

`ScrollableFrame` owns viewport mechanics:

- content/canvas configure handling;
- scrollregion updates;
- auto-hide scrollbar;
- vertical overflow delta;
- scroll reset.

It can affect refit results because content settle, scrollbar visibility, and
canvas width sync happen on configure paths. It should not become the window
fit owner, but refit scheduling must account for its delayed settle behavior.

## Toolkit-neutral Judgment

This is not a Hong Kong-only or Tkinter-only issue. The same structure can
repeat whenever a UI combines:

- nested notebooks or sub-tabs;
- stacked panels;
- collapsible/detail surfaces;
- scrollable content viewports;
- automatic window fitting.

The 07 window geometry policy is sufficient as policy, but the code lacks an
owner that implements the policy boundary. Individual tabs should not each
invent trigger coalescing, measurement suppression, running guards, and
settled-refit semantics.

## Option Comparison

### Option A — Keep `Iso16358Tab` local patch

- Pros: smallest immediate code diff.
- Cons: keeps scheduling, measurement, and mutation mixed in one tab; already
  caused a Windows loop; likely repeats for future EN/AHRI/KS or other nested
  surfaces.
- Decision: reject.

### Option B — Add scheduler to `ui_tk/window_geometry.py`

- Pros: reuses existing geometry module.
- Cons: blurs pure geometry helper responsibility with widget lifecycle,
  trigger registration, suppress guards, and event-loop scheduling.
- Decision: reject as default. Keep `window_geometry.py` focused on geometry
  math/application helpers.

### Option C — Add `ui_tk/window_refit.py` common owner

- Pros: separates dynamic refit orchestration from geometry math and tab
  composition; can own coalescing, pending/running guard, settled refit,
  suppress guard, and trigger registration; easier to fake-test.
- Cons: new owner file and small integration slice needed.
- Decision: recommended.

### Option D — Hotfix only lower blank space

- Pros: fastest if a local constant/measurement tweak happens to work.
- Cons: bypasses the loop lesson; likely reopens the same class of bug.
- Decision: reject unless a future emergency smoke-loop task needs a temporary
  rollback.

## Recommended Direction

Implement a common Tk dynamic content refit owner first. The owner should sit
next to window geometry helpers but keep a different responsibility:

- `ui_tk/window_geometry.py`: geometry calculation/application;
- new `ui_tk/window_refit.py`: event-loop refit orchestration and guards;
- tabs/sections: declare triggers and preferred-size callbacks.

This is a Tkinter implementation of the toolkit-neutral 07 policy. PySide/WPF
or Web can later use equivalent adapter/service concepts without sharing the Tk
module.

## 224 First Implementation Slice

Proposed task:

- `224 — common dynamic content refit owner first slice`

Allowed implementation candidates:

- new `ui_tk/window_refit.py`;
- focused tests, for example `tests/test_ui_tk_window_refit.py`;
- minimal `ui_tk/tabs/iso16358_tab.py` integration;
- `docs/WORK_PLAN.md` and task report.

Include:

- coalesced refit scheduler;
- pending/running guard;
- settled refit callback sequencing;
- suppress guard context for measurement;
- trigger helpers for profile/detail/region and future nested tab changes;
- fake owner tests for duplicate scheduling, reentrant calls, suppress guard,
  and settled sequencing;
- move existing `Iso16358Tab` profile/detail/region scheduler path onto the
  common owner;
- keep direct metric tab-change refit disabled until the owner has passing
  tests and Windows smoke.

Exclude:

- main table migration;
- batch expansion;
- PySide/WPF/Web implementation;
- large `ui_tk` cleanup;
- changes to calculator formulas, region config, fixture/golden, or table
  foundation.

Windows smoke after 224 should verify:

- no Hong Kong profile resize loop;
- CSPF lower blank space behavior;
- profile switch back to Hong Kong;
- CSPF/HSPF metric tab switching if reintroduced;
- detail open/close;
- batch dialog sizing and selected-range fill paste unchanged.

## Validation

- `git diff --check` — passed.
- `python3 -B tools/check_code_structure.py` — passed with the existing soft
  warning that `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git status --short` — reviewed before commit.

Not run:

- pytest — preflight/report-only task with no code or test changes.
- GUI smoke — no UI code changes.

## Next Action

Common dynamic content refit owner first slice.
