# 365. EN14825 SCOP Integration Design / Preflight Report

This report summarizes the design audit and preflight findings for the integration of the EN14825 SCOP (heating) comparison interface.

## Goal
Establish a clear, contract-backed spreadsheet-like design for the EN14825 SCOP comparison interface before actual implementation, checking dependencies and existing structures.

## Scope
* Audit the core calculation engine (`core/calculator_en14825.py`) and config schemas (`data/region_configs/en14825_scop.json`).
* Analyze UI design requirements for the heating calculator: dual-path (Declared/Tested), climate selection, TOL/Tbiv override, and table layout.
* Draft package layout and architectural slice plans.
* Update `docs/WORK_PLAN.md` with targeted checkpoints.

## Non-goals
* No code changes or feature implementation inside `core/`, `apps/`, `tests/`, or config files.
* No changes to expected test fixtures or golden files.

## Audit Summary

### 1. Core Calculator API
* Method: `calculate_scop()`
* Required Points: `A`, `B`, `C`, `D`, `TOL`, `Tbiv`
* Unit expectations:
  * Core expects `kW` for capacities, powers, and design loads.
  * Outdoor Dry-bulb temperature in `°C`.
  * Return energy fields in `kWh` (`qh_kwh`, `active_kwh`, `standby_kwh`, `total_kwh`).
  * COP, SCOP, and ratio percentages are dimensionless.

### 2. Config Properties
* Three Climates: `average` (Tdesignh = -10°C, max Tbiv = 2°C, max TOL = -7°C), `warmer` (Tdesignh = 2°C, max Tbiv = 7°C, max TOL = 2°C), `colder` (Tdesignh = -22°C, max Tbiv = -7°C, max TOL = -15°C).
* Prefill defaults to be set at the UI layer:
  * Average: Tbiv = -10°C, TOL = -11°C
  * Warmer: Tbiv = 2°C, TOL = -11°C
  * Colder: Tbiv = -15°C, TOL = -22°C

## MVC/SoC Judgment
The Separation of Concerns (SoC) model successfully applied to SEER is highly relevant and will be adopted:
* **View/Orchestrator**: `En14825ScopSection` handles widget structure, event bindings, and debounced auto-calculation.
* **Adapter**: `ScopAdapter` manages data normalization, fallback logic, W-to-kW scaling, and engine invocation.
* **Model**: Dataclasses like `ScopPointInput` map individual cells; `ScopResultSummary` contains calculated metrics and status indicators.
* **Headless Table Model**: `ScopTableModel` isolates formatted strings, cell validation states, and cell editability policies.

## Source Owner Boundary Judgment
To keep package boundaries clean, the newly designed SCOP files will reside inside the existing domain package `apps/calculator/ui/en14825/`. No new flat-files will be added to the outer `ui/` directory.

## SCOP Extensibility Judgment
* Multi-Climate Toggling: To meet the design contract, each climate will be represented by an independent, collapsible LabelFrame. If multiple climates are active, separate `ScopTableModel` and `MetricInputTable` widgets are rendered side-by-side or stacked.
* Dynamic TOL/Tbiv: Column headers for TOL and Tbiv columns will update their text dynamically to reflect user-entered dry-bulb temperatures.

## Changed Files
* `docs/designs/2026-06-11-en14825-scop-gui-integration-design.md` (created)
* `result_reports/active/365_en14825_scop_integration_design_preflight.md` (created)
* `docs/WORK_PLAN.md` (modified)

## Validation
Verification was performed via static tools:
* `python3 -B tools/check_code_structure.py`
* `git diff --check`
* `git status --short`

## Next Suggested Action
Begin implementation of Slice 1: Define `ScopPointInput`, `ScopPointComputed`, `ScopAdapter`, `ScopTableModel`, and write corresponding non-GUI unit tests inside `tests/test_apps_calculator_ui_en14825.py`.

## Project Memory Delta
```yaml
- type: decision
  topic: EN14825 SCOP GUI Integration
  content: Adopt SEER dual-path design for SCOP with climate-specific inputs. Pto/Psb/Pck/Poff auxiliary power is shared at the tab level.
  keywords:
    - en14825
    - scop
    - gui
    - contract
  assertionStatus: verified
  source: 365_en14825_scop_integration_design_preflight.md
```
