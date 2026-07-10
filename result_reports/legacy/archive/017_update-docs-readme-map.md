# Update Docs README Map

## Goal

Update `docs/README.md` so its document map and agent document-work guidance match the current docs/router structure.

## Scope

- Update only `docs/README.md` for the source documentation change.
- Keep existing standard-specific document structure explanation.
- Do not edit `AGENTS.md`, `AGENT_TASK_ROUTER.md`, `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md`, `project_log.md`, code, tests, or model artifacts.

## Changed Files

- `docs/README.md`: added `WORK_PLAN.md` and `REFACTOR_PLAN.md` roles, added `docs/architecture/`, `docs/knowledge/`, and `docs/archive/` area guidance, clarified WORK_PLAN vs REFACTOR_PLAN roles, and changed agent document-work guidance to conditional router-based reading.
- `result_reports/active/017_update-docs-readme-map.md`: compact result report for this docs-only task.

## Verification

- `git diff -- docs/README.md`: reviewed.
- `git diff --name-only`: showed `docs/README.md` plus pre-existing unrelated ` AGENTS_md_slimming_plan.md` deletion.
- `git diff --cached --name-only` before source commit: `docs/README.md` only.
- `rg -n "WORK_PLAN|REFACTOR_PLAN|architecture|knowledge|archive|AGENT_TASK_ROUTER|FORMULA_REFERENCE_GUIDE" docs/README.md`: verified requested terms are present.
- `git diff --check -- docs/README.md`: OK.
- Tests were not run per user instruction.
- `docs/archive/AGENTS_FULL.md` was not read or modified.

## Known Risks

- The working tree had unrelated pre-existing changes before this task: deleted ` AGENTS_md_slimming_plan.md` and untracked `docs/archive/AGENTS_md_slimming_plan.md`. They were left untouched and excluded from commits.

## Commit / Push

- Source commit: `29ae0ea docs: update docs readme map`.
- Report commit: separate `report: record docs readme map update` commit after this report is staged.
- Push: source and report commits are pushed together after the report commit.
