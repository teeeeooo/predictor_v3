# Arc 14B-4 - Legacy Mapping CSV To JSON Rule Reconstruction Audit

Status: active reference

## Goal

Audit whether the old "single CSV to mapping.json" workflow can be
reconstructed from the current repository, current consumers, existing docs,
fixtures, and limited git history evidence.

## Background

Arc 14A/14B already established a generic Mapping Entity / Master Data boundary
and a read-only Data Mapping Manager surface. This audit does not implement
CSV import, export, CRUD, save, reload, runtime cascade, schema changes, or data
fixture changes.

The working direction before this audit was:

- do not return to a complex multi-file import/export package;
- if import survives, it must be a simple compatibility path, not the main edit
  workflow;
- prefer UI CRUD for final mapping edits;
- keep export as a read-only review snapshot unless a separate contract proves
  otherwise.

## Current mapping.json Read/Consume Flow

| Area | Current owner | Behavior |
| --- | --- | --- |
| Default path | `core.mapping.paths.MAPPING_JSON_FILE` | Points to `data/mapping.json` under the repo data directory. |
| Raw JSON load | `core.mapping.repository.load_mapping_data()` | Returns a dict from JSON. Missing or invalid JSON returns `{}` after a controlled message. |
| Predict cache/reload | `apps.predict.mapping.mapping_repository.PredictMappingRepository` | Caches the raw mapping dict for Predict controllers and can reload it. |
| Train/Data Mapping read adapter | `core.mapping.entity_runtime_adapter.load_runtime_mapping_catalog()` | Loads raw mapping data and adapts table-shaped sections into a read-only `MappingEntityCatalog`. Empty/missing data raises a provider error. |
| Train/Data Mapping UI | `apps.train.services.data_mapping_service.DataMappingService` and controller/panel | Uses the runtime provider by default, shows source/load errors, and leaves Import/Export/Save/Reload disabled. It does not parse raw JSON in the UI. |
| Predict dropdowns | `apps.predict.adapters.dropdown_option_adapter.DropdownOptionAdapter` | Reads section keys for base dropdown options, except `ref_type` and `exp_type`, which have hard-coded fallback options. |
| Predict autofill/cascade | `core.mapping.autofill.build_autofill_updates()` | Reads raw section/attribute keys for simple lookups, ODU dependent options, clears, and `cond_specs` composite lookup. |

Section impact summary:

| Section | Used by | Purpose | Missing impact | Test/fixture evidence |
| --- | --- | --- | --- | --- |
| `idu` | Dropdown adapter, autofill | IDU options and `ID Volume` lookup. | Empty IDU dropdown; `id_volume` clears on edit. | `tests/test_core_mapping_autofill.py`, `tests/test_apps_predict_mapping_controller.py`, runtime adapter tests. |
| `evap_index` | Dropdown adapter, autofill | Evap options and `Evap Area` / `Evap Volume` lookup. | Empty Evap dropdown; evap auto values clear. IDU Size filter is still not implemented. | Mock smoke generator/tests, schema rows. |
| `odu` | Dropdown adapter, autofill | ODU options and `OD Volume` lookup; ODU edit triggers dependent clear/options. | Empty ODU dropdown; dependent options/cond values clear. | Autofill, Predict controller, dropdown tests. |
| `compressor` | Dropdown adapter, autofill | Compressor options and `Comp EER` / `Comp cc` lookup. | Empty compressor dropdown; compressor auto values clear. | Dropdown and mock smoke tests. |
| `fin_type`, `pi`, `row` | Dropdown adapter | Optional base options for dependent dropdown columns before row-specific options exist. | Base dropdown options empty; row-specific ODU cascade can still supply options after ODU edit. | Mock mapping generator includes these sections. |
| `odu_cascade` | Autofill | ODU -> allowed fins, pis, rows. | Dependent dropdown options empty after ODU edit. | Autofill and Predict dropdown tests. |
| `cond_specs` | Autofill | Composite lookup from `odu + fin_type + pi + row` to `Cond Area` / `Cond Volume`. | Cond values clear unless a complete key exists. | Autofill and Predict controller tests. |
| `ref_type`, `exp_type` | Dropdown adapter fallback | Refrigerant / expansion-device options. | Current fallback still works without mapping sections. | Dropdown adapter fallback tests. |
| `Sheet1` | No current runtime consumer | Produced by the current CSV branch of the converter. | Data Mapping UI can display it as a generic section, but Predict dropdown/autofill does not use it. | Current `core.mapping.update` CSV branch. |

## Expected mapping.json Shape

The current runtime expects a top-level JSON object where each useful section is
a dictionary of row key to row value. Row values are usually dictionaries of
attribute key to scalar value, though `odu_cascade` uses list values and the
read adapter preserves those as visible values.

| Section | Row key meaning | Value shape | Nested/list | Derived key | Evidence |
| --- | --- | --- | --- | --- | --- |
| `idu` | IDU option/code | `{"ID Volume": number}` plus optional future attributes such as `Size`. | Scalar values. | No. | Schema/autofill tests. |
| `evap_index` | Evap index option | `{"Evap Area": number, "Evap Volume": number}` plus optional `Size`. | Scalar values. | No. | Schema rows, mock mapping. |
| `odu` | ODU option/code | `{"OD Volume": number}`. | Scalar values. | No. | Schema/autofill tests. |
| `compressor` | Compressor option/code | `{"Comp EER": number, "Comp cc": number}`. | Scalar values. | No. | Schema rows, mock mapping. |
| `fin_type`, `pi`, `row` | Option value | Usually `{}`. | Empty dicts. | No. | Mock mapping. |
| `odu_cascade` | ODU option/code | `{"Available_Fins": [...], "Available_Pis": [...], "Available_Rows": [...]}`. | Lists. | Yes, generated from ODU spec rows by the Excel converter. | `core.mapping.update`, autofill tests. |
| `cond_specs` | Composite `"{odu} {fin} {pi} {row}"` | `{"Cond Area": number, "Cond Volume": number}`. | Scalar values. | Yes, composed by runtime converter/autofill logic. | `core.mapping.update`, autofill tests. |

Important mismatch: the current runtime shape above is not the same as the
legacy wide fixture headers. The fixture has headers such as `Volume`,
`Evap area`, `EER`, `cc`, and a separate `Cond Index`; current consumers expect
`ID Volume`, `OD Volume`, `Evap Area`, `Comp EER`, `Comp cc`, and compose
`cond_specs` keys as `ODU Fin Pi Row`.

## Legacy CSV/Script Evidence

Evidence found:

- `scripts/update_mapping.py` exists and calls `core.mapping.update.update_mapping_to_json()`.
- The original initial script had the same broad behavior before it moved into
  `core.mapping.update`: Excel/CSV accepted, ODU sheet special-cased, other
  sheets converted by first column.
- For `.xlsx`/`.xls`, sheet names become top-level section keys.
- For `.csv`, the converter reads one DataFrame as `{"Sheet1": df_single}`.
  There is no current branch that splits a single wide CSV into `idu`,
  `evap_index`, `odu`, `compressor`, `odu_cascade`, and `cond_specs`.
- `tests/fixtures/mapping/mapping_tables_legacy_wide.csv` is the only current
  wide CSV evidence. It was added as compatibility evidence and docs explicitly
  say not to treat it as the canonical manager export format.
- Limited history file/object searches did not find a deleted dedicated
  single-wide-CSV parser, data/mapping.json sample, or header contract beyond
  the current converter and the fixture.

Evidence not found:

- No tracked `data/mapping.json` sample.
- No test that runs `mapping_tables_legacy_wide.csv` through a converter.
- No executable rule for blank-column section boundaries in the wide CSV.
- No authoritative alias table from fixture headers to current runtime keys.
- No evidence that `Cond Index` should override or equal the runtime
  `ODU Fin Pi Row` composite key.

## Single CSV Import Feasibility

Judgment: C - legacy single CSV import reconstruction is not feasible from the
current repo evidence.

The current consumer shape can be partially inferred, and the fixture makes a
human-readable old wide layout visible. That is not the same as reconstructing
a safe legacy conversion rule.

Potential column groups if a new compatibility parser were explicitly designed:

| Wide CSV block | Candidate output | Required aliases/decisions |
| --- | --- | --- |
| `Compressor`, `EER`, `cc` | `compressor` | Map `EER` -> `Comp EER`, `cc` -> `Comp cc`. |
| `Size`, `Evap Index`, `Evap area`, `Evap Volume` | `evap_index` | Map `Evap area` -> `Evap Area`; decide whether `Size` is required now or future-only. |
| `IDU`, `Volume`, `Size` | `idu` | Map `Volume` -> `ID Volume`; retain `Size` for future filter rules. |
| First `ODU`, `Volume` | `odu` | Distinguish the base ODU block from the later condenser-spec ODU block; map `Volume` -> `OD Volume`. |
| Second `ODU`, `Fin type`, `Pi`, `Row`, `Cond Index`, `Cond Area`, `Cond Volume` | `odu_cascade`, `cond_specs` | Decide whether to ignore `Cond Index`, validate it, or use it; current runtime composes `ODU Fin Pi Row`. |
| `Ref type`, `Exp type` | Optional `ref_type`, `exp_type` | Current dropdown fallback does not require these mapping sections. |

Validation could catch blank keys, duplicate row keys, missing required columns,
non-numeric spec values, missing ODU cascade lists, and missing complete
`cond_specs` combinations.

Validation would have difficulty catching wrong header alias decisions, swapped
duplicate `ODU` blocks, incorrect `Cond Index` semantics, stale dropdown
options that are technically present, and user edits that make cross-section
relationships plausible but wrong.

Because these rules would be new design decisions rather than recovered legacy
rules, import should not be the next implementation slice.

## Export Role Decision

Export should remain a read-only review snapshot, not an editable reimport
contract.

| Candidate | Strength | Weakness | Decision |
| --- | --- | --- | --- |
| Single CSV snapshot | Easy to open and share as one file. | Recreates the wide-layout ambiguity, duplicate headers, blank separators, and implicit section rules. Users may treat it as an edit contract. | Avoid as the primary export. |
| XLSX workbook snapshot | One file, separate sheets per section, easy human review, better fit for section-shaped data. | Requires spreadsheet tooling/dependency policy; Excel/Numbers type coercion and locked-down spreadsheet environments can still distort values. | Best human-review candidate when export is implemented. |
| Pretty JSON snapshot | Exact runtime shape, dependency-free, best for backup/debug. | Less friendly for non-technical review and comparison. | Good fallback or developer snapshot. |

The export label and documentation should say review/snapshot/backup, not
template/import/edit. A future implementation can offer a one-file XLSX review
snapshot and/or a pretty JSON snapshot, but should not promise that exported
files can be edited and imported back.

## Recommended Direction

C - legacy single CSV import restoration is not feasible enough to drive the
next implementation.

Recommended next action: design the Data Mapping Manager UI CRUD workflow using
the current `MappingEntityCatalog` boundary. Keep Import disabled or remove it
from the first editable workflow. Keep Export scoped to read-only snapshots.

## Excluded Direction

Do not implement or reintroduce in this arc:

- CSV import;
- export as an edit/reimport contract;
- mapping.json write/save;
- runtime reload;
- multi-file import/export packages;
- `groups.csv` / `fields.csv` / `data/<group>.csv`;
- normalized `values.csv`;
- schema, feature catalog, fixture, golden, UI, or production code changes.

## Open Questions

- If a real production `data/mapping.json` exists outside this checkout, compare
  it against the inferred shape before any future persistence work.
- If a business requirement later demands the old wide CSV, treat it as a new
  compatibility-parser design with explicit aliases, not as recovered legacy
  behavior.
- Decide the first read-only export snapshot format during the CRUD workflow
  design. XLSX workbook is the strongest human-review candidate; pretty JSON is
  the safest exact snapshot.

## Next Action

Arc 14B-5 - Data Mapping Manager UI CRUD workflow design with Import disabled
and Export scoped to read-only review snapshots.
