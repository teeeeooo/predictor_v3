# 226 — Content-hugging Window Sizing Redesign Preflight

## Goal

Decide whether the current automatic window fit approach can deliver
content-hugging UX, or whether the sizing/refit implementation needs a small
redesign before another Hong Kong sizing patch.

## Windows Reproduction Conditions

- Switching from another profile back to Hong Kong still leaves lower blank
  space.
- Selecting Hong Kong again while already on Hong Kong creates a normal-sized
  view.
- Switching only CSPF/HSPF metric tabs does not resize the window.
- Opening and closing detail normalizes the height.
- Profile/detail changes visibly flicker.
- Batch dialog has some blank space too, but it is excluded from this task.

## Current Structure Analysis

`ui_tk/window_refit.py`:

- owns event-loop orchestration;
- coalesces refit requests;
- supports extra settle cycles;
- prevents duplicate/reentrant scheduling;
- does not compute geometry.

`ui_tk/window_geometry.py`:

- owns geometry calculation/application helpers;
- applies `fit_window_to_preferred_content()` as a one-shot geometry mutation;
- applies `grow_window_by_vertical_delta()` as a second possible geometry
  mutation;
- does not own scheduling, trigger registration, or measurement semantics.

`Iso16358Tab`:

- renders profile content;
- measures preferred size;
- temporarily selects hidden Hong Kong metric tabs for width protection;
- computes height from the current visible metric tab;
- calls `fit_window_to_preferred_content()`, then possibly
  `grow_window_by_vertical_delta()`, then clamps and resets scroll.

`ScrollableFrame`:

- owns canvas/content configure handling;
- updates scrollregion and scrollbar visibility;
- can change requested size after content is packed or after the canvas width
  syncs.

## Blank Space Cause Judgment

The remaining blank space is unlikely to be fixed reliably by adding more
settle cycles.

The likely path is:

1. Profile switch renders and packs Hong Kong content.
2. Nested notebook and scrollable frame continue settling requested size and
   canvas/scrollbar state.
3. The refit path can apply geometry using an intermediate requested size.
4. Later user actions, such as selecting the same Hong Kong profile again or
   toggling detail, produce another measurement after the visible content is
   stable, so the window hugs content better.

This is a content measurement / geometry application sequencing issue, not a
calculator or profile issue.

## Flicker Cause Judgment

Flicker is likely caused by multiple visible geometry mutations across a single
user action:

- the current profile content is packed/unpacked;
- `fit_window_to_preferred_content()` can resize once;
- `grow_window_by_vertical_delta()` can resize again;
- configure handlers in `ScrollableFrame` can update scrollbar/width state
  around the same time;
- later refits may resize again after content settles.

The current approach can be stable against infinite loops but still visibly
flicker because geometry is applied before the final visible content size is
known.

## Content-hugging UX Target

- Initial open uses current visible content size.
- Profile switch uses the new profile's visible content size.
- Detail open/close uses the visible detail state.
- Lower blank space is UX NG.
- Visible resize/flicker should be minimized.
- Hidden content may protect width, but should not reserve height.
- Height follows current visible content.
- Oversized content uses internal scroll.
- Window position remains on-screen and avoids unnecessary recentering.
- Refit loops must not occur.

## Option Comparison

### Option A — Continue adding settle cycles

- Pros: smallest code change.
- Cons: already insufficient; does not guarantee final visible size; can add
  latency and still flicker.
- Decision: reject as primary direction.

### Option B — Coalesce profile switch to one final fit

- Pros: reduces flicker; aligns with content-hugging UX; keeps common refit
  owner useful.
- Cons: needs a refit callback shape that measures final preferred size before
  applying geometry.
- Decision: use as part of the recommended direction.

### Option C — Split visible-content measurement from geometry mutation

- Pros: directly addresses stale size and hidden-height risk; makes tests
  easier; clarifies owner boundaries.
- Cons: slightly larger implementation slice than another local patch.
- Decision: use as part of the recommended direction.

### Option D — Fixed default window + scroll

- Pros: avoids resize/flicker.
- Cons: violates calculator content-hugging goal and can hide useful visible
  result area behind scroll.
- Decision: reject for the main calculator sizing target.

## Recommended Direction

Use a combination of Option B and Option C:

- keep the common refit owner;
- make the refit callback compute the final visible-content preferred size
  first;
- apply geometry once per refit action;
- keep hidden content out of height decisions;
- treat overflow/scroll as part of the same final fit decision instead of a
  second visible resize where possible;
- keep direct metric tab-change refit disabled until Windows smoke proves the
  profile/detail path is stable.

## 227 First Implementation Slice

Proposed task:

- `227 — content-hugging window sizing implementation first slice`

Include:

- refit callback path that measures final visible content size before applying
  geometry;
- one geometry application per profile/detail refit where possible;
- current visible content height as the height source;
- hidden metric tabs used only for width protection;
- lower blank space reduction for Hong Kong profile return;
- flicker reduction by avoiding intermediate geometry application;
- focused tests for preferred-size calculation and one-apply behavior.

Exclude:

- batch dialog sizing;
- main table migration;
- batch expansion;
- PySide/WPF/Web implementation;
- 07 policy update until implementation and Windows smoke validate the final
  behavior.

## Why No 07 Policy Update Now

The existing 07 policy already states the intended direction: visible current
content height, settled refit, no geometry loop, and scroll for overflow. The
implementation behavior has not yet been validated on Windows, so updating the
policy now would risk documenting an unproven mechanism. Policy follow-up
should happen after 227 and Windows smoke.

## Validation

- `git diff --check` — passed.
- `python3 -B tools/check_code_structure.py` — passed with the existing soft
  warning that `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git status --short` — reviewed before commit.

Not run:

- pytest — preflight/report-only task with no code/test changes.
- GUI smoke — no UI code changes.

## Next Action

Content-hugging window sizing implementation first slice.
