# Bundle 2A Requirements Excel Dependency Foundation

## Goal

Create a dependency declaration structure for the three app entrypoints and
record the Excel read/write dependency policy required before Arc 14D-R resumes.

## Scope

- Audit current dependency manifests and import evidence.
- Add app-scoped requirements files.
- Document Excel dependency rules for generated XLSX write/export and existing
  user Excel reads.
- Add app install guidance.
- Keep implementation out of scope.

## Non-goals

- No XLSX export implementation.
- No Excel import or `xlwings` read implementation.
- No Runtime Cascade, Data Mapping CRUD, Predict schema, Feature Catalog, ML,
  model, calculator, fixture, or golden expected changes.

## Slice Results

- 2A-0: OK - no existing project dependency manifest found; production import
  candidates classified; `openpyxl` evidence remains archive/test metadata only
  before this bundle; `xlwings` was not installed in the macOS dev environment.
- 2A-1: OK - created `requirements/base.txt`, `train.txt`, `predict.txt`,
  `calculator.txt`, `excel.txt`, and `dev.txt`.
- 2A-2: OK - recorded Excel dependency policy and updated Arc 14D state docs.
- 2A-3: OK - added README install entrypoint; `openpyxl` import passed;
  `xlwings` import is optional/manual in this macOS environment and is not
  installed.
- 2A-4: OK - report created; final validation and push recorded in terminal.

## Requirements Structure

- `requirements/base.txt`: common app baseline; currently no third-party
  package is shared by all three entrypoints.
- `requirements/train.txt`: Train/Admin runtime; includes `base.txt`,
  `excel.txt`, PySide6, and current ML training dependencies.
- `requirements/predict.txt`: Predict runtime; includes `base.txt`, PySide6,
  and current inference dependencies; excludes Excel dependencies.
- `requirements/calculator.txt`: Calculator runtime; includes `base.txt` only
  because Tkinter is stdlib.
- `requirements/excel.txt`: optional Excel dependencies: `openpyxl` and
  `xlwings`, with policy comments.
- `requirements/dev.txt`: development/focused validation; includes train,
  predict, and calculator requirements plus `pytest`.

## Excel Dependency Rule

- Existing user Excel read: `xlwings` in Windows user environments.
- DRM-sensitive user Excel read: do not directly parse user-provided workbooks
  with `openpyxl`; use the `xlwings`/Excel automation workflow unless a future
  task explicitly changes the policy.
- Generated predictor_v3 XLSX write/export: `openpyxl`.
- Arc 14D-R: approved to use `openpyxl` for generated read-only XLSX snapshot
  export.
- `xlsxwriter`: excluded from this decision.

## Environment Distinction

- macOS development: `openpyxl` import/write validation can be automated;
  `xlwings` automation is optional/manual because it depends on Excel
  installation, permissions, and license state.
- Windows user environment: `openpyxl` is allowed for generated XLSX
  write/export, and `xlwings` is allowed for existing user Excel read workflows.

## Changed Files

- `README.md`
- `docs/WORK_PLAN.md`
- `docs/development/dependencies.md`
- `docs/designs/2026-07-06-arc14d-data-mapping-xlsx-export-ui-polish.md`
- `docs/designs/README.md`
- `requirements/base.txt`
- `requirements/train.txt`
- `requirements/predict.txt`
- `requirements/calculator.txt`
- `requirements/excel.txt`
- `requirements/dev.txt`
- `result_reports/active/706_bundle2a-requirements-excel-dependency-foundation.md`

## Verification

- 2A-0 `git diff --check`: OK.
- 2A-0 `git status --short`: clean.
- 2A-1 `python3 -m pip install -r requirements/dev.txt --dry-run`: OK;
  actual install not performed.
- 2A-1 `python3 -m pip install -r requirements/train.txt --dry-run`: OK;
  actual install not performed.
- 2A-1 `git diff --check`: OK.
- 2A-2 path/link text check with `rg`: OK.
- 2A-2 `git diff --check`: OK.
- 2A-3 `python3 -c "import openpyxl; print(openpyxl.__version__)"`: OK,
  `3.1.5`.
- 2A-3 `python3 -c "import xlwings; print(xlwings.__version__)"`:
  optional/manual, failed with `ModuleNotFoundError` because `xlwings` is not
  installed in the macOS dev environment.
- 2A-3 `git diff --check`: OK.

- Final `git diff --check`: OK.
- Final `python3 -B tools/check_code_structure.py`: OK with pre-existing soft
  LOC/class warnings unrelated to this docs/requirements bundle.
- Final `python3 -B tools/code_checker/build_reference_map.py --check`: OK,
  freshness `FRESH`; informational commit/dirty-worktree notes only.
- Final `python3 -m pip install -r requirements/dev.txt --dry-run`: OK; actual
  install not performed.
- Final `python3 -m pip install -r requirements/train.txt --dry-run`: OK;
  actual install not performed.
- Final `python3 -c "import openpyxl; print(openpyxl.__version__)"`: OK,
  `3.1.5`.
- Final `python3 -c "import xlwings; print(xlwings.__version__)"`:
  optional/manual, failed with `ModuleNotFoundError` because `xlwings` is not
  installed in the macOS dev environment.

## Known Risks

- Requirements are intentionally unpinned because the project had no existing
  version pinning policy and no minimum-version evidence was introduced in this
  bundle.
- `requirements/train.txt` includes `requirements/excel.txt`; this is
  deliberate because Train currently writes XLSX training logs and owns the
  Arc 14D-R Data Mapping generated XLSX export follow-up.
- `xlwings` automation was not smoked on macOS.

## Scope Compliance

- production source changed: no.
- app behavior changed: no.
- XLSX export implemented: no.
- Excel import implemented: no.
- Runtime Cascade changed: no.
- unrelated refactor: no.

## Commit / Push

- 2A-0 commit: none; audit had no file change.
- 2A-1 commit: `bb9c426f` (`chore: add app requirements files`).
- 2A-2 commit: `3f7bee82` (`docs: record excel dependency policy`).
- 2A-3 commit: `a1fde310` (`docs: add dependency install guide`).
- 2A-4 report commit: recorded in terminal response.
- Push: final status recorded in terminal response with local and remote SHA.

## Next Suggested Action

Arc 14D-R - Resume XLSX Export + UI Polish.
