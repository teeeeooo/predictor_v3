# 269 Windows Validation Closeout for Main Paste Policy / Validation Arc

## Goal

Close out the 265–268 main paste policy alignment / visible validation /
focused test correction arc after Windows validation.

## Scope

Report-only closeout. No code or test changes.

## Arc Summary

| # | Work | Status |
|---|---|---|
| 265 | Main paste policy alignment — raw text paste, visible invalid marking, execution blocking | Implemented |
| 266 | Focused test correction for validation/paint semantics | Test-only |
| 267 | Windows-discovered stale tests / import / event simulation issues fixed | Test-only |
| 268 | Callback-count failure audited; test expectation corrected after contract decision | Test-only |

## Windows Validation Result

| Suite | Passed | Skipped | Assertion Failures |
|---|---|---|---|
| `test_ui_tk_excel_like_table_controller.py` | 32 | 1 | 0 |
| `test_ui_tk_metric_input_table_validation.py` | 19 | 2 | 0 |
| `test_ui_tk_metric_input_table_adapter.py` | 23 | 1 | 0 |

**Skipped reason:** Python 3.14.5 Tcl/Tk `init.tcl` environment issue.

**Verdict:** No assertion failures. Paste policy arc is Windows-validated.

## Decision

- Main paste policy is aligned with the common UX contract.
- Invalid paste rejection is superseded by raw-text paste + visible marking +
  execution blocking.
- Remaining skipped tests are environment skips, not code defects.
- 265–268 arc is closed.

## Remaining Risks

- `metric_input_table.py` (445 LOC) and `excel_like_table_controller.py`
  (401 LOC) exceed the 400 LOC soft limit. Next addition must trigger helper
  extraction.
- `TkTableController` switch is still future work.
- Field-schema validation for text/categorical/required/range remains a future
  slice.

## Next

**AI-generated code risk checklist adoption audit.**

Assess how the current project guardrails (AGENTS.md, AGENT_TASK_ROUTER.md,
Design Gate, code structure checker) overlap with AI-generated code risk
patterns, and whether a short checklist can be adopted into existing owner docs
without creating a new large document.

## Project Memory Delta

- Main calculator table paste policy: raw text paste → field-level validation
  → visible invalid marking → execution blocking.
- Callback contract: batch operations emit 1 callback; individual text
  mutations emit 1 callback per mutation. `DebouncedAutoCalc` coalesces
  calculation triggers.
- Stable test contract for typing: final value and undo restore, not callback
  count.
