# 522 Arc 7 Mapping Package Move

## Goal

Move mapping path, repository, and pure update conversion ownership under
`core/mapping/` while preserving root/script compatibility.

## Moved Owners

- `core.mapping.paths`: actual owner for `MAPPING_JSON_FILE`.
- `core.mapping.repository`: actual owner for `load_mapping_data`.
- `core.mapping.update`: actual owner for `update_mapping_to_json`.
- `core.mapping.autofill`: documented target owner for ODU cascade,
  cond_specs lookup, and dropdown-to-auto-fill extraction.

## Compatibility

- `core.constants` re-exports `MAPPING_JSON_FILE`.
- `core.utils` re-exports `load_mapping_data`.
- `scripts.update_mapping` re-exports `update_mapping_to_json` and keeps
  `select_excel_file()` with PyQt file-dialog behavior outside core mapping.

## Excluded

- No mapping JSON schema changes.
- No mapping/autofill behavior extraction from legacy UI in this slice.
- No PyQt/PySide/Tk import inside `core/mapping`.
- No calculator, PySide6 Predictor recovery, worker/progress, Trainer, data,
  model artifact, fixture/golden, dependency, or public API behavior changes.

## Verification

- `python3 -B -m py_compile core/mapping/*.py core/constants.py core/utils.py scripts/update_mapping.py`: passed.
- Mapping path equality smoke: passed.
- Mapping repository identity smoke: passed.
- Script/core update function identity smoke: passed.
- `rg -n "PyQt5|PySide6|tkinter|QFileDialog|QApplication" core/mapping`: no matches.
- `git diff --check`: passed.
- `git status --short`: checked.

## Next Action

Slice 6 - Caller import policy, focused smoke, and Arc 7 closeout.
