# Design Gate — Arc 12 Calculator UseCase Boundary Audit

## Goal
- Formalize the calculator UI/application boundary audit for Arc 12.
- Establish the first narrow implementation target: ISO/ISEER 2-point single calculation, followed by matching batch reuse.
- Preserve current calculator behavior while moving reusable orchestration out of Tk UI sections.

## Context
- Calculator engines already live under `core.calculators`.
- `app_calculator.py`, `apps.calculator.app`, and the top-level Tk shell are acceptably thin.
- Several Tk calculator sections still own application orchestration: text parsing, profile selection, core calculator construction/call, result row formatting, detail DTO assembly, and widget updates.
- Future calculator runtime surfaces and predictor-calculator integration should reuse an application boundary instead of copying Tk section orchestration.

## Audit Summary
| Area | Finding | Decision |
| --- | --- | --- |
| Entrypoint / shell | `app_calculator.py`, `apps.calculator.app`, and `apps/calculator/ui/calculator_app.py` are thin shell/composition owners. | Keep current launcher/shell boundary. |
| ISO/ISEER 2-point | The section directly imports the core dispatcher, resolves profiles, creates calculators, calls `calculate_cspf`, formats rows, and builds detail data. | First extraction target. |
| Hong Kong CSPF/HSPF | Sections repeat direct UI orchestration and core dispatcher usage. | Follow-up candidates after the ISO/ISEER pattern lands. |
| SASO T3 | UI section creates calculators and mutates calculator config for scenario selection. | Higher-risk follow-up; do not use as first extraction. |
| EN14825 | UI-local adapters provide partial separation, but ownership remains under the UI package. | Defer until the simpler application pattern is proven. |
| AHRI SEER2/HSPF2 | UI-local adapters are the best current pattern, and core envelope helpers already exist. | Use as reference evidence, not the first extraction target. |
| Batch surfaces | Generic batch controller/table split is acceptable, but profile handlers still own row calculator orchestration. | Migrate ISO/ISEER batch after the single usecase lands. |

## Target Dependency Direction
```text
View / Tk Section
-> Controller / event glue
-> Calculator Application UseCase
-> Calculator Core Adapter / Dispatcher Port
-> core.calculators
```

The application usecase must not import Tkinter, PySide6, widget classes, table models, or UI panels.

## Boundary Decision
| Item | Common/Core | Specialized/Handler/UI/ML/Adapter | Reason |
| --- | --- | --- | --- |
| Calculator formulas and public result dicts | `core.calculators` | none | Formula/config/golden/public result contracts are protected. |
| Profile selection for calculator UI usecases | `apps.calculator.application.profile_resolver` | UI may call the application resolver | Routing must be UI-runtime-neutral. |
| Core calculator construction | `apps.calculator.adapters.core_calculator_dispatcher` delegates to `core.calculators.dispatcher` | Usecases depend on the adapter boundary | Avoid direct dispatcher imports in Tk sections and batch handlers. |
| ISO/ISEER 2-point row/detail assembly | `apps.calculator.application.iso_iseer_2point` | Tk section renders returned DTOs | Shared single and batch behavior should not live in widgets. |
| Widget lifecycle/layout/status rendering | none | Tk section and result/detail views | UI remains responsible for display and interaction. |

## Data Shape / API Boundary
- Input: raw or numeric full/half capacity and power values for ISO/ISEER 2-point calculation.
- Output: UI-neutral status, result rows compatible with the current result table, detail sources, detail summaries, and controlled error text.
- Public API impact: none for core calculators, profile IDs, result dicts, fixtures, or golden expected values.
- Backward compatibility: existing visible ISO/ISEER single and batch result/status behavior must be preserved.

## Required Tests
- Application package import guards for no Tkinter/PySide dependency.
- Profile resolver parity with existing UI resolver behavior.
- Dispatcher adapter delegation to the existing core dispatcher.
- ISO/ISEER usecase empty, invalid, and valid smoke outputs.
- Source guards that the ISO/ISEER section and batch handler no longer import the core dispatcher after their migration slices.
- Focused calculator/batch regression tests from the Arc 12 work spec.

## Migration / Refactor Path
1. Slice 1: add `apps.calculator.application` and `apps.calculator.adapters` foundation with profile resolver and dispatcher adapter ownership.
2. Slice 2: extract ISO/ISEER 2-point single calculation into an application usecase and wire the Tk section to render its output.
3. Slice 3: update ISO/ISEER batch handler to reuse the application evaluator/usecase.
4. Slice 4: close out Arc 12 first-pattern extraction and choose the next calculator extraction target.

## Non-goals
- Full calculator rewrite.
- SASO, Hong Kong, EN14825, or AHRI implementation changes in the first extraction.
- Calculator formula, config semantics, profile ID, fixture, golden expected, or public result dict changes.
- Tk visual layout redesign or batch UX changes.
- Broad plugin/universal calculator abstraction.

## Risks
| Risk | Impact | Mitigation |
| --- | --- | --- |
| Moving too many standards at once | Behavior regression and unclear ownership | Keep first implementation to ISO/ISEER 2-point only. |
| Application DTOs accidentally become Tk-specific | Reuse boundary fails | Add import guards and keep DTOs UI-neutral. |
| Batch output keys drift | Export/copy regressions | Preserve existing batch result keys and add focused handler tests. |
| SASO config mutation remains | Known architecture debt persists | Record as follow-up candidate, not hidden scope. |

## Implementation Slices
1. Arc 12 Slice 1 - Calculator Application Boundary Foundation.
2. Arc 12 Slice 2 - ISO/ISEER 2-point Single UseCase Extraction.
3. Arc 12 Slice 3 - ISO/ISEER 2-point Batch Reuse.
4. Arc 12 Slice 4 - Closeout / Next Extraction Decision.

## Next Codex Implementation Prompt
```text
Run Arc 12 Slice 1 - Calculator Application Boundary Foundation.

Create the application package and dispatcher adapter foundation, move pure
profile routing out of the UI package where practical, add focused import and
delegation tests, and preserve calculator formulas/configs/golden/public result
contracts.
```
