# 206 Calculator Tk Hong Kong CSPF Batch

## Goal

Implement the first `calculator_tk` batch mode slice for Hong Kong CSPF only. The new surface is a simple one-row-per-case repeated calculation table; it is not internal formula trace and not detail/bin trace.

## Preflight

- Branch: `main`.
- `origin/main` fast-forward check: already up to date.
- Design owner: `result_reports/active/205_calculator-tk-batch-mode-design-plan.md`.
- Existing single-case owner: `ui_tk/sections/hong_kong_cspf_section.py`.
- UI insertion point: the Hong Kong metric notebook in `ui_tk/tabs/iso16358_tab.py`.
- Boundary decision:
  - common batch model/table/controller owns row-per-case UI mechanics
  - Hong Kong CSPF spec/handler owns row-to-core mapping and result formatting
  - core calculator/profile/dispatcher path is reused unchanged

No blocker was found.

## Changed Files

- `ui_tk/batch_models.py`
- `ui_tk/batch_case_table.py`
- `ui_tk/batch_controller.py`
- `ui_tk/sections/hong_kong_cspf_batch_spec.py`
- `ui_tk/sections/hong_kong_cspf_batch_section.py`
- `ui_tk/tabs/iso16358_tab.py`
- `tests/test_ui_tk_batch_models.py`
- `tests/test_ui_tk_hong_kong_cspf_batch_spec.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/206_calculator-tk-hong-kong-cspf-batch.md`

## Batch Model / Surface Structure

- Added toolkit-neutral batch model primitives:
  - `BatchColumnRole`
  - `BatchRowState`
  - `BatchColumnSpec`
  - `BatchProfileSpec`
  - `BatchTableModel`
- Column roles distinguish `input`, `result`, and `status`.
- `BatchTableModel` stores text rows and only allows `set_results()` to write result/status columns.
- `BatchCaseTable` renders input columns as editable entries and result/status columns as read-only labels.
- TSV paste into input columns is supported; pasted rows can extend the table.
- `BatchCalculationController` runs explicit batch calculation and clears results.

## Hong Kong CSPF Handler

- Added `HongKongCspfBatchHandler`.
- Initial columns:
  - `Case`
  - `Declared`
  - `35 Full Cap`
  - `35 Full Power`
  - `35 Half Cap`
  - `35 Half Power`
  - `CSPF`
  - `CSEC`
  - `Status`
- Handler reuses:
  - `build_cspf_input()`
  - `resolve_profile_id("Hong Kong", "CSPF")`
  - `create_calculator_for_profile(profile_id="hong_kong_cspf")`
  - `summarize_cspf_result()`
- Invalid row input returns row-local `Status` and does not raise to abort the batch.

## UI Integration

- Added `HongKongCspfBatchSection`.
- Added a separate `CSPF Batch` tab after the existing Hong Kong `CSPF` tab.
- Existing single-case Hong Kong CSPF section remains unchanged and keeps immediate calculation.
- Batch uses explicit `Run Batch`.
- Batch provides `Clear Results` and `Add Row`.
- No import/export, graph, detail/bin schema, formula trace, or mock/demo row was added.

## Verification

Executed:

```text
python -m py_compile ui_tk/batch_models.py ui_tk/batch_case_table.py ui_tk/batch_controller.py ui_tk/sections/hong_kong_cspf_batch_spec.py ui_tk/sections/hong_kong_cspf_batch_section.py ui_tk/tabs/iso16358_tab.py
```

Result: passed.

```text
python -m pytest -q tests/test_ui_tk_batch_models.py
```

Result: `4 passed`.

```text
python -m pytest -q tests/test_ui_tk_hong_kong_cspf_batch_spec.py
```

Result: `3 passed`.

```text
python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py
```

Result: `24 passed`.

```text
python3 -B tools/check_code_structure.py
```

Result: exited `0` with existing warning:

```text
[W] ui_tk/sections/bin_detail_panel.py: file exceeds 400 LOC soft limit (437). Consider splitting before adding more responsibilities.
```

```text
git diff --check
```

Result: passed.

```text
git status --short
```

Result: only intended files changed before commit.

Not executed:

- `python app_calculator_tk.py`
  - Reason: `DISPLAY` is empty in this Codex environment, so GUI smoke requires user/Windows manual verification.

## Manual Smoke Needed

On Windows or a local GUI-capable host:

- Launch `python app_calculator_tk.py`.
- Select `Hong Kong`.
- Confirm existing `CSPF` tab still auto-calculates without `Run Batch`.
- Open `CSPF Batch`.
- Confirm starter row is a real case, not a demo/mock row.
- Click `Run Batch` and confirm `CSPF=4.939`, `CSEC=358.3`, `Status=OK`.
- Paste TSV values into input columns and run batch.
- Confirm invalid row input shows row-local `Status` while valid rows still calculate.
- Confirm `Clear Results` clears result/status cells without clearing inputs.
- Confirm `Add Row` adds an editable blank case row.

## Scope Compliance

- No calculator core formula changes.
- No profile id or dispatcher public behavior changes.
- No region config, fixture, or golden changes.
- No detail/bin schema, graph/export, internal formula trace, HSPF/EN/AHRI/KS batch, or C# WPF work.
- No `app_calculator.py` cleanup/deletion.

## Next Action

Run Windows/manual GUI smoke for the Hong Kong CSPF batch slice. If accepted, proceed to the common detail/bin result schema design.

## Commit / Push

- Final commit hash and push status are recorded in the terminal summary for this task.

## Project Memory Delta

```yaml
- type: decision
  topic: calculator_tk_hong_kong_cspf_batch_first_slice
  content: predictor_v3 adds calculator_tk Hong Kong CSPF batch mode as a separate explicit-run CSPF Batch tab using common batch model/table/controller boundaries plus a Hong Kong CSPF handler that reuses the existing profile resolver, dispatcher, input helper, and result formatter.
  keywords:
    - predictor_v3
    - calculator_tk
    - Hong Kong CSPF
    - batch mode
    - row per case
  assertionStatus: observed
  source: result_reports/active/206_calculator-tk-hong-kong-cspf-batch.md
```
