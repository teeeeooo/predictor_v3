# Train/Admin UI/UX Overhaul — Governing Design

Status: proposed active governing design  
Date: 2026-07-14

## 1. Purpose

The current Train/Admin application has the required technical foundations, but
its information architecture and interaction design are not suitable for routine
engineering use. This design authorizes a substantial presentation-layer
overhaul, including replacement of existing panels where necessary, while
preserving established domain, application, runtime, schema, mapping, and ML
compatibility boundaries.

The target is a Train/Admin workspace in which an engineer can define data,
manage concrete mapping values, prepare and run training, understand readiness
and blockers, and hand resulting artifacts to Predict without manually
coordinating internal CSV and JSON contracts.

## 2. Product Surface

`app_train.py` continues to expose four main tabs:

1. Predict
2. Train / Model
3. Data Definition
4. Data Mapping

The Predict tab remains embedded and operational, but its internal UI/UX overhaul
is deferred.

The current program covers:

- common Train/Admin shell and status surfaces;
- Train / Model;
- Data Definition;
- Data Mapping.

CSV exchange remains part of Data Mapping rather than becoming a fifth tab.

## 3. Current Problem

The existing surfaces expose internal state and diagnostic structures more
prominently than the user's actual workflow.

- Data Definition behaves like a schema/projection report rather than a practical
  definition manager.
- Data Mapping cannot be properly designed or validated when `mapping.json` is
  absent.
- Some mapping projection and persistence paths still assume fixed attributes.
- Save, Reload, dirty state, validation, restart impact, retraining impact, and
  runtime readiness are fragmented or too implicit.
- Current tables do not yet provide spreadsheet-quality interaction for frequent
  data work.
- Repository-safe validation must rely on fixtures and mock data while real
  company data remains external.

Cosmetic restyling is not sufficient. The overhaul must improve task flow,
information architecture, state communication, recovery, and editing efficiency.

## 4. Confirmed Ownership

| Area | Owner responsibility |
| --- | --- |
| Data Definition | Defines columns, features, mapping requirements, mapping attributes, projection intent, and readiness impact. |
| Data Mapping | Edits concrete mapping rows and values for already-defined mapping structures. |
| `config/predict/schema.csv` | Primary Predict/Data Definition source under the active staged owner-switch design. |
| `config/ml/features.csv` | ML compatibility/projection contract under the active Arc 15 staging. |
| `data/mapping.json` | Runtime mapping value source of truth. |
| Mapping exchange files | Human-readable exchange and backup representation of the Data Mapping draft. |
| Legacy wide CSV fixture | One-time bootstrap/migration evidence only. |
| Train / Model | Training execution, artifact status, readiness visibility, and results workflow. |
| Predict | Runtime case entry and prediction workflow; internal UX redesign deferred. |

### Structural versus value changes

- Adding a mapping row or changing a value belongs to Data Mapping.
- Adding a mapping attribute or column belongs to Data Definition.
- Import must never silently create a previously undefined attribute.
- Unknown imported columns are blocked and redirected to Data Definition.
- Data Definition does not edit row values in `mapping.json`.
- Data Mapping does not become the structural schema owner.

Example:

```text
Add "Cond Inner Area"
    Data Definition: define the attribute and type/role
    Data Mapping: enter values for each ODU/Fin/Pi/Row combination
    CSV exchange: include the already-defined column
```

## 5. Data and Privacy Policy

The repository does not contain actual company mapping data, training data, or
production model artifacts.

Repository validation uses:

- schema fixtures;
- mapping fixtures;
- generated or curated mock training data;
- mock model/training workflows where needed.

Fixture values are synthetic, but their structure, relationships, names, and data
types match the real company-local contract.

Repository validation may prove:

- parsing and projection correctness;
- schema/mapping/training-header consistency;
- GUI workflow behavior;
- save/reload and export/import round-trip behavior;
- pipeline execution and artifact loading;
- feature name/order/type preservation.

It must not claim:

- real prediction accuracy;
- generalization performance;
- feature importance validity;
- production mapping completeness;
- production readiness from mock data alone.

Those require company-local validation.

## 6. Legacy Bootstrap Policy

`tests/fixtures/mapping/mapping_tables_legacy_wide.csv` is validation-only data
whose structure mirrors the real legacy source.

Its role is limited to:

```text
legacy wide fixture/source
    -> explicit legacy bootstrap parser
    -> editor/runtime-equivalent mapping representation
    -> existing validation
    -> fixture or local mapping.json
```

The legacy file is not the future edit format, normal Import format, or canonical
exchange format. The parser uses explicit tested rules rather than claiming to
reconstruct the lost historical script exactly.

`Cond Index` remains a recognized legacy-layout column but is only a historical
Excel VLOOKUP helper; bootstrap ignores its values. Condenser runtime identity is
Fin-Type-dependent: F&T uses ODU + Fin Type + Pi + Row, while PFC uses ODU + Fin
Type + Row and normalizes the fixed-width legacy Pi placeholder to absent.

## 7. Mapping Exchange Direction

The normal workflow is GUI-first:

```text
Data Definition defines structure
    -> Data Mapping edits values
    -> mapping.json save
    -> exchange export when needed
```

One export operation produces seven human-readable group CSV files plus one
sectioned bundle CSV:

```text
idu.csv
evap_index.csv
odu.csv
compressor.csv
refrigerant.csv
expansion.csv
odu_cond_specs.csv
<user-selected-name>.csv
```

The bundle file name is user-controlled. Its format is identified internally:

```csv
__FORMAT__,mapping_bundle_v1
```

Each section is explicit:

```csv
__SECTION__,compressor
Compressor,Comp EER,Comp cc
Comp A,3.5,13
```

`mapping_bundle_v1` is a format version, not a mandatory file name or user
revision counter.

### Initial import policy

- Import supports the sectioned bundle format.
- Import loads into an unsaved Data Mapping draft.
- Import never writes `mapping.json` automatically.
- The user reviews changes and validation before Save.
- Initial behavior is full-snapshot replacement, not automatic merge.
- Unknown sections, attributes, duplicate keys, invalid types, and unsupported
  format versions block import without mutating the current draft.
- Individual group CSV import and complex merge are deferred.

## 8. UX Principles

1. **Task first** — primary actions and tables represent the user's workflow.
2. **Explicit state** — clean, dirty, blocked, warning, saved,
   restart-required, retrain-required, and missing-resource states are distinct.
3. **Safe editing** — destructive actions explain their effect and issues point
   to the affected group, row, and field.
4. **Spreadsheet behavior** — editable tables follow the active spreadsheet UX
   contract.
5. **Intent-driven definition** — users express what they want; the UI previews
   schema, mapping, Predict, ML, restart, and retraining impacts.
6. **Progressive disclosure** — advanced metadata remains accessible without
   dominating the default view.
7. **Shared visual language** — tables, toolbars, status, issues, empty states,
   and dialogs use reusable common components suitable for later Predict reuse.

## 9. Phase Plan

### Phase 1 — Mapping/Data Foundation
Legacy fixture bootstrap, populated mapping state, dynamic mapping attributes,
and cross-fixture consistency.

### Phase 2 — Data Mapping UX Overhaul
Production-usable value editing, spreadsheet behavior, safe persistence, and
mapping exchange export/import.

### Phase 3 — Data Definition UX Overhaul
Intent-driven definition editing, mapping attribute creation, impact preview,
and controlled compatibility boundaries.

### Phase 4 — Train/Model and Shell UX Overhaul
Training readiness/execution/results, common shell state, and shared visual
components.

### Deferred — Predict UX Overhaul
Fresh audit and redesign after Train/Admin foundations are stable.

## 10. Delivery Model

Each phase uses a separate branch and Draft PR.

Within a phase:

```text
one independently verifiable slice
    -> implementation and focused validation
    -> one logical commit
    -> push to the phase branch
```

At phase completion:

```text
full phase validation
    -> required design/current-state updates
    -> closeout commit if needed
    -> Draft PR becomes Ready
    -> review and merge
```

The next phase begins from the merged previous phase. Slice is the commit/push
boundary; Phase is the merge boundary.

## 11. Compatibility Constraints

Preserve unless an explicit phase authorizes otherwise:

- controller/service/domain ownership;
- runtime `mapping.json` consumption;
- schema and ML compatibility contracts;
- feature names, order, and types;
- model artifact compatibility rules;
- independent Cooling and Heating models, including monotone constraints;
- atomic saves and backups;
- Predict mapping dropdown/autofill behavior;
- public APIs and diagnostics schemas;
- fixture/mock validation boundaries.

Presentation code may be replaced substantially. Data contracts must not be
changed merely to simplify UI work.

## 12. Global Acceptance

The program is complete when:

- each Train/Admin tab clearly communicates purpose and next action;
- mapping structure and values have enforced ownership;
- fixture-backed Data Mapping can be edited, validated, saved, reloaded,
  exported, and imported safely;
- a supported mapping attribute can be defined and populated without raw JSON;
- definition changes expose restart, retraining, training-header, and model impact;
- Train/Model clearly communicates readiness, execution, failures, and artifact state;
- common UI components are reusable for later Predict work;
- mock validation proves workflow and contract correctness without claiming real
  model quality.

## 13. Non-goals

- Calculator UI or formula changes.
- Production data inclusion in the repository.
- Automatic production model retraining.
- Predict internal redesign during Phases 1–4.
- Schema live reload unless separately designed.
- Silent definition creation from imported CSV columns.
- Reusing the legacy wide CSV as the future exchange format.
