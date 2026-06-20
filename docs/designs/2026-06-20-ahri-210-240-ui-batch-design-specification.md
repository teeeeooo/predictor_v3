# AHRI 210/240 UI and Batch Design Specification

## Status

- Lifecycle: active reference for the AHRI 210/240 implementation arc.
- Design Gate: prompt-supplied boundary is sufficient.
- Next implementation slice: AHRI SEER2 main UI foundation.

This record is an implementation contract, not a global UI/UX rule owner.
Global table, layout, input/result, and architecture rules remain owned by the
active UI/UX and architecture documents.

## 1. Purpose

Define the approved main and batch UI contract for AHRI 210/240 SEER2 and
HSPF2 before implementation begins.

The implementation must preserve these principles:

- split the AHRI surface by metric: `SEER2` and `HSPF2`;
- use table-first engineering input surfaces;
- calculate automatically;
- keep final results compact;
- keep UI parsing/conversion/omission behind adapter or handler boundaries;
- reuse EN14825 table and batch visual/interaction patterns;
- do not add noisy user-facing batch diagnostics.

## 2. Scope

In scope:

- AHRI top-level calculator tab and metric navigation;
- SEER2 and HSPF2 main UI contracts;
- SEER2 and HSPF2 batch contracts;
- visible units and point ordering;
- optional-point editability and core omission policy;
- HSPF2 batch draft/active/superset snapshot behavior;
- owner boundaries, acceptance criteria, and implementation slices.

Out of scope:

- calculator equation or public result-key changes;
- config, schema, fixture, golden, or formula-parity changes;
- EN14825 behavior changes;
- file upload, XLSX, DRM, CI, pre-push, or packaging work;
- new batch export behavior beyond existing Copy/CSV utilities.

## 3. Navigation and Metric Boundary

The calculator top level adds one AHRI tab:

```text
ISO 16358 | EN14825 | AHRI 210/240
```

Inside AHRI, use a metric selector:

```text
SEER2 | HSPF2
```

Only the selected metric section is shown. `HP` and `AC` are not top-level
tabs; they are values of the SEER2 `Type` option.

The AHRI parent tab owns navigation and visible-section selection only. It does
not own calculation logic.

## 4. Shared Units and Behavior

| Quantity | Visible unit |
| --- | --- |
| Temperature | `°C`, one decimal place |
| Capacity | `Btu/h` |
| Power | `W` |
| SEER2 | `Btu/(W·h)`, displayed as `SEER2` |
| HSPF2 | `Btu/(W·h)`, displayed as `HSPF2` |

Shared behavior:

- input changes trigger automatic calculation;
- incomplete or invalid input leaves the final result blank;
- incomplete input does not open a modal error;
- main result surfaces do not add a status/message result field;
- visible Celsius values are converted at the adapter/handler boundary when
  the core requires another unit;
- UI sections do not contain unit-conversion or calculation policy.

`Cut Out` and `Cut In` are visible/input in Celsius. Implementations must not
rely on `-40` having the same numeric value in Celsius and Fahrenheit.

## 5. SEER2 Main UI

### 5.1 Layout

Use this vertical order:

1. compact calculation options;
2. SEER2 test conditions and data table;
3. compact SEER2 result table;
4. later batch action wiring when the batch slice is implemented.

The compact option surface contains:

```text
Type: HP / AC
```

- `Type` applies only to SEER2.
- Initial implementation default: `HP`.
- The handler maps the selected type to the existing core contract.

### 5.2 Point Table

Use this exact order:

```text
A_Full | B_Full | B_Low | E_Int | F_Low
```

| Row | A_Full | B_Full | B_Low | E_Int | F_Low |
| --- | --- | --- | --- | --- | --- |
| Condition / Temp | 35.0°C | 27.8°C | 27.8°C | 23.9°C | 17.2°C |
| Capacity [Btu/h] | editable | editable | editable | editable | editable |
| Power [W] | editable | editable | editable | editable | editable |
| EER2 | auto/read-only | auto/read-only | auto/read-only | auto/read-only | auto/read-only |

### 5.3 Result

Place a compact table below the input table:

```text
AHRI 210/240 SEER2 결과

| SEER2 |
|-------|
|       |
```

Do not create a right-side result panel. The final result contract emphasizes
`SEER2`; point EER2 values remain read-only table details.

## 6. HSPF2 Main UI

### 6.1 Layout

Use this compact order:

1. option bar;
2. numeric options table;
3. A2 Cooling Anchor mini table;
4. HSPF2 Heating Points table;
5. compact HSPF2 result table.

Avoid a tall field-per-row form.

### 6.2 Option Bar

```text
Region: IV     Measured: ☑ H42  ☐ H12  ☐ H22
Flags: ☐ H1N=H32 Hz  ☑ MinSpd
```

| Option | Default |
| --- | --- |
| Region | IV |
| H42 | ON |
| H12 | OFF |
| H22 | OFF |
| H1N=H32 Hz | OFF |
| MinSpd | ON |

Keep checkbox labels short. The `Measured:` and `Flags:` group labels provide
context.

### 6.3 Numeric Options

| Cd | Defrost Credit | Cut Out [°C] | Cut In [°C] |
| --- | --- | --- | --- |
| 0.25 | 1.0 | -40.0 | -40.0 |

Hidden handler defaults:

| Key | Default |
| --- | ---: |
| `defrost_t_test_minutes` | 90 |
| `defrost_t_max_minutes` | 720 |

Do not expose these hidden defaults in the UI.

### 6.4 A2 Cooling Anchor

A2 is a separate mini table between numeric options and heating points:

| Row | A2 |
| --- | --- |
| Capacity [Btu/h] | editable |
| Power [W] | editable |

A2 is required, entered directly, and never borrowed from SEER2 `A_Full`.
Keep both capacity and power to preserve the point tuple contract even if the
current core consumes only capacity.

### 6.5 Heating Points

Use this exact order:

```text
H01 | H11 | H1N | H2Int | H32 | H42 | H12 | H22
```

| Point | Temperature |
| --- | ---: |
| H01 | 16.7°C |
| H11 | 8.3°C |
| H1N | 8.3°C |
| H2Int | 1.7°C |
| H32 | -8.3°C |
| H42 | -15.0°C |
| H12 | 8.3°C |
| H22 | 1.7°C |

The table rows are:

```text
Condition / Temp
Capacity [Btu/h]
Power [W]
```

H42/H12/H22 editability is controlled by their checkboxes:

| Point state | UI cells | Core envelope |
| --- | --- | --- |
| ON | editable and required | include point key |
| OFF | read-only blank | omit point key entirely |

Never send disabled optional points as zero, empty text, or a placeholder tuple.

### 6.6 Result

Place a compact `HSPF2` result table below the heating table. Do not create a
right-side panel or EN14825-style climate result groups.

## 7. Shared Batch Matrix Contract

AHRI batch follows the EN14825 batch mental model.

- one logical case uses two physical rows: `Capacity`, `Power`;
- do not create a one-row-per-case wide table;
- result cells appear only on the first physical row;
- second-row result cells are blank/read-only;
- input changes trigger automatic calculation;
- impossible/incomplete calculations leave all result cells blank;
- do not expose `Status`, `Message`, `ERROR`, or `PENDING` columns;
- internal row state may exist only for controller behavior;
- existing Add/Remove, Copy, and CSV utilities may be reused.

Condition temperatures remain in compact column labels or a read-only strip.
Do not add a third physical `Condition / Temp` row to batch matrices.

## 8. SEER2 Batch

Common input:

```text
Type: HP / AC
```

Point order:

```text
A_Full | B_Full | B_Low | E_Int | F_Low
```

Preferred labels:

```text
A_Full (35.0°C)
B_Full (27.8°C)
B_Low (27.8°C)
E_Int (23.9°C)
F_Low (17.2°C)
```

Result columns:

```text
SEER2
```

Do not add EER detail columns in the first implementation.

Snapshot contract:

```text
AhriSeer2BatchSnapshot
- common_values
  - type
- cases
  - case input values
```

Results are recalculated after restore and are not durable snapshot state.

## 9. HSPF2 Batch

### 9.1 Common Inputs

Mirror the main HSPF2 option and numeric surfaces:

- Region IV;
- Measured H42/H12/H22 toggles;
- H1N=H32 Hz and MinSpd flags;
- Cd, Defrost Credit, Cut Out [°C], Cut In [°C];
- hidden defrost defaults 90/720 injected by the handler.

### 9.2 Matrix

Use this exact point order:

```text
A2 | H01 | H11 | H1N | H2Int | H32 | H42 | H12 | H22
```

A2 is case-specific and therefore belongs in the batch matrix rather than the
common input surface. A2 may omit a temperature suffix in its header.

H42/H12/H22 toggles control both cell editability and core input inclusion.
Disabled values remain recoverable in the superset case store, but their point
keys are omitted from the active core envelope.

### 9.3 Results

Use these exact result columns:

```text
HSPF2 | H12 | H22 | H42
```

`H12`, `H22`, and `H42` are source-display columns, not numeric input/result
values.

| Internal meaning | Display |
| --- | --- |
| tested/provided input | measured |
| equation-derived value | calculated |
| omitted and unused | not provided |

Expected value sets:

- H12: `measured` or `calculated`;
- H22: `measured` or `calculated`;
- H42: `measured` or `not provided`.

If required input is incomplete or invalid, leave `HSPF2`, `H12`, `H22`, and
`H42` blank for that case.

## 10. HSPF2 Batch Dynamic State

HSPF2 batch separates draft controls from the active applied matrix.

```text
AhriHspf2BatchSnapshot
- common_values
  - region
  - h42_enabled
  - h12_enabled
  - h22_enabled
  - h1n_h32_same_hz
  - min_spd
  - cd
  - defrost_credit
  - cut_out_c
  - cut_in_c
- active_options
  - last successfully applied matrix-defining options
- cases
  - superset input store, including hidden optional values
```

Required behavior:

- preserve draft common values even when apply fails;
- keep the current matrix/spec/handler on the last valid active options;
- preserve hidden H42/H12/H22 values across rebuilds;
- rebuild/reconfigure editability only after valid options are applied;
- recalculate results from common values and cases after restore;
- do not persist result values as primary snapshot state.

A lightweight `Apply Options required` state may be shown near common controls.
It is not a batch result column.

## 11. Ownership Boundaries

### Core

- owns existing AHRI equations and return behavior;
- does not own UI units, widgets, editability, or snapshot state.

### Adapter / Handler

- parses text and maps point tuples;
- converts visible Celsius inputs to core-native units when necessary;
- injects hidden defrost defaults;
- omits disabled optional point keys;
- maps source states to user-facing words;
- returns blank display values for incomplete/invalid rows.

### Main UI Section

- owns widget composition, input collection, auto-calc wiring, cell roles, and
  compact result rendering;
- does not embed equation, conversion, or omission policy.

### Batch Spec / Profile / Dialog

- headless specs own physical rows, point order, result columns, and cell roles;
- profiles own common controls and profile-local dynamic state;
- dialog wrappers own Toplevel lifecycle and snapshot handoff;
- parent sections own only button, dialog reference, snapshot, and cleanup.

## 12. Visual and Interaction Parity

Use current EN14825 SEER/SCOP main and batch implementations as reference parity
for:

- table colors and borders;
- editable, read-only, unavailable, and result cell treatment;
- selection and spreadsheet interaction;
- compact spacing and alignment;
- result-table placement;
- two-row batch layout and first-row-only result display;
- hidden-first dialog construction and lifecycle cleanup.

Do not introduce a new AHRI color palette. Global behavior remains governed by
the UI/UX SSOT and Tkinter adapter documents.

## 13. Supersession and Compatibility

This record supersedes the AHRI-specific table sketches in
`2026-05-17-calculator-horizontal-table-input-ui.md` where they conflict.
In particular, this contract adds/fixes:

- A2 as a standalone HSPF2 main mini table and first batch point;
- H42/H12/H22 optional-point behavior;
- final HSPF2 point order;
- hidden 90/720 defrost defaults;
- dynamic draft/active/superset batch state;
- source-display result columns.

The older record remains useful as table/matrix and unit-boundary history.

## 14. Required Implementation Acceptance

Each coding slice must include focused tests for its new boundary. At minimum:

- exact metric and point ordering;
- Celsius one-decimal labels;
- editable/read-only/result cell roles;
- auto-calc and blank-on-incomplete behavior;
- Type and HSPF2 option mapping;
- optional-point key omission, never zero/blank injection;
- hidden default injection;
- batch physical row structure;
- source-display mapping;
- snapshot close/reopen restore and hidden-value recovery;
- parent/dialog duplicate-open and cleanup lifecycle.

## 15. Approved Implementation Slices

1. **Design specification** — this document; no code changes.
2. **SEER2 main UI foundation** — AHRI tab, metric path, Type, point table,
   compact result; no batch or HSPF2.
3. **SEER2 batch** — static two-row matrix, handler/profile/dialog, parent
   wiring; result `SEER2` only.
4. **HSPF2 main UI foundation** — compact options, numeric table, A2 mini
   table, heating table, optional editability, HSPF2 result.
5. **HSPF2 batch** — dynamic matrix, optional omission, source columns,
   draft/active/superset snapshot, parent wiring.
6. **AHRI lifecycle closeout** — main/batch smoke, focused final superset,
   documentation and next-arc decision.

Do not combine slices 2–5 without a separately approved scope expansion.

## 16. Next Action

Implement the AHRI SEER2 main UI foundation only.
