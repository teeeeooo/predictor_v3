# 084 — ISO16358-2 HSPF Official Exact Fixture Hygiene + Calculator Table Input / Unit Boundary Design

## Goal

1. Separate "official data" from "current implementation status" inside
   the ISO16358-2 HSPF official exact fixture so that the fixture stays
   a clean reference and the per-case xfail bookkeeping does not
   pollute it.
2. Document a horizontal table-input UI for AHRI / EN14825 so the
   future UI slice can replace the long vertical `QFormLayout` while
   keeping AGENTS.md UI guardrails.
3. Document the ML W ↔ calculator-native unit boundary so that ML /
   inverse-search keeps W canonical and the adapter alone is
   responsible for conversion to profile-native units.

This task only ships fixture hygiene + design docs. No calculator core
change, no UI implementation, no unit adapter implementation, no ML
caller change, no xfail relaxation.

## Scope

- `tests/fixtures/iso16358_hspf_official_exact_cases.json`: remove
  `current_status` field from each case; keep input / description /
  expected unchanged.
- `tests/test_iso16358_hspf_official_exact_golden.py`: introduce
  module-level `XFAIL_CASE_IDS` constant and drive xfail marking from
  it instead of from the fixture.
- `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`:
  new combined design doc (table input + unit boundary).
- `docs/WORK_PLAN.md`: short status update referencing the new design
  and the fixture-hygiene split.
- `result_reports/active/084_fixture-hygiene-and-calculator-table-unit-boundary-design.md`:
  this report.

## Non-goals

- No mismatch analysis or fix for the 11 xfailed ISO16358-2 HSPF cases.
- No edit to `core/calculator_iso16358.py`.
- No edit to expected HSTL / HSEC / HSPF values.
- No relaxation of `xfail(strict=True)`.
- No UI implementation (table or otherwise).
- No `core/calculator_unit_adapter.py` implementation.
- No `CalculatorInputEnvelope` field change.
- No ML caller wiring.
- No `app_calculator.py` redesign.
- No fixture rename, split, or large reorganization.
- No region config edit.

## Verification

- `python3 -B -m py_compile tests/test_iso16358_hspf_official_exact_golden.py`
  → OK
- `python3 -B -m pytest tests/test_iso16358_hspf_official_exact_golden.py -q`
  → `6 passed, 11 xfailed` (1 sanity + 5 match cases pass, 11 mismatch
  cases stay strict-xfail; same total counts as before the hygiene
  change).
- `python3 -B -m pytest tests/test_calculator_input_adapter.py tests/test_calculator_prediction_adapter.py tests/test_calculator_ranking_adapter.py -q`
  → all green (60 passed when run together with the official-exact
  suite, 11 xfailed reflect only the official-exact xfails).
- `python3 -B -m pytest -q`
  → `370 passed, 34 xfailed`. Matches baseline (audit_5 baseline was
  `364 passed, 23 xfailed`; the +6 / +11 delta is exactly the 16
  parametrised official-exact cases + 1 sanity test that were added in
  report 083, and is unchanged by this hygiene refactor).

## Task Results

### Task 1 — Fixture hygiene (ISO16358-2 HSPF official exact)

- Removed the `current_status` field from every entry of
  `cases[*]` in
  `tests/fixtures/iso16358_hspf_official_exact_cases.json`. The fixture
  now carries only `case_id`, `description`, `points`, and `expected`
  per case, plus the shared `units`, `comparison`, `config`,
  `point_pool`, `bin_hours`, and `notes` blocks.
- Reworded the fixture top-level `description` to make the new
  contract explicit: official data only, no current-implementation
  status fields.
- Moved the xfail case-id list into the test module as
  `XFAIL_CASE_IDS = frozenset({3, 4, 8, 9, 10, 11, 12, 13, 14, 15, 16})`
  at the top of
  `tests/test_iso16358_hspf_official_exact_golden.py`. The constant has
  a short docstring-style comment explaining that it tracks current
  calculator behavior, that the fixture must not be edited to silence
  xfail, and that this is the only place to update when a case starts
  matching.
- `official_exact_case_params()` now selects xfail by
  `case["case_id"] in XFAIL_CASE_IDS` instead of by
  `case["current_status"] == "mismatch"`. Mark semantics
  (`xfail(strict=True)`, reason text) are unchanged.
- case #13 / case #14 description duplicate is preserved exactly as the
  user provided it. The sanity test
  `test_official_exact_fixture_preserves_16_cases_and_duplicate_13_14`
  still passes.
- Test behavior is identical to before the hygiene change: 5 match
  cases pass, 11 mismatch cases stay strict-xfail, 1 sanity test
  passes.

### Task 2 — Horizontal table-input UI design

- New design doc:
  `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`.
- Pattern: `QTableView` + `QAbstractTableModel` (+ `QStyledItemDelegate`
  for editing). `QTableWidget` and `setCellWidget` shortcuts are
  explicitly disallowed. `blockSignals` calls must be wrapped in
  `try/finally`.
- Table shape per profile:
  - AHRI SEER2 — columns: `A_Full, B_Full, B_Low, E_Int, F_Low`;
    rows: `능력 [Btu/h]`, `전력 [W]`.
  - AHRI HSPF2 — columns: `H01, H11, H12, H1N, H22, H2Int, H32`;
    rows: `능력 [Btu/h]`, `전력 [W]`; auxiliary inputs (`t_off`,
    `t_on`, `defrost_t_test_minutes`, `defrost_t_max_minutes`) in a
    separate compact `QFormLayout`.
  - EN14825 SEER — columns: `A, B, C, D`;
    rows: `능력 [kW]`, `전력 [kW]`.
  - EN14825 SCOP — columns: `A, B, C, D, TOL, Tbiv`;
    rows: `능력 [kW]`, `전력 [kW]`; auxiliary inputs
    (`p_design_h`, `climate`, `TOL_temp_c`, `Tbiv_temp_c`,
    `p_to_w`, `p_sb_w`, `p_ck_w`, `p_off_w`) in a separate compact
    `QFormLayout`.
- Per-cell unit column is explicitly forbidden. Units live on the row
  label or the table title only, because the calculator profile fixes
  the input unit.
- Recommended first-slice order:
  1. AHRI SEER2 table input (first slice).
  2. AHRI HSPF2 table input.
  3. EN14825 SCOP table input.
  4. EN14825 SEER table input.
  5. Drop unused `input_widgets_*` dict keys.
  6. Wire the unit adapter (separate slice).
- During each slice the existing `input_widgets_ahri`,
  `input_widgets_hspf2`, `input_widgets_en` dicts are not deleted in
  one step; the new model keeps the dict keys populated until the
  dict-style reads at the calculate-action site are also migrated.

### Task 3 — Calculator unit boundary

- Same design doc as task 2, "Unit boundary" sections.
- ML canonical unit: capacity W, power W (regardless of target
  calculator profile). Applies to ML / inverse-search output and to
  any `source="ml_prediction"` PredictedPointsEnvelope.
- Calculator-native units per profile:
  - ISO16358 / KS C 9306 → capacity W, power W.
  - AHRI SEER2 / AHRI HSPF2 → capacity Btu/h, power W.
  - EN14825 SEER / SCOP → capacity kW, power kW.
- Conversion factors:
  - `W → Btu/h = W × 3.412141633`
  - `W → kW = W / 1000`
- Source vocabulary stays
  `manual_candidate / ml_prediction / fixture`, unchanged.
- `manual_candidate` (and `fixture`) input is interpreted as
  profile-native. The UI row label is the unit contract.
- `ml_prediction` input is interpreted as W canonical and must pass
  through the unit adapter before reaching a calculator.
- The unit adapter (future slice) is the single conversion site.
  Calculator core, UI table model, and ML callers do not perform unit
  conversion.
- The future adapter envelope will carry a
  `units_trace = {source_units, target_units, conversion_applied}`
  marker; the `CalculatorInputEnvelope` schema is not yet changed in
  this design phase.
- Suggested next implementation steps after this design:
  1. AHRI SEER2 table input slice (UI only, no unit adapter).
  2. `core/calculator_unit_adapter.py` first slice — convert
     ml_prediction (W) into AHRI SEER2 native (Btu/h, W) and emit
     `units_trace`; add unit adapter smoke tests.
  3. Extend the unit adapter to ISO / KS / EN profiles.
  4. Migrate the remaining UI table slices (AHRI HSPF2, EN14825 SCOP,
     EN14825 SEER).
  5. Wire the unit adapter into the ML / inverse-search caller path.

## Test Results

- `python3 -B -m py_compile tests/test_iso16358_hspf_official_exact_golden.py`
  → exit 0.
- `python3 -B -m pytest tests/test_iso16358_hspf_official_exact_golden.py -q`
  → `6 passed, 11 xfailed in 0.06s` (sanity + 5 match cases pass; 11
  mismatch cases stay strict-xfail).
- `python3 -B -m pytest tests/test_calculator_input_adapter.py tests/test_calculator_prediction_adapter.py tests/test_calculator_ranking_adapter.py -q`
  → all green; with the official-exact suite included, `60 passed, 11
  xfailed`.
- `python3 -B -m pytest -q`
  → `370 passed, 34 xfailed`.

## Changed Files

- `tests/fixtures/iso16358_hspf_official_exact_cases.json` — removed
  `current_status` field from every case; reworded top-level
  description; expected / input / case_id / description / notes
  unchanged.
- `tests/test_iso16358_hspf_official_exact_golden.py` — added
  `XFAIL_CASE_IDS` constant; `official_exact_case_params()` reads
  xfail status from the constant instead of the fixture.
- `docs/designs/2026-05-17-calculator-horizontal-table-input-ui.md`
  — new design doc covering AHRI / EN14825 horizontal table input UI
  and the ML W ↔ calculator-native unit boundary.
- `docs/WORK_PLAN.md` — short note that the fixture status is now in
  the test module and the table-input / unit-boundary design doc
  exists; near-term execution order references the new design.
- `result_reports/active/084_fixture-hygiene-and-calculator-table-unit-boundary-design.md`
  — this report.

## Known Failures / Risks

- The 11 mismatched ISO16358-2 HSPF cases (3, 4, 8, 9, 10, 11, 12, 13,
  14, 15, 16) remain `xfail(strict=True)`. Mismatch analysis is
  explicitly deferred. Touching expected values to silence xfail is
  blocked by the new fixture contract.
- Per-cell unit override on the future table UI is a real risk because
  the legacy form already labels every cell. The design doc flags this
  and bans per-cell unit widgets.
- Mixed dict / model reads during a partial UI migration could regress
  the calculate action. The design doc requires each slice to keep the
  dict keys populated until the corresponding read site is migrated.
- `ml_prediction` payloads at non-W units would silently break the
  calculator if the adapter does not fail-fast. The design doc
  requires fail-fast in the adapter slice.

## Next Suggested Action

1. Slice A — implement only the AHRI SEER2 horizontal table input as a
   `QAbstractTableModel`, keeping the existing `input_widgets_ahri`
   dict populated. Add an offscreen PyQt smoke test that exercises
   model-driven AHRI SEER2 → existing calculate path.
2. After Slice A is stable, take the unit adapter slice as a separate
   `core/calculator_unit_adapter.py` change (no UI work in the same
   commit). Add unit adapter smoke + fail-fast tests.

## Scope Compliance

- Calculator core (`core/calculator_iso16358.py`, calculator profile
  files, region configs) was not modified.
- Expected HSTL / HSEC / HSPF values were not modified.
- `XFAIL_CASE_IDS` was not narrowed; xfail strictness is preserved.
- No UI code was modified.
- No unit adapter / ML caller code was added.
- No envelope schema (`CalculatorInputEnvelope`,
  `CalculatorResultEnvelope`, `PredictedPointsEnvelope`,
  `RankingCandidateEnvelope`) field change.
- AHRI / EN14825 calculator wiring, `app_calculator.py`,
  `ui/calc_window.py` were not modified.
- `tests/test_calculator_schema_boundaries.py` was not modified.
- No fixture rename, split, or reorganization beyond removing a single
  redundant field.

## Commit / Push

- Source / docs commit: fixture hygiene + design doc + WORK_PLAN
  status note in one commit, separate from the report commit.
- Report commit: this report as its own commit using
  `report: ...` style.
- Both commits to be pushed to `origin/work/iso-separation-plan`.
