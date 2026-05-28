# 188a Design First Gate Update

## Goal

Add a "Design First Gate" to `AGENT_TASK_ROUTER.md` that separates
design slices from implementation slices for high-impact work.

## Background

Tasks 186–187 (ISO/ISEER 2-point Tkinter design and implementation)
confirmed that jumping straight into implementation risks getting
trapped in existing skeletons or temporary structures. Splitting the
work into a design slice followed by an implementation slice proved
safer and produced clearer scope boundaries.

## Design First Gate

Location: `AGENT_TASK_ROUTER.md`, between **Project Memory Recall Gate**
and **Result Report Workflow**.

### Design slice required for

- New features (e.g., SASO, multi/batch, graph/detail, calculator routing, profile/standard expansion)
- User flow changes
- UI tab/section/navigation structure changes
- Input structure or result surface changes
- Calculator routing / profile/standard selection changes
- Test fixture/golden expected structure changes
- Cross-layer refactors
- Public helper/interface changes that affect future extension boundaries
- Any work with large scope or high rollback cost

### Design slice rules

1. No source/test changes during design.
2. Audit existing reference/current structure.
3. Compare candidate approaches.
4. Select exactly one recommended approach.
5. Write a design doc or active report.
6. Explicitly state implementation scope and excluded scope.

### Implementation slice rules

1. Implement only from the approved design doc/report.
2. If implementation deviates from the design, stop and report rather than silently adjusting.
3. No scope creep.
4. No unrelated refactor.

### Hotfix / micro-cleanup exceptions

- Typo, docstring, unused import
- Clear behavior-preserving extraction
- Urgent hang/hotfix

These may skip the design slice, but scope and prohibited work must be
written narrowly.

## Changed Files

1. `AGENT_TASK_ROUTER.md` — added **Design First Gate** section.
2. `docs/WORK_PLAN.md` — added task 4s (188-a) checkpoint.

## Verification

- `python3 -B tools/check_code_structure.py`: OK (no findings).
- `git diff --check`: clean.
- No Python source/test changes.

## Next Action

188-b: 187-c report/manual smoke cleanup.
