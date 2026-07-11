# Clean Hexagonal MVC UI Refactor

record:
  date: 2026-07-11
  topic: clean-hex-mvc-ui-refactor
  tags: architecture, hexagonal, mvc, legacy-retirement, ui-ux, regression
  memory_review: updated
  memory_reason: record execution failure terminalization, ML projection save guards, and desktop window/viewport owner boundaries

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
- Data Definition schema saves now stop when a draft would change the existing
  ML compatibility fingerprint while no `features.csv` projection writer
  exists. The core save-plan owns the comparison; label and notes edits remain
  writable because they do not participate in that fingerprint.
- Predict controllers retain the active case IDs for a run. An unexpected
  runner failure now leaves existing terminal rows unchanged, maps only
  still-running rows to infrastructure errors through the result adapter, and
  summarizes the resulting session state before runner disposal.

## Legacy Diagnostic Retirement Mapping

| Deleted asset / verification item | Classification | Active replacement / preservation location |
| --- | --- | --- |
| `core/_legacy/calculator_iso16358_legacy.py`, legacy package init | Deleteable | Removed implementation only; production owners remain `core/calculators/standards/iso16358.py` and `ks_c9306.py`. |
| `tests/_legacy/README.md`, package init | Deleteable | Retirement mapping in this record replaces the directory-local warning; no runtime or oracle assertion was owned by the init files. |
| CSPF T1 diagnostic variants and mismatch direction in `test_iso16358_cspf_iso_t1_default_diagnostics.py` | Replaced | `tests/test_iso16358_cspf_iso_t1_2point_control_samples.py`, `test_iso16358_cspf_official_tool_formula_diagnostics.py`, and the Southeast Asia CSPF report retain the active diagnostics. |
| KS CSPF 6.504 / 1943.798 / 298.852 oracle from the same file | Preserved | `tests/test_iso16358_legacy_evidence_preservation.py` runs the values against the active KS calculator. |
| `test_iso16358_cspf_profile_calculation.py` | Replaced | Active T1 production/golden tests plus `tests/test_iso16358_cspf_t3_profile.py` cover calculation, optional-point, and positive-result behavior without the legacy implementation. |
| `test_iso16358_cspf_profile_resolver.py` | Replaced | T1 config/control tests and active T3/SASO resolver tests cover required/optional levels and 29/46 degree derivation factors. |
| KS official golden and curve assertions in `test_iso16358_hspf_golden_diagnostic.py` | Replaced | `tests/helpers/iso16358_hspf_samples.py` and `tests/test_iso16358_hspf_validation.py` retain total and bin-level oracle assertions. |
| Seven-case workbook matrix, former strict-xfail rationale, Case 3 component/routing cells, and converted-workbook observations from that file | Preserved | Existing `tests/fixtures/iso16358_hspf_golden_fixtures.json`, new evidence-only `tests/fixtures/asnzs_excel_hspf_compat/legacy_case3_diagnostic_observations.json`, and `tests/test_iso16358_legacy_evidence_preservation.py`. No xfail was reintroduced. |
| Legacy calculator simulation helpers and trace-only output in that file | Deleteable | They exercised retired internals and supplied no additional accepted expected values after the evidence above was separated. |
| `test_iso16358_hspf_h8_trace.py` branch/formula invariants | Replaced | `tests/test_iso16358_hspf_formula_micro.py`, `test_iso16358_hspf_frost_trace.py`, and `test_iso16358_hspf_official_exact_golden.py`; print-only audit output was deleteable. |

## Evidence And Verification

- Full active suite: `1603 passed, 2 xfailed` in 41.05 seconds. The two expected
  xfails are the documented AS/NZS Case 3 external component/load-hours data
  gaps, not stale compatibility tests.
- Focused numeric regression: 84 ISO 16358, KS C 9306, EN14825, AHRI, and fixed
  ML artifact/mock prediction tests passed.
- Focused batch/window regression: 120 Tk batch tests passed, including dialog
  close/reopen and two-axis viewport behavior.
- Pre-merge correction focused checks passed for the Data Definition save
  contract/writer/controller, Predict usecase/controller/worker/result adapter,
  and retained ISO legacy evidence. The evidence inventory adds no xfail or
  skip and does not execute the retired calculator.
- macOS Computer Use inspected all three running apps. Calculator standard tabs
  and HSPF2 batch overflow were visible; a deliberately narrowed batch window
  exposed the horizontal scrollbar. Predict scrolled from input columns to the
  result columns. Train exposed the four intended tabs and their primary
  sections. A later post-test screenshot retry was unavailable because the Mac
  had locked; the final small display/master/scrollbar adjustments were covered
  by automated tests.
- Final branch-head full-suite, structure, staged-change, compile/import, diff,
  and divergence results are recorded after the correction validation below.

## Final Branch-Head Verification

- Correction-focused suite: `138 passed` in 4.96 seconds across Data
  Definition, Predict failure handling, legacy evidence preservation,
  calculator foundation, batch viewport, and common window policy.
- Full active suite: `1617 passed, 2 xfailed` in 44.12 seconds with no skips.
  The xfails remain the two documented AS/NZS Case 3 external-reference gaps.
- Structure check passed with the same nine pre-existing soft warnings. Syntax,
  production-module import, evidence JSON, worktree/cached diff, and prohibited
  calculator/config/golden path checks passed.
- The full staged branch tree was evaluated from `origin/main` in a detached
  verification worktree: cached diff check and agent change gate both passed.
  Running the gate only against the correction commit reports the expected
  append-only lifecycle conflict because this audit explicitly required the
  already-committed branch record to be updated and prohibited a new record;
  neither the gate nor Git history was rewritten to bypass that policy.

## Changed Files

- Predict/Train application, port, adapter, controller, composition, and UI
  owners under `apps/predict/` and `apps/train/`.
- Data Definition projection/save-plan/writer owners, Predict infrastructure-failure
  mapper/usecase/controller flow, and their focused tests.
- Calculator/window/theme owners under `apps/calculator/ui/`, `apps/common/ui/`,
  and `ui_common/`.
- Active tests, structure guard, mock-smoke tooling, project/architecture/UI
  owner docs, project log, and memory seed.
- Evidence-only legacy Case 3 observations and the active legacy evidence
  preservation test; calculator formula and golden fixtures were not edited.
- Retired compatibility sources/tests and tracked `.DS_Store` files.

## Known Risks

- Native Windows UI behavior was not manually exercised; screen-geometry policy
  has pure tests and macOS native verification only.
- Actual production model and training artifacts are absent from the workspace;
  mapping/runtime readiness also remains limited to repository fixtures. ML
  verification therefore uses the fixed mock artifact and existing contract
  tests; no unfinished ML feature work was added.
- Existing formula-heavy calculator owners and a few mature UI/controller files
  remain above warning thresholds. They were reviewed and intentionally not
  split because mechanical extraction would increase numeric regression risk or
  add structure without a new responsibility boundary.
