# 296 Active Report Lifecycle Cleanup

## Goal

Archive completed active reports into summaries and reduce active report count from 31 to within manageable range.

## Scope

- Summarize and archive 28 completed active reports.
- Keep 3 active reports that are still needed for next actions.
- Update WORK_PLAN and project_log.

## Active Report Count Before / After

- Before: 31 active reports
- After: 3 active reports

## Summaries Created

| Summary | Covered Reports | Arc |
|---|---|---|
| 292 | 265–269 | Main paste policy and visible validation |
| 293 | 270–273 | Code checker reference map and evidence gate |
| 294 | 276–278 | Result formatting and BinDetailPanel cleanup |
| 295 | 261, 263–264, 279–291 | Controller switch, ResultPanel focus preservation, GUI smoke closeout |

## Reports Archived

28 reports moved to `result_reports/archive/`:

- 261, 263–264, 265–269, 270–273, 276–278, 279–291

## Reports Kept Active and Why

| Report | Reason |
|---|---|
| 262 | Main table migration candidate check — preflight completed, migration implementation pending |
| 274 | ui_tk cleanup preflight — preflight completed, cleanup implementation pending |
| 275 | Code quality guardrail backlog registration — backlog registered, processing pending |

## WORK_PLAN / project_log Changes

- WORK_PLAN: removed "Active report lifecycle cleanup follow-up" from Next Actions; added 292–295 completion note.
- project_log: added compact decision for lifecycle cleanup completion.

## Excluded Scope

- No code or test changes.
- No controller switch expansion performed.
- Memory seed not modified (no new durable decision beyond existing workflow rules).

## Validation

| Check | Result |
|---|---|
| Active report count | 3 |
| Archive report count | 311 |
| Git diff check | Clean |

## Next

- Controller switch expansion readiness.
