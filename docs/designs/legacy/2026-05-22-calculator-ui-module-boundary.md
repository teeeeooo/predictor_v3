# Design Gate — Calculator UI Module Boundary

> **Scope note.** This design fixes the **module structure** of the
> calculator UI inside `ui/`. It inherits the UI/UX SSOT
> (`docs/ui_ux/00_UI_UX_SYSTEM.md`,
> `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`,
> `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`,
> `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`), the
> calculator-specific table shape doc
> (`docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`),
> and the action-model decision
> (`docs/designs/2026-05-22-calculator-action-model-alignment.md`,
> Option A — auto-calc unified).
>
> This doc does **not** redefine calculator core, profile dispatcher,
> region config, unit adapter, ML, table UX contract, or PyQt adapter
> rules. It only fixes how the calculator UI code is split between
> modules under `ui/`.

## Background

`ui/calc_window.py` has grown to ~852 LOC. It hosts the
`CalculatorWindow` shell, three tab init methods (`init_iso_tab`,
`init_en_tab`, `init_ahri_tab`), per-tab read / convert / calculate
helpers, profile combo loading, `on_calculate` dispatch, validation
helpers, and inline error styling. Audit 107 flagged the long-term
risk; reports 108–112 built the supporting foundations (theme tokens,
EN layout polish, action model decision, `values_changed` signal,
train/predict drift baseline) without changing the file's overall
shape.

Adding Slice β (AHRI/EN auto-recompute wiring) on top of the current
shape would push `calc_window.py` further past the size that's
comfortable to reason about. This micro-design fixes the module
boundary **before** Slice β, so the recompute work lands in narrowly
scoped files instead of growing the shell.

## Current responsibilities

`ui/calc_window.py` today owns, in one file:

| Responsibility | Lines (approx) | Stays in shell? |
| --- | --- | --- |
| `InputValidationError` class | 47–52 | No — moves to `ui/calculator_errors.py` |
| `CalculatorWindow.__init__` / `init_ui` (tabs, `계산 실행` button, `result_label`) | 54–125 | Yes (shell) |
| `bind_error_reset` helper | 127–129 | No — moves to `ui/calculator_errors.py` |
| `init_iso_tab` (thin: instantiates `IsoCspfSingleWidget`) | 131–137 | Yes (shell), no further split needed |
| `init_en_tab` (SEER table + SCOP climate cards + standby) | 139–287 | No — moves to `ui/calculator_en_tab.py` |
| `init_ahri_tab` (system type + SEER2 + extras + HSPF2 v3 form) | 289–416 | No — moves to `ui/calculator_ahri_tab.py` |
| `scan_configs` / `_populate_ahri_profiles` / `_populate_en_profiles` | 418–466 | Yes for `scan_configs`; per-tab populate moves with each tab |
| `on_region_changed_iso/en/ahri` | 468–502 | Per-tab populate moves with each tab; ISO version is already a thin pass |
| `_load_hspf2_calc` | 504–508 | Moves with AHRI tab |
| `_get_float_val` | 510–525 | No — shared helper in `ui/calculator_errors.py` (or `ui/_calc_input_helpers.py`) |
| `_read_ahri_seer2_table_points` / `_read_ahri_hspf2_table_points` / `_read_ahri_seer2_point` | 527–619 | Moves with AHRI tab |
| `on_calculate` dispatch | 621–650 | Yes (shell), trimmed to tab-level delegation |
| `_clear_all_errors` | 652–656 | Yes (shell) — calls into per-tab `clear_errors()` |
| `calculate_ahri` / `_build_hspf2_v3_input` / `calculate_hspf2_v3` | 658–720 | Moves with AHRI tab |
| `calculate_iso` (no-op pass) | 722–724 | Yes (shell) for now; removed after Slice γ when result panel is per-tab |
| `_read_en_table_points_kw` / `_selected_scop_climates` / `calculate_en` | 726–end | Moves with EN tab |

Already extracted today:

- `ui/calculators_2point.py::IsoCspfSingleWidget` — full ISO tab,
  auto-calc, result panel, detail tabs. Not touched in this plan.
- `ui/spreadsheet_table.py` — `SpreadsheetTableModel` (with
  `values_changed` from Slice α), `SpreadsheetTableView`, factories
  `make_ahri_seer2_table_model`, `make_ahri_hspf2_table_model`,
  `make_en14825_seer_table_model`, `make_en14825_scop_table_model`.
- `ui/theme.py` — color / font / spacing token registry +
  `color()` / `spacing()` / `font_token()` helpers.

## Target module boundary

```
ui/
├── calc_window.py              # CalculatorWindow shell, tabs, dispatch
├── calculators_2point.py       # IsoCspfSingleWidget (unchanged)
├── spreadsheet_table.py        # SpreadsheetTableModel/View (unchanged)
├── theme.py                    # tokens (unchanged)
├── calculator_en_tab.py        # EN14825 tab widget + read + calc + result text
├── calculator_ahri_tab.py      # AHRI tab widget + SEER2/HSPF2 read + calc + result text
├── calculator_result_panel.py  # shared per-tab result/status surface (Slice γ)
├── calculator_recompute.py     # debounced auto-recompute helper (Slice β)
└── calculator_errors.py        # InputValidationError, _get_float_val, error styling
```

Not every module ships at the same time. Order is in **Extraction
order** below; the first slice creates only what is needed for that
slice.

## Public interfaces

The interfaces below are the target contracts. Each extraction slice
introduces only the subset it needs.

### `ui/calculator_errors.py`

```python
class InputValidationError(Exception):
    def __init__(self, message: str, widget=None): ...

def bind_error_reset(widget) -> None: ...
def clear_error_style(widget) -> None: ...
def apply_error_style(widget) -> None: ...  # uses theme tokens
def parse_number(text: str) -> float: ...
def get_float_val(widget, field_name, *, allow_empty=False, allow_zero=False) -> float: ...
```

- No PyQt object types are imposed beyond `QLineEdit` for `widget`.
- Error styling uses `retired theme module` tokens (no inline hex).

### `ui/calculator_en_tab.py`

```python
class EN14825Tab(QWidget):
    values_changed: pyqtSignal  # forwarded from inner SpreadsheetTableModels
    profile_changed: pyqtSignal  # optional, for Slice β subscribers

    def __init__(self, parent=None, *, calculator_factory): ...

    # UI lifecycle
    def populate_profiles(self, profiles): ...
    def set_calculator(self, calc): ...

    # Inputs and results
    def read_inputs(self) -> EN14825Inputs: ...    # raises InputValidationError
    def calculate(self) -> str: ...                 # returns result_text (W→kW happens inside)
    def clear_errors(self) -> None: ...
```

- Owns `en_seer_group`, `en_scop_group`, `en_standby_group`, climate
  dict, `input_widgets_en`, `_read_en_table_points_kw`,
  `_selected_scop_climates`.
- W → kW conversion stays **inside** `EN14825Tab.calculate`; core
  calculator continues to receive kW.

### `ui/calculator_ahri_tab.py`

```python
class AHRITab(QWidget):
    values_changed: pyqtSignal
    profile_changed: pyqtSignal

    def __init__(self, parent=None, *, calculator_factory): ...
    def populate_profiles(self, profiles): ...
    def set_calculator(self, seer2_calc, hspf2_calc): ...
    def read_inputs(self) -> AHRIInputs: ...
    def calculate(self) -> str: ...
    def clear_errors(self) -> None: ...
```

- Owns SEER2 + HSPF2 tables, system-type radios, HSPF2 v3 derivation
  helpers, `_read_ahri_seer2_table_points`,
  `_read_ahri_hspf2_table_points`, `_read_ahri_seer2_point`,
  `_build_hspf2_v3_input`, `calculate_ahri`, `calculate_hspf2_v3`.

### `ui/calculator_result_panel.py` (Slice γ)

```python
class CalculatorResultPanel(QWidget):
    """Per-tab result/status panel.

    Replaces the window-level single result_label so each tab has its
    own result + status (matches IsoCspfSingleWidget's existing shape).
    """

    def set_result_text(self, text: str) -> None: ...
    def set_status(self, text: str, *, kind: str = "info") -> None: ...
    def clear(self) -> None: ...
```

### `ui/calculator_recompute.py` (Slice β)

```python
class DebouncedRecompute:
    """QTimer-based debounce wrapper.

    Subscribes to a model's ``values_changed`` and calls a callback on
    a single-shot timer. Used by EN14825Tab and AHRITab to wire
    auto-recompute without duplicating debounce logic.
    """

    def __init__(self, callback, *, interval_ms: int = 250): ...
    def connect(self, signal) -> None: ...
    def disconnect(self, signal) -> None: ...
    def trigger_now(self) -> None: ...
```

### `ui/calc_window.py` (shell after extractions)

```python
class CalculatorWindow(QWidget):
    def __init__(self): ...
    def init_ui(self): ...                # tabs, top-level button (demoted in γ)
    def on_calculate(self): ...           # dispatches to active tab.calculate()
    def _clear_all_errors(self): ...      # delegates to each tab.clear_errors()
```

- Shell holds `tab_iso` (`IsoCspfSingleWidget`), `tab_en`
  (`EN14825Tab`), `tab_ahri` (`AHRITab`), profile combo wiring stays in
  shell only to the extent of `scan_configs` plus the `populate_*`
  forward. Per-tab profile changes are owned by each tab.

## Dependency direction

```
calc_window.py
    │
    ├──> calculators_2point.IsoCspfSingleWidget   (ISO tab)
    ├──> calculator_en_tab.EN14825Tab            ──┐
    ├──> calculator_ahri_tab.AHRITab             ──┤
    │                                              │
    │   per-tab modules import:                    │
    │     retired spreadsheet table module  (model/view/factories)
    │     retired theme module              (tokens)
    │     ui.calculator_errors  (InputValidationError, get_float_val, styling)
    │     ui.calculator_recompute  (DebouncedRecompute)      [β]
    │     ui.calculator_result_panel.CalculatorResultPanel   [γ]
    │     core.calculators.dispatcher.create_calculator_for_profile
    │     core.calculators.profiles
    │                                              │
    └────────────────────────────────────────────  │
                                                   │
        core/                                      │
            calculator_*.py        <───────────────┘
            calculator_dispatcher.py
            calculator_profiles.py
```

- UI → core is one-way. Core never imports `ui/`.
- Per-tab modules do not import each other. The shell mediates.
- `ui.calculator_errors` is the only shared UI helper that the tabs
  share; it has no PyQt-specific dependencies beyond `QLineEdit`
  styling.

## Extraction order

Sliced for safety. Each slice ships independently with its own report.
Slice numbers continue from the action-model slices in design doc
`2026-05-22-calculator-action-model-alignment.md` so the overall plan
reads in one line.

### Slice ε — Extract `ui/calculator_errors.py` (recommended next)

- Move `InputValidationError`, `bind_error_reset`, `_get_float_val`,
  the error styling string (already token-bound in 108), and a small
  `parse_number` helper.
- `calc_window.py` imports the helpers. No behavioral change.
- Verification: full pytest. legacy Qt binding-bearing CI runs UI smoke; existing
  `_get_float_val` callers (`calculate_ahri`, `_build_hspf2_v3_input`,
  `_read_en_table_points_kw`, EN/AHRI input read) keep working through
  the import alias.

### Slice ζ — Extract `ui/calculator_en_tab.py`

- Move `init_en_tab`, `on_region_changed_en`, `_populate_en_profiles`,
  `_read_en_table_points_kw`, `_selected_scop_climates`, `calculate_en`
  to `EN14825Tab`. `calc_window.py` keeps the tab insertion and
  delegates `calculate_en()` → `self.tab_en.calculate()`.
- `EN14825Tab` exposes `values_changed` (forwarded from its
  `SpreadsheetTableModel` instances), preparing the Slice β wiring.
- Verification: full pytest. legacy Qt binding CI runs `tests/test_app_calculator_
  ui_smoke.py` EN smoke (9 tests including 109's standby-position
  smoke). Public attributes touched by smoke (`window.en_seer_group`,
  `window.en_scop_group`, `window.en_standby_group`,
  `window.input_widgets_en[...]`, `window.en_scop_climates[...]`) stay
  reachable as `window.tab_en.<attr>` and, where the smoke imports
  expect, as aliases on `CalculatorWindow` for backward compatibility.

### Slice η — Extract `ui/calculator_ahri_tab.py`

- Move `init_ahri_tab`, `on_region_changed_ahri`,
  `_populate_ahri_profiles`, `_load_hspf2_calc`,
  `_read_ahri_seer2_table_points`, `_read_ahri_hspf2_table_points`,
  `_read_ahri_seer2_point`, `_build_hspf2_v3_input`, `calculate_ahri`,
  `calculate_hspf2_v3` to `AHRITab`.
- Same alias strategy for smoke: `window.ahri_seer2_model` /
  `window.ahri_hspf2_model` / `window.input_widgets_ahri` /
  `window.input_widgets_hspf2` / `window.radio_hp` / `window.radio_ac`
  stay reachable.
- Verification: full pytest. legacy Qt binding CI runs `tests/test_app_calculator_
  ui_smoke.py` AHRI smoke (button click + HSPF2 required validation).

### Slice β (now downstream of ε/ζ/η) — AHRI/EN auto-recompute wiring

- Add `ui/calculator_recompute.py::DebouncedRecompute` and connect
  `EN14825Tab.values_changed` + `AHRITab.values_changed` to per-tab
  `calculate()` (with debounce). Demote window-level `계산 실행` button
  to optional "Recalculate now".
- Result text continues to land in the existing surface until Slice γ
  promotes per-tab result panels.

### Slice γ — Per-tab result/status surface unification

- Add `ui/calculator_result_panel.py::CalculatorResultPanel` and embed
  one instance per tab (`EN14825Tab`, `AHRITab`). Remove or reduce
  window-level `result_label`. `calculate_iso` no-op disappears
  (`IsoCspfSingleWidget` already owns its result panel; shell no
  longer dispatches to ISO).

### Slice δ — Error feedback alignment

- Replace `QMessageBox.warning` for `InputValidationError` with
  per-tab status banner via `CalculatorResultPanel.set_status(text,
  kind="error")`. Keep `QMessageBox.critical` only for truly
  unexpected exceptions, with truncated message + log routing.

## Non-goals

- Hong Kong HSPF UI surface (separate slice, kept after δ).
- Unit adapter expansion (ISO / KS / EN profiles).
- ML / inverse-search work.
- Calculator core / profile dispatcher / region config changes.
- Replacing `SpreadsheetTableModel` / `SpreadsheetTableView` /
  `IsoCspfSingleWidget`.
- Replacing 108 token foundation. Token registry stays in `ui/theme.py`.
- Rewriting smoke tests around private internals; smoke continues to
  use public window attributes (with alias forwarding when needed).
- Calculator design doc rewrites; this doc references but does not
  rewrite the table-shape design doc or the action-model design doc.

## Test strategy

- Each extraction slice ships green against
  `tests/test_app_calculator_ui_smoke.py` (legacy Qt binding environment) and
  `tests/test_calculator_schema_boundaries.py`.
- ε: pure helper. New unit tests in `tests/test_calculator_errors.py`
  for `get_float_val` / `parse_number` boundary cases; existing
  callers stay untouched.
- ζ / η: alias forwarding maintained on `CalculatorWindow` so existing
  smoke does not need to change. If forwarding becomes ugly, add a
  one-line smoke test confirming `window.tab_en` and `window.tab_ahri`
  exist with the expected widget type.
- β: drive `EN14825Tab.tables[...]._signal_emit_via_helper()`-style
  paths from the test, **not** wall-clock waits on the debounce
  timer. The Slice β report (post this design) covers test design.
- γ: per-tab `result_panel` objectName + layout-index smoke (same
  style as 109's `test_en_standby_group_is_positioned_above_*`).
- δ: monkeypatch `QMessageBox.warning` to verify it is no longer
  called for `InputValidationError` after δ.

## Status

- Decision: extract calculator UI into per-tab modules + shared
  helpers as described above.
- Slice α (`SpreadsheetTableModel.values_changed`): **completed**
  (111).
- Slice ε (`ui/calculator_errors.py`): **next implementation slice**.
- Slices ζ → η → β → γ → δ follow in order.
- Hong Kong HSPF UI surface: deferred until δ.
- Train/Predict UI small refactor: still scheduled with ML / inverse-
  search return (112).
