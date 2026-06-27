# 519 Arc 7 Package Shell Boundary Imports

## Goal

Create importable package owner paths for Arc 7 without moving implementation
yet.

## Scope

- Added `core/ml/` package shell for inference, training, registry,
  preprocessing, features, and artifacts ownership.
- Added `core/predictor_schema/` package shell for predictor column schema
  ownership.
- Added `core/mapping/` package shell for mapping paths, repository, autofill,
  and pure update conversion ownership.
- Added `core/common/` package shell as the long-term common helper boundary.

## Changed Files

- `core/ml/__init__.py`
- `core/ml/inference.py`
- `core/ml/training.py`
- `core/ml/registry.py`
- `core/ml/preprocessing.py`
- `core/ml/features.py`
- `core/ml/artifacts.py`
- `core/predictor_schema/__init__.py`
- `core/predictor_schema/columns.py`
- `core/mapping/__init__.py`
- `core/mapping/paths.py`
- `core/mapping/repository.py`
- `core/mapping/autofill.py`
- `core/mapping/update.py`
- `core/common/__init__.py`
- `result_reports/active/519_arc7-package-shell-boundary-imports.md`

## Excluded

- No implementation move in this slice.
- No root caller import changes.
- No behavior changes, calculator movement, PySide6 recovery, worker/progress,
  Trainer work, dependency changes, data/model artifact changes, fixture/golden
  changes, or public API changes.

## Verification

- `python3 -B -m py_compile core/ml/*.py core/predictor_schema/*.py core/mapping/*.py`: run.
- owner import smoke: run.
- `git diff --check`: run.
- `git status --short`: run.

## Next Action

Slice 3 - ML implementation move.
