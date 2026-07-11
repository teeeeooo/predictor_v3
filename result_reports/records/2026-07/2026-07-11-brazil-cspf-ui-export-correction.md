```yaml
record:
  date: 2026-07-11
  topic: Brazil CSPF UI and export structure correction
  tags: calculator, brazil, cspf, tkinter, presentation, export, batch, architecture
  memory_review: updated
  memory_reason: Record the single feature-package boundary and removal of public Row Status output.

change_gate:
  new_source: split
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Close the Brazil CSPF audit findings left after the initial UI/export polish:
hardcoded Rule 1 text, flat single-surface ownership, inconsistent alignment,
missing semantic cell highlights, long batch labels, and public Row Status output.

# Contract / Behavior Changed

- Brazil single composition, cell-rendered presentation, pure export document,
  and Tk clipboard/file/CSV adapters now live in one feature package.
- Rule 1 compact and full text both use the core result multiplier; application
  presentation still consumes the core-owned passed decision without recomputing it.
- Single result values use the shared result/pass background; Rule and Final
  OK/NG cells use shared pass/error backgrounds while retaining text.
- Brazil batch exposes exactly nine shortened result headings. Row Status was
  removed from schema, snapshots, Copy, and CSV while controller row state remains.
- Shared batch infrastructure gained only a generic repaint hook; Brazil-specific
  judgement-key mapping stays in the Brazil package.

# Evidence And Verification

- Focused Brazil application, single UI/export, batch matrix, and per-cell-role
  tests cover dynamic 1.4/1.5 text, exact schemas, alignment, semantic backgrounds,
  status fallback, stale clearing, snapshot, Copy, and CSV behavior.
- Structure, compile/import, staged-change, and full-suite results are recorded in
  the terminal handoff for the same commit.

# Changed Files

- `apps/calculator/ui/brazil_cspf/`
- `apps/calculator/ui/batch_dialogs/profiles/brazil_cspf/`
- shared batch repaint/token wiring and Brazil application display formatting
- focused Brazil application/UI/structure-guard tests and current work plan

# Known Risks

Tk rendering is guarded programmatically through widget alignment, text, background,
and visible-schema assertions. Platform GUI injection may still be unavailable; no
core formulas, golden fixtures, detail styling, or other profile surfaces changed.
