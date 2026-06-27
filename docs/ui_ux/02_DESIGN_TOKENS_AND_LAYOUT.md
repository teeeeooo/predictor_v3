# 02. Design Tokens and Layout

## Role and scope

- This document defines **design tokens** (color, typography,
  spacing) and **layout rules** that apply to every desktop project
  in this organization.
- Tokens here are **names**, not final hex codes. Each project may
  bind these names to concrete values in its own theme module. Until
  a project commits a palette, the names are the contract.
- Toolkit-specific implementation (QPalette, ttk.Style, etc.) lives
  in the adapter documents.
- For `predictor_v3` semantic visual-role organization and
  neutral-first visual philosophy, see
  `04_VISUAL_DESIGN_ARCHITECTURE.md`; this document continues to own
  token and layout naming.
- For `predictor_v3`, `ui_common/visual_tokens.py` is the active
  toolkit-neutral semantic token owner for upcoming PySide6 Predict/Train
  visual parity work. It does not apply styles by itself; concrete PySide6
  styling belongs in a later adapter/surface slice.

## 1. Color tokens

The token name is the contract. The "intended role" describes what
the token is for, not its exact appearance.

| Token | Intended role |
| --- | --- |
| `color.bg.app` | App-level window background. Neutral, recedes. |
| `color.bg.card` | Card / panel background. Slightly elevated over `bg.app`. |
| `color.bg.header` | Table / section header background. Distinct from body. |
| `color.bg.cell.readonly` | Read-only or auto-computed cell background. |
| `color.bg.cell.invalid` | Cell whose value fails validation. Subtle, not alarming. |
| `color.border` | Default border / divider. Low contrast. |
| `color.text.primary` | Main body text. Highest readability. |
| `color.text.secondary` | Supporting / caption text. Lower emphasis. |
| `color.text.disabled` | Foreground for disabled controls. |
| `color.accent` | Primary action color. Brand-leaning. |
| `color.success` | Success state (completion banners, valid markers). |
| `color.warning` | Warning state (recoverable issues, soft caution). |
| `color.danger` | Destructive / error state (failures, destructive actions). |

Notes:

- A read-only cell uses `color.bg.cell.readonly` plus a foreground
  derived from `color.text.secondary` or `color.text.disabled`.
  Never communicate "read-only" with background alone if the
  background is close to the editable background.
- An invalid cell uses `color.bg.cell.invalid` and/or a border drawn
  in `color.danger`. The user must still be able to edit it.
- `color.accent`, `color.success`, `color.warning`, `color.danger`
  must be distinguishable for users with common color-vision
  deficiencies. Pair color with shape or icon when the difference
  carries meaning.

## 2. Typography

Token names again; sizes and weights are bound per project.

| Token | Intended use |
| --- | --- |
| `font.window_title` | Main window title bar and large screen titles. |
| `font.card_title` | Title at the top of a card / panel. |
| `font.section_label` | Section heading inside a card. |
| `font.body` | Default body text. Forms, labels, dialog copy. |
| `font.table.header` | Table column headers. |
| `font.table.cell` | Table cell content. |
| `font.caption` | Helper text, hint text, footnotes. |

Rules:

- One font family for the whole app unless there is a clear reason
  for monospace (numeric tables, code).
- The numeric table column is allowed to use a tabular / monospace
  variant so columns line up.
- Do not introduce more than two font sizes per card.

## 3. Spacing

Token names express layout intent.

| Token | Intended use |
| --- | --- |
| `space.outer` | Outer margin between the window edge and content. |
| `space.card` | Padding inside a card. |
| `space.section` | Vertical gap between sections inside a card. |
| `space.row` | Vertical gap between adjacent rows of form fields. |
| `space.button` | Horizontal gap between adjacent buttons. |
| `space.cell` | Internal padding inside a table cell. |

Rules:

- Spacing tokens are consistent across screens in the same project.
  Do not freestyle pixel values per dialog.
- Table cells use `space.cell` for internal padding, not extra
  spacers between rows.

## 4. Button design

Buttons use tokens, not raw colors.

- **Primary action**: filled with `color.accent`, contrasting text.
  One primary per dialog.
- **Secondary action**: outlined or low-fill, body-text foreground.
  Multiple per dialog are fine.
- **Toolbar / action button**: small, icon optional, secondary-style
  by default.
- **Destructive button**: filled with `color.danger` or outlined in
  `color.danger`. Used for delete / clear / discard.
- **Disabled button**: foreground from `color.text.disabled`, no
  hover effect, cursor does not change to a clickable pointer.
- Padding inside a button uses `space.cell`-class values; do not let
  buttons collapse to a single character of height.

Rules:

- Buttons must look distinct from labels and from non-clickable
  badges. See `00_UI_UX_SYSTEM.md` §4.
- Never style a non-button element to look like a primary button.

## 5. Card layout

- A card is a rounded or bordered container that groups a single
  concern (one form, one table, one summary).
- Each card has internal padding `space.card`.
- Sections inside a card are separated by `space.section`, not by
  horizontal rules unless the visual weight requires one.
- Cards have a title in `font.card_title`. Sections inside use
  `font.section_label`.
- Do not nest cards more than one level deep.

## 6. Dialog layout

- Dialogs have a title, a body, and an action row. The action row is
  the last visible row.
- Primary action is on the right (or trailing edge for RTL); cancel
  / dismiss is to its left. Match the host OS convention when there
  is a strong platform expectation.
- Dialog body uses card-style padding `space.card`.
- Dialogs are centered on their parent and constrained so they never
  open off-screen.
- Modal dialogs gate the next step; modeless dialogs are used for
  inspectors and side panels.

## 7. Dynamic sizing rules

- A single fixed input must **not** stretch to full width simply
  because it is alone in its row. Constrain its width to a sensible
  maximum and let the remaining space stay empty.
- Multiple fixed inputs use a compact grid or a wrap layout — not a
  single column of full-width fields.
- For the initial-value table, optimize for 2–7 points being visible
  on one screen without scrolling. This is the common case.
- When the number of points grows large, prefer one of:
  - reduce the entry width per point so more points fit, or
  - introduce internal scrolling **within** the table while keeping
    headers visible.
- Do not introduce a horizontal scroll bar on the root window.
  Horizontal scrolling stays inside the table widget when needed.
- Long labels are truncated with an ellipsis or wrap to two lines.
  Do not blow up the column width to accommodate one long label.
- Every table column declares a sensible `min` and `max` width.
  Columns that auto-expand to consume the table width must still
  respect those bounds.
- Progress dialogs paint before the blocking work begins. Schedule
  the work on the event loop after the first paint completes.
- Numeric values rendered in tables and labels go through the
  project's compact numeric formatter (see `00_UI_UX_SYSTEM.md`
  §8).

## 8. Window Geometry And Screen Caps

- Window initial size, minimum size, maximum size, screen margins,
  visible caps, and preferred visible ratios are layout policy values.
  They must not be owned as raw numbers inside component or app shell
  modules.
- Toolkit-neutral placement, auto-fit, multi-monitor, viewport, and
  scroll behavior policy is owned by
  `07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md`.
- Toolkit implementations place these values in a named layout owner.
  For Tkinter, use `ui_tk/layout_constants.py` or an equivalent
  toolkit-local layout owner, then import the named constants/ratios
  into shell modules such as `ui_tk/calculator_app.py`.
- Prefer helpers based on content-requested size and screen/content
  ratios over fixed pixel dimensions. The shell may calculate geometry,
  but the policy values used by that calculation come from the owner.
- If a fallback value is unavoidable, it is still a named constant in
  the owner file, not an inline literal in the component.

### 8.1 Initial geometry order of operations

1. Render the initial UI state first so every visible widget, panel,
   selector, tab header, and result surface is realized. This includes
   default inputs, auto-calculated summaries, and any content that
   affects natural size.
2. Measure the **root / app-level rendered requested size** after the
   initial paint is stable.
3. Apply a content-based safety margin (named constant in the layout
   owner, not a hard-coded pixel number).
4. Apply the **screen cap** last, clamping to visible screen bounds so
   the window is never placed outside the display.
5. Derive the centered position from the final clamped size.

### 8.2 Separation of concerns

- **Initial geometry** is the first window size shown at startup.
  It should reflect the rendered content size, not a fixed pixel value
  or a screen-ratio minimum.
- **Resize minimum** is the smallest size a user is allowed to shrink
  the window to. It may differ from the initial geometry and must not
  force the initial window to be larger than the computed content size.
- **Screen cap** is the maximum safe window size for the current
  display. It is applied after content sizing, not as an initial floor.
- **Scrollbar visibility** is a fallback affordance. It should be shown
  only when the content genuinely exceeds the available viewport.
  Scrollbar visibility changes must not trigger geometry mutation,
  pack/forget loops, or content width sync cascades.

### 8.3 Event-loop safety

- Geometry mutation, scrollbar pack/forget, and content width
  synchronization must never call each other synchronously inside the
  same `<Configure>` handler path. If one of them must react to a
  resize event, queue the dependent work on the event loop or let the
  next natural paint cycle apply it.
- A component-specific `preferred_initial_size()` helper may be used
  only when the root requested size does not reflect the actual
  content (for example, because a scroll container or virtualized
  surface hides the true content height). In that case the helper
  measures the natural size of the visible content directly.

## 9. Empty state and helper text

- Empty tables and empty result panels must show a short empty-state
  message that tells the user what to do next.
- Helper text under an input uses `font.caption` and
  `color.text.secondary`. Keep it short; this is not a tooltip.
- Error messages on a field use `color.danger` foreground; do not
  rely on color alone.

## 10. Visual value ownership and portable adoption

- Each adopting project provides a concrete token owner file. Widget
  and component modules consume those values instead of introducing raw
  colors, local spacing tokens, fixed-pixel table width rules, or
  window geometry literals.
- A project may bind this common semantic contract through a
  toolkit-local owner while adoption is incremental; a complete theme
  migration is not required before component ownership is enforced.
- The portable architecture kit includes the owner file, component
  skeleton, toolkit adapter, and a configured ownership guard together
  with these common documents. See
  `06_PORTABLE_UI_UX_ADOPTION_GUIDE.md`.

## 11. What this document does not include

- Final hex codes. Each project owns its palette and binds these
  tokens to concrete values in its own theme or toolkit binding owner
  module.
- Toolkit-specific implementation. legacy Qt binding stylesheet and ttk.Style
  details live in the adapter documents under `adapters/`.
- Code examples. This document is the token / layout contract; the
  adapter documents are where toolkit-specific snippets go, if any.

## 12. Related documents

- `00_UI_UX_SYSTEM.md` — common UX principles.
- `01_TOOLKIT_SELECTION_POLICY.md` — toolkit choice.
- `03_SPREADSHEET_TABLE_UX_CONTRACT.md` — common table UX.
- `04_VISUAL_DESIGN_ARCHITECTURE.md` — `predictor_v3` semantic
  visual roles and visual design direction.
- `06_PORTABLE_UI_UX_ADOPTION_GUIDE.md` — portable adoption kit and
  visual-value ownership boundary.
- `adapters/PYQT_TABLE_IMPLEMENTATION.md` — legacy Qt binding table rules.
- `adapters/TKINTER_TABLE_ADAPTER.md` — Tkinter table adapter rules.
