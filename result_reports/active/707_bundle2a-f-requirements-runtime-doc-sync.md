# Bundle 2A-F Requirements Runtime Doc Sync

## Goal

Correct the Bundle 2A requirements structure so Predict has the real model
inference runtime dependencies, then sync architecture, active-docs, packaging,
and Arc 14D-R documentation.

## Why Correction Was Needed

Bundle 2A created app-scoped requirements, but `requirements/predict.txt`
declared only PySide6, joblib, numpy, and pandas. Real Predict runtime loads
`model.pkl` with `joblib.load()` and calls stored model objects' `.predict()`.
Training stores XGBoost model objects, so Predict also needs the shared ML
runtime containing `xgboost` and `scikit-learn`. `optuna` remains training-only.

## Slice Results

- 2A-F0: OK - audited current requirements, ML training/inference evidence,
  architecture stale areas, active-docs gap, and packaging docs gap.
- 2A-F1: OK - added `requirements/ml_runtime.txt`; train and predict now share
  ML runtime; Predict excludes `optuna` and Excel dependencies.
- 2A-F2: OK - synced dependency owner docs, project architecture, active docs,
  packaging workflow/guide, Work Plan, and Arc 14D design/index records.
- 2A-F3: OK - report created; final validation and push recorded in terminal.

## Requirements Structure After Correction

- `requirements/base.txt`: shared app baseline; unchanged.
- `requirements/ml_runtime.txt`: Train/Predict shared ML runtime:
  `joblib`, `numpy`, `pandas`, `scikit-learn`, `xgboost`.
- `requirements/excel.txt`: optional Excel policy dependencies:
  `openpyxl`, `xlwings`; unchanged.
- `requirements/train.txt`: includes `base.txt`, `ml_runtime.txt`,
  `excel.txt`, PySide6, and train-only `optuna`.
- `requirements/predict.txt`: includes `base.txt`, `ml_runtime.txt`, and
  PySide6; excludes Excel dependencies and train-only `optuna`.
- `requirements/calculator.txt`: includes `base.txt`; unchanged.
- `requirements/dev.txt`: includes train, predict, calculator, and `pytest`;
  unchanged.

## Runtime Boundary

- Predict includes ML runtime: yes.
- Predict excludes training-only `optuna`: yes.
- Train includes ML runtime: yes.
- Train includes Excel dependency: yes.
- Calculator excludes ML/Excel dependency unless needed: yes.

## Excel Policy Confirmation

- Existing user Excel read: `xlwings`.
- Generated XLSX write/export: `openpyxl`.
- DRM-sensitive user Excel read avoids direct `openpyxl`: yes.
- macOS `xlwings` automation remains optional/manual.
- Windows user environment allows `xlwings` for user Excel reads and
  `openpyxl` for generated XLSX write/export.
- `xlsxwriter` remains excluded.

## Documentation Sync Summary

- `docs/development/dependencies.md`: added `ml_runtime.txt`, Train/Predict
  boundary, Predict model runtime rationale, and package-name policy.
- `docs/architecture/project_architecture.md`: updated Predict Schema v2
  projection, key-based dropdown compatibility, Data Mapping Manager editor
  owners, ref/exp one-hot boundary, Train/Predict runtime dependency boundary,
  and dependency/environment boundary.
- `ACTIVE_DOCUMENTS.md`: registered `docs/development/dependencies.md` as the
  dependency installation and Excel policy owner.
- `docs/agent_workflows/PACKAGING_WORKFLOW.md`: added app-scoped requirements
  as packaging dependency evidence and excluded `dev.txt` as default deployment
  source.
- `docs/PACKAGING.md`: added app requirements baseline and Predict binary
  dependency considerations.
- `docs/WORK_PLAN.md` and Arc 14D design/index docs: updated next condition to
  Bundle 2A-F and kept Arc 14D-R implementation pending.

## Validation

- 2A-F0 `git diff --check`: OK.
- 2A-F0 `git status --short`: clean.
- 2A-F1 `python3 -m pip install -r requirements/dev.txt --dry-run`: OK.
- 2A-F1 `python3 -m pip install -r requirements/predict.txt --dry-run`: OK.
- 2A-F1 `python3 -m pip install -r requirements/train.txt --dry-run`: OK.
- 2A-F1 `git diff --check`: OK.
- 2A-F2 path/reference `rg` check: OK.
- 2A-F2 `git diff --check`: OK.

- Final `git diff --check`: OK.
- Final `python3 -B tools/check_code_structure.py`: OK with pre-existing soft
  LOC/class warnings unrelated to this docs/requirements bundle.
- Final `python3 -B tools/code_checker/build_reference_map.py --check`: OK,
  freshness `FRESH`; informational commit/dirty-worktree notes only.
- Final `python3 -m pip install -r requirements/dev.txt --dry-run`: OK.
- Final `python3 -m pip install -r requirements/predict.txt --dry-run`: OK.
- Final `python3 -m pip install -r requirements/train.txt --dry-run`: OK.
- Final `python3 -c "import openpyxl; print(openpyxl.__version__)"`: OK,
  `3.1.5`.
- Final `python3 -c "import xlwings; print(xlwings.__version__)"`:
  optional/manual, failed with `ModuleNotFoundError` because `xlwings` is not
  installed in the macOS development environment.

## Excluded Scope

- No production Python source changes.
- No tests, data files, model files, fixtures, or golden expected changes.
- No XLSX export, JSON/XLSX export UI, Data Mapping UI polish, Predict invalid
  badge fix, Excel import, `xlwings` read, `openpyxl` write implementation,
  Runtime Cascade, Data Mapping CRUD, Predict Schema CSV, Feature Catalog, ML,
  model, or calculator logic changes.
- No dependency version pinning policy introduced.

## Known Risks

- Requirements remain unpinned by policy.
- Dry-run validation confirms package resolution but does not perform a clean
  environment install or PyInstaller package build.
- `xlwings` is not installed in the current macOS development environment;
  automation validation remains optional/manual.

## Commit / Push

- 2A-F0 commit: none.
- 2A-F1 commit: `026f10cd` (`fix: add ml runtime requirements`).
- 2A-F2 commit: `2f49e4b` (`docs: sync dependency architecture packaging`).
- 2A-F3 report commit and push: recorded in terminal response.

## Next Suggested Action

Arc 14D-R - Resume XLSX Export + UI Polish.
