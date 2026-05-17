# 045_iso-separation-step2a-prerename-audit

## Goal
- `iso_seperation_plan.md` Step 2a를 수행한다.
- `core/calculator_iso16358.py` legacy rename 전에 direct import sites를 분류하고, Step 2b의 atomic rename/import retarget 기준을 고정한다.

## Scope
- Audit/report only.
- No calculator, test, fixture, region config, UI behavior, workbook/reference file changes.
- `project_log.md`에는 Step 2a audit decision만 기록.

## Evidence Commands
- `git status --short --branch` → clean branch at start of audit: `work/iso-separation-plan...origin/work/iso-separation-plan`.
- `rg -l "from core\\.calculator_iso16358 import ISO16358Calculator|import core\\.calculator_iso16358 as iso" tests core ui | sort`
  - Found 33 test files and 1 UI file.
- `rg -n "from core\\.calculator_iso16358 import ISO16358Calculator|import core\\.calculator_iso16358 as iso|ISO16358Calculator\\(" tests core ui | sort`
  - Confirmed direct constructor/import sites.
- `rg -n "ISO16358Calculator|calculator_iso16358" ui/calculators_2point.py core/calculator_dispatcher.py`
  - Confirmed 3 UI sites in `ui/calculators_2point.py`; dispatcher has no active ISO import/branch.
- `python3 -B -m pytest tests -q`
  - `269 passed, 16 failed, 13 xfailed`.
  - Failure set remains pre-existing ISO HSPF formula/golden/diagnostic failures.

## Direct Import Inventory
| File | Step 2b action | Classification | Step 3/4 intent |
| --- | --- | --- | --- |
| `tests/test_iso16358_cspf_iso_t1_2point_control_samples.py` | keep path, retarget import to `_legacy` | pure ISO CSPF contract | Step 3 CSPF reactivate on new ISO |
| `tests/test_iso16358_cspf_iso_t1_default_config.py` | keep path, retarget import to `_legacy` | pure ISO CSPF contract | Step 3 CSPF reactivate |
| `tests/test_iso16358_cspf_iso_t1_default_golden.py` | keep path, retarget import to `_legacy` | pure ISO CSPF contract | Step 3 CSPF reactivate |
| `tests/test_iso16358_cspf_iso_boundary_eer_control_regression.py` | keep path, retarget import to `_legacy` | pure ISO CSPF contract | Step 3 CSPF reactivate |
| `tests/test_iso16358_cspf_clause67_bin_diagnostics.py` | keep path, retarget import to `_legacy` | pure ISO CSPF diagnostic/contract | Step 3 CSPF reactivate if still relevant |
| `tests/test_iso16358_cspf_official_tool_formula_diagnostics.py` | keep path, retarget import to `_legacy` | pure ISO CSPF diagnostic/contract | Step 3 CSPF reactivate if still relevant |
| `tests/test_iso16358_hspf_formula_micro.py` | keep path, retarget import to `_legacy` | pure ISO HSPF formula contract | Step 3 HSPF reactivate |
| `tests/test_iso16358_hspf_pure_iso_track_a.py` | keep path, retarget import to `_legacy` | pure ISO HSPF track A | Step 3 HSPF reactivate |
| `tests/test_iso16358_hspf_compatibility_boundary.py` | keep path, retarget import to `_legacy` | pure ISO HSPF boundary guard | Step 3 HSPF reactivate |
| `tests/test_iso16358_hspf_smoke.py` | keep path, retarget import to `_legacy` | pure ISO HSPF smoke | Step 3 HSPF reactivate |
| `tests/test_iso16358_hspf_validation.py` | keep path, retarget ISO import to `_legacy`; keep KS import as-is | mixed file, ISO validation + KS validation already direct KS | Step 3 may split/retarget ISO portions |
| `tests/test_iso16358_hspf_golden.py` | keep path, retarget ISO import to `_legacy`; keep KS import as-is | mixed file, ISO golden + KS golden already direct KS | Step 3 may split/retarget ISO portions |
| `tests/test_iso16358_hspf_ks_oracle.py` | keep path, retarget ISO common import to `_legacy`; keep KS import as-is | KS/ISO formula comparison | Step 3 decide whether new ISO can replace legacy side |
| `tests/test_iso16358_cspf_hong_kong_config.py` | keep path, retarget import to `_legacy` | regional ISO CSPF | Step 3 CSPF reactivate |
| `tests/test_iso16358_cspf_india_iseer_config.py` | keep path, retarget import to `_legacy` | regional ISO CSPF | Step 3 CSPF reactivate |
| `tests/test_iso16358_cspf_saso_config.py` | keep path, retarget import to `_legacy` | regional ISO CSPF | Step 3 CSPF reactivate |
| `tests/test_iso16358_cspf_saso_t3_regression.py` | keep path, retarget import to `_legacy` | regional ISO CSPF | Step 3 CSPF reactivate |
| `tests/test_iso16358_cspf_t3_profile.py` | keep path, retarget import to `_legacy` | regional/T3 ISO CSPF | Step 3 CSPF reactivate |
| `tests/test_iso16358_cspf_asean_report_examples.py` | keep path, retarget import to `_legacy` | regional ISO CSPF examples | Step 3 CSPF reactivate if examples remain official |
| `tests/test_iso16358_hspf_hong_kong_config.py` | keep path, retarget import to `_legacy` | regional ISO HSPF | Step 3 HSPF reactivate |
| `tests/test_iso16358_cspf_profile_calculation.py` | move to `tests/_legacy/`, retarget import to `_legacy` | diagnostic/mixed profile calculation | Rebuild later against profile/dispatcher if needed |
| `tests/test_iso16358_cspf_profile_resolver.py` | move to `tests/_legacy/`, retarget import to `_legacy` | diagnostic/mixed resolver detail | Rebuild later against new manifest/dispatcher if needed |
| `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py` | move to `tests/_legacy/`, retarget ISO import to `_legacy`; keep KS import as-is | diagnostic/mixed ISO + KS spot | Rebuild narrower diagnostics later |
| `tests/test_iso16358_hspf_h8_trace.py` | move to `tests/_legacy/`, retarget import to `_legacy` | diagnostic trace | Rebuild only if H8 trace remains needed |
| `tests/test_asnzs_hspf_excel_compat_component_accumulation.py` | keep path, retarget module import to `_legacy` | ASNZS negative assertion | Step 4 retarget negative target to new ISO or keep legacy depending intent |
| `tests/test_asnzs_hspf_excel_compat_component_energy.py` | keep path, retarget module import to `_legacy` | ASNZS negative assertion | Step 4 reassess |
| `tests/test_asnzs_hspf_excel_compat_component_row_mapping.py` | keep path, retarget module import to `_legacy` | ASNZS negative assertion | Step 4 reassess |
| `tests/test_asnzs_hspf_excel_compat_helper_column_reconstruction.py` | keep path, retarget module import to `_legacy` | ASNZS negative assertion | Step 4 reassess |
| `tests/test_asnzs_hspf_excel_compat_helper_columns.py` | keep path, retarget module import to `_legacy` | ASNZS negative assertion | Step 4 reassess |
| `tests/test_asnzs_hspf_excel_compat_helper_cop.py` | keep path, retarget module import to `_legacy` | ASNZS negative assertion | Step 4 reassess |
| `tests/test_asnzs_hspf_excel_compat_output_anchors.py` | keep path, retarget module import to `_legacy` | ASNZS negative assertion | Step 4 reassess |
| `tests/test_asnzs_hspf_excel_compat_partial_impl.py` | keep path, retarget module import to `_legacy` | ASNZS negative assertion | Step 4 reassess |
| `tests/test_asnzs_hspf_excel_compat_result_envelope.py` | keep path, retarget module import to `_legacy` | ASNZS negative assertion | Step 4 reassess |
| `ui/calculators_2point.py` | retarget import to `_legacy`; constructor sites unchanged | UI transition path | Step 5 swap to new ISO/profile dispatcher |

## Step 2b Atomic Change Plan
- `git mv core/calculator_iso16358.py core/calculator_iso16358_legacy.py`.
- Add new `core/calculator_iso16358.py` skeleton:
  - `ISO16358Calculator.__init__(config_path: str)` raises `NotImplementedError`.
  - `calculate_cspf(...)` raises `NotImplementedError`.
  - `calculate_hspf(...)` raises `NotImplementedError`.
  - No alias to legacy.
- Retarget direct test imports:
  - `from core.calculator_iso16358 import ISO16358Calculator` → `from core.calculator_iso16358_legacy import ISO16358Calculator`.
  - `import core.calculator_iso16358 as iso` → `import core.calculator_iso16358_legacy as iso`.
- Create `tests/_legacy/__init__.py`.
- Move diagnostic/mixed tests with `git mv`:
  - `tests/test_iso16358_cspf_profile_calculation.py`
  - `tests/test_iso16358_cspf_profile_resolver.py`
  - `tests/test_iso16358_cspf_iso_t1_default_diagnostics.py`
  - `tests/test_iso16358_hspf_h8_trace.py`
- Retarget `ui/calculators_2point.py` import to `_legacy`.
- `core/calculator_dispatcher.py` currently has no active ISO import/branch, so Step 2b only needs doc/comment correction if an ISO legacy reference is introduced during edit.

## Verification Plan For Step 2b
- `python3 -B -m py_compile core/calculator_iso16358.py core/calculator_iso16358_legacy.py core/calculator_ks_c9306.py ui/calculators_2point.py`.
- `python3 -B -m pytest tests -q`.
- Expected full-suite baseline: `269 passed, 16 failed, 13 xfailed`.
- `rg -n "from core\\.calculator_iso16358 import|import core\\.calculator_iso16358 as iso" tests ui core`
  - Expected: no test/UI legacy callers left on new skeleton path.
  - New skeleton import may appear only in future Step 3 tests or explicitly intentional code.
- `rg -n "calculator_iso16358_legacy" tests ui core`
  - Expected: all preserved legacy callers visible.
- UI smoke is manual/weak unless PyQt runtime can be exercised in this environment; if not run, report as weaker-verified.

## Baseline Failures
- Full suite after Step 2a audit: `269 passed, 16 failed, 13 xfailed`.
- The 16 failures are ISO HSPF formula/golden/diagnostic failures and are expected pre-existing baseline for this workstream:
  - `tests/test_iso16358_hspf_formula_micro.py` — 4 failures.
  - `tests/test_iso16358_hspf_golden.py` — 10 failures.
  - `tests/test_iso16358_hspf_pure_iso_track_a.py` — 1 failure.
  - `tests/test_iso16358_hspf_validation.py` — 1 failure.

## Changed Files
- `project_log.md`
- `result_reports/active/045_iso-separation-step2a-prerename-audit.md`

## Known Risks
- Step 2b is intentionally broad. A single missed import will route a legacy test into the new NotImplemented skeleton and fail immediately.
- Diagnostic/mixed moves can change pytest node IDs even if behavior is unchanged; report Step 2b counts and moved paths explicitly.
- ASNZS negative assertion tests inspect ISO module/class source. Retargeting them to `_legacy` preserves behavior for Step 2, but Step 4 must decide whether each assertion should target the new ISO skeleton or legacy residue.

## Commit / Push
- project log commit: pending at report creation time.
- report commit: pending at report creation time.
