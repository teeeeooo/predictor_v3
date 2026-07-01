# KOREA Guide Table Helper Cleanup

## Goal

Reduce duplicated KOREA CSPF/HSPF midpoint guide table UI code without changing
calculator behavior.

## Scope

- Added `KoreaMidpointGuideTable` as a small Tk UI helper under
  `apps/calculator/ui/sections/`.
- Moved guide row/address ownership, read-only table creation, value display,
  and status display into the helper.
- Updated KOREA CSPF/HSPF sections to delegate guide display while preserving
  `guide_table` and `guide_controller` test-visible attributes.

## Non-goals

- No core KS C 9306 formula, config, profile, public result contract, fixture,
  or golden changes.
- No batch/detail framework refactor.
- No base section class or broad abstraction.
- No report lifecycle cleanup and no Arc 13.5 work.

## Verification

- `python3 -B -m compileall -q apps/calculator tests`: OK.
- `python3 -B -m pytest -q tests/test_calculator_korea_cspf_usecase.py tests/test_calculator_korea_hspf_usecase.py tests/test_calculator_korea_detail_contract.py tests/test_ui_tk_korea_batch_profiles.py tests/test_apps_calculator_ui_korea_tab.py`:
  OK with headless Tk skips, 16 passed and 2 skipped.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing hotspot
  warnings plus code-map freshness reminder.
- `git diff --check`: OK.
- `git status --short`: reviewed before commit.

## Task Results

- Guide helper extraction: OK.
- CSPF/HSPF section cleanup: OK.
- Behavior preservation: focused usecase/detail/batch/tab tests passed or
  skipped only where Tk display was unavailable.

## Structure Warnings

- No changed KOREA source file emitted a structure soft warning.
- LOC moved from duplicated section code into a 67 LOC helper:
  - `korea_cspf_section.py`: 301 -> 262 LOC.
  - `korea_hspf_section.py`: 316 -> 274 LOC.
- `code_map_check`: skipped. The prompt's allowed files did not include
  `docs/code_map/CODEBASE_REFERENCE_MAP.md`; structure guard reported the
  expected freshness reminder.

## Known Risks

- Tk visual/manual smoke was not run in this headless environment.
- Sections remain above the 250 LOC soft planning threshold, but this cleanup
  reduced duplication and did not add responsibilities.

## Commit / Push

- Commit: performed after report finalization; final hash is reported in the
  terminal response.
- Push: not run per prompt.
