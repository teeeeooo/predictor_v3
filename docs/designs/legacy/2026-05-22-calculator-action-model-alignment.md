# Design Gate — Calculator Action Model Alignment

> **Scope note.** This micro-design fixes only the **action model**
> (when calculation runs, where results land, how errors surface) for
> the calculator UI. It inherits the UI/UX SSOT:
>
> - Common UX root: `docs/ui_ux/00_UI_UX_SYSTEM.md`
> - Design tokens / layout: `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md`
> - Table UX contract: `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
> - PyQt adapter: `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`
>
> It does not redefine table behavior, calculator core, profile
> dispatch, unit adapter, or ML. Layout polish is also out of scope —
> EN tab polish was done in 109 and AHRI/ISO polish is deferred.

## Background

After 106 (UI/UX SSOT adoption), 107 (calculator UI audit), 108
(design token foundation), and 109 (EN14825 layout polish), the
remaining recommended slice from 107 is **action model alignment**.
predictor_v3's calculator UI today mixes two action models inside one
window, which violates UI/UX SSOT §10 ("Buttons that look like
buttons but do nothing").

## Current behavior

Source: `ui/calc_window.py`, `ui/calculators_2point.py`,
`ui/spreadsheet_table.py`, smoke under `tests/test_app_calculator_
ui_smoke.py`.

| Tab | Action model | Trigger | Where result lands | Error path |
| --- | --- | --- | --- | --- |
| ISO (`IsoCspfSingleWidget`) | **auto-calc** | `ProfileInputGridModel.values_changed`, `declared_capacity.textChanged`, `chk_saso_min.toggled`, profile combo; `TwoPointTableModel` debounce 300ms | tab-local `RegionResultTableModel` + `status` label + detail tabs | inline cell BG / tooltip; no QMessageBox |
| AHRI SEER2 | **explicit button** | window-level `계산 실행` (`on_calculate` → `calculate_ahri`) | window-level `result_label` | `QMessageBox.warning` for `InputValidationError`, `QMessageBox.critical` for other |
| AHRI HSPF2 v3 | **explicit button** (chained inside SEER2 when system_type == HP) | same `계산 실행` | concatenated into `result_label` string | same |
| EN SEER | **explicit button** | `계산 실행` → `calculate_en` | `result_label` | same |
| EN SCOP (multi-climate) | **explicit button** | same | `result_label` (single-line concat of climates) | same |
| Hong Kong HSPF | profile/dispatcher only | — (no UI surface) | — | — |

Key code shapes:

- `ui/calc_window.py::on_calculate` dispatches by `currentWidget()`.
  `calculate_iso()` is a literal `pass` with the comment "2점식 ISO/
  ISEER 탭은 실시간 계산이므로 수동 계산 버튼 동작 안 함". → the
  primary action button is a no-op while ISO is the active tab. Direct
  SSOT §10 violation.
- AHRI / EN table models (`make_ahri_seer2_table_model`,
  `make_ahri_hspf2_table_model`, `make_en14825_seer_table_model`,
  `make_en14825_scop_table_model`) are produced by `ui/spreadsheet_
  table.py::SpreadsheetTableModel`. That model emits `dataChanged`
  on every set / paste / clear but does **not** expose a high-level
  `values_changed` signal. The ISO grid (`ProfileInputGridModel` in
  `ui/calculators_2point.py`) has its own `values_changed`
  `pyqtSignal`.
- `calculate_*` paths raise `InputValidationError` (a custom exception
  with a `widget` attribute that gets red-border styling) and other
  exceptions surface as a critical `QMessageBox`.
- Test protection:
  - `tests/test_app_calculator_ui_smoke.py` exercises **button-click
    paths** for AHRI (`calculate_button_displays_*`) and EN
    (`calculate_button_displays_*_result_text`). It does **not** test
    ISO; ISO is covered by the model-level golden under `tests/test_
    iso16358_*` and the spreadsheet-table tests.
  - `tests/test_spreadsheet_table_model.py` / `test_spreadsheet_
    table_view.py` cover TSV / paste / clear / undo at the common
    model level, not the auto-recompute path.

## SSOT criteria (extracted)

From `docs/ui_ux/00_UI_UX_SYSTEM.md`:

- §3 "Reduce required clicks for the primary task."
- §4 "Disabled buttons must look disabled. Do not silently no-op a
  fully-styled active button."
- §5 / §6 progress + completion + error feedback contract.
- §10 forbidden patterns include "Buttons that look like buttons but
  do nothing", "Long-running work on the UI thread without a progress
  dialog", "Stack traces shown directly to the end user".

From `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`:

- §10 keyboard-only workflow required. Users must be able to fill a
  table by paste / navigate / clear without touching the mouse.
- The contract is silent on auto vs explicit recompute; that decision
  is left to the project.

From 109 (`result_reports/active/109_en14825-layout-polish.md`):

- EN layout polish moved standby and aux rows but left the explicit
  `계산 실행` button untouched on purpose, deferring the action-model
  decision to this micro-design.

There is no conflict between the documents. The action-model decision
is project-level inside the bounds set by `00_UI_UX_SYSTEM.md` §3 / §4
/ §10.

## Option A — Auto-calc unified

- AHRI / EN tables emit a `values_changed`-equivalent signal; the tab
  re-runs `calculate_ahri` / `calculate_en` on edits, paste, clear,
  undo, profile switch.
- ISO behavior stays as today.
- The window-level `계산 실행` button is removed or demoted to a
  secondary "Recalculate now" action that is never required.
- Each tab gets its own result / status surface (extending what ISO
  already does); the global `result_label` either goes away or is kept
  only as a status banner.
- Errors land **inline** on the offending field (existing red-border
  styling) + per-tab status banner. `QMessageBox` is reserved for
  destructive / truly unexpected exceptions.

## Option B — Explicit action unified

- ISO loses auto-calc. `_recalculate` is only called when the user
  clicks `계산 실행`.
- AHRI / EN keep current behavior.
- ISO `RegionResultTableModel`, `status` label, debounce timer, and
  `values_changed` wiring are removed or guarded.
- A single window-level result surface (`result_label`) keeps a
  consistent display for all tabs; per-tab result panels collapse into
  one shared panel.

## Comparison

| Criterion | Option A (auto-calc) | Option B (explicit) |
| --- | --- | --- |
| Required clicks for primary task | 0 (just edit) | +1 every change |
| "Button does nothing" risk | gone (button removed/demoted) | gone (button always runs) |
| Result-stale risk | low — recompute is debounced | medium — user can forget to click |
| Error feedback | inline per-field + per-tab status banner | popup `QMessageBox` per click (today's path) |
| Progress need | recompute is ≪ 1s for current profiles → no progress UI required | same |
| Implementation surface | `SpreadsheetTableModel` needs a `values_changed` signal; `calc_window` re-wires AHRI / EN; per-tab result surface for AHRI / EN | invert ISO auto-calc; remove ISO debounce + `values_changed` connection; collapse per-tab result into shared `result_label` |
| Test impact | AHRI / EN smoke that asserts "button click → result_label" needs an extension path for "edit → tab-local result panel". Existing button click can stay as an explicit recompute fallback in option A. | ISO needs new smoke covering button-click recompute; existing ISO debounce-based behavior assumed by `tests/test_iso16358_*` golden indirectly relies on calculate path, not auto-trigger — likely no change. |
| Hong Kong HSPF UI surface fit | The HK HSPF surface inherits the same shared shell as ISO CSPF (already auto-calc). Option A is the natural fit. | HK HSPF would have to fight the existing CSPF auto-calc pattern of `IsoCspfSingleWidget`. |
| Independence from unit adapter / ML | Independent. Action-model alignment touches UI wiring only. | Independent. |

## Decision

**Option A — Auto-calc unified.**

Rationale:

- 00 §3 ("reduce required clicks") tilts toward auto. predictor_v3
  inputs are small (5 SEER2 cooling points × 2 rows, 7 HSPF2 heating
  points × 2 rows, 4–6 EN SCOP columns per climate × 2 rows, 2–4 ISO
  CSPF points). Recompute is essentially instantaneous.
- 00 §10 "buttons that do nothing" is presently violated **on the
  ISO tab** specifically — the `계산 실행` button is wired but
  `calculate_iso()` is `pass`. Option A removes the violation by
  removing the button (or demoting it). Option B fixes the violation
  by giving the ISO tab a real action, at the cost of forcing extra
  clicks across all tabs.
- The ISO tab already has the best result/status surface
  (`RegionResultTableModel` + `status` label + detail tabs). Option A
  promotes that pattern to AHRI / EN. Option B regresses ISO to the
  weaker single-line `result_label`.
- The Hong Kong HSPF UI surface (deferred to a later slice) plugs
  into `IsoCspfSingleWidget`, which is already auto-calc; Option A
  keeps that path coherent.
- Implementation risk is contained: AHRI / EN tables share a single
  factory (`SpreadsheetTableModel`), so adding one `values_changed`
  signal there propagates to every AHRI / EN tab. No calculator core,
  unit adapter, ML, or profile dispatcher changes are required.

Option B is rejected because:

- It costs every user a click per recompute.
- It regresses the strongest existing surface (ISO result panel).
- It does not improve the existing "raw stack trace in `QMessageBox.
  critical`" hazard noted in 00 §10; that's solved orthogonally in
  Slice δ below.

## Implementation slices

Each slice is independent. Layout polish, HK HSPF UI, and unit adapter
work are explicitly excluded from these slices.

### Slice α — `SpreadsheetTableModel.values_changed` signal

- Purpose: give AHRI / EN tables the same high-level "values were
  edited" signal that the ISO grid already has.
- Modify: `ui/spreadsheet_table.py`. Emit `values_changed` after
  `set_cell`, `paste_tsv`, `clear_cells`, and `undo`. Use
  `pyqtSignal()`.
- Include: signal declaration + emit points, plus a unit test in
  `tests/test_spreadsheet_table_model.py` that confirms the signal
  fires on edit / paste / clear / undo and does not fire on read-only
  operations.
- Exclude: any change to AHRI / EN calc paths, layout, or the
  button-click smoke tests.
- Preconditions: none.
- Verification: `pytest tests/test_spreadsheet_table_model.py -q`,
  `tests/test_spreadsheet_table_view.py -q`, full suite.

### Slice β — AHRI / EN auto-recompute wiring

- Purpose: connect AHRI SEER2 / HSPF2 and EN SEER / SCOP tables to a
  debounced recompute. Demote the window-level `계산 실행` button to
  an optional "Recalculate now" action; it must no longer be the only
  way to compute.
- Modify: `ui/calc_window.py`. Connect each AHRI / EN model's
  `values_changed` (from Slice α) to a per-tab debounced
  `_recalculate_ahri` / `_recalculate_en`. Refactor existing
  `calculate_ahri` / `calculate_en` into a "compute + render" pair so
  both the button path and the auto path call the same compute.
- Include: per-tab `RegionResultTableModel`-style or simpler
  read-only result surface (text label area scoped to the tab; not
  yet the polished card from Slice γ). Reuse existing strings.
- Exclude: ISO behavior, result panel polish (Slice γ), error panel
  redesign (Slice δ), HK HSPF UI, unit adapter, ML, layout token
  changes beyond what 108 / 109 already cover.
- Preconditions: Slice α.
- Verification: extend `tests/test_app_calculator_ui_smoke.py` so the
  AHRI / EN smoke pair covers both an "edit → debounced auto-recompute
  populates the tab-local result surface" path and the existing
  "click button → result populated" fallback. ISO smoke unchanged.

### Slice γ — Per-tab result / status surface unification

- Purpose: align the result / status surface across all four tabs so
  users see the same shape (result table / metric line + status
  label). The window-level single `result_label` is removed or
  reduced to a hidden fallback.
- Modify: `ui/calc_window.py`. Optionally introduce a small
  `_CalculatorResultPanel` helper to keep the AHRI / EN panel
  consistent with ISO's `RegionResultTableModel` + `status` label.
  Use `ui/theme.py` tokens (108) for spacing.
- Include: layout-level result surface only. No table contract / no
  validation rewiring.
- Exclude: ISO `RegionResultTableModel` internals (no change), AHRI
  / EN compute logic (Slice β already in place), error feedback
  policy (Slice δ).
- Preconditions: Slice β. Slice α only.
- Verification: smoke that each tab has its own `*_result_panel`
  attribute / objectName and that compute results land there instead
  of the window-level label. Full suite.

### Slice δ — Error feedback alignment

- Purpose: replace blocking `QMessageBox.warning` for input
  validation with the per-tab status banner already promoted in
  Slice γ; keep `QMessageBox.critical` only for unexpected
  exceptions. Address 00 §10 "stack trace shown directly to the end
  user" by funneling unknown exception strings through a short
  user-facing message and a debug log path.
- Modify: `ui/calc_window.py`. `InputValidationError` keeps the
  red-border per-field styling (108 token PoC already covers this);
  the popup goes away. `Exception` path keeps a critical popup but
  truncates to a short message and logs the trace.
- Include: error styling and message routing only. No copy changes.
- Exclude: validator changes inside `_get_float_val` /
  `_read_*_table_points` (path unchanged), table coloring contracts.
- Preconditions: Slice γ.
- Verification: smoke that an invalid input no longer raises a
  `QMessageBox.warning` (mock or stub the message box) and that the
  status banner shows the user message. Full suite.

## Non-goals

- Layout polish on AHRI / ISO tabs.
- Hong Kong HSPF UI surface.
- Unit adapter expansion (ISO / KS / EN profiles).
- ML / inverse-search work.
- Calculator core changes (formulas, golden, fixture, xfail).
- Profile / dispatcher / region config edits.
- Replacing the spreadsheet contract or PyQt adapter.

## Test strategy

- Slice α: pure unit test on `SpreadsheetTableModel.values_changed`
  using `QT_QPA_PLATFORM=offscreen`.
- Slice β: extend `tests/test_app_calculator_ui_smoke.py`. Existing
  button-click smoke tests stay; new "edit → debounced recompute"
  smoke tests use the new signal directly to avoid timing flakiness
  (drive the slot, not wall-clock waiting for the debounce).
- Slice γ: layout smoke (objectName + parent index checks, in the
  same style as 109's `test_en_standby_group_is_positioned_above_*`).
- Slice δ: monkeypatch `QMessageBox.warning` to assert it is no
  longer called for `InputValidationError`. Existing critical popup
  smoke can be added similarly.
- No screenshot tests. No pixel-perfect tests. No new dependencies on
  network or filesystem.

## Status

- Decision: Option A — Auto-calc unified.
- Implementation start: Slice α (next).
- Slices β / γ / δ follow in order. HK HSPF UI surface (a separate
  slice tracked in `docs/WORK_PLAN.md`) waits until Slice γ has
  shipped so that the new HSPF surface inherits the unified result
  panel pattern.
