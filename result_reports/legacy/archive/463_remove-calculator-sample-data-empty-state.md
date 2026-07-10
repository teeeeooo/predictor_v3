# 463 Remove Calculator Sample Data And Establish Empty State

## Goal

Remove automatic product-performance samples from calculator profile UIs while
retaining standard, option, and calculation-condition defaults and preserving
all existing explicit calculation/detail behavior.

## Scope

- Removed EN14825 SEER/SCOP, AHRI HSPF2, ISO/ISEER 2-point, Hong Kong
  CSPF/HSPF, and SASO T3 performance prefills.
- Deleted the isolated AHRI HSPF2 DEV sample owner.
- Moved reusable regression samples into a test-only owner.
- Added explicit blank-profile result/detail waiting behavior and focused guards.

## Non-goals

- No core, config, schema, fixture, golden, equation, batch contract, detail
  feature, or UI token behavior changed.
- No DEV/demo sample loader was added.
- The legacy calculator entrypoint is reserved for task 9.

## Task Results

- EN14825 keeps Tdesignc, Cd, Type, auxiliary zero-power defaults, SCOP climate
  selection, Tbiv, and TOL while Pdesign and performance matrices start blank.
- AHRI keeps SEER2 Type and HSPF2 region/options/numeric conditions while all
  HSPF2 A2/heating performance values start blank.
- ISO/ISEER, Hong Kong, and SASO performance tables start blank; SASO retains
  the optional 35 Min selection.
- Blank profiles now show input-waiting states instead of demo results or numeric
  input errors. Invalid non-empty input remains an error.
- Existing calculation/detail tests inject explicit samples through
  `tests/calculator_ui_sample_values.py`.

## Verification

- Empty-state contract: 3 tests passed.
- Focused EN14825/AHRI/ISO/Hong Kong/SASO regression superset: 163 collected;
  157 passed on the first run and six stale prefill-dependent EN expectations
  failed. Those tests were converted to explicit test samples, then both affected
  EN files passed all 48 tests. No production source changed after that run.
- `python3 -B tools/check_code_structure.py` passed hard rules; existing soft
  warnings remain for the large EN SEER/SCOP sections and SCOP adapter.
- Code map was stale after the preceding local commits and sample-owner removal;
  regenerated once, then `--check` reported fresh.
- `git diff --check` passed.
- Cached change gate is run after explicit staging.

## Reference Parity

The existing empty-state policy and the already-complete EN/AHRI detail panels
were used as the contract. Production sample values were not relocated to a new
runtime owner; only tests retain explicit fixtures.

## Changed Files

- calculator profile sections under `apps/calculator/ui/sections/`
- removed `apps/calculator/ui/ahri/hspf2_mock_data.py`
- focused calculator UI tests and `tests/calculator_ui_sample_values.py`
- `tests/test_ui_tk_calculator_empty_state.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/463_remove-calculator-sample-data-empty-state.md`

## Known Risks

- No user-triggered DEV/demo sample loader exists; adding one would require a
  separate contract that cannot alter the production empty state.
- GUI visual smoke is not repeated in this slice; widget contracts and existing
  focused UI suites cover the changed behavior.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Structure Warnings: existing soft limits only; this slice removes prefills and
adds only bounded waiting-state branches to the affected sections.

Read Ledger:

- calculator empty-state design policy and task 8 range; reason: preserve the
  approved keep/remove classification.
- affected profile constructors and recalculate paths only; reason: remove
  prefills and distinguish blank input from invalid input.
- focused profile/detail tests; reason: move demo dependencies to test fixtures.
- broad read: none.
- repeated read: EN tests after stale prefill expectations failed.

## Commit / Push

Task 8 is committed locally as one commit. Push is intentionally deferred until
task 9 completes the nine-task sequence.

## Project Memory Delta

No durable memory-seed change is needed: the existing empty-state policy already
owns the decision, and this slice implements it without changing the contract.

## Next Suggested Action

Audit `app_calculator_tk.py`, decide delete versus shim from repository evidence,
then perform the final nine-commit validation and single push.
