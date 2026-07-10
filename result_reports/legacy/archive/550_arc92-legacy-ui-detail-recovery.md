# Arc 9.2 Legacy UI Detail Recovery

## Goal

Inspect the retired legacy `ui/` implementation from Git history and identify
the detailed UX, behavior, and architecture evidence needed for the Arc 9.5
PySide6 visual/table parity slice.

## History Ref

- Inspected ref: `f8adf7075563838dc8217833b46242ad618fc3ae`
- This is the last known pre-retirement ref before the Arc 9.1 `ui/` deletion.

## Inspected Legacy Files

- `ui/base_model.py`
- `ui/base_view.py`
- `ui/spreadsheet_table.py`
- `ui/predict_window.py`
- `ui/train_window.py`
- `ui/theme.py`

## Key Findings

| File | Useful evidence | Do not carry forward |
| --- | --- | --- |
| `ui/base_model.py` | `COLUMNS`-driven headers, row/column shape, `input` vs `auto`/`result` editability, background color role, `DROPDOWN_TARGET` auto-fill, `source` / `mapping_key` relations, row-level refresh, `ml_feature` extraction, `ref_type` / `exp_type` one-hot conversion. | PyQt model ownership, direct mapping traversal in the table model, visible result mutation in the input model. |
| `ui/base_view.py` | Dropdown affordance while not editing, one-click popup, mapping-backed option lists, fallback `ref_type` / `exp_type` options, schema width and row height, dynamic dropdown update API. | Binding-specific delegate code and direct view/controller coupling. |
| `ui/spreadsheet_table.py` | TSV parse/format, CRLF/CR/LF normalization, trailing newline handling, empty input handling, selected rectangle copy, paste anchor, out-of-bounds paste drop, Delete/Backspace clear, Ctrl+C/V/Z, Tab/Enter navigation, invalid numeric background/tooltip, snapshot undo with max depth 64, idempotent signal/undo suppression, high-level `values_changed`. | Calculator-specific table factories and PyQt guard structure are evidence only for Train/Predict. |
| `ui/predict_window.py` | Model status, mapping/model load visibility, clear all, ODU dependent dropdown update, upstream ODU clear of dependent fin/pi/row/cond specs, `cond_specs` key composition, row skip when cooling capacity is blank, row-level error handling, result adapter targets. | TODO result placeholders, monolithic window/controller, direct model/mapping calls from widgets. |
| `ui/train_window.py` | Trainer/admin layout inventory: mapping update action, CSV selector, train action, model status/log surface, worker concept, log/finished signals, duplicate run prevention, success/failure handling. | PyQt thread implementation and direct script calls from UI. Worker/progress/cancel belongs to later arcs. |
| `ui/theme.py` | Semantic token categories for app/card/header/readonly/invalid/text/accent/status/border, fonts, spacing. | Legacy token module as owner; Arc 9.5 should consume `ui_common.visual_tokens` and add a PySide6 adapter if needed. |

## Gap Table

| Area | Already in current harvest | Missing / insufficient | Target |
| --- | --- | --- | --- |
| Visual/table parity | Split workspace, dropdown affordance, internal `case_id`, table gaps listed. | Schema width/row height, input/auto/result visual distinction, read-only but copyable cells, fallback dropdowns, dependent update boundary, invalid tooltip/status. | Arc 9.5 |
| Spreadsheet UX | Copy/paste/clear/undo/navigation named as gaps. | Exact TSV rules, paste bounds behavior, snapshot depth, idempotent operation behavior, click/type replace-on-type candidate, no business logic in table model. | Arc 9.5 table parity slice |
| Mapping/autofill | Dependent dropdowns mentioned broadly. | `DROPDOWN_TARGET`, `source`/`mapping_key`, IDU simple mapping, ODU cascade, upstream clear, `cond_specs` key composition, missing mapping status. | Arc 9.5 |
| Row-to-ML/results | Internal `case_id` and result lookup noted. | `ml_feature`, `ref_type`/`exp_type` one-hot, row skip/validation policy, model missing controlled status, row-level prediction errors, reject legacy TODO placeholders. | Arc 9.5 / Arc 10 boundary |
| Train admin | Feature inventory exists. | Tab-level inventory, dataset path, train action, log/status surface, worker idea placement. | Arc 11, with worker/progress detail in Arc 10/11 only if scoped |
| Visual tokens | `ui_common.visual_tokens` named. | Explicit evidence-only status for `ui/theme.py`, semantic token adoption checklist, PySide6 adapter gap. | Arc 9.5 |

## Next Slice Document Update Plan

- Move harvest from `docs/ui_ux/` to `docs/designs/`.
- Expand it into an Arc 9.5 acceptance reference with sections for table
  visual/interaction parity, spreadsheet behavior, mapping/autofill,
  row-to-ML/result parity, predict surface hierarchy, train admin inventory,
  token adoption, and deferred arc routing.
- Keep `docs/ui_ux/` as portable owner contracts only.

## Verification

- Legacy files were inspected directly via `git show <ref>:ui/<file>`.
- `git diff --check`: to be run before slice closeout.
- `git status --short`: to be run before slice closeout.

## Excluded Scope

- No production code changes.
- No legacy `ui/` restoration.
- No PySide6 implementation.
- No worker/progress/cancel or trainer execution implementation.
