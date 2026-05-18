# Design Gate — Calculator Horizontal Table Input UI + Unit Boundary

> **Scope note.** This design doc is **calculator-specific**. It
> defines the AHRI / EN14825 table shape (columns, rows, unit
> labels), the ML W ↔ calculator-native unit boundary, and the
> migration order from the current vertical `QFormLayout` to a
> horizontal table. Spreadsheet-like behavior (copy/paste TSV,
> multi-cell paste, Delete clear, Ctrl+Z undo, Tab/Enter navigation,
> numeric validation, paste path isolation, 1-click editor lifecycle,
> `blockSignals` try/finally) is **not** owned here — it is owned by
> `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`. Every slice below
> implicitly follows that contract; do not duplicate its rules in this
> document.

## Goal

Two coupled design decisions for the calculator UI / adapter layer. No
implementation in this slice.

1. Replace the long vertical `QFormLayout` per-point input on the
   AHRI SEER2, AHRI HSPF2, EN14825 SEER, EN14825 SCOP tabs with a
   horizontal table input shaped like the existing ISO16358 layout
   (conditions across columns, `능력` / `전력` rows). UI implementation
   itself is deferred to follow-up slices.
2. Fix the unit boundary between ML / inverse-search and the
   calculator. ML stays in W canonical units; the calculator takes
   profile-native units (W, Btu/h, kW). Unit conversion is an adapter
   responsibility, not a calculator or core responsibility, and unit
   adapter implementation is deferred to a follow-up slice.

## Context

- Current `ui/calc_window.py` already has flat dicts
  `input_widgets_ahri`, `input_widgets_hspf2`, `input_widgets_en` built
  with `QFormLayout.addRow(...)` per cell. The forms grow long and the
  per-cell unit label is repeated for every row.
- ISO16358 CSPF and HSPF tabs already use a table-style input with
  conditions across columns; the AHRI / EN14825 tabs deviate from that
  pattern.
- AGENTS.md UI guardrail mandates `QTableView` + `QAbstractTableModel`
  + `QStyledItemDelegate` and forbids new `QTableWidget` /
  `setCellWidget` usage. A short-term `QTableWidget` shortcut is
  explicitly disallowed for the migration.
- The envelope adapter chain
  (`PredictedPointsEnvelope` → `CalculatorInputEnvelope` →
  `CalculatorResultEnvelope` → `RankingCandidateEnvelope`)
  documented in
  `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`
  defines per-point `capacity_unit` and `power_unit`, but does not yet
  pin which side is ML-canonical and which side is calculator-native.
  That gap is what task 3 fixes.

## Confirmed Decisions

### Table input UI

- Every AHRI / EN14825 table follows the global
  `docs/ui/SPREADSHEET_TABLE_CONTRACT.md`. The spreadsheet-like UX,
  copy/paste (TSV), multi-cell paste, Delete clear, Ctrl+Z undo,
  Tab/Enter navigation, numeric validation, paste path isolation,
  1-click editor lifecycle, and `blockSignals` try/finally rules are
  not restated here; the contract is the single owner.
- The new input surface for AHRI / EN14825 is a `QTableView` driven by
  a `QAbstractTableModel`. Each table is profile-shape-aware (column
  set is fixed by the calculator profile).
- Test conditions are columns; rows are `능력` and `전력`. Auxiliary
  parameters that are not per-condition (e.g. `t_off`, `t_on`,
  `defrost_*`, climate, design loads, standby powers) live in a
  separate compact `QFormLayout` next to the table, not as extra rows
  or columns.
- The unit column is intentionally not part of the table. Units are
  carried only on the row label or the table title because the
  calculator profile already pins the input units.

### Unit boundary

- ML / inverse-search uses W as the canonical capacity and power unit.
- Calculator profile-native units are fixed per standard:
  - ISO16358 / KS C 9306: capacity W, power W
  - AHRI SEER2 / AHRI HSPF2: capacity Btu/h, power W
  - EN14825 SEER / SCOP: capacity kW, power kW
- Manual UI input is interpreted as profile-native (the unit on the row
  label is the truth).
- `ml_prediction` source PredictedPointsEnvelope payloads are
  interpreted as W canonical regardless of target profile.
- Unit conversion happens in a future adapter (e.g. a
  `core/calculator_unit_adapter.py`); calculator core, UI table model,
  and ML callers do not perform unit conversion.
- Adapter envelopes will eventually carry a
  `units_trace = {source_units, target_units, conversion_applied}`
  marker so envelope consumers can verify the conversion path. The
  envelope schema change is deferred to the adapter slice.

## Core vs Handler Boundary

| Item | Core / Calculator | Adapter / UI / ML | Reason |
| --- | --- | --- | --- |
| Test point unit interpretation | Native unit per profile, fixed | Adapter converts ML W → profile-native | Calculator never sees mixed-unit input. |
| Per-cell unit on UI | Only on row label / table title | Per-cell unit chooser forbidden | Unit is a profile property, not a per-cell variable. |
| Auxiliary inputs (`t_off`, climate, design loads) | Calculator argument | Separate compact form, not the table | Table is restricted to per-condition (capacity, power). |
| ML output unit | Always W | Adapter converts to profile-native | ML model lives outside calculator schema. |
| ML caller responsibility | No conversion | Must declare `source="ml_prediction"` so adapter applies conversion | Source vocabulary already locked. |
| Manual UI source | No conversion | Declares `source="manual_candidate"` and uses native unit | UI label is the unit contract. |

## Data Shape / API Boundary

### AHRI SEER2 table

| | A_Full | B_Full | B_Low | E_Int | F_Low |
| --- | --- | --- | --- | --- | --- |
| 능력 [Btu/h] | | | | | |
| 전력 [W] | | | | | |

- columns: `A_Full, B_Full, B_Low, E_Int, F_Low`
- rows: `능력 [Btu/h]`, `전력 [W]`
- no auxiliary form

### AHRI HSPF2 table

| | H01 | H11 | H12 | H1N | H22 | H2Int | H32 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 능력 [Btu/h] | | | | | | | |
| 전력 [W] | | | | | | | |

- columns: `H01, H11, H12, H1N, H22, H2Int, H32`
- rows: `능력 [Btu/h]`, `전력 [W]`
- compact auxiliary form: `t_off`, `t_on`,
  `defrost_t_test_minutes`, `defrost_t_max_minutes`

### EN14825 SEER table

| | A | B | C | D |
| --- | --- | --- | --- | --- |
| 능력 [W] | | | | |
| 전력 [W] | | | | |

- columns: `A, B, C, D`
- rows: `능력 [W]`, `전력 [W]`
- compact auxiliary form: `p_design_c_w` (W), standby powers (W)
- UI 입력 단위는 W로 통일하며, `core/calculator_en14825.py`
  (`calculate_seer`)는 kW를 그대로 받는다. `ui/calc_window.py`가
  EN core 호출 직전 W → kW (1/1000) 변환을 수행한다.

### EN14825 SCOP table (multi-climate)

각 climate (Average / Warmer / Colder)는 개별 SCOP table + 보조
form (card) 한 벌을 갖는다. SCOP 계산은 사용자가 checkbox로 선택한
climate 만 순회하며 `calculate_scop(..., climate=climate_key)`를
반복 호출한다. 최소 1개 climate는 선택되어야 하고, 기본값은
Average만 checked 이다.

| | A | B | C | D | TOL | Tbiv |
| --- | --- | --- | --- | --- | --- | --- |
| 능력 [W] | | | | | | |
| 전력 [W] | | | | | | |

- columns: `A, B, C, D, TOL, Tbiv`
- rows: `능력 [W]`, `전력 [W]`
- per-climate compact auxiliary form: `p_design_h_w` (W),
  `Tbiv_temp_c`, `TOL_temp_c`
- per-climate default temp prefill (UI-only, 사용자 수정 가능):
  - Average: `Tbiv_temp_c = -10`, `TOL_temp_c = -11`
  - Warmer: `Tbiv_temp_c = 2`, `TOL_temp_c = -11`
  - Colder: `Tbiv_temp_c = -15`, `TOL_temp_c = -22`
- 공통 standby form (W): `p_to_w`, `p_sb_w`, `p_ck_w`, `p_off_w`
  (기본 prefill 0.0)
- UI 입력 단위는 W로 통일하고 `core/calculator_en14825.py`
  (`calculate_scop`)와 `data/region_configs/en14825_scop.json`은
  kW/core 기준을 유지한다. UI가 EN core 호출 직전 W → kW 변환을
  수행하고, region config는 수정하지 않는다.

### Unit boundary table

| Layer | Capacity | Power | Notes |
| --- | --- | --- | --- |
| ML / inverse-search canonical | W | W | Single canonical unit irrespective of target profile. |
| ISO16358 / KS C 9306 calculator | W | W | Matches canonical, no conversion. |
| AHRI SEER2 / HSPF2 calculator | Btu/h | W | Capacity converted from W with `W → Btu/h = W × 3.412141633`. |
| EN14825 SEER / SCOP calculator | kW | kW | Capacity and power converted from W with `W → kW = W / 1000`. |
| Manual UI input | Profile-native unit *except EN14825*: AHRI 능력 Btu/h, ISO16358/KS C 9306 W. EN14825 UI 입력은 W로 통일하고 UI 가 core 호출 직전 W → kW 변환을 수행한다 (core/region config는 kW 그대로). | 동일 | Row label is the unit contract, no per-cell unit chooser. |
| `ml_prediction` envelope input | W | W | Adapter must convert to profile-native before building CalculatorInputEnvelope. |

## Required Tests (future slices)

- Adapter unit conversion smoke: feed a `source="ml_prediction"`
  PredictedPointsEnvelope at W to each profile and confirm the
  resulting CalculatorInputEnvelope is in profile-native units.
- Adapter unit conversion fail-fast: ml_prediction with non-W input is
  rejected; manual_candidate with non-profile-native input is rejected.
- UI table smoke: AHRI SEER2 first-slice `QAbstractTableModel`
  populates `input_widgets_ahri`-equivalent dict shape so the
  calculator action does not regress.

## Migration / Refactor Path

The existing `input_widgets_*` dicts are not removed in one step. Each
profile migrates independently and the dict reads stay valid until the
profile-specific cutover is shipped.

1. **AHRI SEER2 table (first slice).** Add a new
   `AhriSeer2InputTableModel(QAbstractTableModel)` and replace only the
   AHRI SEER2 portion of the AHRI tab. Keep AHRI HSPF2 vertical form
   unchanged. The `input_widgets_ahri` dict keys for SEER2 are
   populated from the table model so `calculate_ahri()` keeps working.
2. **AHRI HSPF2 table.** Reuse the same model base class, swap the
   AHRI HSPF2 portion. Keep the auxiliary `t_off / t_on / defrost_*`
   inputs in a small `QFormLayout` next to the table.
3. **EN14825 SCOP table.** Add a `En14825InputTableModel` parameterized
   by profile metric. SCOP first because it has more columns; the
   compact auxiliary form already exists in `calc_window.py`.
4. **EN14825 SEER table.** Reuse the same model with the SEER
   profile-specific column set.
5. **Drop unused `input_widgets_*` dict keys.** Only after all four
   profiles are on the table model and the dict-style reads have been
   replaced by model-based reads.
6. **Wire the unit adapter.** After the table input migrations are
   complete (or in parallel as an independent adapter-only slice),
   introduce `core/calculator_unit_adapter.py` with profile-aware
   conversion driven by the source vocabulary
   (`ml_prediction` / `manual_candidate` / `fixture`).

## Non-goals

- No `core/calculator_unit_adapter.py` implementation in this slice.
- No `CalculatorInputEnvelope` field change in this slice.
- No ML caller wiring in this slice.
- No UI implementation, no `app_calculator.py` redesign.
- No calculator engine, region config, or expected/golden change.
- No change to the source vocabulary
  (`manual_candidate / ml_prediction / fixture`).

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Per-cell unit override sneaks back in for "convenience" | Breaks the unit boundary contract | Row label is the only unit surface; reviewer rejects any per-cell unit widget. |
| `QTableWidget` is used as a stop-gap | Violates AGENTS.md UI guardrail | All four slices must use `QAbstractTableModel`; review must check this. |
| Mixed dict / model reads during partial migration | Calculator action regresses | Each profile slice keeps existing dict keys populated from the model until the dict-style read site is also migrated. |
| ml_prediction at non-W slips into calculator | Wrong metric | Adapter is the only conversion site; envelope rejects mismatched units. |

## Implementation Slices

1. **Slice A — AHRI SEER2 table input only.** First slice; no other
   profile or adapter change.
2. **Slice B — AHRI HSPF2 table input.** After Slice A is stable.
3. **Slice C — EN14825 SCOP table input.** Separate `QTableView`
   instance, same model base.
4. **Slice D — EN14825 SEER table input.** Profile-specific column
   set.
5. **Slice E — Unit adapter.** New `core/calculator_unit_adapter.py`
   that takes a PredictedPointsEnvelope and emits a
   profile-native CalculatorInputEnvelope, with a `units_trace`
   metadata block.

## Next Codex Implementation Prompt

```text
Implement Slice A only.

- New module: ui/calc_table_model_ahri_seer2.py.
- New class: AhriSeer2InputTableModel(QAbstractTableModel) with fixed
  columns A_Full, B_Full, B_Low, E_Int, F_Low and rows 능력 [Btu/h],
  전력 [W].
- Replace only the AHRI SEER2 portion of input_widgets_ahri in
  ui/calc_window.py with a QTableView bound to the new model.
- Keep AHRI HSPF2 vertical QFormLayout unchanged.
- Keep input_widgets_ahri keys A_Full_cap / A_Full_pow / ...
  populated from the model so calculate_ahri() keeps reading the same
  dict.
- Do not introduce QTableWidget or setCellWidget.
- Wrap blockSignals updates in try/finally.
- Do not touch the calculator core, region config, or expected values.
- Do not implement the unit adapter.

Tests:
- Add a smoke test that constructs the AHRI tab in offscreen PyQt and
  asserts the AHRI SEER2 dict keys are still readable by the existing
  AHRI calculate path after writing to the model.
```
