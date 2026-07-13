```yaml
record:
  date: 2026-07-13
  topic: saso-partial-row-tone-correction
  tags: calculator, tkinter, saso-t3, partial, semantic-tone, correction
  memory_review: updated
  memory_reason: SASO partial results require mixed calculated and invalid row presentation while retaining one exportable result shape.
```

# Change Reason

The SASO T3 Single partial result correctly retained the optional error row and
required calculated row, but its result surface applied calculated tone to every
non-identity cell. The optional error row therefore looked successful.

# Contract / Behavior Changed

The SASO section now passes the canonical optional scenario label as a local
invalid-row hint when the existing usecase status is `partial`. The SASO result
surface applies invalid tone only to that row's non-identity cells and preserves
calculated tone on the required row. Fully valid results remain calculated.

Recovery from invalid optional input uses the existing same-shape in-place grid
update, restoring calculated tone and background without replacing widgets.
Application results, row order, Copy/CSV payloads, detail data, Batch behavior,
and all calculator contracts remain unchanged.

# Evidence And Verification

- SASO Single, semantic, export, detail, and Batch focused selection passed 89 tests.
- The final full Tk Calculator UI selection passed 677 tests.
- Python compilation, whitespace checks, and the structure guard passed; the
  ten warnings are unchanged soft-limit hotspots outside this bounded slice.

# Changed Files

- SASO T3 Single section and result table
- SASO controller-switch regression tests
- Memory seed and report index

# Known Risks

No Windows visual smoke was performed. The correction is guarded at widget tone,
background, identity, in-place recovery, input highlight, and export payload
levels through real Tk tests.

This record supplements
`2026-07-13-calculator-nested-placeholder-audit-correction.md` for the SASO
partial-result case; the earlier record remains append-only evidence.
