```yaml
record:
  date: 2026-07-14
  topic: train-admin-phase2-slice2bc-native-blocker
  tags: train-admin, mapping, phase-2, slice-2b, slice-2c, native-macos, computer-use, blocker
  memory_review: updated
  memory_reason: Preserve the repeated AppKit accessibility failure and prevent automated evidence from being mistaken for native interaction proof.
change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Slice 2B+2C requires three bounded native macOS interaction scenarios after the
automated gates. The native app rendered on an unlocked desktop, but Computer
Use interaction with the populated PySide6 table reproducibly crashed in the
macOS accessibility bridge before any required scenario could complete.

# Observed Boundary

- The native Train/Admin window and populated Data Mapping workspace rendered.
- Computer Use read the initial onscreen window state.
- Two fresh-process table click attempts terminated Python with
  `EXC_BAD_ACCESS` / `SIGSEGV` in AppKit `NSAccessibility` hierarchy accessors.
- A bounded keyboard-only retry did not deliver paste or custom shortcuts to the
  Qt table.
- Paste/Undo, PFC Pi interaction, and issue-navigation/Save/Reload are therefore
  not claimed as native-verified, and no new PNG was produced.

# Separate Automated Evidence

- Slice 2B intermediate gate passed 131 tests.
- The final impacted offscreen regression passed 223 tests, including paste,
  clear, grouped Undo, PFC Pi policy, baseline dirty state, issue navigation,
  Save/Reload failure preservation, and synthetic round-trip coverage.
- The temporary runtime source remained byte-identical to the protected
  synthetic fixture. Neither it nor `data/mapping.json` was modified.

# Follow-up

Resolve or externally bypass the macOS Qt/AppKit accessibility interaction
failure, then run only the three required Batch scenarios and add screenshots.
Until then PR #15 remains Draft/Open and Slice 2D must not begin.
