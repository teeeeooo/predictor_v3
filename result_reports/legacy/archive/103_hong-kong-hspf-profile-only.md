# 103 — Hong Kong HSPF Profile Registration (profile-only slice)

- Mode: implementation (registry + tests + docs).
- Branch: work/iso-separation-plan.
- Predecessor: 102 audit — concluded that Hong Kong HSPF core/config/test was complete, dispatcher already supported `calculator_id="iso16358"`, but no `hong_kong_hspf` profile was registered and no ISO HSPF UI surface existed.
- Scope: register `hong_kong_hspf` in the calculator profile registry and protect the resolve/dispatcher smoke with tests. UI input surface is **not** added. ISO HSPF unit adapter / envelope is **not** added.

## Task 1 — registry change

- File modified: `core/calculator_profiles.py`
- New profile row inserted directly after `hong_kong_cspf`:
  - `profile_id="hong_kong_hspf"`
  - `standard="ISO_16358"`
  - `region="hong_kong"`
  - `metric="HSPF"`
  - `mode="heating"`
  - `calculator_id="iso16358"`
  - `config_path="data/region_configs/hong_kong.json"`
  - `enabled=True`
- Relationship to `hong_kong_cspf`: same `config_path` and same `calculator_id`. Only `metric` / `mode` diverge. CSPF profile row is untouched.

## Task 2 — profile resolve + dispatcher smoke

- `tests/test_calculator_profiles.py`
  - Added `hong_kong_hspf` to the enabled profile set assertion in `test_list_calculator_profiles_returns_enabled_profiles_only`.
  - Added `test_resolve_hong_kong_hspf_by_profile_id_returns_hong_kong_json` — asserts profile_id, standard, region, metric, mode, calculator_id, config_path.
  - Added `test_resolve_hong_kong_hspf_by_selector` — resolves via `(standard, region, metric, mode) = (ISO_16358, hong_kong, HSPF, heating)`.
  - Added `test_hong_kong_cspf_and_hspf_share_config_but_resolve_independently` — guards that CSPF/HSPF share config_path/calculator_id but resolve as separate enabled profiles.
- `tests/test_calculator_dispatcher.py`
  - Added `hong_kong_hspf` to the existing ISO profile parametrize (`test_dispatcher_returns_iso_calculator_for_iso_profiles`).
  - Added `test_dispatcher_hong_kong_hspf_smoke_calculates_hspf` — uses the dispatcher to instantiate the calculator, confirms it has `calculate_hspf`, then runs HK golden case 1 (`rated_heating_capacity=6300`, `7_full=6300/1500`, `7_half=3200/800`) and asserts `hspf ≈ 3.643` (the same value protected by `test_iso16358_hspf_hong_kong_config.py`).
- `core/calculator_dispatcher.py`: **not modified.** The existing `calculator_id == "iso16358"` branch already constructs `ISO16358Calculator(config_path)`, which exposes `calculate_hspf`. Dispatcher smoke test passes without code changes.

## Task 3 — preservation of Hong Kong HSPF core/config/golden

- `tests/test_iso16358_hspf_hong_kong_config.py`: 9 / 9 pass after the registry change (no expected / fixture / engine modifications).
- `tests/test_iso16358_hspf_official_exact_golden.py`: 16 / 16 pass (16-case official-exact golden unchanged, `XFAIL_CASE_IDS` still empty).
- `tests/test_calculator_schema_boundaries.py`: passes — the new profile row does not introduce new keys at the calculator/region-config/adapter boundary.
- Confirmation: profile registration is metadata-only; no calculation path, region config field, or envelope key changes.

## Task 4 — docs / log

- `docs/WORK_PLAN.md`: appended one line under "Current milestone focus" stating that Hong Kong HSPF is core/config/test + profile/dispatcher smoke complete (profile shares HK config with `metric=HSPF` / `mode=heating`, dispatcher reuses the existing `iso16358` branch, UI surface still absent). Near-term execution order is unchanged and remains:
  1. ISO table Excel-like behavior patch
  2. ISO result/read-only table copy TSV
  3. unit adapter 확장: ISO / KS / EN profile
  4. ML / inverse-search 복귀 준비
- `project_brief.md`: appended a "Hong Kong HSPF 상태" bullet — "core/config/test + profile resolve 완료, UI surface 미완료" — under "현재 상태 및 마일스톤".
- `project_log.md`: appended `### Follow-up — Hong Kong HSPF profile registration` (Result / Verification / Decision). Justification: per `AGENT_TASK_ROUTER.md` §“coding work / architecture-sensitive changes”, calculator registry / profile manifest changes are an explicit log trigger. Most recent two log sections (`Follow-up — audit_3 immediate next actions completion`, `Follow-up — audit_2 immediate next actions completion`) are about adapter envelope and earlier ISO separation work and do not merge cleanly with this profile-only registration, so a new short subsection was added rather than amending an existing one.
- Result report lifecycle maintenance (active → archive/summaries reconciliation): **out of scope** per task brief. Noted as pending under Known Risks.

## Verification

```
python3 -B -m py_compile core/calculator_profiles.py
→ ok

python3 -B -m pytest tests/test_calculator_profiles.py -q
python3 -B -m pytest tests/test_calculator_dispatcher.py -q
python3 -B -m pytest tests/test_iso16358_hspf_hong_kong_config.py -q
python3 -B -m pytest tests/test_iso16358_hspf_official_exact_golden.py -q
python3 -B -m pytest tests/test_calculator_schema_boundaries.py -q
→ combined 70 passed

python3 -B -m pytest -q
→ 430 passed, 4 skipped, 23 xfailed
```

## Known Risks

- ISO HSPF UI input surface still absent. Adding `hong_kong_hspf` makes the profile reachable programmatically but not from `app_calculator.py`; downstream consumers should not assume HSPF availability just because the profile resolves.
- ISO HSPF unit adapter / envelope coverage is still AHRI SEER2 only. ranking/ML callers must not flow HK HSPF through `core/calculator_unit_adapter.py` until that adapter is extended.
- result_reports lifecycle maintenance (active → archive/summaries reconciliation) pending — intentionally not performed this turn.

## Files Modified

- `core/calculator_profiles.py` (new `hong_kong_hspf` profile row)
- `tests/test_calculator_profiles.py` (enabled set + resolve / selector / shared-config tests)
- `tests/test_calculator_dispatcher.py` (ISO parametrize + HSPF smoke)
- `docs/WORK_PLAN.md` (one-line status update)
- `project_brief.md` (Hong Kong HSPF status bullet)
- `project_log.md` (new Follow-up subsection)
- `result_reports/active/103_hong-kong-hspf-profile-only.md` (this report)
