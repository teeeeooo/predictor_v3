# 179-a Workflow Tokenization Guard Update

## Goal

Reduce token-heavy UI smoke-loop churn and clarify that window geometry policy values belong in layout/token owners, not app shell modules.

## Modified Files

- `AGENT_TASK_ROUTER.md`
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/179a_workflow-tokenization-guard-update.md`

## Key Decisions

- UI manual-smoke micro-fixes may use smoke-loop mode: source/test only, no WORK_PLAN/report/project_log/memory seed, no full pytest, focused tests only, commit/push still required.
- Once the user confirms the smoke loop is stable, stable checkpoint mode can briefly update manual smoke guide, WORK_PLAN, and result report.
- Agents should follow a diff/read budget: name-only, stat, `rg`, small `sed` ranges, then narrow hunk reads; pytest detail is failure-centered.
- Window initial size, min/max size, screen margins, visible caps, and preferred visible ratios must be named constants/ratios in a layout owner such as `ui_tk/layout_constants.py`.

## Verification

- `python3 -B tools/check_code_structure.py`: passed.
- `git diff --name-only`: reviewed.
- `git diff --stat`: reviewed.
- `git diff --check`: passed.

## Next Action

Tkinter scroll wheel and geometry tokenization implementation.

## Scope Compliance

- Python source/test files were not modified.
- `project_log.md` was not modified.
- `result_reports/memory/project_memory_seed.md` was not modified.
- No lifecycle summary/archive maintenance was performed.

## Commit / Push

- Docs commit: `5ec92a2` (`docs: add ui smoke loop workflow guards`).
- Report commit: this commit (`report: workflow tokenization guard update`).
- Push: completed to `origin/work/ui-ux-ssot-adoption` through this report commit.
