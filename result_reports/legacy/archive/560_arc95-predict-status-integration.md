# 560 - Arc 9.5 Predict Status Integration

## Goal

Connect Arc 9 mapping/validation/result state to visible Predict status
surfaces without moving business logic into table models or changing core ML,
mapping, or schema behavior.

## Changes

- Result table now reflects row result status:
  - `error` / `invalid`: invalid background;
  - `partial`: warning background;
  - `complete`: result background;
  - `ResultRow.message`: cell tooltip.
- Predict workspace bottom surface now includes a result badge summarizing:
  - pending;
  - running;
  - completed;
  - invalid input;
  - errors.
- Input edits now show a controlled status note when the mapping file is
  missing, while keeping autofill through `InputEditController`.
- Added tests for result error background/tooltip and result badge error state.

## Boundary Decision

The UI reads `PredictSession` / `ResultRow` state and renders status. Mapping
load/autofill still belongs to `InputEditController` and `core.mapping`;
prediction execution still belongs to `PredictionController` /
`PredictionService`. Table models do not call the mapping repository,
prediction service, training execution, or calculator logic.

## Excluded Scope

- No prediction worker/progress/cancel.
- No Trainer execution.
- No mapping Excel update execution.
- No model training execution.
- No ML algorithm, feature list, preprocessing formula, model artifact, mapping
  JSON schema, calculator formula/config/fixture/golden, or public result
  contract changes.

## Verification

- `python3 -B -m py_compile apps/predict/**/*.py core/mapping/*.py core/predictor_schema/*.py apps/common/**/*.py`: passed.
- `python3 -B -c "import app_predict"`: passed.
- `python3 -B -m pytest tests -k "predict or mapping or validation or result"`: 249 passed, 1012 deselected.
- `git diff --check`: passed.
- `git status --short`: checked before closeout.

## Known Remaining Gaps

- Detailed per-row status column/filter/search remains future result-surface
  polish.
- Worker/progress/cancel remains Arc 10.
- Real model success smoke remains blocked by absent `model/model.pkl` in this
  checkout.

## Next

Slice 6 - Train shell visual parity from design asset.
