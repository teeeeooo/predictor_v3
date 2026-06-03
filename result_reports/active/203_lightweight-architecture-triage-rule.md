# 203 Lightweight Architecture Triage Rule

## Goal

- Add a lightweight architecture triage rule to `AGENT_TASK_ROUTER.md`.
- Let coding tasks decide whether Design First Gate is needed without forcing a full design slice for every small task.
- Keep existing Design First Gate semantics unchanged.

## Scope

- Router rule wording only.
- Work plan and previous merge report follow-up notes.
- No code behavior changes.

## Changed Files

- `AGENT_TASK_ROUTER.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/202_main-merge-execution.md`
- `result_reports/active/203_lightweight-architecture-triage-rule.md`

## Router Rule Change Summary

- Added `Architecture Triage for Coding Tasks` to the Quick Route Index.
- Added a short router section after Shared Guardrails.
- New triage asks whether the task adds a new responsibility/surface, may repeat across standards/profiles/sections, or bypasses existing owners/helpers/adapters.
- If all answers are No, scoped implementation may proceed.
- If any answer is Yes, owner/boundary/adapter needs are checked first.
- Large-impact or high-rollback-cost work still uses the existing Design First Gate and design slice.
- Docs-only, whitespace-only, report lifecycle, and clear behavior-preserving micro cleanup can skip full preflight.

## Verification

- Process check found no leftover pytest/python process beyond the check command itself.
- `python3 -B tools/check_code_structure.py`
  - Passed with existing soft-limit warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git diff --check`
  - Passed.
- `git status --short`, `git diff --name-only`, `git diff --stat`
  - Confirmed docs/rule/report-only changes.
- Pytest was not run because this was docs/rule-only.

## Known Risks

- The new triage is intentionally lightweight and does not replace Design First Gate.
- It depends on agents applying the Yes/No check before coding rather than treating it as a design document substitute.

## Next Action

- C# WPF spike branch creation remains the next work item.

## Excluded

- No code changes.
- No AGENTS.md edit.
- No prompt-writing rules document added.
- No C# WPF spike, PySide6 migration, project log, memory seed, summaries, or unrelated router rewrite.
