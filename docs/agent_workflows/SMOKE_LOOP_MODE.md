# UI Smoke-loop Mode

## Role

This document owns fast iteration rules for manual UI smoke feedback loops.

Use this mode only when the user explicitly says smoke-loop mode, or when the
user asks for quick small fixes based on immediate manual UI smoke results.

## Applies To

- Tkinter/PyQt UI micro-fixes after manual smoke.
- Same-surface display, focus, scroll, selection, shortcut, spacing, or
  interaction regressions.

## Rules

- Modify source/test only.
- Do not update `docs/WORK_PLAN.md`, `project_log.md`, or
  `result_reports/memory/project_memory_seed.md`.
- Do not create a result record for an ordinary smoke-loop correction.
- Create a compact record only when the bug is repeated, non-obvious,
  platform/manual-only, cross-owner, or cannot be protected by an automated
  regression guard.
- Do not run full pytest.
- Run validation in tiers:
  - first: focused owner tests for the changed surface/controller/helper;
  - second: impacted boundary tests if the owner touches shared behavior;
  - final: import checks, py_compile, or targeted smoke guards required by the
    prompt.
- For Computer Use or onscreen GUI checks, avoid a repeated accessibility-tree
  loop:
  - run focused owner tests before the GUI action when practical;
  - use one bounded state read and the minimum keyboard/click action needed;
  - if the GUI check exposes a source bug, add/update the focused guard first,
    then rerun one bounded GUI check after the fix;
  - record extra skipped GUI checks in the terminal note instead of expanding
    the smoke loop.
- Reuse already confirmed policy context; if policy docs are needed, read only
  one short relevant section.
- Commit/push with a small, specific UI fix message.

## Exclusions

Do not use smoke-loop mode for:

- core calculator changes;
- golden/fixture/config/schema changes;
- ML/Predictor changes;
- public API or diagnostics schema changes;
- any change needing broader design or validation.

## Stable Checkpoint

When the user says the loop is stable, a follow-up checkpoint may update the
manual smoke guide or current plan only when their owned state changed. A
compact record still requires a normal Result Record trigger.
