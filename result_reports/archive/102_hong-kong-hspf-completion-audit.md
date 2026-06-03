# 102 — Hong Kong HSPF Completion Audit

- Mode: audit-only (no code/config/test/fixture/UI changes)
- Branch: work/iso-separation-plan
- Scope: assess whether Hong Kong HSPF is "complete" at the core/config/test level alone, or whether profile / dispatcher / UI wiring is required for an end-to-end completion claim.

## Task 1 — current HSPF implementation coverage (core/config/test)

Confirmed artifacts:

- `data/region_configs/hong_kong.json`
  - `hspf.enabled = true`
  - `hspf.profile = "iso16358_2_hspf"` (binds to the common ISO 16358-2 HSPF engine)
  - `hspf.standard = "ISO 16358-2"`
  - `hspf.extended_mode = false`
  - `hspf.correction = { cd: 0.25, aux_cop: 1.0 }`
  - `hspf.frost_boundaries = { lower: -7.0, upper: 5.5 }`
  - `hspf.load_line` present: `source = "rated_heating_capacity"`, `zero_load_temp = 17.0`, `full_load_temp = 0.0`, `rated_capacity_factor = 0.82` (ISO 16358-2 §6.2 reference).
  - `hspf_bin_hours` present: 11 bins, j=1..11, tj=6..16 °C, total nj = 240 h.
- `core/calculator_iso16358.py::calculate_hspf`
  - When `hspf.profile == "iso16358_2_hspf"` the method delegates straight to `calculate_hspf_iso16358_common(...)`. Same engine the official-exact 16-case golden runs against (no Hong-Kong-specific branch).
- `tests/test_iso16358_hspf_hong_kong_config.py` — 9 tests, all pass on this branch (see verification below). Covers: 2 golden HSPF values (3.643 / 4.572), 240 h bin total, explicit `rated_heating_capacity` required, validation of point dicts, `aux_cop > 0`, and the “2_half measured input is ignored when derived by footnote d” invariant.

Conflict check vs. latest ISO 16358-2 HSPF common engine (post-099/100):
- The two HK golden numbers are anchored to footnote-d derivation of 2_full / 2_half from 7_full / 7_half plus the −7 fallback factors `0.64 / 0.82` (see the inline comments in the tests). The common engine uses `_iso_hspf_resolve_common_points` + `_iso_hspf_common_load_line` + frost handling, which is the same code path exercised by the 16/16 official-exact golden. No 2_full/2_half/2_full_f/2_half_f policy regression observed — both suites pass simultaneously, so the HK config does not depend on a divergent policy.
- `extended_mode = false` and no `_full_f / _half_f` extended fixtures are required for the HK suite; the −7 fallback factors are applied through the common path used by the 099 fix.

Result: core + config + test layer for Hong Kong HSPF is **green** against the current common engine.

## Task 2 — profile / dispatcher / UI exposure

- `core/calculator_profiles.py`
  - `hong_kong_cspf` is registered (`standard=ISO_16358`, `metric=CSPF`, `mode=cooling`, `calculator_id=iso16358`, `config_path=data/region_configs/hong_kong.json`).
  - **No `hong_kong_hspf` profile exists.** There is no `ISO_16358 / HSPF` heating profile of any region in the registry today (`ks_c9306_hspf`, `ahri_usa_hspf2`, `asnzs_excel_hspf_compat` are the only HSPF entries).
- `core/calculator_dispatcher.py`
  - Already supports `calculator_id == "iso16358"` → constructs `ISO16358Calculator(config_path)`. Because `ISO16358Calculator` exposes both `calculate_cspf` and `calculate_hspf`, **no dispatcher branch change is required** to surface an HSPF profile; only a new profile row pointing at `calculator_id="iso16358"` plus `metric="HSPF"`, `mode="heating"` is needed.
- `tests/test_calculator_profiles.py` / `tests/test_calculator_dispatcher.py`
  - Both reference `hong_kong_cspf` only. No HSPF row to assert against today.
- `ui/calc_window.py`
  - Calculator window wires AHRI SEER2, AHRI HSPF2 v3, and EN14825 SEER/SCOP via profile-resolver-backed combos. ISO16358 calculators (HK CSPF, India ISEER, SASO T3, generic T1) are exposed through `ui/calculators_2point.py` (`_build_hong_kong_inputs`, `_recalculate_hong_kong` → `calculate_cspf`). **There is no UI input table that feeds `calculate_hspf` for any ISO16358 region.**
- `tests/test_app_calculator_ui_smoke.py`
  - Only AHRI SEER2 / AHRI HSPF2 v3 / EN14825 smokes. No ISO HSPF UI smoke exists, consistent with the absence of UI input.

Minimum connection scope needed to expose Hong Kong HSPF (audit only, no implementation):
1. **Profile-only**: add a `hong_kong_hspf` row to `_CALCULATOR_PROFILES` (`standard=ISO_16358`, `region=hong_kong`, `metric=HSPF`, `mode=heating`, `calculator_id=iso16358`, `config_path=data/region_configs/hong_kong.json`). This alone makes `create_calculator_for_profile(profile_id="hong_kong_hspf")` work (dispatcher already routes `iso16358`).
2. **Dispatcher**: no change needed (validated above).
3. **UI input**: a heating input table (rated_heating_capacity + 7_full/7_half capacity & power) is missing for ISO16358 HSPF and would be the new surface. This is heavier than for CSPF because the existing `ui/calculators_2point.py` 2-point grid is cooling-only.
4. **Result envelope / ranking adapter**: today’s envelope chain (`PredictedPoints → CalculatorInput → CalculatorResult → RankingCandidate`) is wired for AHRI SEER2 only (`core/calculator_unit_adapter.py`). ISO16358 HSPF would need its own unit adapter slice before it can participate in ranking. Profile + UI exposure can land without this if the goal is calculator-only.

## Task 3 — completion classification

Classification: **#3 — core/config/test 완료, profile 추가만으로는 “계산기 호출 가능” 까지만 도달. 사용자에게 노출하려면 profile + UI 입력 구조도 필요.** (Dispatcher branch is already in place, so option 3 collapses to option 2+4 in practice.)

Rationale:
- Core engine and config: complete and verified by 9 dedicated HK tests + 16/16 official-exact golden using the same common engine.
- Profile registry: Hong Kong HSPF is **not registered**. Without a profile row, `resolve_calculator_profile` / `create_calculator_for_profile` cannot reach it programmatically; today it is only reachable by direct `ISO16358Calculator("data/region_configs/hong_kong.json").calculate_hspf(...)` instantiation.
- Dispatcher: already capable (no work).
- UI: no HSPF input table for any ISO16358 region; HK HSPF cannot be invoked from `app_calculator.py`.
- ML/envelope: not wired for ISO HSPF.

“완료”라고 부를 수 있는 범위 (today, work/iso-separation-plan @ c0fb66b):
- **core 완료** — yes.
- **config 완료** — yes.
- **test 완료** — yes (HK config tests + common-engine golden).
- **profile 완료** — **no** (missing `hong_kong_hspf`).
- **dispatcher 완료** — yes (no change needed; `iso16358` path covers it once profile is added).
- **UI 완료** — **no** (no ISO HSPF input surface).
- **ML / envelope 완료** — **no** (no ISO HSPF unit adapter).

따라서 현 상태에서 Hong Kong HSPF는 “**ISO 16358-2 HSPF common-engine 위에서 라이브러리 호출로 동작이 검증된 region config**” 까지만 “완료” 라고 부를 수 있다. 사용자-facing “계산기 완료” 로 부르려면 최소한 profile 등록 + UI 노출이 추가로 필요하다.

Suggested minimum follow-up to call it “end-user complete” (proposal only; not executed):
- Step A — profile-only: add `hong_kong_hspf` profile row + extend `tests/test_calculator_profiles.py` and `tests/test_calculator_dispatcher.py` to assert it resolves and constructs an `ISO16358Calculator`. Smallest possible diff, no UI/ML coupling.
- Step B — UI input slice: introduce an ISO16358 HSPF input surface (rated_heating_capacity + 7_full/7_half table) reusing the spreadsheet-table contract; add a UI smoke. This is the riskier step because it’s a new horizontal table family.
- Step C — envelope/unit adapter: only if HK HSPF needs to participate in ranking/ML.

## Task 4 — report and WORK_PLAN

- Report path: `result_reports/active/102_hong-kong-hspf-completion-audit.md` (this file).
- `docs/WORK_PLAN.md`: **not modified** in this audit. Rationale: the audit conclusion is that further steps (profile-only / UI input / envelope) are discretionary; WORK_PLAN’s current Near-term execution order item 3 already lists “unit adapter 확장” and “ML / inverse-search 복귀 준비” after the ISO table UX patch slice. No new commitment is being made — only options are documented here for the next planning pass.
- Result-report lifecycle maintenance (active → archive moves, summaries, project_log lifecycle): **out of scope** per task brief.

## Verification

```
python3 -B -m pytest tests/test_iso16358_hspf_hong_kong_config.py tests/test_iso16358_hspf_official_exact_golden.py tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py tests/test_app_calculator_ui_smoke.py -q
→ 62 passed, 1 skipped

python3 -B -m pytest -q
→ 425 passed, 4 skipped, 23 xfailed
```

## Known Risks

- Result-report lifecycle maintenance pending (active → archive/summaries reconciliation) — intentionally not performed this turn.
- Adding `hong_kong_hspf` profile without a UI surface would create a profile that is resolvable programmatically but not reachable from `app_calculator.py`; downstream consumers (ranking, ML adapter) should not assume HSPF availability just because the profile exists.
- ISO HSPF horizontal-table input UI does not exist yet; reusing the spreadsheet-table contract is straightforward but is a net-new table family (cooling-only today in `ui/calculators_2point.py`).

## Files Modified

- `result_reports/active/102_hong-kong-hspf-completion-audit.md` (new, this report)
