# Slice 2B+2C Native macOS Evidence Manifest

- Verification commit: `2e9e00bdd562b5780b45eb6b9b495dde9016f745`
- Platform: native macOS onscreen PySide6; no offscreen Qt platform
- Computer Use: attempted
- Display wake: performed with a safe key; unlocked Finder desktop confirmed
- Entry point: temporary native harness importing the production `TrainShell`
- Temporary source: `/tmp/predictor_v3_slice2bc_native/runtime_mapping.json`, copied
  from the repository's synthetic runtime-equivalent fixture
- Protected data: `data/mapping.json` and the repository fixture were not
  modified or installed into a production location
- Temporary source recovery: no mutation occurred; after the attempts it was
  byte-identical to the source synthetic fixture
- Previous evidence: Slice 2A native behavior screenshots remain unchanged and
  were not rerun

## Attempted interaction

The native Train/Admin window launched successfully on the unlocked desktop,
showed the Data Mapping tab, populated group navigation, toolbar, and primary
table. Computer Use could read the initial full-window state.

The first accessibility-element click followed by a coordinate click attempt on
the populated primary table terminated Python. A fresh process reproduced the
termination with a single Computer Use coordinate click. Both macOS diagnostic
reports classify the failure as `EXC_BAD_ACCESS` / `SIGSEGV` on the main thread
inside AppKit `NSAccessibility` hierarchy accessors. A subsequent native launch
with bounded keyboard injection remained rendered, but paste, custom shortcut,
and controller actions did not reach the Qt widget.

## Scenario status

| Required scenario | Native status | Separate automated evidence |
| --- | --- | --- |
| Paste + one-step Undo | Blocked before mutation | Spreadsheet interaction tests cover rectangular and column paste plus grouped Undo |
| F&T to PFC Pi guard | Blocked before mutation | UI flags, service command boundary, non-shifting paste, compound Undo tests pass |
| Issue navigation + Save/Reload | Blocked before mutation | Structured navigation, baseline, persistence failure/success, and round-trip tests pass |

No screenshot was captured because none of the required interactions completed.
Native rendering and automated regression are intentionally not reported as a
substitute for native interaction evidence. The impacted offscreen regression
passed 223 tests, but the Batch native acceptance remains blocked.
