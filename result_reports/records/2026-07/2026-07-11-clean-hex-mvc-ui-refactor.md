# Clean Hexagonal MVC UI Refactor

record:
  date: 2026-07-11
  topic: clean-hex-mvc-ui-refactor
  tags: architecture, hexagonal, mvc, legacy-retirement, ui-ux, regression
  memory_review: updated
  memory_reason: record the current execution-port, ML catalog compatibility, and desktop window/viewport owner boundaries

change_gate:
  new_source: split
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner

## Change Reason

The active desktop code had accumulated retired calculator code, stale tests,
duplicate Predict table views, a superseded Train Feature Catalog UI, and
toolkit lifecycle dependencies crossing controller/application boundaries. The
desktop surfaces also had first-show geometry, multi-monitor placement, and
wide batch-table scrolling defects.

## Contract / Behavior Changed

- Predict and Train now assemble runtime-neutral DTOs, usecases, and execution
  ports at explicit composition roots; PySide runners own thread/process
  lifecycle and controllers do not import concrete runners.
- The retired calculator implementation, legacy test directory, dead Predict
  split tables, and superseded Train Feature Catalog Manager UI were removed.
  The core ML feature catalog and `config/ml/features.csv` compatibility
  contract remain.
- Calculator, Predict, and Train share a restrained neutral/teal visual system.
  User-facing status values are consistent, table/result hierarchy is clearer,
  and disabled non-functional placeholders were removed.
- Calculator startup is hidden until its initial fit settles, dialogs preserve
  off-primary-monitor coordinates, and batch viewports provide a stable
  horizontal scrollbar plus local Shift+wheel scrolling. Qt shells use a
  shared available-screen initial-size policy.
- Calculator formulas, public calculation result shapes, Predict schema, and
  fixed-artifact ML numeric behavior were not intentionally changed.

## Evidence And Verification

- Full active suite: `1603 passed, 2 xfailed` in 41.05 seconds. The two expected
  xfails are the documented AS/NZS Case 3 external component/load-hours data
  gaps, not stale compatibility tests.
- Focused numeric regression: 84 ISO 16358, KS C 9306, EN14825, AHRI, and fixed
  ML artifact/mock prediction tests passed.
- Focused batch/window regression: 120 Tk batch tests passed, including dialog
  close/reopen and two-axis viewport behavior.
- macOS Computer Use inspected all three running apps. Calculator standard tabs
  and HSPF2 batch overflow were visible; a deliberately narrowed batch window
  exposed the horizontal scrollbar. Predict scrolled from input columns to the
  result columns. Train exposed the four intended tabs and their primary
  sections. A later post-test screenshot retry was unavailable because the Mac
  had locked; the final small display/master/scrollbar adjustments were covered
  by automated tests.
- Structure, staged-change, compile/import, and diff checks are required for
  the final staged closeout.

## Changed Files

- Predict/Train application, port, adapter, controller, composition, and UI
  owners under `apps/predict/` and `apps/train/`.
- Calculator/window/theme owners under `apps/calculator/ui/`, `apps/common/ui/`,
  and `ui_common/`.
- Active tests, structure guard, mock-smoke tooling, project/architecture/UI
  owner docs, project log, and memory seed.
- Retired compatibility sources/tests and tracked `.DS_Store` files.

## Known Risks

- Native Windows UI behavior was not manually exercised; screen-geometry policy
  has pure tests and macOS native verification only.
- Real model, mapping, and training artifacts are absent from the workspace.
  ML verification therefore uses the fixed mock artifact and existing contract
  tests; no unfinished ML feature work was added.
- Existing formula-heavy calculator owners and a few mature UI/controller files
  remain above warning thresholds. They were reviewed and intentionally not
  split because mechanical extraction would increase numeric regression risk or
  add structure without a new responsibility boundary.
