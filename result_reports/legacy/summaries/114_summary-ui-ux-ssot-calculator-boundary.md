# 114 — Summary: UI/UX SSOT Adoption + Calculator UI Module Boundary

## Summary Scope

Active reports 102~113. Workstream: UI/UX SSOT adoption,
Calculator UI audit + token foundation + EN layout polish, action
model decision (auto-calc unified), `SpreadsheetTableModel.
values_changed` signal foundation, Train/Predict drift audit, and the
final Calculator UI module boundary plan that gates the upcoming
refactor + recompute slices.

## Covered Reports

- `102_hong-kong-hspf-completion-audit.md`
- `103_hong-kong-hspf-profile-only.md`
- `104_iso-table-excel-like-behavior-patch.md`
- `105_active-documents-chain-audit-fix.md`
- `105_iso-result-table-copy-tsv.md`
- `106_ui-ux-ssot-adoption.md`
- `107_calculator-ui-ux-audit-against-ssot.md`
- `108_calculator-ui-design-token-foundation.md`
- `109_en14825-layout-polish.md`
- `110_calculator-action-model-micro-design.md`
- `111_spreadsheet-table-values-changed-signal.md`
- `112_train-predict-ui-architecture-drift-audit.md`
- `113_calculator-ui-module-boundary-plan.md`

## Key Decisions

- **UI/UX SSOT adoption** (106): `docs/ui_ux/` is the active UI/UX
  SSOT root. Legacy `docs/ui/SPREADSHEET_TABLE_CONTRACT.md` was
  **deleted**; legacy full text lives only at
  `docs/ui_ux/_source/SPREADSHEET_TABLE_CONTRACT_legacy_pyqt.md` as
  history.
- **Design token foundation** (108): `ui/theme.py` registers the
  toolkit-agnostic token names from
  `docs/ui_ux/02_DESIGN_TOKENS_AND_LAYOUT.md` and binds them to the
  current inline hex values conservatively. Pure Python — importable
  without PyQt5. Error-styling PoC applied at one site.
- **EN14825 layout polish** (109): standby section moved to the top
  as a compact horizontal row; single-input row widths capped; SCOP
  climate cards normalized with `theme_spacing` tokens. Core /
  W→kW / keys / defaults unchanged.
- **Action model alignment** (110): chose **Option A — auto-calc
  unified**. Slice order α → β → γ → δ for the wiring + result panel
  + error feedback. ISO already auto-calc.
- **`SpreadsheetTableModel.values_changed`** (111, Slice α): added
  high-level signal that fires exactly once per user-level operation
  (edit / paste / clear / undo) only when at least one cell changes.
  12 model-level tests added.
- **Train/Predict UI drift audit** (112): app entrypoints are thin;
  Predict/Train windows are ≤ 164 LOC and not yet monolith. Inline
  hex, ref/exp literal duplication between `base_model.py` and
  `base_view.py`, and ML-result-key magic strings in `predict_window.
  on_predict_clicked` are real but small. **Deferred** to a small
  refactor phase at the time of ML / inverse-search return — explicitly
  **not** mixed with the Calculator action-model slices.
- **Calculator UI module boundary** (113): completeness-first
  decision to plan the file split **before** Slice β. Target
  structure: shell `ui/calc_window.py` + per-tab
  `ui/calculator_en_tab.py` / `ui/calculator_ahri_tab.py` + shared
  helpers `ui/calculator_errors.py` / `ui/calculator_recompute.py`
  (β) / `ui/calculator_result_panel.py` (γ). Extraction order ε → ζ
  → η → β → γ → δ.
- **Recommended next implementation slice (forward-looking)**:
  Slice ε — extract `ui/calculator_errors.py`
  (`InputValidationError`, `parse_number`, `bind_error_reset`,
  `clear_error_style`, `apply_error_style`, `get_float_val`).

## Completed Work

- Hong Kong HSPF core/config/test + dispatcher smoke (102, 103).
- ISO input grid Excel-like behavior patch — Ctrl+C, Delete /
  Backspace clear, invalid mark, Enter / Shift+Enter / Tab /
  Shift+Tab (104).
- ISO read-only / result table TSV copy via
  `selected_cells_to_tsv` + `ReadOnlyCopyTableView` (105).
- Active-documents chain audit fix (105 variant).
- UI/UX SSOT adoption + legacy delete + active reference migration
  (106).
- Calculator UI/UX audit against new SSOT (107).
- `ui/theme.py` token foundation + 32 token tests + PoC application
  (108).
- EN14825 tab layout polish (109).
- Action-model micro-design with Option A decision (110,
  `docs/designs/2026-05-22-calculator-action-model-alignment.md`).
- `SpreadsheetTableModel.values_changed` Slice α + 12 model tests
  (111).
- Train/Predict UI drift audit + deferred refactor phase plan (112).
- Calculator UI module boundary design + architecture subsection
  + extraction order (113,
  `docs/designs/2026-05-22-calculator-ui-module-boundary.md`).

## Remaining Work

- Slice ε — `ui/calculator_errors.py` extraction (next).
- Slice ζ — `ui/calculator_en_tab.py` extraction.
- Slice η — `ui/calculator_ahri_tab.py` extraction.
- Slice β — AHRI / EN auto-recompute wiring built on top of ε / ζ / η.
- Slice γ — per-tab result/status surface unification (replaces
  window-level `result_label`; `calculate_iso` no-op removed).
- Slice δ — error feedback alignment (`InputValidationError` →
  per-tab status banner; `QMessageBox.critical` kept only for
  unexpected exceptions with truncated message + log routing).
- Hong Kong HSPF UI surface design / first slice (after δ).
- Unit adapter expansion — ISO / KS / EN profile in
  `core/calculator_unit_adapter.py` (non-UI, independent track).
- ML / inverse-search return prep.
- Train/Predict UI small refactor phase (scheduled with ML return).

## Architecture / Design Decisions

- UI/UX SSOT root and adapter docs live under `docs/ui_ux/`.
- `docs/architecture/project_architecture.md` §5 has new
  `Calculator UI module boundary` subsection (113) that names the
  per-tab + shared-helper structure and the principle that
  `calc_window.py` stays a shell.
- Two new design records:
  - `docs/designs/2026-05-22-calculator-action-model-alignment.md`
  - `docs/designs/2026-05-22-calculator-ui-module-boundary.md`
- Calculator-horizontal-table design doc (`2026-05-17-calculator-
  horizontal-table-input-ui.md`) was updated in 106 to inherit
  UI/UX SSOT.
- Calculator core, profile dispatcher, region config, result
  envelope, and ML adapter boundary contracts are unchanged in this
  workstream.

## Active Documents Sync Judgment

- 106 already added UI/UX SSOT rows (`docs/ui_ux/00..03`,
  adapters, legacy source) and migrated the calculator-horizontal
  design doc's outbound to the new SSOT paths.
- The two new design docs from 110 / 113 are not yet listed in
  `ACTIVE_DOCUMENTS.md` Design Records — they will be added in this
  lifecycle commit.
- No other active document owner / inbound / outbound relationships
  changed during 102–113. The result-report summary itself is not an
  active owner document and is not added to the inventory.

## Project Log Sync Judgment

- Latest `project_log.md` entry is "Hong Kong HSPF profile
  registration" (matching 102 / 103).
- 106 (UI/UX SSOT adoption), 110 (action model Option A decision),
  and 113 (Calculator UI module boundary plan) are **not** yet in
  `project_log.md`. They are architecture / boundary decisions worth a
  short append per `AGENT_TASK_ROUTER.md`'s Documentation Sync gate.
- One append is added in this lifecycle commit covering the three
  decisions above. Report archive moves alone are not logged.

## Archive Candidates

All 13 covered reports move to `result_reports/archive/` with
filenames and numbers unchanged.

## Active Reports After Maintenance

`result_reports/active/` is empty after this maintenance. No
in-progress reports remain.

## Next Suggested Actions

1. **Slice ε — extract `ui/calculator_errors.py`** (`Input
   ValidationError`, `parse_number`, `bind_error_reset`,
   `clear_error_style`, `apply_error_style`, `get_float_val`). Add
   `tests/test_calculator_errors.py` for helper boundaries.
2. Slice ζ — extract `ui/calculator_en_tab.py` with alias forwarding
   for existing smoke attributes (`en_seer_group`, `en_scop_group`,
   `en_standby_group`, `input_widgets_en`, `en_scop_climates`,
   `en_seer_model`, `en_seer_view`).
3. Slice η — extract `ui/calculator_ahri_tab.py` (`ahri_seer2_model`,
   `ahri_hspf2_model`, `input_widgets_ahri`, `input_widgets_hspf2`,
   `radio_hp`, `radio_ac`).
4. Slice β / γ / δ as per `2026-05-22-calculator-ui-module-boundary
   .md` and `2026-05-22-calculator-action-model-alignment.md`.
5. Hong Kong HSPF UI surface — after δ.
6. Unit adapter expansion (ISO / KS / EN) — non-UI, independent.
7. ML / inverse-search return + Train/Predict UI small refactor phase.

## Verification

- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q`
  → 3 passed.
- `python3 -B -m pytest -q` → 462 passed, 6 skipped, 23 xfailed
  (UI-related tests skipped in this environment because PyQt5 is not
  installed; CI / company-PC environment exercises them).
- Working tree was clean at start; this maintenance produces a
  single lifecycle commit covering summary + archive moves +
  `ACTIVE_DOCUMENTS.md` design record append + `project_log.md`
  append.
