# 408 EN14825 SEER batch partial row and label correction

## Goal

Align the SEER batch headless contract with automatic-calculation UX before
dialog wiring.

## Scope

- Changed partially entered required rows from `BatchRowState.ERROR` to
  `BatchRowState.PENDING`.
- Kept fully blank rows as PENDING and nonnumeric/adapter failures as ERROR.
- Changed A/B/C/D point labels to `A (35°C)` through `D (20°C)`.
- Updated focused tests and WORK_PLAN.

## Rationale

- During automatic entry, a partial row is incomplete rather than invalid and
  should not continuously increase the dialog invalid count.
- Matrix labels are user-facing once dialog wiring begins, so temperature units
  should be explicit before that surface is built.

## Non-goals

- No dialog, section, common-input, copy/export, or snapshot wiring.
- No adapter, core, config, result schema, or golden changes.
- No change to genuinely invalid numeric or calculation failure behavior.

## Verification

- `python3 -B -m py_compile apps/calculator/ui/en14825/seer_batch.py tests/test_apps_calculator_ui_en14825_batch.py`
  OK.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_batch.py` OK:
  8 passed.
- Code map regeneration not needed: no source symbol, module, import, or LOC
  structure changed.
- `git diff --check` OK.
- `git status --short` reviewed before commit.

## Project Memory Delta

- none.

## Next Action

EN14825 SCOP batch headless spec/handler foundation.
