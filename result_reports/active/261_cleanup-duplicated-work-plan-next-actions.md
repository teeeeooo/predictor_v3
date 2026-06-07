# 261 Clean Up Duplicated WORK_PLAN Next Actions

## Goal

Remove a duplicated Next Actions item in WORK_PLAN.md after summary 260 closeout.

## Change

- Removed duplicate `ui_tk folder cleanup` item #2 that repeated the Main table migration description.
- Renumbered remaining items: Main table migration (#1), ui_tk folder cleanup (#2), EN/AHRI/KS expansion (#3).

## Excluded Scope

- No code, tests, architecture docs, or memory seed changes.
- No project_log.md changes (micro-cleanup, no durable decisions).
- No summary 260 changes.

## Validation

- `git diff --check`: clean
- `git status --short`: 1 file modified

## Next

Main table migration candidate check (design-gated analysis).
