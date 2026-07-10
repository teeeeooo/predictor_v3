# KS HSPF Official Oracle Closeout Summary

## Goal

- Close out the KS C 9306 HSPF official oracle correction and archive the
  active implementation report.
- Preserve the official-calculator decision without reopening calculator code.

## Scope

- Covered source report:
  `result_reports/active/650_ks-hspf-load-line-intersection-golden.md`
- Implementation commit:
  `8e98c6c48076cbdc448e34e828c77c9881dac33f`
- Changed implementation files in the covered work:
  `core/calculators/standards/ks_c9306.py`,
  `tests/helpers/iso16358_hspf_samples.py`,
  `tests/test_iso16358_hspf_validation.py`

## Outcome

- KS C 9306 HSPF official total and bin-level oracle now passes.
- The fix preserved CSPF, ISO16358 HSPF, AHRI/EN calculators, public schema,
  `korea.json` schema, and official expected values.
- No direct bin-energy override or arbitrary correction factor was added.

## Effective Ratio Decision

For `round_test_values=true`, KS HSPF non-max frost curves use
rounding-aware effective defrost/no-frost ratios derived from rounded maximum
defrost anchors:

- capacity effective ratio: `4165 / 4665`
- power effective ratio: `1604 / 1700`

This resolved the remaining mismatch after the `rated_maximum` branch fixes.

## Verification

Covered implementation validation:

- `python3 -m py_compile core/calculators/standards/ks_c9306.py`: OK
- `python3 -m pytest tests/test_iso16358_hspf_validation.py -q`: OK, 40 passed
- `python3 -m pytest tests/test_iso16358_hspf_validation.py tests/test_iso16358_hspf_official_exact_golden.py -q`: OK, 57 passed
- optional KS oracle set: OK, 59 passed
- `python3 -B tools/check_code_structure.py`: OK with existing warnings
- `git diff --check`: OK

Closeout validation:

- pytest not run because this closeout is docs/report lifecycle only.

## Deferred Note

- PRH `Pheater * frunning` remains intentionally unimplemented. It is
  non-impact for the current no-auxiliary-heater official oracle and should be
  handled as a separate schema/API task if future auxiliary-heater models need
  official KS coverage.

## Next Action

- Resume Arc 13.5 Feature Catalog Editor Design Gate.

## Memory Seed

- Registered summary-level decision for the KS C 9306 HSPF frost effective
  ratio in `result_reports/memory/project_memory_seed.md`.
