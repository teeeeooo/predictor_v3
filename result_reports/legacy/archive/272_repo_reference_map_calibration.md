# 272 Repo Reference Map Calibration

## Goal

Improve the predictor_v3 code_checker reference map so it is useful as a
pre-write evidence gate. Reduce noise in duplicate helpers, hotspot sections,
keyword groups, and import edges while keeping the map compact.

## Scope

- Refine scanner symbol classification (top-level vs method vs nested).
- Filter framework method noise from duplicate candidates.
- Split hotspots into Active and Legacy / Deferred sections.
- Rename Owner Groups to Keyword Hit Groups with clearer semantics.
- Improve import edge granularity (module prefix instead of top-level only).
- Split renderer long function into section helpers.
- Add focused tests.
- Regenerate compact map.

## Excluded Scope

- AGENTS/ROUTER hook policy adoption (deferred to next slice).
- Semantic clone detection.
- Full call graph.
- CI / pre-commit hook.
- Lumin plugin integration.
- ui_tk cleanup or controller switch.

## Current Noise Root Causes (Task 1)

1. **Duplicate section noise**: Scanner treated all functions uniformly. Class
   methods like `grid`, `pack`, `data`, `keyPressEvent` were listed as
   extraction candidates. These are toolkit framework methods, not reusable
   helpers.
2. **Legacy dominance**: `core/_legacy/` and old `ui/` PyQt files occupied
   the top of the unified hotspot list, pushing current active risks
   (`ui_tk/metric_input_table.py`, etc.) below the fold.
3. **Renderer self-hotspot**: `render_compact_map()` was 87 LOC, triggering
   its own long-function warning.
4. **Keyword overmatching**: `table` keyword included `row`, `column`, `cell`,
   causing core calculator and predictor files to appear in the table group.
5. **Import edge granularity**: Edges showed only top-level modules
   (`ui_tk/foo.py -> ui_tk`), which is too coarse to assess layer coupling.

## Symbol Kind Calibration (Task 2)

**Change**: `Symbol` dataclass now carries a `kind` field:
- `"class"`
- `"top_level_function"`
- `"method"`
- `"nested_function"`
- `"constant"`

**Implementation**: `_SymbolVisitor` tracks a context stack (`"class"` or
`"function"`). When a `FunctionDef` is visited:
- Module level (no context) -> `"top_level_function"`
- Inside a class -> `"method"`
- Inside a function -> `"nested_function"`

**Backwards compatibility**: `FileInfo.functions` property returns all
function kinds concatenated, preserving existing hotspot analysis callers.

## Duplicate Noise Reduction (Task 3)

**Changes**:
- `find_duplicate_symbols` now scans only `classes + top_level_functions +
  constants`. Methods are excluded from extraction-candidate analysis.
- Added `_FRAMEWORK_METHOD_NOISE` set containing 30+ common UI framework
  method names (`grid`, `pack`, `rowCount`, `columnCount`, `data`,
  `headerData`, `setData`, `flags`, `keyPressEvent`, `paintEvent`, etc.).
- Symbols matching this set are excluded regardless of kind.

**Result**: Duplicate section dropped from 220+ entries to ~20 focused
entries. Actual repeated helpers like `_validate_source`, `_bin_details`,
`_metric_value`, `_kwh_value`, `ISO16358Calculator` remain visible.

## Hotspot Split (Task 4)

**Change**: `find_hotspots` now returns `(active_hotspots, legacy_hotspots)`.

**Categorization rules**:
- `core/_legacy/` -> legacy
- `ui/` (old PyQt) -> legacy
- `scripts/` -> deferred
- Everything else -> active

**Renderer**: Two separate tables rendered:
- `## Active Hotspots`
- `## Legacy / Deferred Hotspots`

**Result**: Active files (`ui_tk/metric_input_table.py`,
`ui_tk/excel_like_table_controller.py`, `ui_tk/batch_matrix_table.py`,
`ui_tk/sections/bin_detail_panel.py`) now appear in the first section.
Legacy files (`core/_legacy/...`, `ui/calculators_2point.py`) are in the
second section.

## Keyword Hit Group Refinement (Task 5)

**Changes**:
- Section title: `Owner Groups` -> `Keyword Hit Groups`
- Added description: "These are search cues based on file paths and top-level
  symbol names, not ownership declarations."
- Removed `row`, `column`, `cell` from `OWNER_KEYWORDS["table"]` to reduce
  overmatching into core calculator files.

**Result**: `table` group is now tighter (25 files vs 41 before). Core
files like `core/predictor.py` and `core/constants.py` no longer appear in
`table`.

## Import Edge Granularity (Task 6)

**Change**: `compute_import_edges` now shows up to the first 3 parts of the
imported module path.

**Before**: `ui_tk/foo.py -> ui_tk`
**After**: `ui_tk/foo.py -> ui_tk.table.surface`

**Result**: Edges are now specific enough to assess which sub-packages are
coupled, without building a full call graph.

## Renderer Split (Task 7)

**Changes**: `render_compact_map()` was 87 LOC. Split into 8 focused helpers:
- `_render_header`
- `_render_layer_overview`
- `_render_keyword_groups`
- `_render_hotspots` (reused for both active and legacy)
- `_render_duplicates`
- `_render_import_edges`
- `_render_usage`

`render_compact_map()` now only orchestrates: ~15 LOC.

**Result**: `renderer.py` no longer appears in its own hotspot list.

## Tests (Task 8)

Created `tests/test_code_checker_reference_map.py` (9 tests):

1. `test_scanner_symbol_kinds` — verifies class / top_level_function /
   method / nested_function / constant separation.
2. `test_duplicate_excludes_methods_and_framework_noise` — verifies `grid`
   (framework method) is excluded from duplicates.
3. `test_duplicate_includes_repeated_top_level_helpers` — verifies
   `normalize_input` (top-level) is still included.
4. `test_hotspot_active_vs_legacy_split` — verifies `ui_tk/` goes to active,
   `core/_legacy/` and `ui/` go to legacy.
5. `test_keyword_hit_group_not_ownership` — verifies keyword matching works
   and doesn't over-categorize.
6. `test_import_edge_shows_module_prefix` — verifies 3-part module prefix
   is rendered.
7. `test_renderer_has_active_and_legacy_hotspot_sections` — verifies both
   sections exist in output.
8. `test_renderer_has_duplicate_framework_filter_note` — verifies the caveat
   about framework method filtering is present.
9. `test_renderer_long_function_not_self_hotspot` — verifies renderer.py no
   longer triggers its own long-function warning.

All 9 tests pass.

## Map Regeneration Result (Task 9)

- **Command**: `python3 -B tools/code_checker/build_reference_map.py`
- **Output**: 226 lines (under 300-line target)
- **Duplicate section**: ~20 entries, no framework method noise
- **Active hotspots**: 27 entries, current risk files at top
- **Legacy hotspots**: 5 entries, separated
- **Import edges**: Module-prefix granularity, 40 displayed + 248 more
- **Caveat**: "evidence, not source of truth" retained

## Remaining Risks

- **Map staleness**: Still manual regeneration. No CI or pre-commit hook.
- **AGENTS/ROUTER hook policy**: Whether to mandate "run code_checker before
  new surface/helper creation" is deferred to next slice.
- **Keyword hit groups**: Still based on substring matching. Path-weighted
  refinement could be a future enhancement.
- **Duplicate filtering**: The `_FRAMEWORK_METHOD_NOISE` list is curated.
  New framework methods from future toolkits may need to be added.

## Next

- Reference Evidence Gate hook policy adoption (AGENTS.md / AGENT_TASK_ROUTER.md)
- Or further code_checker calibration if map usage reveals new noise patterns.

## Validation

| Check | Command | Result |
|-------|---------|--------|
| Map generation | `python3 -B tools/code_checker/build_reference_map.py` | OK, 226 lines |
| Focused tests | `python3 -B -m pytest tests/test_code_checker_reference_map.py` | 9 passed |
| Structural guard | `python3 -B tools/check_code_structure.py` | No new violations |
| Compile check | `py_compile` on all 4 modules | OK |
| Git diff check | `git diff --check` | Clean |

## Modified Files

- `tools/code_checker/scanner.py`
- `tools/code_checker/analyzer.py`
- `tools/code_checker/renderer.py`
- `tools/code_checker/build_reference_map.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `tests/test_code_checker_reference_map.py`
- `docs/WORK_PLAN.md`
