# 158. Project-wide Visual Design Architecture Adoption

## Goal

Translate the uploaded Figma-inspired design source into a
`predictor_v3`-wide visual design architecture SSOT that covers retained
PyQt Predict/Train direction and the Tkinter Calculator direction without
turning web inspiration into literal desktop styling requirements.

## Scope

- Inspect the inspiration source, current UI/UX SSOT chain, Tkinter final UX
  contract, current work plan, and relevant memory entries.
- Add `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md`.
- Add narrow cross-references in the specified UI/UX and Tkinter design docs,
  register the active document, and update the near-term work order.
- Record this report and verify the existing structural/test baseline.

## Non-goals

- No UI, PyQt, Tkinter, token code, calculator, dispatcher, profile, test,
  fixture, marker, expected-value, or packaging implementation change.
- No color-value or existing condition-cell-color change.
- No source inspiration edit or retirement action.
- No PyQt calculator source retirement, lifecycle maintenance,
  `project_log.md` update, or `project_memory_seed.md` update.

## Project Memory Recall Gate

Searches were restricted to the user-specified keywords with `rg -n` against
`result_reports/memory/project_memory_seed.md`; the seed was not read in
full and was treated as evidence below the current prompt, rules, and active
owner docs.

Relevant entries confirmed:

- The spreadsheet table UX contract is the single owner of PyQt table
  spreadsheet behavior and its Excel-like interaction baseline.
- PyQt Predict and Train remain retention candidates while the
  calculator-only PyQt retirement direction is held behind Tkinter work.
- Windows PyInstaller size measurement and additional PyQt-host validation
  remain pending follow-ups.

## Task Results

### Task 1 - Source and Existing SSOT Relationship

- Confirmed the uploaded source file as
  `docs/ui_ux/_source/DESIGN_figma_inspiration.md`. The file existed as
  user-supplied untracked input at task start and was not modified or staged
  by this task.
- Treated that file as inspiration/reference material, not an active owner
  document or SSOT.
- Extracted the transferable philosophy: monochrome/neutral-first chrome,
  semantic use of color, table-first productivity surfaces, selectively
  rounded/pill geometry, clear/dashed focus treatment, an 8 px conceptual
  rhythm, typography hierarchy, and optional mono-like structural labels.
- Confirmed that literal source prescriptions conflict with engineering UI
  needs if copied directly: black-and-white-only chrome cannot erase table
  header, validation, condition, result, or status meaning.
- Confirmed compatibility with the existing owners:
  `00_UI_UX_SYSTEM.md` remains common UX root,
  `02_DESIGN_TOKENS_AND_LAYOUT.md` remains token/layout owner, and
  `03_SPREADSHEET_TABLE_UX_CONTRACT.md` remains behavior owner.
- Confirmed the Tkinter final UX contract already inherits UI/UX/table
  direction, while memory and work-plan evidence keep Predict/Train PyQt in
  the long-term UI scope rather than excluding it.

### Task 2 - Visual Architecture SSOT

- Added `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md` as the
  `predictor_v3` project-wide visual design architecture SSOT.
- The document states that neutral-first chrome is the default but is not a
  black-and-white-only rule; color remains an information channel.
- It explicitly preserves existing PyQt header colors, condition-based cell
  colors, and result/status colors for later semantic inventory and mapping.
- It defines candidate semantic roles without setting concrete values:
  `surface.default`, `text.default`, `border.default`, `table.header`,
  `table.input`, `table.fixed`, `table.calculated`, `table.invalid`,
  `table.warning`, `table.selected`, `table.focus`, `result.good`,
  `result.warning`, and `result.error`.
- It covers both PyQt Predict/Train and Tkinter Calculator, allowing
  toolkit-specific adaptation while requiring shared meaning.
- It rejects literal copying of Figma variable fonts, exact CSS radii, rgba
  glass effects, hero gradients, and web-specific type recipes.

### Task 3 - SSOT and Active Document Links

- `docs/ui_ux/00_UI_UX_SYSTEM.md` now points to `04` as the
  `predictor_v3` project-wide visual philosophy and semantic-role document.
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md` now cross-references `04`
  while retaining ownership of token and layout naming.
- `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md` now
  declares inheritance of `04`.
- `ACTIVE_DOCUMENTS.md` registers `04` as the active project-wide visual
  architecture SSOT with PyQt Predict/Train and Tkinter Calculator outbound
  adoption scope.
- The inspiration source was not registered as an active SSOT because it is
  external-inspired source material whose literal rules are not the
  predictor_v3 desktop contract.

### Task 4 - Work Plan

- `docs/WORK_PLAN.md` records completion of project-wide visual architecture
  adoption and preserves the hold on PyQt calculator-only source retirement.
- The recommended order is now:
  1. Existing PyQt visual/color/token inventory, without code changes.
  2. Toolkit visual token foundation.
  3. Tkinter table/grid input foundation.
  4. Tkinter auto-calc debounce/helper foundation.
  5. ISO Hong Kong CSPF/HSPF table plus auto-calc vertical slice.
- Windows PyInstaller size measurement remains pending until a Windows host
  is available.

### Task 5 - Report and Memory Delta

- This report records the adoption decision, evidence boundary, changes,
  verification, and next action.
- Project Memory Delta contains two durable decisions only; the seed is not
  modified in this ordinary docs task.
- Result report lifecycle maintenance is excluded because the prompt
  expressly forbids active/archive/summary moves and lifecycle maintenance;
  no summary/archive threshold action is part of this adoption task.

### Task 6 - Verification

- `python3 -B tools/check_code_structure.py`:
  `code structure guard: OK (no findings)`.
- `python3 -B -m pytest -q -rxXs`:
  `566 passed, 32 skipped, 19 xfailed in 1.92s`.
- The full suite result matches the expected current baseline exactly.

## Changed Files

- `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md` - new project-wide visual
  architecture SSOT.
- `docs/ui_ux/00_UI_UX_SYSTEM.md` - added visual architecture owner link.
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md` - added semantic visual-role
  cross-reference without rewriting token rules.
- `docs/designs/2026-05-23-tkinter-calculator-final-ux-contract.md` - linked
  the Tkinter final UX to the project-wide visual architecture.
- `ACTIVE_DOCUMENTS.md` - registered the new active SSOT document.
- `docs/WORK_PLAN.md` - recorded adoption and revised recommended action
  order.
- `result_reports/active/158_project-wide-visual-design-architecture-adoption.md`
  - this report.

## Verification

- Branch gate: confirmed `work/ui-ux-ssot-adoption` before editing.
- Source guard: `docs/ui_ux/_source/DESIGN_figma_inspiration.md` was read as
  evidence only and not edited or staged.
- Forbidden-file guard: no edits to code, tests, `project_log.md`,
  `result_reports/memory/project_memory_seed.md`, lifecycle folders, or
  source-retirement assets.
- `python3 -B tools/check_code_structure.py`: `code structure guard: OK (no
  findings)`.
- `python3 -B -m pytest -q -rxXs`: `566 passed, 32 skipped, 19 xfailed in
  1.92s`; baseline maintained.

## Known Failures / Risks

- Concrete visual-token values and current PyQt styling mappings remain
  intentionally unresolved until the proposed read-only inventory and token
  foundation steps.
- The user-provided inspiration file is locally untracked and is excluded
  from this task's commit scope; the new SSOT records its observed path but
  does not promote or modify the source.

## Next Suggested Action

Run a read-only Existing PyQt visual/color/token inventory across
Predictor/Trainer/Calculator remnants, capturing headers, conditional cell
states, result/status treatments, and inline styles for subsequent semantic
role mapping.

## Scope Compliance

- Only the requested visual architecture doc, specified cross-reference
  documents, `ACTIVE_DOCUMENTS.md`, `docs/WORK_PLAN.md`, and this report
  were changed.
- No code, implementation, token values, colors, tests, sources, retirement
  actions, fixtures, expected values, skips, xfails, core, profile,
  dispatcher, packaging run, `project_log.md`, memory seed, or lifecycle
  movement was performed.

## Commit / Push

- Source/docs commit: `101ba79` (`docs: adopt project-wide visual design
  architecture`).
- Report is committed separately after this content is finalized; the report
  commit hash and pushed branch are included in the terminal completion
  report.
- Documentation sync judgment: `docs/WORK_PLAN.md` and
  `ACTIVE_DOCUMENTS.md` were required by the requested new active SSOT and
  action-order change. `project_log.md`, refactor plan, project brief, and
  specification notes are excluded by explicit scope and are not modified.

## Project Memory Delta

```yaml
- type: decision
  topic: project-wide-visual-design-architecture
  content: "predictor_v3 adopts docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md as its project-wide visual design architecture SSOT, translating a Figma-inspired neutral-first and table-first philosophy while preserving semantic engineering colors for headers, condition-based cells, results, and status."
  keywords:
    - UI/UX SSOT
    - visual design
    - semantic color
    - PyQt
    - Tkinter
  assertionStatus: observed
  source: result_reports/active/158_project-wide-visual-design-architecture-adoption.md
- type: decision
  topic: visual-architecture-adoption-order
  content: "predictor_v3 visual architecture adoption proceeds with a read-only PyQt visual/color/token inventory and toolkit semantic token foundation before Tkinter table/grid and auto-calc vertical-slice implementation; PyQt calculator retirement and Windows packaging measurement remain gated."
  keywords:
    - visual design
    - design token
    - PyQt
    - Tkinter
    - retirement
  assertionStatus: observed
  source: result_reports/active/158_project-wide-visual-design-architecture-adoption.md
```
