# 06. Portable UI / UX Adoption Guide

## Role and scope

This guide defines the minimum adoption kit for carrying the common
UI/UX architecture into another desktop application. It connects the
common contracts to the project-owned code and verification needed to
make the contracts enforceable.

In predictor_v3, this is an adoption guide under the
[temporary behavior baseline](README.md#temporary-behavior-baseline). Another
project chooses its own scope and binding before using it. Reusing this guide
does not make all documents active in another project or select its toolkit.
It does not prescribe a palette or widget library.

Global `desktop-table-ui` and `desktop-window-lifecycle` Skills own reusable
interaction/lifecycle workflows. The selected local documents own concrete
keys, visual roles, surface shape, acceptance, and deliberate deviations.

## 1. Adoption kit

A usable adoption carries all of the following pieces together:

| Part | Responsibility |
| --- | --- |
| Selected UI/UX owner docs | Locally adopted behavior, table, layout, and surface obligations; link reusable workflows to their global Skill owners. |
| Project binding document | The selected toolkit, supported surfaces, deliberate deviations, and rollout order for the adopting project. |
| Token owner file | Concrete color, typography, spacing, and state values used by the project's UI widgets. |
| Toolkit adapter | Mapping from the common contracts to framework layout, focus, validation, and interaction mechanisms. |
| Table/result/card component owner | Reusable widgets or builders that render matrix and summary surfaces from the owned tokens. |
| Optional interaction controller | Excel-like selection, TSV copy/paste, clear, undo, and keyboard traversal registered against table metadata. |
| Optional graph/detail component | Lightweight detail visualization, such as a Canvas-based surface, when the product flow needs it. |
| Visual value ownership guard | A small configured check that prevents component-local visual values from bypassing the token owner. |

Copying `docs/ui_ux/` alone is not an adoption. A project must also
carry or create its binding document, token owner, component skeleton,
toolkit adapter decisions, and guard configuration.

## 2. Ownership boundary

- Common documents define semantic roles and interaction obligations.
- The project binding document states which roles and surfaces are in
  active use.
- The token owner is the only location where component-facing concrete
  visual values are introduced.
- Component and widget files consume owned tokens. They do not newly
  define raw colors, raw spacing values, or fixed-pixel table width
  rules to solve alignment locally.
- When a component needs a new visual role, add the role to the token
  owner first, then consume it from the component.
- Toolkit adapters own framework mechanics; they do not become a
  second palette or layout-value owner.

The owner may be a toolkit-local binding over a toolkit-neutral semantic
foundation. This allows incremental adoption without requiring a
whole-application theme migration.

## 3. Table and result components

A matrix/table component should provide role-bearing cells and enough
metadata for an optional interaction controller to register later:

- table surface, header cell, row-header cell, editable cell, and
  static cell roles;
- row/column addresses and editable field order;
- responsive parent-driven stretching with character/font-based initial
  sizing;
- state visuals imported from the token owner.

A result component should expose compact summary table roles and status
feedback without requiring a raw output dump. Result and input
components should share the same visual-value ownership rule.

A separate interaction-controller module is optional; the required table
behavior is not optional once a surface is declared table-complete under
[the table completion gate](03_SPREADSHEET_TABLE_UX_CONTRACT.md#completion-gate).
An incremental component may be incomplete, provided its missing behavior is
reported. Graph/detail remains conditional on the product flow. Neither kind
of staging moves visual-value ownership back into individual widgets.

## 4. Minimal guard

The ownership guard verifies a boundary rather than enforcing a
complete style system:

- configure component scan roots;
- configure token owner and deliberate allowlist paths;
- report component-local raw color values;
- report component-local visual constants such as color, font, spacing,
  or fixed width/height token declarations;
- exclude calculation code, documents, fixtures, and legacy evidence
  unless a project explicitly brings them into the UI adoption scope.

The guard does not inspect every numeric literal and does not decide a
project's palette. Its purpose is to keep new visual values flowing
through the configured owner.

### Current Predictor owners and guard limits

- Concrete semantic values: [visual tokens](../../ui_common/visual_tokens.py).
  Calculator's [layout constants](../../apps/calculator/ui/layout_constants.py)
  and [theme adapter](../../apps/calculator/ui/theme.py) provide local bindings.
  Document vocabulary is not an exact inventory of runtime token keys.
- Tk table surface and interaction: [MetricInputTable](../../apps/calculator/ui/metric_input_table.py),
  [TkTableController](../../apps/calculator/ui/table/controller.py), and
  [surface protocol](../../apps/calculator/ui/table/surface.py). Inspect current
  callers before creating another component/controller.
- The existing [staged change gate](../agent_workflows/AGENT_CHANGE_GATES.md)
  uses [UI literal checks](../../tools/agent_change_gate_ui_literals.py).
  It checks added staged lines in Calculator, Train/Predict, and legacy UI
  roots. Existing hex-color rules are errors; direct numeric arguments in
  selected Qt sizing/spacing methods are warnings. Unchanged old literals are
  not retroactively checked. Shared PySide bindings are
  [style](../../apps/common/ui/style.py) and
  [window policy](../../apps/common/ui/window_policy.py), outside the surface
  scan. This is not a full token-ownership scanner: computed values, nested
  `QSize`, and CSS sizes are not resolved. Passing does not prove full adoption.
- Current table deviations are owned by
  [surface bindings](03_SPREADSHEET_TABLE_UX_CONTRACT.md#temporary-surface-bindings).
  Current toolkit decisions are owned by [toolkit policy](01_TOOLKIT_SELECTION_POLICY.md).

## 5. Reference evidence

Prior implementations in other applications or repositories can
provide evidence for useful component or controller patterns. They do
not name this architecture and do not replace the common contract,
project binding document, token owner, or toolkit adapter.

## 6. Adoption checklist

- Select the common owner documents relevant to the product surfaces.
- Write the project binding and identify the concrete token owner file.
- Build or adapt table/result/card components that consume owned values.
- Define the toolkit adapter behavior for resizing, focus, and
  validation.
- Add interaction or graph/detail components only when required by the
  product phase.
- Configure one ownership boundary guard for adopted component roots.
- Verify representative components and the guard before expanding the
  surface inventory.

## Related documents

- `00_UI_UX_SYSTEM.md` - common UI/UX SSOT root.
- `02_DESIGN_TOKENS_AND_LAYOUT.md` - semantic token and layout
  contract.
- `03_SPREADSHEET_TABLE_UX_CONTRACT.md` - table interaction
  obligations.
- `05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md` - matrix/result surface
  roles.
- `adapters/TKINTER_TABLE_ADAPTER.md` - Tkinter table implementation
  mapping.
