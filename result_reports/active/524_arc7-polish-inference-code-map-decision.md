# 524 Arc 7 Polish - Inference Cleanup and Code Map Decision

## Goal

Clean up the small Arc 7 inference residue before starting Arc 8 calculator
package restructuring.

## Scope

- Removed the unreachable duplicate block after `build_input_df()` return in
  `core/ml/inference.py`.
- Confirmed root/new inference wrapper identity still holds.
- Checked code map freshness.

## Changed Files

- `core/ml/inference.py`
- `result_reports/active/524_arc7-polish-inference-code-map-decision.md`

## Code Map Decision

`python3 -B tools/code_checker/build_reference_map.py --check` still reports the
code map as stale. It was not regenerated in this slice because Arc 8 will move
calculator package ownership next; regenerating once after the structure move is
the cleaner lifecycle point. The stale state is recorded here and must be
handled in the Arc 8 focused smoke / code map refresh slice.

## Verification

- `python3 -B -m py_compile core/ml/inference.py core/predictor.py`: passed.
- Root/new `build_input_df` and `predict_row` identity smoke: passed.
- `python3 -B tools/code_checker/build_reference_map.py --check`: stale,
  recorded.
- `git diff --check`: passed.
- `git status --short`: checked.

## Excluded

- No behavior changes.
- No ML algorithm, feature, artifact, mapping schema, calculator behavior,
  PySide6 recovery, worker/progress, Trainer, dependency, data/model artifact,
  fixture, golden, or public contract changes.

## Next Action

Slice 2 - Calculator package shell and owner boundary.
