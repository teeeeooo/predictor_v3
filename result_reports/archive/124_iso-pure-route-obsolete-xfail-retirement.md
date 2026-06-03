# 124 — ISO Pure-Route Obsolete Xfail Retirement

## Goal

ISO pure-route Formula 45/49/47/50 xfail 4개가 현재도 필요한 production guard인지 확인하고, obsolete experiment로 판단되면 해당 tests만 제거한다. Core calculator, expected, fixture, profile, dispatcher는 수정하지 않는다.

## Scope

- `tests/test_iso16358_hspf_pure_iso_track_a.py`의 xfail 4개와 passing smoke 역할 확인.
- Official exact golden / boundary COP / frost trace / `-7_ext` default tests와 중복/대체 관계 확인.
- Obsolete로 판단된 xfail test block 제거.
- `docs/WORK_PLAN.md`에 결과와 next action 짧게 반영.
- 본 report 작성.

## Non-goals

- Core calculator 수정.
- Expected / fixture 수정.
- Profile / dispatcher 수정.
- `tests/_legacy` 또는 AS/NZS xfail 수정.
- PyQt fatal-abort 해결.
- Tkinter 기능 구현.
- PyInstaller 실행.
- Legacy cleanup.
- Result report lifecycle maintenance.
- `project_log.md`, `ACTIVE_DOCUMENTS.md`, architecture 문서 수정.
- AGENTS_FULL.md 열람.

## Task 1 Results

확인한 xfail 4개:

| test | reason | fixture shape / expected | current `--runxfail` failure |
| --- | --- | --- | --- |
| `test_pure_iso_track_a_half_to_full_formula_45_non_frost_route_level_xfail` | Formula 45 route deferred; current route uses capacity-linear interpolation | one-bin 7C, `7_full` + `7_half`, hand-calculated HSEC `333.3333333333333` | assertion mismatch: actual HSEC `332.4593827903378` |
| `test_pure_iso_track_a_half_to_full_formula_49_frost_route_level_xfail` | Formula 49 frost route deferred; current route uses capacity-linear interpolation | one-bin -7C, `7_full`/`7_half`/`-7_full`/`-7_half`, hand-calculated HSTL `1150.0` | assertion mismatch: actual HSTL `1500.0` |
| `test_pure_iso_track_a_full_to_extended_formula_47_non_frost_route_level_xfail` | Formula 47 route deferred; current route falls back to saturated handling | one-bin 7C, `7_full` + `7_ext`, no `7_half` | runtime/schema mismatch: normalizer requires `7_half` |
| `test_pure_iso_track_a_full_to_extended_formula_50_frost_route_level` | Formula 50 active but differs from hand-calculated pure ISO contract | one-bin -7C, ad hoc `7_half` plus `7_ext`/`-7_full`/`-7_ext`, hand-calculated HSEC `516.1290322580645` | assertion mismatch: actual HSEC `535.6634845349414` |

Passing tests kept in `tests/test_iso16358_hspf_pure_iso_track_a.py`:

- Fixture identity and non-AS/NZS workbook-reference guards.
- Fixture contains cases smoke.
- One-bin cycling + degradation coefficient smoke.
- Formula 44/48 min-to-half route-level smoke.
- Saturated auxiliary route-level smoke.

Replacement / overlap checks:

- `tests/test_iso16358_hspf_official_exact_golden.py`: `XFAIL_CASE_IDS` is empty and official exact 16-case production golden passes.
- `tests/test_iso16358_hspf_boundary_cop_alignment.py`: focused Formula 45 endpoint invariant, Formula 47 trace-key skip-safe check, Formula 50 endpoint/spec-form checks.
- `tests/test_iso16358_hspf_frost_trace.py`: frost flag boundary behavior.
- `tests/test_iso16358_hspf_extended_default.py`: `-7_ext` measured passthrough and two-step default factor.
- Reports 097/099/100/122/123 confirm the endpoint/frost/default/official exact coverage and the latest obsolete-candidate judgment.

## Task 2 Results

Classification: **obsolete — test removal** for all four xfails.

Judgment basis:

- Official exact 16-case golden now covers production ISO16358-2 HSPF behavior at the user-facing calculator level.
- Boundary COP alignment tests protect Formula 45/47/50 endpoint/trace invariants more directly than the old one-bin pure-route expected values.
- Frost trace and `-7_ext` default tests protect the specific frost/default behavior that previously drove HSPF mismatch work.
- The four xfail tests do not protect a current user region/profile behavior. They encode Track A experiment contracts from before original-text audit and official-golden consolidation.
- One fixture shape is not even aligned with current required input schema (`7_half` missing in the Formula 47 case).
- Expected values are hand-calculated experimental targets, not the current official exact fixture source or current calculator contract.
- Failure indicates obsolete contract/schema assumptions rather than a production regression that should remain pinned as xfail.

Targeted `--runxfail` before removal:

- `python3 -B -m pytest tests/test_iso16358_hspf_pure_iso_track_a.py -q --runxfail` -> 4 failed, 7 passed.
- Failure types: 3 assertion mismatches, 1 runtime/schema mismatch (`7_half` required).

## Task 3 Results

Removed from `tests/test_iso16358_hspf_pure_iso_track_a.py`:

- Formula 45 half-to-full non-frost xfail test.
- Formula 49 half-to-full frost xfail test.
- Formula 47 full-to-extended non-frost xfail test.
- Formula 50 full-to-extended frost xfail test.

No helper/import was removed:

- `pytest`, `json`, `pathlib`, `ISO16358Calculator`, and `load_pure_iso_track_a_fixture()` remain used by the kept passing tests.
- Fixture JSON was not edited because fixture/expected changes are out of scope.

Kept tests:

- 4 fixture metadata/guard tests.
- 3 route-level passing smoke tests: cycling, Formula 44/48 min-half, saturated auxiliary.

Xfail count change:

- Full-ish suite xfail count dropped from 23 to 19.
- Remaining xfails are `tests/_legacy` 17 + AS/NZS case3 2.

## Task 4 Results

`docs/WORK_PLAN.md` now records:

- ISO pure-route Formula 45/49/47/50 obsolete experiment xfails were removed.
- Full-ish baseline moved to 19 xfailed.
- Remaining xfail cleanup order: `tests/_legacy` diagnostic reason/owner cleanup, AS/NZS case3 external reference compatibility decision, Windows PyInstaller size measurement when a Windows host is available.
- PyQt fatal-abort handling remains a separate environment slice.

Lifecycle maintenance is excluded:

- This task creates one active report (`124`) after the previous lifecycle summary cleared active reports.
- No archive/summaries movement is needed or allowed in this slice.

## Task 5 Results

Verification:

- `python3 -B tools/check_code_structure.py` -> `code structure guard: OK (no findings)`.
- `python3 -B -m pytest tests/test_iso16358_hspf_pure_iso_track_a.py -q -rxX` -> 7 passed.
- `python3 -B -m pytest tests/test_iso16358_hspf_official_exact_golden.py -q` -> 17 passed.
- `python3 -B -m pytest tests/test_iso16358_hspf_boundary_cop_alignment.py tests/test_iso16358_hspf_frost_trace.py tests/test_iso16358_hspf_extended_default.py -q` -> 17 passed, 1 skipped.
- Full-ish suite excluding 4 PyQt fatal-abort files -> 568 passed, 1 skipped, 19 xfailed.

Official exact golden result:

- 17 passed, with 16 parametrized golden cases passing and no xfail markers active.

Remaining xfail count:

- 19 xfailed: 17 `tests/_legacy` diagnostic/reference xfails + 2 AS/NZS case3 reference/full-row-data prerequisite xfails.

## Changed Files

- `tests/test_iso16358_hspf_pure_iso_track_a.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/124_iso-pure-route-obsolete-xfail-retirement.md`

## Known Risks

- The pure-route fixture JSON still contains obsolete case data for the removed tests. It was intentionally not edited because fixture/expected changes are out of scope.
- Historical docs and archived reports still mention Pure ISO Track A xfails. Those are historical records and were not rewritten.
- Remaining xfails are intentionally untouched: 17 legacy diagnostics and 2 AS/NZS case3 reference/full-row-data prerequisites.

## Scope Compliance

No core calculator, expected, fixture, profile, dispatcher, `tests/_legacy`, AS/NZS tests, PyQt tests, Tkinter code, `project_log.md`, `ACTIVE_DOCUMENTS.md`, architecture docs, archive/summaries, or lifecycle maintenance files were modified.

## Commit / Push

- Commit: this lifecycle/source/report commit.
- Push: pending.
