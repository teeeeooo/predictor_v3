# 411 Validation superset deduplication rule

## Goal

Remove ambiguity that allowed overlapping focused test suites to be rerun
during final validation.

## Scope

- Added one rule to `DIFF_READ_BUDGET.md`: when a final focused suite is a
  superset of earlier checks, run only that superset rather than repeating its
  covered subsets.

## Changed Files

- `docs/agent_workflows/DIFF_READ_BUDGET.md`
- `result_reports/active/411_validation_superset_deduplication_rule.md`

## Verification

- Target paragraph reviewed in context.
- `git diff --check`: OK.

## Known Risks

- None. This changes agent execution discipline only, not product behavior.

## Commit / Push

- Validation passed; documentation and report are committed and pushed
  together.
