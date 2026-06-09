# 292 Summary - Main Paste Policy and Visible Validation Arc (265-269)

## Covered Reports

Archived by this summary:

- `265_main-paste-policy-alignment.md`
- `266_correct-265-paste-policy-tests.md`
- `267_fix-windows-tk-failures-after-266.md`
- `268_audit-callback-count-failure.md`
- `269_windows-validation-closeout-paste-policy-arc.md`

Reports intentionally kept active: none for this arc.

## Arc Purpose

Align `MetricInputTable + ExcelLikeTableController` paste policy with the common table UX contract (raw text paste, visible invalid marking, execution blocking), fix tests for the new behavior, and close out after Windows validation.

## Completed Work

| # | Work | Status |
|---|---|---|
| 265 | Main paste policy alignment — raw text paste, visible invalid marking, execution blocking | Implemented |
| 266 | Focused test correction for validation/paint semantics | Test-only |
| 267 | Windows-discovered stale tests / import / event simulation issues fixed | Test-only |
| 268 | Callback-count failure audited; test expectation corrected after contract decision | Test-only |
| 269 | Windows validation closeout for paste policy arc | Report-only |

## Key Decisions

- Paste policy: allow raw text paste, mark invalid fields visibly, block calculation execution.
- `MetricInputTable.get_numeric_values()` now validates all fields and manages visible invalid state.
- `ExcelLikeTableController._paste()` removed atomic pre-validation; selection painting handles invalid background.
- Windows validation: 32+19+23 tests passed with only Tcl/Tk environment skips.

## Remaining Next Actions

- Main table migration candidate check (report 262, kept active).
- Controller switch expansion (blocker cleared after 291).

## Superseded / Corrected Judgments

- None.

## Risks

- Paste behavior change affects all calculator sections using `MetricInputTable`.
- Invalid background painting relies on visible validation state from 264.
