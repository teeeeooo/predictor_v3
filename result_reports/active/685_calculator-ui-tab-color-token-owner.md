# Calculator UI Tab Color Token Owner

## Goal

Resolve the calculator UI structure guard error caused by a raw hex color literal in `apps/calculator/ui/calculator_app.py`.

## Scope

- Moved the selected top-notebook tab foreground value out of the Tk shell code and into the calculator UI visual owner module.
- Updated `CalculatorTkApp` to consume the owned constant.

## Changed Files

- `apps/calculator/ui/layout_constants.py`
- `apps/calculator/ui/calculator_app.py`

## Verification

- `python3 -B -m py_compile apps/calculator/ui/calculator_app.py apps/calculator/ui/layout_constants.py` - OK
- `python3 -B tools/check_code_structure.py` - OK, with existing soft warnings only
- `python3 -B tools/code_checker/build_reference_map.py --check` - STALE, existing reference map freshness warning recorded

## Structure Warnings

- Changed files: none.
- Repository-level existing warnings remain for large historical files and code-map freshness.

## Change Gate

- Reuse/commonization decision: reused existing calculator UI visual owner `apps/calculator/ui/layout_constants.py`; no new helper, adapter, surface, or public interface was introduced.
- Repeated local-policy risk: low. The literal now follows the same constant consumption pattern as sibling calculator UI surfaces.
- `code_map_check`: checked; stale map was reported but not regenerated because this change does not add or reshape source ownership.

## Known Risks

- No visual regression run was performed; the value is unchanged and only its ownership moved.
- The broader calculator UI constants still contain historical concrete visual values by design as the configured owner path.

## Commit / Push

- Source commit: `91aee47`
- Report commit: recorded in final terminal response
- Push: recorded in final terminal response
