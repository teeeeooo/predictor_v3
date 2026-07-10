# 193-d CSV Export Closeout And Next Slice

## Goal

Close out 193-c CSV export manual smoke, remove self-referential report commit/push pending wording, and choose the next single slice.

## Scope

- Updated 193-c manual check from needed to completed.
- Removed self-referential docs/report commit and push pending wording from 193-c.
- Recorded a compact active-report commit/push recording principle in WORK_PLAN.
- Compared the next candidates and selected one next slice.

## Manual Smoke Closeout

193-c table CSV export foundation manual smoke completed with no issues found:

- ISO / ISEER result comparison CSV export saves normally.
- ISO / ISEER bin trace CSV export saves the currently selected trace.
- SASO result comparison CSV export saves normally.
- SASO bin trace CSV export follows required/optional selection state.
- Korean/special characters open correctly in Excel.
- File dialog cancel returns without error.
- Existing trace expand/collapse, profile switch, resize, and scroll behavior remains normal.

## Report Recording Principle

- Active reports should record task content, changed files, verification, manual check needs/results, excluded scope, and next action.
- Active reports should not record the docs/report commit hash that includes that same report.
- Active reports should not leave `pending at report creation` commit/push wording.
- Commit and push results belong in the final chat report.

## Candidate Comparison

- Candidate A: Hong Kong CSPF trace implementation.
  - User value: completes the next trace coverage gap for an existing Hong Kong metric.
  - Size: small; 193-a audit found CSPF-style `bin_details`.
  - Fit: directly reuses the existing trace/export pattern and `BinTraceTable`.
  - Risk: low if HSPF is explicitly excluded.
  - Rollback cost: low because the change can stay section-local.
- Candidate B: Bin graph parity with SPOT-style HTML export reference mapping.
  - User value: higher visual value, but graph surface and export mapping need reference review first.
  - Size/risk: larger than CSPF trace; graph/HTML export path can affect layout and artifact decisions.
  - Best next step later: reference mapping before implementation.
- Candidate C: Multi/batch design.
  - User value: potentially broad, but not as connected to the current trace/export closeout.
  - Size/risk: needs Toplevel lifecycle, repeated inputs, result persistence, and design decisions.
  - Best next step later: separate design slice.

## Selected Next Slice

**Hong Kong CSPF trace implementation**

Purpose:

- Add Hong Kong CSPF `bin_details` trace table using the existing `BinTraceTable` pattern.

Implementation / check scope:

- CSPF section-local trace retention.
- Collapsed trace UI for Hong Kong CSPF only.
- Reuse existing `BinTraceTable` and CSV export hook if applicable.
- Keep `ResultPanel` summary path intact.
- Focused CSPF trace lifecycle tests and smoke.

Excluded scope:

- No Hong Kong HSPF trace.
- No heating trace schema implementation.
- No graph or graph export.
- No core/config/golden/profile registry changes.
- No ResultPanel refactor or shared framework.

Why now:

- It is the smallest stable continuation of the completed trace/export work.
- It uses an audited compatible result shape.
- It avoids graph/export layout risk and avoids multi/batch design expansion.

## Verification

- `python3 -B tools/check_code_structure.py`: OK.
- `git diff --check`: OK.
- `git status --short`: checked before commit.
- `git diff --name-only`: checked before commit.
- `git diff --stat`: checked before commit.

## Changed Files

- `result_reports/active/193c_table-csv-export-foundation.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/193d_csv-export-closeout-next-slice.md`

## Excluded Scope

- No source/test changes.
- No CSV implementation changes.
- No graph, graph export, Hong Kong trace implementation, HSPF schema implementation, multi/batch, or EN/AHRI work.
- No lifecycle summary/archive or memory/project log updates.
