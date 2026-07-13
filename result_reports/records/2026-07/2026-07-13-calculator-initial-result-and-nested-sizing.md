```yaml
record:
  date: 2026-07-13
  topic: calculator-initial-result-and-nested-sizing
  tags: calculator, tkinter, placeholder, result-surface, notebook, viewport, correction
  memory_review: updated
  memory_reason: Initial non-result surfaces and selected-child Notebook allocation are durable cross-profile Calculator presentation contracts.
```

# Change Reason

ISO/KS Single screens initially measured without their final result footprint,
while short EN/AHRI nested tabs retained the requested height of taller sibling
tabs. Calculation or tab switching could therefore expose clipped results,
blank lower space, or unnecessary vertical overflow.

# Contract / Behavior Changed

ISO/ISEER, Hong Kong, SASO T3, Brazil, and KS result owners now render their
final headers and fixed field/row structure with `-` values and an input-waiting
status before a successful calculation. Placeholder presentation remains
separate from logical rows/summaries, so Copy/CSV continues to emit the existing
no-result status. Validation and calculation errors update the stable surface
instead of collapsing it.

The shared visible-content lifecycle now applies the selected nested child's
settled requested height to the actual Tk Notebook client allocation and then
refreshes the canvas scrollregion before fitting the shell. EN SEER/SCOP and
AHRI SEER2/HSPF2 therefore shrink and grow reproducibly while preserving the
existing shell cap, scrolling, scheduling, and monitor placement policies.

# Evidence And Verification

- The final focused result/geometry selection passed 72 tests.
- The final full Tk Calculator UI selection passed 673 tests, including ISO/KS
  placeholders, EN/AHRI round trips, and HSPF2 Batch geometry diagnostics.
- Python compilation, whitespace validation, and the structure guard passed;
  the ten reported warnings are unchanged soft-limit hotspots.
- A visible macOS Tk launch confirmed the initial ISO/ISEER result table,
  placeholder rows, input-waiting status, and result actions on first display.

# Changed Files

- Shared ResultPanel, lifecycle measurement/controller, and scrollable viewport
- ISO/ISEER, Hong Kong, SASO T3, Brazil, and KS Single result surfaces
- Focused result/export, lifecycle, and visible-sizing tests
- Work plan, memory seed, and report index

# Known Risks

Tk internal controls were not exposed through macOS accessibility, so visible
coordinate-driven EN/AHRI tab switching was not used as acceptance evidence.
The real Tk widget smoke and automated sizing diagnostics cover those round
trips and HSPF2 Batch geometry. Windows visual smoke remains unperformed.
