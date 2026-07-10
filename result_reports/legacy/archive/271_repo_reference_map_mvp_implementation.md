# 271 Repo Reference Map MVP Implementation

## Goal

Implement the MVP for the predictor_v3 codebase reference map based on the
270 design slice.

## Scope

- Create `tools/code_checker/` package with modular scanner / analyzer /
  renderer / orchestrator.
- Generate initial `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- Update `.gitignore` for `.code_checker/` cache directory.
- Update `docs/WORK_PLAN.md` to reflect that the prior
  "AI-generated code risk checklist adoption audit" is absorbed into the
  reference map workflow.

## What Was Done

1. **Package scaffold**
   - `tools/code_checker/__init__.py`
   - `tools/code_checker/scanner.py` — AST visitor extracting symbols
     (classes, functions, constants), imports, and LOC per file.
   - `tools/code_checker/analyzer.py` — layer overview, owner keyword groups,
     hotspot detection (LOC / class count / long-function thresholds),
     duplicate-symbol candidates, and internal import edges.
   - `tools/code_checker/renderer.py` — compact Markdown generator with
     truncation guards (owner groups > 5 files summarized, top-20 duplicates,
     top-40 import edges) to keep the map under 300 lines.
   - `tools/code_checker/build_reference_map.py` — thin orchestrator script
     (≈ 50 LOC) that wires the above modules and writes the map.

2. **Map generation**
   - Ran `python3 -B tools/code_checker/build_reference_map.py` successfully.
   - Output: 218 lines, well under the 300-line soft target.

3. **Git hygiene**
   - Added `.code_checker/` to `.gitignore`.
   - Created `docs/code_map/` directory for the tracked compact map.

4. **Plan update**
   - `docs/WORK_PLAN.md`: replaced the standalone "AI-generated code risk
     checklist adoption audit" next action with 271, noting absorption into
     the reference map flow.

## Verification

| Check | Command | Result |
|-------|---------|--------|
| Map generation | `python3 -B tools/code_checker/build_reference_map.py` | OK, 218 lines |
| Structural guard | `python3 -B tools/check_code_structure.py` | No new violations; pre-existing 4 soft-limit warnings unchanged |
| Git diff check | `git diff --check` | Clean |

## Modified Files

- `tools/code_checker/__init__.py`
- `tools/code_checker/scanner.py`
- `tools/code_checker/analyzer.py`
- `tools/code_checker/renderer.py`
- `tools/code_checker/build_reference_map.py`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `.gitignore`
- `docs/WORK_PLAN.md`

## Design Decisions

- **Module separation**: scanner / analyzer / renderer / orchestrator split
  respects the AGENTS.md responsibility boundary rule and keeps every file
  under 250 LOC.
- **Truncation policy**: The compact map summarizes large groups rather than
  listing every file, keeping the human-readable reference small. The full
  dataset can be dumped to `.code_checker/` cache in a future slice if
  needed.
- **Internal import edges only**: Standard-library and third-party imports are
  filtered out so the edge list focuses on cross-layer coupling inside the
  repo.

## Remaining Risks / Next Slice

- **AGENTS/ROUTER hook policy**: Whether to add an explicit "run code_checker
  before/after" clause to AGENTS.md or AGENT_TASK_ROUTER.md is deferred to
  the next slice after the map has been used in practice.
- **Map staleness**: The map includes a "last updated" header, but automatic
  regeneration is not yet wired. Manual or slice-level regeneration is the
  current policy.
- **Detailed cache**: No `.code_checker/` JSON dump is produced yet; that is
  a future-phase enhancement if cross-session full-symbol search becomes
  necessary.
