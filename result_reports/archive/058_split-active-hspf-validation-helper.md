# 058 Split Active HSPF Validation Helper

## Goal

Remove active HSPF validation test dependency on `tests._legacy` diagnostic helpers.

## Scope

- `tests/test_iso16358_hspf_validation.py`
- `tests/helpers/iso16358_hspf_samples.py`
- `tests/helpers/__init__.py`

## Changed Files

- `tests/helpers/__init__.py`
- `tests/helpers/iso16358_hspf_samples.py`
- `tests/test_iso16358_hspf_validation.py`
- `result_reports/active/058_split-active-hspf-validation-helper.md`

## Verification

- `rg -n "tests\\._legacy" tests/test_iso16358_hspf_validation.py tests -g '!tests/_legacy/**'` returned no active test dependency.
- `python3 -B -m pytest tests/test_iso16358_hspf_validation.py tests/_legacy/test_iso16358_hspf_golden_diagnostic.py tests/_legacy/test_iso16358_hspf_h8_trace.py -q`
  - `60 passed, 17 xfailed`

## Known Risks

- The helper currently duplicates sample data from the legacy diagnostic file rather than moving every diagnostic use site at once. This keeps behavior stable and avoids changing legacy diagnostic xfail semantics.

## Commit / Push

- Source commit: `e0cafcc` (`test: split active HSPF validation helper`).
- Report commit: this commit (`report: record active HSPF validation helper split`).
- Push: deferred until final objective push.
