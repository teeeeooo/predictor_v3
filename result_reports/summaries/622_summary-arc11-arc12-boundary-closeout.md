# 622 Summary - Arc 11 / Arc 12 Boundary Closeout

## Goal

Compress the completed Arc 11 boundary correction continuation and Arc 12
calculator application-boundary reports into one lifecycle summary so current
work can rely on owner docs, focused tests, and this summary instead of active
intermediate reports.

## Covered Reports

- `result_reports/archive/603_active-report-lifecycle-cleanup-arc10-arc11.md`
- `result_reports/archive/604_arc11-hexagonal-boundary-reopen.md`
- `result_reports/archive/605_train-execution-process-adapter.md`
- `result_reports/archive/606_predict-execution-usecase-port.md`
- `result_reports/archive/607_arc11-hexagonal-boundary-correction-closeout.md`
- `result_reports/archive/608_arc11-boundary-cleanup.md`
- `result_reports/archive/609_training-service-validation-only.md`
- `result_reports/archive/610_arc12-calculator-boundary-audit.md`
- `result_reports/archive/611_calculator-application-boundary-foundation.md`
- `result_reports/archive/612_iso-iseer-2point-usecase-extraction.md`
- `result_reports/archive/613_iso-iseer-2point-batch-usecase-reuse.md`
- `result_reports/archive/614_arc12-calculator-usecase-boundary-closeout.md`
- `result_reports/archive/615_arc12-saso-t3-usecase-extraction.md`
- `result_reports/archive/616_arc12-hong-kong-cspf-usecase-extraction.md`
- `result_reports/archive/617_arc12-hong-kong-hspf-usecase-extraction.md`
- `result_reports/archive/618_arc12-en14825-boundary-correction.md`
- `result_reports/archive/619_arc12-ahri-boundary-correction.md`
- `result_reports/archive/620_arc12-boundary-consistency-audit.md`
- `result_reports/archive/621_arc12-calculator-boundary-final-closeout.md`

## Consolidated Result

Arc 11 was reopened after the initial trainer execution foundation to correct
the Train/Predict hexagonal boundary. Production Train execution now runs
through an execution port and killable process runner adapter, with terminate
then kill fallback and cleanup that prevents partial final model promotion on
cancel/error. Predict execution orchestration is behind a UI/runtime-neutral
usecase and execution port, while the PySide QThread worker remains an adapter
implementation. `TrainingService` was reduced back to resource status and
request validation; DEV/test backend execution moved to mock-smoke tooling.

Arc 12 completed the calculator UI/application boundary correction for the
automated scope. ISO/ISEER 2-point single and batch established the first
application usecase pattern. SASO T3, Hong Kong CSPF/HSPF, EN14825, and AHRI
paths were then moved to application-owned usecases/adapters or thin UI shims
that delegate orchestration. Completed UI sections and matching batch paths no
longer directly own core dispatcher orchestration or calculator config mutation
where targeted by Arc 12.

Calculator formulas, configuration semantics, profile IDs, fixture/golden
expected values, public result contracts, ML algorithms, preprocessing, feature
registries, and generated mock artifacts remained out of scope for the covered
work.

## Durable Decisions

- Arc 11 Predict/Train correction supersedes the earlier trainer execution
  foundation acceptance: execution orchestration belongs behind application
  usecases/ports, while PySide/QProcess/QThread details belong to adapters.
- `TrainingService` owns Train resource status and request validation only; it
  is not a production training execution owner.
- Arc 12 calculator UI/batch orchestration for the targeted standards belongs
  behind application usecases/adapters or thin UI shims, not direct UI-owned
  dispatcher/config mutation.
- Matching calculator batch paths should reuse the corresponding application
  usecases/adapters where applicable.
- Arc 13 ML Pipeline Stabilization is unblocked after Arc 12, but remains a
  separate arc and should not be mixed into calculator boundary cleanup.

## Verification Evidence

The covered reports recorded focused automated evidence for:

- Train process runner, cancellation, temp artifact cleanup, service boundary,
  DEV mock Train execution, and Predict-after-Train smoke behavior.
- Predict usecase/port behavior and PySide runner adapter boundary.
- ISO/ISEER, SASO T3, Hong Kong CSPF/HSPF, EN14825, and AHRI calculator
  application-boundary behavior across single/detail/batch paths where covered.
- Compile checks, focused pytest selections, code-map freshness checks,
  structure guard runs, and `git diff --check`.

The final Arc 12 closeout recorded focused calculator application/usecase tests
as passing, code-map check as fresh, structure guard as passing with known soft
warnings, and Slice 10 split evidence for EN/AHRI where the broad selector had
stalled in the EN Tk segment.

## Known Risks / Open Items

- Manual GUI smoke remains user-run for the covered Train/Predict and
  calculator UI paths.
- Real production model quality, accuracy, physical trends, and feature
  importance were not validated by DEV mock smoke.
- Existing structure soft warnings remain in known core/EN hotspots.
- EN/AHRI broad focused selector had a known stall in the EN Tk segment during
  Slice 10; split focused groups were used as acceptance evidence.
- Memory seed size exceeds the dedicated maintenance threshold; this lifecycle
  cleanup only performs the required summary registration and minimal durable
  entry update.

## Archive Decision

All covered reports are completed history or intermediate implementation
evidence now represented by this summary, current project state docs, focused
tests, and source. No covered report needs to remain active for Arc 13 start or
future manual-smoke evidence.

## Project Memory Seed Sync Judgment

The memory seed is updated with this summary under Source Summaries, the prior
Arc 11 correction source is repointed from an active report to this summary, and
one compact Arc 12 durable decision is added. No individual report-level entries
are backfilled.

## Next Action

Arc 13 - ML Pipeline Stabilization, unless the user asks for manual GUI smoke or
dedicated memory seed maintenance first.

## Slice 12 Addendum - Calculator Outbound Adapter Boundary Hardening

Goal:

- Harden the remaining calculator outbound construction/config boundary after
  Arc 12 closeout without reopening the full Arc 12 audit.

Changed files:

- `apps/calculator/adapters/ahri_calculator_factory.py`
- `apps/calculator/adapters/en14825_calculator_factory.py`
- `apps/calculator/adapters/saso_t3_calculator.py`
- `apps/calculator/application/ahri/seer2_adapter.py`
- `apps/calculator/application/ahri/hspf2_adapter.py`
- `apps/calculator/application/en14825/seer_adapter.py`
- `apps/calculator/application/en14825/scop_adapter.py`
- `apps/calculator/application/saso_t3/usecase.py`
- `tests/test_calculator_application_boundary.py`
- `tests/test_calculator_ahri_application_boundary.py`
- `tests/test_calculator_en14825_application_boundary.py`
- `tests/test_calculator_saso_t3_usecase.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/memory/project_memory_seed.md`

Boundary decision:

- Calculator application code may parse UI-ready inputs, call application-level
  workflows, and interpret calculator outputs, but core calculator construction,
  concrete EN14825 creation, dispatcher calls, and SASO T3 config override live
  behind `apps/calculator/adapters/` outbound gateways.
- No universal calculator abstraction was added. Slice 12 uses focused AHRI,
  EN14825, and SASO T3 gateways only.
- Stub calculator injection remains available in AHRI and EN14825 application
  adapters so focused tests do not need concrete core construction.

Verification:

- `python3 -B -m compileall -q app_calculator.py apps/calculator core/calculators`: OK.
- `python3 -B -m pytest tests --collect-only -q -k "calculator_application or saso or en14825 or ahri"`: OK, selected scope reviewed.
- `python3 -B -m pytest tests -k "calculator_application"`: OK.
- `python3 -B -m pytest tests -k "saso"`: OK.
- EN14825 focused file group: OK.
- AHRI focused file group: OK.
- `python3 -B -m pytest tests -k "ahri or seer2 or hspf2"`: OK.
- `python3 -B -m pytest tests -k "en14825"`: stopped after the known EN Tk
  profile-switch segment stopped producing progress; EN acceptance uses the
  completed focused file group above.
- `python3 -B tools/code_checker/build_reference_map.py --check`: STALE, then regenerated once.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK after regeneration.
- `python3 -B tools/check_code_structure.py`: OK with existing soft warnings.

Known risk:

- EN14825 application adapters still contain the established UI-to-core
  translation logic and remain above the soft LOC threshold; Slice 12 only moved
  outbound construction behind adapters.
- The broad EN14825 selector still has the known Tk profile-switch progress
  stall; focused EN groups passed.

Next action:

- Arc 13 - ML Pipeline Stabilization.

## Slice 13 Diagnostic Addendum - EN14825 Tk Selector Stall

Reproduced:

- Yes. `python3 -B -m pytest tests -k "en14825"` and faulthandler-backed
  `pytest -vv -s -o faulthandler_timeout=20 tests -k "en14825"` both stopped
  at
  `tests/test_ui_tk_en14825_profile_switch_fit.py::test_profile_switch_to_en14825_seer_keeps_positive_geometry`.

Minimal reproducer:

- `python3 -B -m pytest -vv -s tests/test_ui_tk_calculator_empty_state.py tests/test_ui_tk_en14825_profile_switch_fit.py`
- Narrower reproducer:
  `python3 -B -m pytest -vv -s tests/test_ui_tk_calculator_empty_state.py::test_en14825_profiles_keep_options_but_start_without_performance_data tests/test_ui_tk_en14825_profile_switch_fit.py`
- A plain local probe also reproduced the stall with: create and destroy one
  `tk.Tk()` root, then create a second withdrawn root, build
  `CalculatorTkApp(root=second_root)`, and call `second_root.update()`.

Likely cause:

- Classification: C. Tk environment / headless test isolation issue.
- The stalled frame is `tkinter.__init__.py:update`, reached from
  `test_profile_switch_to_en14825_seer_keeps_positive_geometry` line 28.
- `tests/test_ui_tk_en14825_profile_switch_fit.py` passes by itself and each
  individual test passes by itself.
- The previous/next file check shows the preceding empty-state Tk test file is
  sufficient to trigger the stall, while running the profile-switch file before
  the SCOP batch dialog file passes.
- Local probes showed the issue is not EN formula/config behavior and not a
  specific EN section callback: even an empty prior `Tk()` root followed by a
  second withdrawn root with `CalculatorTkApp` can stall on `update()`.
- Reusing one root with a destroyed `Toplevel` instead of destroying one `Tk()`
  root and creating another avoids the stall.

Affected files:

- `tests/test_ui_tk_calculator_empty_state.py`
- `tests/test_ui_tk_en14825_profile_switch_fit.py`
- `apps/calculator/ui/calculator_app.py`
- `apps/calculator/ui/auto_calc.py`
- `apps/calculator/ui/window_refit.py`

Fix needed:

- Yes, but not in Slice 13. The fix should target Tk test isolation / pending
  event draining, not calculator formulas, config, profile IDs, golden expected
  values, public result contracts, or production calculation behavior.

Validation commands run:

- `python3 -B -m pytest tests --collect-only -q -k "en14825"`: OK, 123 selected.
- `python3 -B -m pytest -vv -s tests/test_ui_tk_en14825_profile_switch_fit.py`: OK.
- Four individual profile-switch tests: OK.
- `PYTHONFAULTHANDLER=1 python3 -B -m pytest -vv -s -o faulthandler_timeout=20 tests -k "en14825"`: reproduced stall and captured stack in `tkinter.update`.
- Previous/profile/next file combinations: previous empty-state file plus
  profile-switch file reproduced; profile-switch plus next SCOP batch dialog
  file passed.

Next action:

- Arc 12 Slice 14 - EN Tk Headless Test Isolation.
