# 04. Visual Design Architecture

## Purpose

This document is the project-wide visual design architecture SSOT for
`predictor_v3`. It translates a Figma-inspired visual direction into rules
for a desktop engineering application without replacing the common UI/UX,
toolkit, token/layout, or spreadsheet behavior contracts.

## Source Inspiration

- `docs/ui_ux/_source/DESIGN_figma_inspiration.md` is inspiration source
  material, not an active contract or direct SSOT.
- The active `predictor_v3` visual SSOT is this document:
  `docs/ui_ux/04_VISUAL_DESIGN_ARCHITECTURE.md`.
- The source contributes a neutral-first interface, restrained geometry,
  clear focus treatment, typography hierarchy, and regular spacing rhythm.
  Those ideas are translated for analysis and calculation screens rather than
  copied as a web marketing UI.
- Figma-specific variable fonts, exact CSS radius values, rgba glass
  surfaces, hero gradients, and exact tracking/weight recipes are
  inspiration only. They are not desktop UI requirements.

## Scope

- Applies across `predictor_v3` desktop UI, including long-term Predict and
  Train PyQt surfaces and the Tkinter calculator direction.
- Governs visual philosophy and semantic visual roles. It does not choose a
  toolkit or prescribe widget implementation.
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
- Share one visual philosophy across toolkits; implement it through each
  toolkit's supported adapter and styling mechanisms.

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

Existing PyQt header color, condition-based cell color, and result/status
color rules are not discarded. They remain valid engineering information and
must be organized over time as semantic token or semantic role bindings.
Concrete mappings from existing application styles into these roles remain
deferred to a follow-up inventory and adapter/adoption task.

The toolkit-neutral code foundation for these semantic roles is
`ui_common/visual_tokens.py`. It provides plain Python lookup values for
future adapters; existing PyQt and Tkinter UI are not migrated by its
introduction.

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

- Table/grid surfaces are a core interaction primitive across
  `predictor_v3`, not a calculator-only presentation choice.
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
  through project tokens and toolkit layout behavior rather than scattered
  literal values.
- Table-dense workflows remain compact enough to expose needed data without
  sacrificing click targets, legibility, or keyboard use.
- Use rounded containers and pill-like actionable controls selectively to
  communicate grouping and action hierarchy.
- Exact web radii or mandatory circular treatment for every control are not
  adopted; desktop platform behavior and data density take precedence.

## Focus, Selection, and Validation

- Keyboard focus is always visible. A dashed or otherwise clear focus
  indicator is preferred where the toolkit renders it reliably and
  accessibly.
- Table focus, selection, and validation are distinct meanings:
  `table.focus`, `table.selected`, and `table.invalid` must not collapse into
  one appearance.
- Validation color must not prevent editing and must not be the only signal
  of invalid content.
- Toolkit-native accessibility and high-contrast behavior override purely
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

## Toolkit Adaptation Principles

- PyQt and Tkinter share this visual philosophy, semantic role vocabulary,
  and table-first direction.
- Concrete widgets, style APIs, focus rendering, state binding, and token
  adapters may differ between toolkits.
- `01_TOOLKIT_SELECTION_POLICY.md` remains the owner of toolkit choice, and
  toolkit adapter documents remain the owners of implementation constraints.
- No application mixes PyQt and Tkinter widgets to achieve visual alignment.

## PyQt Application Notes

- Predict and Train PyQt applications are part of the long-term adoption
  scope; this architecture is not limited to calculator UI.
- Existing PyQt engineering color rules, including header styling,
  condition-based cell states, and result/status emphasis, are retained until
  an inventory maps them to semantic roles.
- Table-shaped PyQt work continues to follow
  `adapters/PYQT_TABLE_IMPLEMENTATION.md` and the common spreadsheet
  behavior contract.

## Tkinter Application Notes

- The Tkinter calculator final UX follows this project-wide visual
  architecture in addition to its existing behavior and adapter contracts.
- Tkinter may approximate focus, rounded geometry, or state surfaces using
  its supported styling/widget mechanisms; equivalence of meaning matters
  more than pixel-identical rendering.
- This architecture does not expand the current calculator implementation
  scope or authorize its next vertical slice.

## Non-goals

- Reproducing a Figma marketing site or adopting its palette literally.
- Requiring black-and-white-only interfaces or removing meaningful
  engineering state colors.
- Fixing hex/RGB values, font families, radii, spacing literals, or toolkit
  style code in this document.
- Changing current PyQt or Tkinter implementation, calculator behavior,
  table behavior, tests, or source retirement status.
- Replacing token/layout, table behavior, or toolkit adapter owners.

## Adoption Order

1. Inventory existing PyQt visual/color/token usage in Predictor, Trainer,
   and remaining Calculator references without changing code.
2. Establish a toolkit visual token foundation that maps common semantic
   vocabulary to PyQt and Tkinter adaptation points. **Foundation complete:**
   `ui_common/visual_tokens.py`; application wiring is deferred.
3. Build the Tkinter table/grid input foundation under the existing final UX
   contract.
4. Build the Tkinter auto-calc debounce/helper foundation.
5. Deliver the ISO Hong Kong CSPF/HSPF table plus auto-calc vertical slice.

PyQt calculator-only source retirement remains held until the Tkinter final
UX vertical slice verification gate is cleared. Windows `calculator_tk`
packaged size is approximately 11 MB and acceptable for the current deployment
candidate; keep PyQt baseline comparison as a later retirement-gate input.
