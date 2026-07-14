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

## Audit correction follow-up

- Correction verification commit:
  `5b1968eb7e3b493c15cef1c06358d74d44005199`
- Display wake: performed with a safe key; an unlocked Finder desktop was
  confirmed
- Native launch: the production `TrainShell` rendered the populated IDU Data
  Mapping workspace in an onscreen Python.app window without an offscreen Qt
  platform
- Computer Use scope: one initial window-state and screenshot inspection only;
  no table click, edit, paste, selection, or shortcut action was issued
- Native application crash: none during this bounded rendering inspection
- Temporary source:
  `/tmp/predictor_v3_slice2bc_audit_native/runtime_mapping.json`, copied from
  the repository synthetic runtime-equivalent fixture
- Temporary source restoration: after the session it remained byte-identical
  to the protected fixture
- Protected data: the fixture and `data/mapping.json` remain unchanged
- Automated evidence: 32 correction-focused and 285 impacted offscreen tests
  passed; the PR CI check passed

Physical user input was requested for canonical dirty plus paste/Undo/overflow,
the PFC Pi guard, and issue-navigation plus Save/Reload. No completion response
was received during the session. All three scenarios are therefore recorded as
**not performed**, not failed or passed. No new PNG was added.

The previous AppKit accessibility blocker was avoided by issuing no Computer
Use table interaction. It is not considered resolved, and automated evidence is
not substituted for native interaction acceptance. Previous Slice 2A evidence
was not rerun.
