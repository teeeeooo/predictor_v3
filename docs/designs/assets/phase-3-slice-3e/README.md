# Phase 3 Slice 3E native evidence

## Capture contract

- Capture-source commit SHA: `261177a8cef17964d98b1dc5ac11dcd342718a31`
  (the source commit immediately before this evidence-only manifest amend; the
  application and screenshot bytes are unchanged by the amend).
- Native onscreen: yes — visible macOS cocoa windows.
- Fixture/provider: repository synthetic Data Definition fixture plus temporary
  schema and mapping copies created by
  `tools/dev/native_acceptance/run_phase3e_native_scenarios.py`.
- State preparation and interaction: programmatic Qt public panel/controller
  calls and `QTimer`; screenshots use the visible widget's native 2x backing
  store because `QScreen.grabWindow()` returned a null pixmap without screen
  recording access.
- Computer Use inspection: `list_apps()` only, to confirm the native Python app
  process was running. No Qt table click, table hierarchy query, or accessibility
  hit-test was performed.
- Physical interaction: none.
- Runtime/protected fixture changes: none. The scenario driver reported both
  `runtime_fixture_changed: false` and `schema_fixture_changed: false`.
- Known AppKit accessibility table-click path used: no.

## Screenshots

| Evidence | Capture size | State | Actual programmatic interaction |
| --- | --- | --- | --- |
| [01 clean definition — normal](01-clean-definition-normal.png) | 2560x1640 px (1280x820 logical) | Clean inventory, selected Definition detail, and impact | Open Data Definition, select the canonical first inventory row, focus search |
| [02 dirty saveable impact](02-dirty-saveable-impact.png) | 2560x1640 px (1280x820 logical) | Unsaved projection-neutral Add/Edit impact, Save enabled | Submit a valid controlled Add command and select the added Definition |
| [03 blocked compatibility](03-blocked-compatibility.png) | 2560x1640 px (1280x820 logical) | Compatibility-blocked dirty draft and accessible blocker action | Apply a controlled ML-impacting edit and focus Review blockers |
| [04 saved Mapping handoff](04-saved-mapping-handoff.png) | 2560x1640 px (1280x820 logical) | Successful schema Save, clean state, and saved Mapping Requirement | Execute the guarded schema Save against a temporary schema copy, then focus the handoff selector |
| [05 exact Data Mapping coverage](05-data-mapping-exact-coverage.png) | 2560x1640 px (1280x820 logical) | Exact group/attribute coverage context with first unresolved target | Open the saved handoff through the shell and programmatically focus the exact unresolved mapping cell |
| [06 definition compact](06-definition-compact.png) | 1800x1280 px (900x640 logical) | Compact toolbar/filter reflow with primary actions reachable | Resize the visible native window and focus the inventory |
| [07 no-match recovery](07-no-match-recovery.png) | 2560x1640 px (1280x820 logical) | Search no-match with stale detail cleared and recovery guidance | Enter a deterministic no-match query and focus the search clear/recovery path |

All seven rows share the capture-source SHA, native/fixture/interaction
classification, protected-file result, and table-accessibility exclusion stated
above.
