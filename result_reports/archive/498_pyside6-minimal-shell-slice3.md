# 498 PySide6 Minimal Shell Slice 3

## Goal

Add the minimal executable PySide6 Predict and Trainer shell windows while
keeping table, prediction, training, and mapping behavior deferred.

## Scope

- `PredictShell` is now a `QMainWindow` titled `HVAC V3 Predictor`.
- `PredictWorkspace` is now a minimal `QWidget` placeholder.
- `TrainShell` is now a `QMainWindow` titled `HVAC V3 Trainer`.
- `TrainShell` has three tabs: `Predict`, `Train / Model`, and `Data Mapping`.
- The `Predict` tab reuses `apps.predict.ui.workspace.PredictWorkspace`.
- Train/model and data-mapping tabs use placeholder panels only.

## Changed Files

- `apps/predict/app.py`
- `apps/predict/ui/shell.py`
- `apps/predict/ui/workspace.py`
- `apps/train/app.py`
- `apps/train/ui/shell.py`
- `apps/train/ui/train_model_panel.py`
- `apps/train/ui/data_mapping_panel.py`
- `result_reports/active/498_pyside6-minimal-shell-slice3.md`

## Verification

- `python3 -B -m py_compile app_predict.py app_train.py apps/predict/app.py apps/predict/ui/shell.py apps/predict/ui/workspace.py apps/train/app.py apps/train/ui/shell.py` - passed.
- `python3 -B -c "from apps.predict.ui.workspace import PredictWorkspace; from apps.train.ui.shell import TrainShell"` - passed.
- `QT_QPA_PLATFORM=offscreen` GUI construction smoke with both shells shown and
  closed by `QTimer` - passed with exit code 0.
- `python3 -B tools/check_code_structure.py` - passed with pre-existing
  calculator soft-limit warnings and code-map freshness warning.
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: minimal GUI shell skeleton only.
- Full manual GUI smoke with long-running `python app_predict.py` /
  `python app_train.py`: not run to avoid leaving windows/event loops open in
  the agent session. The short offscreen construction smoke covered shell
  instantiation.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `docs/architecture/pyside6_train_predict_architecture.md`: shell, tab, and
  PredictWorkspace reuse contract.
- `apps/predict/app.py`, `apps/predict/ui/shell.py`,
  `apps/predict/ui/workspace.py`: Predict shell implementation scope.
- `apps/train/app.py`, `apps/train/ui/shell.py`: Trainer shell and Predict tab
  reuse scope.

Structure / code map judgment:

- No common shell abstraction was introduced; predict/train shells remain
  separate per slice instruction.
- New panels are placeholder-only and do not execute training or mapping logic.
- Existing structure warnings are outside this slice.

## Known Risks

- Shells contain placeholder labels only.
- No input table, result table, prediction execution, training worker, or data
  mapping update behavior is implemented.

## Commit / Push

Commit is performed for this slice. Push is deferred until Arc closeout.
