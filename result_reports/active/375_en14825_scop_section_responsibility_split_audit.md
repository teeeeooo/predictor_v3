# 375 EN14825 SCOP Section Responsibility Split Audit

## Goal

Audit `apps/calculator/ui/sections/en14825_scop_section.py` after the
post-implementation soft LOC warning and decide whether SCOP Slice 3 can proceed
without first splitting responsibility.

## Scope / Non-goals

- Scope: responsibility inventory, MVC/SoC judgment, split candidate proposal,
  next action decision, and compact `WORK_PLAN` update.
- Non-goals: no source code, tests, tools, architecture workflow docs, UI/UX
  docs, memory seed, project log, summary/archive lifecycle, fixture/golden, or
  Report 372/373 edits.

## Evidence Checked

- `AGENTS.md` was already checked directly from the repo earlier in this
  session.
- Owner docs checked by narrow ranges:
  - `AGENT_TASK_ROUTER.md` Architecture Triage and Result Report Workflow.
  - `docs/agent_workflows/UI_SURFACE_WORKFLOW.md` Preflight Structure Guard and
    Post-implementation Soft Warning Triage.
  - `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` View boundaries,
    stop conditions, warning acceptance, and source file owner boundary policy.
  - `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md` report requirement,
    compact report mode, warning triage, and active report count wording.
  - `docs/WORK_PLAN.md` Next Actions.
- Target files checked by method/owner ranges:
  - `apps/calculator/ui/sections/en14825_scop_section.py`
  - `apps/calculator/ui/en14825/scop_adapter.py`
  - `apps/calculator/ui/en14825/scop_table_model.py`
  - `apps/calculator/ui/en14825/scop_models.py`
  - `apps/calculator/ui/sections/en14825_seer_section.py` as comparison.

## Responsibility Inventory

`en14825_scop_section.py` currently owns:

- UI construction: frame, auxiliary inputs, three climate cards, three
  `MetricInputTable` instances, result panel, controller setup, callback wiring.
- Climate card/toggle handling: climate activation state, collapse/expand, auto
  recalc scheduling, and parent refit callback.
- Input parsing: auxiliary `StringVar` parsing and table text parsing through
  `parse_numeric_cell`.
- Table text to `ScopPointInput` mapping: per-column construction for A/B/C/D,
  TOL, and Tbiv.
- Dynamic TOL/Tbiv table update: effective temperature resolution and header
  replacement.
- Adapter/table model orchestration: `ScopAdapter.compute_points()`,
  `ScopAdapter.calculate()`, `ScopTableModel` creation, static cell updates, and
  controller repaint.
- Result summary formatting: `ScopResultSummary` to `ResultSummary` fields and
  status text.
- Cell background/status mapping: table position to row/column, model state to
  UI colors.
- Lifecycle/refit trigger: debounced auto-calc, destroy disposal, climate toggle
  refit callback.

Existing owner files already cover:

- `scop_models.py`: raw input, computed point, and result summary data models.
- `scop_adapter.py`: climate data lookup, temperature override resolution,
  point computation, W/kW core boundary conversion, core calculation, and result
  state production.
- `scop_table_model.py`: row/column structure, label/header formatting,
  computed display values, and cell state metadata.

## Keep / Split / Defer Judgment

- Keep in section: top-level widget ownership, event forwarding, table/controller
  wiring, climate toggle show/hide, scheduler lifecycle, and parent refit signal.
- Section-local helper method is sufficient: `_parse_float_safe`,
  `_set_static_cell_value`, `_clear_computed_rows`, and `_resolve_cell_bg` until
  a common table-state color resolver emerges across sections.
- Section-local subcomponent file candidate:
  - `en14825_scop_result_formatter.py`: convert `ScopResultSummary` plus climate
    label/status mapping into `ResultSummary`. This removes repeated result
    formatting from the View and is easy to test without Tk.
  - section-local input mapping helper: parse table text values, collect invalid
    fields, and build `ScopPointInput` mapping. This removes schema-ish table
    field mapping from `recalculate_now()` without moving UI widget concerns.
- Existing `apps/calculator/ui/en14825/` owner candidate:
  - keep table value/header/state formatting in `ScopTableModel`;
  - keep core and climate/default calculation boundary in `ScopAdapter`;
  - do not move Tk widget or `MetricInputTable` interactions into these headless
    owners.
- Common framework candidate but deferred: a shared result-summary formatter and
  table state-to-color resolver may become useful after SEER/SCOP/HSPF parity is
  clearer, but this audit does not justify a cross-section framework yet.

## Split Candidates

1. `en14825_scop_result_formatter.py`
   - Reason: result formatting is presentation formatting, repeated in shape
     with SEER, and does not need Tk widgets.
   - Benefit: reduces View accumulation and enables focused unit tests.

2. `en14825_scop_input_mapper.py` or section-local helper module
   - Reason: table text keys and `ScopPointInput` construction are mapping
     responsibility, not widget construction.
   - Benefit: makes invalid-field handling and point input construction testable
     before Slice 3 adds layout/refit work.

3. `en14825_scop_climate_card.py`
   - Reason: the three climate cards repeat a sizeable view subtree and own
     active state, aux variables, table, and controller references.
   - Status: candidate for a later split if Slice 3 needs substantial card-level
     layout/refit behavior. Do not extract solely to reduce line count.

## MVC / SoC Judgment

The section is acceptable as the initial integration slice, but it now mixes
View construction with mapping and result formatting. That is exactly the soft
warning case covered by the current workflow. The adapter and table model
boundaries are mostly correct; the next improvement should remove non-widget
mapping/formatting before adding new layout/refit behavior to the same section.

## Warning Triage

- Structure Warnings: `apps/calculator/ui/sections/en14825_scop_section.py`
  exceeds the 400 LOC soft limit.
- Warning Triage: minimal helper extraction recommended before Slice 3.
- Reason: Slice 3 is expected to add tab composition layout/refit polish, which
  would add lifecycle/layout responsibility to an already large View class.

## Slice 3 Readiness

SCOP Slice 3 should not proceed directly if it adds new section responsibility.
Proceed first with a small helper extraction focused on result formatting and
input mapping. After that, Slice 3 can add layout/refit polish with a clearer
section boundary.

## Changed Files

- `docs/WORK_PLAN.md`
- `result_reports/active/375_en14825_scop_section_responsibility_split_audit.md`

## Validation

- `git diff --check`
- `git status --short`
- `python3 -B tools/check_code_structure.py`
- `find result_reports/active -maxdepth 1 -type f -name '*.md' | wc -l`

## Known Risks / Gaps

- No source implementation was performed, so the LOC warning remains until the
  follow-up extraction.
- The climate-card subcomponent boundary should be revisited only if Slice 3
  requires meaningful card-level layout/refit behavior.
- Exact active report count is intentionally omitted from durable docs.

## Next Suggested Action

Implement a minimal SCOP helper extraction before Slice 3:

- result summary formatter first;
- input mapping helper second if the slice budget allows;
- defer climate card subcomponent unless layout/refit work needs that boundary.

## Project Memory Delta

- none

## Commit / Push

- Final commit hash and push status are reported in terminal output to avoid a
  self-referential report update loop.
