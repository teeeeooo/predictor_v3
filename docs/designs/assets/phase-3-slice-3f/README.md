# Phase 3 Slice 3F native evidence

## Capture contract

- Capture-source commit SHA: `8557f1c0909421694b1a2086f0ce45b9d01ebff5`
  (the source commit immediately before this evidence-manifest amend; application
  and screenshot bytes are unchanged by the amend).
- Native onscreen: yes — visible macOS Cocoa windows.
- Capture source: the visible window rendered into a 2x `QPixmap` target through
  `QWidget.render`. `QScreen.grabWindow()` returned a null pixmap while macOS was
  locked. These are not desktop-composited captures.
- Fixture/provider: repository synthetic Data Definition and runtime-equivalent
  Mapping fixtures copied to temporary schema/mapping paths by
  `tools/dev/native_acceptance/run_phase3f_native_scenarios.py`.
- State preparation: programmatic Qt public panel/controller calls against the
  temporary providers.
- Interaction classification: programmatic only. The actual interaction for each
  state is listed below.
- Computer Use: `list_apps` was attempted, but macOS was locked and automatic
  unlock failed. No app state, Qt table hierarchy, accessibility hit-test, or
  click was obtained.
- Physical interaction: none.
- Runtime/protected fixture changes: none. The scenario driver reported both
  `runtime_fixture_changed: false` and `schema_fixture_changed: false`.
- Known AppKit accessibility table-click path used: no.

## Screenshots

| Evidence | Logical / pixel size | State | Actual programmatic interaction |
| --- | --- | --- | --- |
| [01 clean full-width Inventory and Summary](01-clean-full-width-inventory-summary.png) | 1280x820 / 2560x1640 px | Clean browsing with full-width six-column Inventory, selected summary, concise clean state, and collapsed diagnostics | Loaded the synthetic schema and selected the canonical first definition |
| [02 dirty saveable concise state](02-dirty-saveable-concise-state.png) | 1280x820 / 2560x1640 px | One unsaved saveable change with contextual review and primary Save | Applied one supported controlled Edit; detailed impact remained collapsed |
| [03 blocked actionable state](03-blocked-actionable-state.png) | 1280x820 / 2560x1640 px | Direct model-compatibility blocker, disabled Save, and Reset/review recovery | Applied a controlled compatibility-impacting Edit; Save remained disabled |
| [04 saved Mapping next step](04-saved-mapping-next-step.png) | 1280x820 / 2560x1640 px | Successful schema Save plus saved-only Mapping Requirement next step | Added a supported Mapping attribute and executed guarded Save against the temporary schema copy |
| [05 compact task workspace](05-compact-task-workspace.png) | 900x640 / 1800x1280 px | Compact vertical task flow with reachable primary/secondary actions and full-width Inventory without horizontal scrolling | Reset the draft, resized the visible window to 900x640, and kept diagnostics collapsed |

All five rows share the native/fixture/capture/interaction/protected-file and
accessibility-path classifications stated above.
