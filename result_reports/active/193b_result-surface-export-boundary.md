# 193-b Result Surface / Export Boundary

## Goal

Close out 193-a manual smoke and document the minimum result surface/export boundary before table CSV export work begins.

## Scope

- Updated 193-a report with manual smoke completion and commit/push status.
- Audited current section/result surface responsibilities by targeted class/function listing only.
- Added `docs/designs/2026-05-30-tkinter-result-surface-export-boundary.md`.
- Updated WORK_PLAN so the next implementation slice is `193-c table CSV export foundation`.

## Boundary Decision

- Sections keep profile-specific input, calculation orchestration, validation state, trace selector state, and result wiring.
- Reusable result/trace surfaces own display, formatting, copy text, and a future export data hook.
- A small export helper should own CSV writing and file dialog wrapping.
- `Iso16358Tab` keeps profile switching, scroll reset, and one-shot fit ownership.
- Do not introduce `BaseSection`, presenter/controller layers, or a shared result framework yet.

## Source Responsibility Check

- `IsoIseer2PointSection`: ISO/ISEER input, dual calculation flow, trace retention, trace selector wiring.
- `IsoSasoT3Section`: SASO input, optional 35 Min state, required/optional calculation flow, trace retention, trace selector wiring.
- `BinTraceTable`: cooling bin trace table display, formatting, status, copy, row exposure.
- `IsoIseer2PointResultTable` / `IsoSasoT3ResultTable`: comparison table display, formatting, status, copy, row exposure.
- `Iso16358Tab`: profile shell, section switching, scroll reset, one-shot fit callback.

## Growth Risk

`IsoSasoT3Section` is already carrying input, optional state, calculation orchestration, result updates, trace state, and trace UI. Adding CSV export, graph rendering, graph export, and file handling directly to section scripts would make them too broad. The next slice should extract only the repeated export action, not a large framework.

## Next Implementation Slice

`193-c table CSV export foundation`:

- Add a small CSV export helper.
- Add thin table export hooks on existing table-shaped result/trace surfaces.
- Wire export commands minimally.
- Do not implement graph, graph export, Hong Kong trace, or shared framework.

## Excluded Scope

- No Python source or test changes in this docs-only slice.
- No CSV export implementation.
- No graph or graph export implementation.
- No Hong Kong trace implementation.
- No core/profile/config/golden/fixture/PyQt changes.
- No `project_log.md`, memory seed, summary, archive, or lifecycle maintenance.

## Verification

- `python3 -B tools/check_code_structure.py`: OK.
- `git diff --check`: OK.
- `git status --short`: checked before commit.
- `git diff --name-only`: checked before commit.
- `git diff --stat`: checked before commit.

## Commit / Push

- Docs/report commit: `bb47869 193-b: document result export boundary`
- Push: completed for docs/report commit.

## Project Memory Delta

- none
