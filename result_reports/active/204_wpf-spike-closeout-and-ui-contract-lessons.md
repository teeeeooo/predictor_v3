# 204 WPF Spike Closeout and UI Contract Lessons

## Goal

Close out the C# WPF spike as an experiment, keep its code out of `main`, and record the UI contract guardrails needed before returning to `calculator_tk` work.

## Scope

- Main-branch documentation/report work only.
- No C# WPF code merge.
- No calculator code, core formula, fixture, golden, or region config changes.

## Experiment Branch

- `spike/wpf-calculator-shell`

## Confirmed Strengths

- WPF `DataGrid` can support some Excel-like table behaviors.
- A shell-only C# UI with a Python worker bridge is technically plausible.
- The JSON request/response shape can remain close to a future HTTP contract.
- The experiment helped identify worker/package boundaries before any main adoption.

## Confirmed Problems

- C# WPF adds .NET SDK/runtime validation and Windows GUI build requirements.
- A GUI exe plus Python worker exe introduces packaging and email/distribution friction.
- Region config discovery becomes a packaging concern.
- Worker resolver/error handling becomes a new architectural surface.
- The first UI shape drifted toward a reusable grid demo rather than the current `calculator_tk` section order and immediate-calculation flow.
- WPF table usability had potential, but the worker structure conflicted with the lightweight, single-file, input-immediate purpose of `calculator_tk`.

## Closeout Judgment

- C# WPF is not merged to `main`.
- The spike is recorded as a technology-selection experiment, not as a failed implementation to retry immediately.
- Calculator UI direction returns to Tkinter.
- ML UI should also hold off on C# adoption and instead strengthen the existing Python UI table contract first.

## Lessons

- The root problem was not only language/toolkit choice.
- `docs/ui_ux` contracts must be enforced against the default user-facing screen, not just component demos.
- Existing screen replacement must begin by preserving section order, default visible state, and primary user flow.
- Mock/demo rows and component smoke controls must not appear in the default user workflow.
- Immediate-calculation calculator screens and button-run batch/model workflows need explicit distinction.
- Toolkit adapters implement UX contracts; they do not grant permission to change UX.

## Next Actions

1. Return to `calculator_tk` simple batch mode.
2. Design a common detail/bin result schema.
3. Clean up the current CSPF detail/bin adapter against that schema.
4. Extend HSPF / EN14825 / AHRI / KS detail/bin adapters.
5. Align graph/export work to the common detail/bin schema.

Internal formula trace remains outside the current execution scope and on long hold.

## Changed Files

- `docs/WORK_PLAN.md`
- `docs/ui_ux/00_UI_UX_SYSTEM.md`
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
- `project_log.md`
- `result_reports/active/204_wpf-spike-closeout-and-ui-contract-lessons.md`

## Verification

Executed:

- `git diff --check`
  - passed
- `python3 -B tools/check_code_structure.py`
  - exited `0` with existing warning:
    - `[W] ui_tk/sections/bin_detail_panel.py: file exceeds 400 LOC soft limit (437). Consider splitting before adding more responsibilities.`
- `git status --short`
  - confirmed only intended docs/report changes before commit

Not planned:

- pytest, because this is docs/report-only work.
- GUI smoke, because no UI code changed.

## Known Risks

- The WPF branch remains available for reference, but its code is intentionally absent from `main`.
- Batch/detail schema work still needs implementation slices; this report only sets direction.

## Scope Compliance

- No C# WPF code was copied to `main`.
- No C# retry next action was added.
- No calculator core, fixture, golden, or region config file was changed.
- No report lifecycle/archive movement was performed.

## Commit / Push

- Final commit hash and push status are recorded in the terminal summary for this task.

## Project Memory Delta

```yaml
- type: decision
  topic: wpf_spike_closeout
  content: predictor_v3 closes the C# WPF calculator shell spike without merging WPF code to main; calculator UI work returns to calculator_tk and C# adoption for ML UI remains on hold.
  keywords:
    - predictor_v3
    - WPF
    - calculator_tk
    - UI contract
    - closeout
  assertionStatus: observed
  source: result_reports/active/204_wpf-spike-closeout-and-ui-contract-lessons.md
- type: lesson
  topic: ui_contract_enforcement
  content: predictor_v3 UI contract enforcement must check the default user-facing screen, section order, and primary flow; toolkit adapters and reusable table demos do not authorize UX flow changes or mock/demo rows in production screens.
  keywords:
    - predictor_v3
    - UI UX
    - table contract
    - adapter
    - default screen
  assertionStatus: observed
  source: result_reports/active/204_wpf-spike-closeout-and-ui-contract-lessons.md
```
