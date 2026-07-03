# PySide6 macOS Computer Use Click Crash Spike

## Goal

Narrow whether the Data Mapping GUI crash is caused by predictor_v3 code or by
a broad PySide6/macOS/Computer Use click incompatibility.

## Environment

- Default Python: `3.14.4`
- Python executable: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`
- macOS: `26.5.1`
- Platform: `macOS-26.5.1-arm64-arm-64bit-Mach-O`
- PySide6: `6.11.1`
- Qt: `6.11.1`
- Prior comparison already performed:
  - Python `3.13.14` + PySide6/Qt `6.11.1`: predictor_v3 click crash reproduced.
  - Python `3.12.13` + PySide6/Qt `6.11.1`: predictor_v3 click crash reproduced.

## Minimal Apps Tested

Temporary repro scripts were created under `/tmp/pyside6_ax_spike` and removed
after the spike.

| App | Shape | Repo impact |
| --- | --- | --- |
| `no_table_app.py` | `QApplication`, `QMainWindow`, `QTabWidget`, `QLabel`, `QLineEdit`, `QPushButton` | none |
| `table_app.py` | Same as no-table plus `QTableView` and read-only `QAbstractTableModel` | none |

## Test Matrix

| Surface | System Events named click | Computer Use state query | Computer Use keyboard | Computer Use click |
| --- | --- | --- | --- | --- |
| Minimal no-table app | OK | OK | OK | OK |
| Minimal table app | OK | OK | OK | OK |
| predictor_v3 Data Mapping | OK in prior check | OK in prior check | not retested in this spike | NG in prior check |

Notes:

- The minimal no-table app accepted `keyboard-ok` through Computer Use
  `type_text`, then accepted a Computer Use button click without crash.
- The minimal table app accepted `keyboard-ok` through Computer Use
  `type_text`, then accepted a Computer Use button click without crash.
- System Events named tab/button clicks were OK for both minimal apps.
- predictor_v3 was not re-crashed in this spike because prior crash reports are
  already sufficient and the task asked to keep repeated crash reproduction
  minimal.

## Crash Stack Comparison

No new crash occurred in either minimal app, including the `QTableView` case.

The latest predictor_v3 crash evidence remains:
`~/Library/Logs/DiagnosticReports/Python-2026-07-03-235758.ips`.

Relevant top-frame pattern:

- `EXC_BAD_ACCESS` / `SIGSEGV`
- `-[NSAccessibilityAttributeAccessorInfo getAttributeValue:forObject:]`
- `_NSAccessibilityEntryPointValueForAttribute`
- `accessibilityArrayAttributeCount`
- `__AXCopyAttributeValueForHierarchy`
- `_AXXMIGCopyHierarchy`
- Qt event loop / `QApplication.exec`

The same pattern was also seen in the earlier Python 3.12 and 3.13 predictor_v3
reproductions.

## Findings

- Python version is not the primary discriminator: predictor_v3 reproduced on
  Python 3.12, 3.13, and 3.14 with PySide6/Qt 6.11.1.
- QTableView by itself is not enough to trigger the crash. The minimal table app
  clicked successfully with Computer Use.
- Computer Use keyboard entry is usable in minimal PySide6 apps.
- Computer Use click is usable in minimal PySide6 no-table and table apps.
- The crash is therefore more likely tied to predictor_v3's heavier Train shell
  hierarchy, tab/page composition, table population, or post-click accessibility
  refresh path than to a universal PySide6/macOS/Computer Use click failure.

## Recommended GUI Smoke Policy

- Do not use Computer Use direct click as the default acceptance path for
  predictor_v3 Data Mapping until the narrower app structure trigger is found.
- Computer Use `get_app_state`, screenshots, and keyboard input can remain
  available for bounded diagnostics; they should be treated as weaker evidence
  than a full click workflow when testing predictor_v3.
- Use System Events named clicks or Qt programmatic smoke for predictor_v3 tab
  transitions and button actions while this crash remains open.
- Arc 14B-2 can proceed if its acceptance criteria avoid Computer Use direct
  clicks and use System Events/Qt programmatic smoke plus focused tests.

## Excluded Scope

- No predictor_v3 production code was changed.
- No Data Mapping UI code was changed.
- No dependency, Python, PySide6, or Qt version was changed.
- No packaging, runtime adapter, Arc 14B-2 implementation, or unrelated refactor
  was performed.

## Next Action

Proceed with Arc 14B-2 Data Mapping runtime mapping repository read adapter, but
use System Events or Qt programmatic smoke instead of Computer Use direct clicks.
If direct Computer Use click support is required later, run a narrower
predictor_v3 structure follow-up that incrementally adds Train shell pieces to
the minimal repro until the crash appears.

## Verification

- Minimal no-table app launch: OK
- Minimal no-table System Events click: OK
- Minimal no-table Computer Use keyboard: OK
- Minimal no-table Computer Use click: OK
- Minimal table app launch: OK
- Minimal table System Events click: OK
- Minimal table Computer Use keyboard: OK
- Minimal table Computer Use click: OK
- Temporary repro directory cleanup: OK

Final git validation, commit hash, push result, remote main match, and final
status will be reported in terminal output.

## Commit / Push Note

Final commit/push result will be reported in terminal output.
