# 497 PySide6 Entrypoint Wrapper Switch

## Goal

Switch the root Train/Predict entrypoints to thin wrappers around the new
PySide6 package app boundaries.

## Scope

- Updated `app_predict.py` to import and invoke `apps.predict.app.main`.
- Updated `app_train.py` to import and invoke `apps.train.app.main`.
- Removed root-level PyQt5 `QApplication` construction and legacy `ui.*`
  window imports from both entrypoints.

## Changed Files

- `app_predict.py`
- `app_train.py`
- `result_reports/active/497_pyside6-entrypoint-wrapper-switch.md`

## Verification

- `python3 -B -m py_compile app_predict.py app_train.py apps/predict/app.py apps/train/app.py` - passed.
- `python3 -B -c "import app_predict; import app_train; import apps.predict.app; import apps.train.app"` - passed.
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: entrypoint wrapper switch only.
- GUI smoke: executable PySide6 shell is introduced in the next slice.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `app_predict.py`, `app_train.py`: full root entrypoint replacement scope.
- `apps/predict/app.py`, `apps/train/app.py`: wrapper targets from Slice 1.

Structure / code map judgment:

- Existing root entrypoints became thinner and did not add new responsibilities.
- No common wrapper abstraction was introduced because each root entrypoint maps
  one-to-one to its package app.

## Known Risks

- The package app `main()` functions still raise until the minimal PySide6
  shell is implemented in Slice 3.

## Commit / Push

Commit is performed for this slice. Push is deferred until the Arc closeout per
the updated user request.
