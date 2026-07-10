# KOREA Top-level Tab Skeleton

## Goal

Implement Slice 1 of the KOREA calculator notebook sub-arc: add a top-level
`KOREA` calculator tab with nested `CSPF` and `HSPF` skeleton pages.

## Scope

- Registered `KOREA` in `CalculatorTkApp`.
- Added `KoreaTab` under the existing calculator top-level tab owner package.
- Added focused construction/registration tests for the top-level and nested
  notebooks.
- Regenerated the code reference map after adding a new UI source file.

## Non-goals

- No KS C 9306 core, profile, region config, formula, fixture, or golden
  expected changes.
- No CSPF/HSPF single-input UI, midpoint guide, batch, or detail implementation
  in this slice.

## Reference Parity

- Primary reference checked: `apps/calculator/ui/tabs/ahri210240_tab.py`.
- Reuse outcome: reused the existing `ProfileVisibleContentLifecycleController`
  and nested metric notebook pattern.
- EN14825 was checked only for lifecycle/refit context; common-input sync was
  not copied because Slice 1 only creates the navigation skeleton.

## Verification

- `python3 -B -m pytest -q tests/test_apps_calculator_ui_korea_tab.py`: weaker
  verified; 2 skipped because Tk could not open in the headless environment.
- `python3 -B -m compileall -q apps/calculator tests`: OK.
- `python3 -B tools/check_code_structure.py`: OK with 9 pre-existing soft
  warnings outside the changed source files.
- `python3 -B tools/code_checker/build_reference_map.py`: regenerated
  `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- `git diff --check`: OK.

## Structure Warnings

- No changed/new source file emitted a structure warning.
- Existing warnings remain in calculator core/EN14825/batch hotspot files and
  were not part of this slice.

## change_gate

- owner_boundary: existing `apps/calculator/ui/tabs/` top-level tab package.
- reuse_commonization: `reused-existing-owner`; AHRI nested-tab lifecycle owner
  was reused for the KOREA skeleton.
- code_map_check: `regenerated`; `docs/code_map/CODEBASE_REFERENCE_MAP.md` is
  included in the diff.

## Known Risks

- Automated widget construction assertions were skipped because Tk display
  creation was unavailable. Import/compile/static structure checks passed.
- KOREA tab pages are intentionally empty skeleton frames until Slice 2/3 add
  CSPF/HSPF sections.

## Commit / Push

- Commit: performed after report finalization; final hash is reported in the
  terminal response.
- Push: not run; push is reserved for final Slice 6 closeout.
