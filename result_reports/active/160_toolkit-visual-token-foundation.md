# 160. Toolkit Visual Token Foundation

## Goal

Add a toolkit-neutral semantic visual token foundation shared by future PyQt
and Tkinter adapters, following the project-wide visual architecture without
applying styles to existing UI.

## Scope

- Confirm the active visual architecture, prior evidence, existing theme
  module boundary, and current work order.
- Add a pure Python semantic visual-token registry and contract tests.
- Add narrow documentation links and update the recommended action order.
- Verify with structure guard, compilation, targeted tests, and the full
  suite.

## Non-goals

- No existing PyQt/Tkinter UI style adoption or visual change.
- No replacement, deletion, or wrapper conversion of `ui/theme.py`.
- No change to `ui/spreadsheet_table.py`, `ui_tk/`, Predict/Train apps,
  calculator code, tests outside the new file, fixtures, skips, or xfails.
- No `ACTIVE_DOCUMENTS.md`, `project_log.md`,
  `result_reports/memory/project_memory_seed.md`, or lifecycle maintenance
  changes.

## Project Memory Recall Gate

The requested keywords were searched with `rg -n` against
`result_reports/memory/project_memory_seed.md`; the seed was not read in
full and was treated as evidence below current instructions and active owner
documents.

Relevant memory evidence:

- The spreadsheet table contract remains the owner of Excel-like PyQt table
  behavior.
- PyQt Predict/Train remain retention candidates while calculator-only PyQt
  retirement remains held behind the Tkinter path.
- Windows packaging size measurement and additional PyQt host validation
  remain pending.

The seed does not yet carry the 158 visual architecture decision; the active
`docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md` and report 158 are the direct
evidence for this task. The memory seed is not modified.

## Design Gate Summary

### Confirmed Decisions

- Shared visual-token vocabulary belongs in a new toolkit-neutral pure Python
  module: `ui_common/visual_tokens.py`.
- The module returns plain strings, integers, and font mappings only; PyQt
  and Tkinter binding belongs to future adapters/application slices.
- Existing `ui/theme.py` is retained unchanged as the held calculator-era
  registry and is not routed through the new module.

### Boundary And API

- Common foundation: semantic color, spacing, radius, and font-role
  registries plus strict lookup functions.
- Existing application/adapters: no imports from the new foundation in this
  slice.
- Public API: `visual_color`, `visual_spacing`, `visual_radius`,
  `visual_font`, and `visual_roles`.
- Failure behavior: unknown role or token kind raises `KeyError`; no silent
  fallback exists.

### Risks And Acceptance

- Token values are a baseline vocabulary, not proof that current UI maps to
  them. Later adoption requires a deliberate inventory/mapping task.
- Acceptance is import independence, role/API contract coverage, no existing
  UI wiring, and no regression in the full suite.

## Task Results

### Task 1 - Evidence And Token Scope

- Confirmed `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md` as the visual
  architecture owner and `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md` as the
  token/layout naming owner.
- Confirmed report 158 defines neutral-first chrome, semantic engineering
  color retention, and PyQt/Tkinter project-wide scope.
- A `159` report exists at
  `result_reports/active/159_track-visual-inspiration-source-reference.md`,
  but it tracks the inspiration source and is not an Existing PyQt
  visual/color/token inventory report. The missing inventory report is not
  required for this foundation baseline: report 158 plus current read-only
  inspection of `ui/theme.py`, `ui/spreadsheet_table.py`, and `ui_tk/`
  provide sufficient non-migrating evidence.
- Confirmed `ui/theme.py` is a pure Python calculator-era token registry
  protected by `tests/test_ui_theme_tokens.py`; neither file is modified.
- Confirmed minimum semantic scope:
  colors `surface.default`, `surface.panel`, `text.default`, `text.muted`,
  `border.default`, `border.focus`, `table.header`, `table.input`,
  `table.fixed`, `table.calculated`, `table.invalid`, `table.warning`,
  `table.selected`, `table.focus`, `result.good`, `result.warning`,
  `result.error`; spacing `space.xs` through `space.lg`; radius
  `radius.cell`, `radius.panel`, `radius.pill`; fonts `font.body`,
  `font.label`, `font.mono_label`.

### Task 2 - Token Module

- Added `ui_common/__init__.py` and `ui_common/visual_tokens.py`.
- The module contains no PyQt5, tkinter, core calculator, or external-library
  imports.
- Public helpers:
  `visual_color(role: str) -> str`,
  `visual_spacing(role: str) -> int`,
  `visual_radius(role: str) -> int`,
  `visual_font(role: str) -> dict[str, object]`, and
  `visual_roles(kind: str) -> tuple[str, ...]`.
- Values are plain toolkit-neutral baseline descriptors only; introduction
  of the module changes no rendered UI.

### Task 3 - Test Coverage

- Added `tests/test_visual_tokens.py`.
- Tests cover import independence from both `PyQt5` and `tkinter`, all
  required role categories, unique role names, return-type contracts, and
  strict `KeyError` behavior for unknown roles/kinds.
- Existing `tests/test_ui_theme_tokens.py` remains unchanged and passes
  together with the new foundation tests.

### Task 4 - Documentation And Work Plan

- `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md` now identifies
  `ui_common/visual_tokens.py` as the toolkit-neutral code foundation and
  explicitly defers UI wiring.
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md` links to the semantic code
  foundation without changing its token/layout ownership role.
- `docs/WORK_PLAN.md` records 160 completion, the absent inventory-report
  observation, non-migration boundary, and the next ordered actions:
  Tkinter table/grid foundation, Tkinter debounce/helper foundation, ISO Hong
  Kong vertical slice, macOS manual smoke, then Windows packaging
  measurement when a Windows host is available.
- PyQt calculator source retirement remains held until Tkinter final UX
  vertical-slice verification.

### Task 5 - Report And Memory Delta

- This full report records module/API/role boundaries, test evidence,
  non-migration decisions, and work-plan transition.
- One durable decision is recorded below as Project Memory Delta.
- Result-report lifecycle maintenance is excluded because the prompt
  explicitly forbids it; metadata check found 6 active reports, below the
  routine 8-12 report trigger.

### Task 6 - Verification

- `python3 -B tools/check_code_structure.py`:
  `code structure guard: OK (no findings)`.
- `python3 -B -m py_compile ui_common/visual_tokens.py tests/test_visual_tokens.py`:
  passed.
- `python3 -B -m pytest tests/test_visual_tokens.py tests/test_ui_theme_tokens.py -q`:
  `69 passed in 0.04s`.
- `python3 -B -m pytest -q -rxXs`:
  `603 passed, 32 skipped, 19 xfailed in 1.90s`.
- Compared with the prior baseline `566 passed, 32 skipped, 19 xfailed`,
  passed count increases by 37 for the new tests; skip/xfail counts are
  unchanged and no native abort occurred.

## Changed Files

- `ui_common/__init__.py` - package entrypoint for toolkit-neutral UI
  foundations.
- `ui_common/visual_tokens.py` - semantic visual-token registry and lookup
  API.
- `tests/test_visual_tokens.py` - pure foundation contract tests.
- `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md` - foundation module link and
  completed adoption-order marker.
- `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md` - minimal semantic token-code
  link.
- `docs/WORK_PLAN.md` - foundation completion and next execution order.
- `result_reports/active/160_toolkit-visual-token-foundation.md` - this
  report.

## Known Failures / Risks

- A separate Existing PyQt visual/color/token inventory report described in
  the task background was not present as report 159 in the current checkout;
  implementation therefore deliberately stops at a non-applied foundation.
- Future PyQt/Tkinter adoption must map actual widget states to these roles
  without erasing existing engineering color meaning.

## Next Suggested Action

Implement the Tkinter table/grid input foundation under the existing final UX
contract, using this token module only when a separately scoped adapter/style
application decision authorizes wiring.

## Scope Compliance

- No existing UI module imports or consumes `ui_common.visual_tokens`.
- No modifications were made to `ui/theme.py`, `ui/spreadsheet_table.py`,
  `ui_tk/`, Predict/Train apps, existing tests, `ACTIVE_DOCUMENTS.md`,
  `project_log.md`, or `project_memory_seed.md`.
- No color replacement, UI implementation, source retirement, skip/xfail
  maintenance, or result-report lifecycle action was performed.

## Commit / Push

- Source/docs/test commit: `2c44340` (`feat: add toolkit-neutral visual
  tokens`).
- Report is committed separately after finalization and pushed to
  `origin/work/ui-ux-ssot-adoption`.

## Project Memory Delta

```yaml
- type: decision
  topic: toolkit-visual-token-foundation
  content: "predictor_v3 has a toolkit-neutral visual token foundation in ui_common/visual_tokens.py for semantic color, spacing, radius, and font roles; existing PyQt and Tkinter UI is not migrated in this foundation slice."
  keywords:
    - visual token
    - semantic color
    - PyQt
    - Tkinter
    - UI/UX SSOT
  assertionStatus: observed
  source: result_reports/active/160_toolkit-visual-token-foundation.md
```
