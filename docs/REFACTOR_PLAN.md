# Refactor Plan

## Purpose

- Track only unresolved structural candidates and their start triggers.
- Keep execution in `docs/WORK_PLAN.md`, direction in `project_brief.md`, and
  completed decisions in `project_log.md`.
- A listed candidate is not authorization to refactor.

## Active Candidate — ISO 16358 Internal Helper Extraction

Potential scope: separate point resolution, bin iteration, and energy
accumulation inside the ISO 16358 implementation.

The current `iso16358.py` is an approximately 1,800-LOC single owner, so the
candidate is evidence-based. It remains trigger-only and must not preempt the
next approved product workstream.

Start only when one or more triggers are observed:

- the same ISO branch or accumulation rule must change in multiple places;
- a focused fix cannot be isolated without touching unrelated calculation stages;
- function size or control-flow depth materially obstructs formula review;
- region-specific behavior begins leaking into the global ISO path.

Required boundary:

- keep ISO global logic in the ISO owner and region behavior in config/profile
  or explicit handler boundaries;
- do not absorb KS C 9306 or AS/NZS workbook-oracle conventions;
- preserve public functions, formula behavior, rounding order, diagnostics,
  config meaning, fixtures, and golden expected values;
- treat extraction as no-behavior-change unless an approved formula task says otherwise.

## Active Candidate — Warning-First Code Quality Guards

Add a guard only after a real problem identifies its value and owner. Introduce
one warning at a time, measure noise, then consider enforcement separately.

Candidate checks:

- broad `except` / silent fallback smells;
- compatibility wrapper and re-export inventory;
- long-function, complexity, or nesting warnings beyond current soft limits;
- import-cycle detection;
- fan-in/fan-out summaries.

When introducing a warning, assign its owner from the observed problem. Extend
`tools/check_code_structure.py` only for focused AST/structure checks that fit
its scope. Type and mock audits remain later decisions.

## Deferred

- AS/NZS historical Excel/workbook reconstruction remains deferred until its
  workbook evidence and compatibility scope are available.
- Historical reconstruction must remain separate from production ISO logic and
  must not redefine current golden expectations by inference.

## Non-Goals

- Formula fixes, fixture/golden changes, UI features, ML work, packaging,
  ordinary tests, and documentation cleanup are not refactor tasks.
- Do not revive completed Predict/Train, calculator-boundary, KS, resolver, UI,
  common-engine, plugin-architecture, or package-split plans from old history.
- Do not start speculative cleanup merely because a candidate is documented.

## General Triggers And Guardrails

- Trigger examples: repeated branch conditions, recurring cross-region
  regressions, owner leakage, or code size that blocks safe focused changes.
- Confirm the owner boundary and focused verification before editing.
- Preserve public API, JSON/result schema, diagnostics, region config meaning,
  formula behavior, fixtures, goldens, and compatibility boundaries.
- Use a Design Gate before any change that could alter architecture, schema,
  routing, global-vs-specific behavior, or a public contract.
