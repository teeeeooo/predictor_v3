# 283 Windows Parity Test Closeout

## Goal

Record the Windows execution result for the controller switch parity test
foundation and decide whether the controller switch pilot implementation
can proceed.

## Scope

- Documentation-only closeout.
- No code or test modifications.

## Excluded Scope

- No production code changes.
- No test file changes.
- No controller switch implementation.
- No map regeneration.

## Windows Test Command

```
python -m pytest tests/test_ui_tk_metric_input_table_controller_parity.py -rs -vv
```

## Result

| Run | Passed | Skipped | Failures |
|-----|--------|---------|----------|
| 1st | 13 | 2 | 0 |
| 2nd | 13 | 2 | 0 |

- Python version: `3.14.5`
- Result is stable across two runs; not treated as flaky.

## Skip Reason

Two tests skipped due to local Tcl/Tk install/path issue:
- `Tk not available: Can't find a usable tk.tcl`
- `Tk not available: Can't find a usable init.tcl`
- Message includes `This probably means that Tcl wasn't installed properly.`

This is an environment configuration issue, not a code defect.

## Readiness Decision

- **Assertion failures: 0**
- **Readonly paste corrected test included in the 13 passed.**
- **No production code changes in 281/282.**
- **Remaining skips are local Tcl/Tk environment issue under Python 3.14.5.**

**Decision: controller switch pilot is conditionally GO.**

**Condition:** pilot implementation must be followed by Windows manual smoke
to verify actual GUI behavior after the switch.

## Next

- Controller switch pilot implementation.
- Post-implementation Windows smoke required before marking switch complete.

## Risks

- 2/15 tests skip on Windows due to Tcl/Tk install issue.
- These skipped tests may cover attach/select scenarios that are already
  verified by the 13 passing tests and by existing batch table controller
  tests.
- Full coverage will only be confirmed after post-implementation Windows smoke.
