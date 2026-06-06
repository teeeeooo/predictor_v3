# 04. Visual Design Architecture

## Purpose

This document is the portable visual design architecture owner for
engineering and data-work applications. It translates visual inspiration into
interface rules without replacing the common UI/UX, interface selection,
token/layout, or spreadsheet behavior contracts.

## Source Inspiration

- `docs/ui_ux/_source/DESIGN_figma_inspiration.md` is inspiration source
  material, not an active contract or direct SSOT.
- The active portable visual architecture owner is this document:
  `04_VISUAL_DESIGN_ARCHITECTURE.md`.
- The source contributes a neutral-first interface, restrained geometry,
  clear focus treatment, typography hierarchy, and regular spacing rhythm.
  Those ideas are translated for analysis and calculation screens rather than
  copied as a web marketing UI.
- Figma-specific variable fonts, exact CSS radius values, rgba glass
  surfaces, hero gradients, and exact tracking/weight recipes are
  inspiration only. They are not desktop UI requirements.

## Scope

- Applies across engineering/data application surfaces that need compact,
  structured, task-focused visual design.
- Governs visual philosophy and semantic visual roles. It does not choose a
  GUI framework or prescribe widget implementation.
- Works with `00_UI_UX_SYSTEM.md` for global UX principles,
  `02_DESIGN_TOKENS_AND_LAYOUT.md` for token/layout naming, and
  `03_SPREADSHEET_TABLE_UX_CONTRACT.md` for table interaction behavior.
- `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` concretizes this
  architecture's table-first/result-surface direction for repeated data.

## Design Philosophy

- Use **monochrome / neutral-first chrome** so structure, hierarchy, and data
  remain legible and calm.
- Use color as an information channel for engineering meaning, not as
  decoration.
- Make grid and table surfaces the primary productivity workspace wherever
  users inspect or edit structured numeric data.
- Prefer compact, purposeful screens with clear hierarchy over ornamental
  web-style presentation.
- Share one visual philosophy across interface frameworks; implement it
  through each framework's supported adapter and styling mechanisms.

This is not a black-and-white-only mandate. Existing meaningful color in
headers, condition-based cells, validation, results, and status surfaces is
retained and rationalized by semantic role.

## Monochrome-first Chrome

- Window backgrounds, navigation, panels, toolbars, inactive controls,
  dividers, and ordinary text begin from neutral surface/text/border roles.
- Decorative accents, gradients, glass overlays, or colorful chrome do not
  become defaults merely because they appear in the inspiration source.
- A primary action may be visually strong while staying within a restrained
  neutral-first palette unless its state meaning calls for semantic color.
- Neutral chrome must not flatten hierarchy: contrast, border weight,
  typography, spacing, and selection/focus states still separate regions and
  actions.

## Semantic Color Roles

Existing header color, condition-based cell color, and result/status color
rules are not discarded when they carry engineering meaning. They should be
organized over time as semantic token or semantic role bindings. Concrete
mappings from existing application styles into these roles belong in the
adopting project or interface adapter.

An adopting codebase may provide a framework-neutral token foundation and
framework-specific bindings. Introducing such a foundation does not by itself
migrate existing application screens.

Candidate roles include:

| Semantic role | Intended meaning |
| --- | --- |
| `surface.default` | Default application or panel surface. |
| `text.default` | Primary readable foreground. |
| `border.default` | Ordinary dividers and boundaries. |
| `table.header` | Table header identity and separation from cells. |
| `table.input` | User-editable cell surface. |
| `table.fixed` | Fixed, disabled, or non-editable input context. |
| `table.calculated` | Derived/read-only value surface. |
| `table.invalid` | Invalid input requiring correction. |
| `table.warning` | Usable but cautionary cell or range state. |
| `table.selected` | Selected range or active selection state. |
| `table.focus` | Keyboard focus/current edit target indicator. |
| `result.good` | Successful or favorable result state. |
| `result.warning` | Result that requires attention but is usable. |
| `result.error` | Failed calculation or blocking status. |

Color must be paired with adequate text, shape, icon, border, or label
differences when the state is important. A future inventory determines how
current implementations map into these roles; this document does not change
any current color values.

## Table-first Interaction

- Table/grid surfaces are a core interaction primitive for structured data
  workflows, not a single-screen presentation choice.
- Data-dense input, predicted/observed value inspection, and result review
  should preserve strong row/column readability and meaningful cell states.
- Behavior remains owned by `03_SPREADSHEET_TABLE_UX_CONTRACT.md`; this
  document owns visual direction only.
- Visual states must make editable, fixed/read-only, calculated, invalid,
  warning, selected, and focused cells distinguishable without undermining
  spreadsheet efficiency.

## Typography and Labels

- Establish hierarchy through a small, consistent family of title, section,
  body, table, and caption roles already anticipated by
  `02_DESIGN_TOKENS_AND_LAYOUT.md`.
- Technical signposts and short structural labels may use a restrained
  mono-like treatment when it improves scanning; they must remain readable
  and appropriate to the installed desktop font stack.
- Numeric tables may use tabular or monospace variants to preserve alignment.
- A Figma-specific variable font, unusual weight steps, and exact
  letter-spacing are not requirements.
- User-facing labels continue to describe domain concepts rather than
  internal IDs.

## Spacing, Density, and Geometry

- Treat an 8 px rhythm as the preferred conceptual spacing baseline, mapped
  through project tokens and interface-framework layout behavior rather than
  scattered literal values.
- Table-dense workflows remain compact enough to expose needed data without
  sacrificing click targets, legibility, or keyboard use.
- Use rounded containers and pill-like actionable controls selectively to
  communicate grouping and action hierarchy.
- Exact web radii or mandatory circular treatment for every control are not
  adopted; desktop platform behavior and data density take precedence.

## Focus, Selection, and Validation

- Keyboard focus is always visible. A dashed or otherwise clear focus
  indicator is preferred where the interface framework renders it reliably and
  accessibly.
- Table focus, selection, and validation are distinct meanings:
  `table.focus`, `table.selected`, and `table.invalid` must not collapse into
  one appearance.
- Validation color must not prevent editing and must not be the only signal
  of invalid content.
- Framework-native accessibility and high-contrast behavior override purely
  stylistic attempts to reproduce the source design.

## Result and Status Surfaces

- Results and status messages are content surfaces where semantic color is
  useful: good, warning, and error states should be visible at a glance.
- Status emphasis reflects meaning and severity, not decorative branding.
- Result panels stay readable beside or below table workflows and preserve
  the neutral-first chrome around them.
- Existing result/status highlighting remains in scope for inventory and
  semantic mapping; it is not removed by adoption of this architecture.
- Repeated input and primary output surfaces follow
  `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`: matrix input where data is
  comparable, summary result first, graph/detail as a secondary phase.

## Interface Framework Adaptation Principles

- Approved interface frameworks share this visual philosophy, semantic role
  vocabulary, and table-first direction.
- Concrete widgets, style APIs, focus rendering, state binding, and token
  adapters may differ between frameworks.
- `01_TOOLKIT_SELECTION_POLICY.md` remains the owner of toolkit choice, and
  adapter documents remain the owners of implementation constraints.
- No application mixes incompatible interface frameworks only to achieve
  visual alignment.

## Adoption / Evidence Notes

- Example names are evidence, not scope boundaries.
- Concrete project, product, and framework names may appear in adoption notes
  or evidence sections to explain why a rule exists. They do not limit this
  document's portable visual principles.
- Existing engineering color rules, including header styling, condition-based
  cell states, and result/status emphasis, should be retained until an
  inventory maps them to semantic roles.
- Table-shaped work continues to follow `03_SPREADSHEET_TABLE_UX_CONTRACT.md`
  and the relevant adapter document.

### Current-Codebase Adoption Notes

- Current PyQt and Tkinter examples are evidence for adoption pressure, not
  portable scope boundaries.
- Existing application behavior, source retirement status, and vertical-slice
  sequencing remain project-binding decisions outside this portable principle
  document.

## Non-goals

- Reproducing a Figma marketing site or adopting its palette literally.
- Requiring black-and-white-only interfaces or removing meaningful
  engineering state colors.
- Fixing hex/RGB values, font families, radii, spacing literals, or
  framework-specific style code in this document.
- Changing current implementation behavior, table behavior, tests, or source
  retirement status.
- Replacing token/layout, table behavior, or interface adapter owners.

## Portable Adoption Order

1. Inventory existing visual/color/token usage without changing code.
2. Establish a semantic token foundation or binding layer that maps common
   role vocabulary to framework adaptation points.
3. Build or adopt table/grid input components under the existing UX contract.
4. Build supporting interaction helpers only where the product workflow needs
   them.
5. Deliver one representative vertical slice before expanding visual adoption.

Current-project rollout details, packaging measurements, source retirement
decisions, and named feature slices belong in that project's work plan or
result reports, not in this portable principle body.
