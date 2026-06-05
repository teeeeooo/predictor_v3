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
- Do not create `result_reports/active/` reports.
- Do not run full pytest.
- Run focused tests, import checks, py_compile, or targeted smoke guards.
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

When the user says the loop is stable, a follow-up checkpoint task may update
manual smoke guide, `docs/WORK_PLAN.md`, and a compact report.
