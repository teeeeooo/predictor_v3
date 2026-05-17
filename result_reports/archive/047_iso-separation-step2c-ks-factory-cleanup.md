# 047_iso-separation-step2c-ks-factory-cleanup

## Goal
- Complete `iso_seperation_plan.md` Step 2c.
- Remove KS calculator compatibility state that existed only for the old ISO → KS delegation object-reference path.

## Scope
- `core/calculator_ks_c9306.py`
  - Remove `KSC9306Calculator.from_iso_calculator(...)`.
  - Remove `_iso_calculator_ref` field.
  - Update class docstring now that the compatibility factory is gone.
- `core/calculator_iso16358_legacy.py`
  - Change `_ks_calculator()` to instantiate `KSC9306Calculator` directly with `self.config`, `self.bin_hours`, and `self.Cd`.
- `project_log.md`
  - Record Step 2c result and decision.

## Non-goals
- No new ISO implementation.
- No legacy wrapper removal.
- No KS calculation formula change.
- No test expected/tolerance/xfail changes.
- No data, docs standard notes, workbook/reference files, or UI changes.
- No external web search was needed; this was internal dead-code cleanup after grep confirmation.

## Verification
- `rg -n "from_iso_calculator|_iso_calculator_ref" core tests ui || true` → 0 matches.
- `python3 -B -m py_compile core/calculator_ks_c9306.py core/calculator_iso16358_legacy.py` → passed.
- `python3 -B -m pytest tests/test_iso16358_hspf_ks_oracle.py -q` → `2 passed`.
- `python3 -B -m pytest tests/test_iso16358_hspf_validation.py -q -k ks_c9306` → `26 passed, 9 deselected`.
- `python3 -B -m pytest tests/test_iso16358_hspf_golden.py -q -k ks_c9306` → `8 passed, 24 deselected`.
- KS CSPF spot check:
  - `cspf=6.504`
  - `annual_cooling_kwh=1943.798`
  - `annual_power_kwh=298.852`
- `python3 -B -m pytest tests -q` → `269 passed, 16 failed, 13 xfailed`.

## Task Results
- `KSC9306Calculator` no longer carries an ISO calculator reference.
- Legacy ISO wrapper still preserves old private wrapper behavior by constructing a KS calculator directly from its config/bin-hours/Cd values.
- The expected full-suite baseline remained unchanged.

## Changed Files
- `core/calculator_ks_c9306.py`
- `core/calculator_iso16358_legacy.py`
- `project_log.md`
- `result_reports/active/047_iso-separation-step2c-ks-factory-cleanup.md`

## Known Failures / Risks
- Full-suite baseline still has 16 pre-existing ISO HSPF failures; this cleanup did not alter those expected failures.
- The legacy wrapper still contains KS delegation wrapper methods. That is intentional for Step 2 compatibility and should be removed only when legacy callers are retired or archived.

## Commit / Push
- source commit: `bd9919b refactor: remove KS ISO compatibility factory`
- source push: `origin/work/iso-separation-plan`
- report commit: pending at report creation time.
