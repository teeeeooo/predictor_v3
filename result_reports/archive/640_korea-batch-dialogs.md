# KOREA Batch Dialogs

## Goal

Implement Slice 4 of the KOREA calculator notebook sub-arc: CSPF/HSPF batch
table profiles and single-section batch button wiring.

## Scope

- Added KOREA CSPF and HSPF batch profile files under
  `apps/calculator/ui/batch_dialogs/profiles/`.
- Reused `BatchMatrixTable`, `BatchMatrixCalculationController`, and
  `BatchDialogShell`.
- Wired batch buttons and dialog handles into KOREA CSPF/HSPF sections.
- Added focused headless tests for KOREA batch specs, row handlers, controller
  integration, blank/invalid states, and no-guide batch output.

## Non-goals

- No batch framework rewrite.
- No guide values in batch output.
- No core/formula/config/profile/golden changes.
- No detail view implementation in this slice.

## Reference Parity

- Checked Hong Kong CSPF/HSPF batch profile patterns and existing batch matrix
  model/controller tests.
- Reuse outcome: reused the existing batch shell, matrix table, controller,
  dialog handle, export helper, and auto-calc behavior. KOREA-specific matrix
  specs and handlers remain local because CSPF/HSPF input contracts differ from
  existing Hong Kong profiles.

## Verification

- `python3 -B -m pytest -q tests/test_ui_tk_korea_batch_profiles.py tests/test_calculator_korea_cspf_usecase.py tests/test_calculator_korea_hspf_usecase.py`:
  OK, 14 passed.
- `python3 -B -m compileall -q apps/calculator tests`: OK.
- `python3 -B -m pytest -q tests/test_ui_tk_batch_matrix_models.py tests/test_ui_tk_batch_table_controller.py`:
  OK, 22 passed.
- `python3 -B tools/code_checker/build_reference_map.py`: regenerated
  `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- `python3 -B tools/check_code_structure.py`: OK with 9 pre-existing soft
  warnings outside the changed source files.
- `git diff --check`: OK.

## Structure Warnings

- No changed/new source file emitted a structure warning.
- KOREA CSPF/HSPF section files are near the 250 LOC soft planning threshold
  after adding batch wiring; Slice 5 detail wiring should avoid adding unrelated
  responsibilities.
- Existing warnings remain in calculator core/EN14825/batch hotspot files and
  were not part of this slice.

## change_gate

- owner_boundary: KOREA batch profile files own KOREA matrix specs, row
  handlers, dialog adapters, and dialog wrapper classes; KOREA sections only
  own button/handle event wiring.
- reuse_commonization: `local-with-reason`; shared batch framework owners were
  reused, while profile-specific input/result contracts stayed local.
- code_map_check: `regenerated`; `docs/code_map/CODEBASE_REFERENCE_MAP.md` is
  included in the diff.

## Known Risks

- Tk dialog open/preserve smoke was not run because this environment has no Tk
  display. Headless handler/controller tests passed.
- Section files are close to the soft split threshold before detail wiring.

## Commit / Push

- Commit: performed after report finalization; final hash is reported in the
  terminal response.
- Push: not run; push is reserved for final Slice 6 closeout.
