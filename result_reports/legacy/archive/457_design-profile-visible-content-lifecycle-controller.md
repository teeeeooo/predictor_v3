# 457 Design Profile Visible-Content Lifecycle Controller

## Goal

Freeze the common lifecycle controller owner, interface, policy inputs,
migration sequence, compatibility plan, and hard-gate timing before source work.

## Result

- Selected a feature-owned `apps/calculator/ui/lifecycle/` package and
  `ProfileVisibleContentLifecycleController` composition owner.
- Defined controller-vs-profile responsibilities and the constructor/public
  trigger contract.
- Preserved EN, AHRI, and ISO predicate/settle differences as injected policy.
- Split implementation into EN foundation, AHRI/ISO migration, then enforcement.
- Selected `check_code_structure.py` as the future architecture hard-rule owner.
- Rejected base-class, app-owned, factory-only, and broad-folder flat-helper
  alternatives.

## Validation

- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.
- `git status --short` — only task 2 files staged before commit.

## Changed Files

- `docs/designs/2026-06-21-profile-visible-content-lifecycle-controller-design.md`
- `docs/designs/README.md`
- `docs/WORK_PLAN.md`
- `project_log.md`
- `result_reports/active/457_design-profile-visible-content-lifecycle-controller.md`

## Read Ledger

- task 1 lifecycle audit: owner debt and profile policy matrix; reason: design
  input.
- architecture boundary owner: controller/shell/view and new-source package
  policy ranges; reason: package and responsibility decision.
- focused test references to current private lifecycle fields; reason:
  compatibility/migration plan.
- broad read: none
- repeated read: none

## Next Action

Common lifecycle controller foundation and EN14825 migration.
