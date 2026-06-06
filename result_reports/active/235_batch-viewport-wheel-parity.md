# 235 Batch Viewport Wheel Parity

## Goal

Fix Hong Kong CSPF batch dialog internal table viewport wheel scrolling so the
viewport scrolls when the pointer is over the canvas area, cell frame, editable
entry, read-only label, header, or row header.

## Scope

- Primary route: UI table/viewport correction.
- Cross-cutting gates: focused regression test, structure guard, result report,
  commit/push.
- Owner files: `ui_tk/batch_table_viewport.py` and focused viewport tests.

## Non-goals

- No 234A two-row matrix layout work.
- No batch export/copy-all/xlsx work.
- No calculator core, region config, profile registry, or golden fixture
  changes.
- No Hong Kong main notebook flicker retry.
- No UI-wide refactor or BaseSection introduction.

## Source-of-truth / Parity

- Existing main scroll owner is `ui_tk/scrollable_frame.py`.
- `ScrollableFrame` binds `<MouseWheel>`, `<Button-4>`, and `<Button-5>` on the
  Toplevel with `add="+"`, routes only events whose `event.widget` is contained
  by the scroll surface, uses `mousewheel_units(event)`, breaks handled internal
  wheel events, and unbinds stored Tcl callback ids on destroy.
- Batch viewport previously had canvas/scrollbar containment and scrollregion
  sync only. It did not bind wheel events at the Toplevel, so wheel events over
  child `Entry`/`Label`/cell widgets were not routed to the batch canvas.
- The fix reuses `mousewheel_units` and parity-aligns the same Toplevel binding,
  containment, no-overflow break, and destroy cleanup pattern inside
  `BatchTableViewport`.

## Task Results

- task 1: source-of-truth confirmed in `ScrollableFrame`.
- task 2: batch viewport now routes internal child wheel events to its canvas
  only when vertical overflow exists; external widgets are ignored; Add Row
  `scroll_to_bottom()` behavior is unchanged.
- task 3: added headless regression tests for entry/label routing, external
  ignore, no-overflow behavior, overflow delta, and unbind cleanup.
- task 4: report created; commit/push status recorded below.

## Test Results

- `python3 -B tools/check_code_structure.py`: PASS, existing warning only:
  `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC soft limit.
- `python3 -m py_compile ui_tk/batch_table_viewport.py tests/test_ui_tk_batch_table_viewport.py`:
  PASS.
- `/usr/local/py-utils/venvs/pytest/bin/python -m pytest tests/test_ui_tk_batch_table_viewport.py`:
  PASS, 4 passed.
- `/usr/local/py-utils/venvs/pytest/bin/python -m pytest tests/test_ui_tk_calculator_foundation.py`:
  PASS, 13 passed, 11 skipped.
- `/usr/local/py-utils/venvs/pytest/bin/python -m pytest tests/test_ui_tk_hong_kong_cspf_batch_spec.py tests/test_ui_tk_batch_table_controller.py`:
  PASS, 18 passed.
- `git diff --check`: PASS.
- Required exact `python3 -m pytest ...` commands: FAIL in this environment
  because `/usr/local/bin/python3` has no `pytest` module installed.

## Windows Manual Check

- Open Hong Kong CSPF batch dialog.
- Add Row until the internal viewport overflows.
- Confirm scrollbar is visible.
- Confirm wheel scroll with the pointer over: canvas empty area, table cell
  frame, editable entry, read-only result label, header, and row header.
- Confirm Add Row still scrolls to bottom.
- Confirm close/reopen keeps inputs and added rows.
- Confirm 233D first-show size/blank-space behavior does not regress.

## Changed Files

- `ui_tk/batch_table_viewport.py`
- `tests/test_ui_tk_batch_table_viewport.py`
- `result_reports/active/235_batch-viewport-wheel-parity.md`

## Known Failures / Risks

- Codex did not run Windows GUI smoke; platform behavior needs the manual check
  above.
- The default `python3 -m pytest` runner is unavailable in this container, so
  pytest verification used the available pytest venv.

## Documentation Sync

- `project_log.md`: not needed; this is a local parity correction using an
  existing source-of-truth pattern, not a new durable project decision.
- `docs/WORK_PLAN.md`: not needed; no next-action or execution-order change.
- `docs/REFACTOR_PLAN.md`: not needed; no refactor candidate or split strategy
  change.
- `project_brief.md`: not needed; no new-session handoff change.
- `ACTIVE_DOCUMENTS.md`: not needed; no active doc owner or relationship
  change.

## Scope Compliance

- Reused existing `mousewheel_units` and parity-aligned with `ScrollableFrame`.
- No unrelated files or forbidden calculator/config/export surfaces changed.
- No full pytest run.

## Commit / Push

- Commit: `a2e2351`
- Push: pending

## Project Memory Delta

- none
