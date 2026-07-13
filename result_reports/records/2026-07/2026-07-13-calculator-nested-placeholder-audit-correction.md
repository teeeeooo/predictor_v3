```yaml
record:
  date: 2026-07-13
  topic: calculator-nested-placeholder-audit-correction
  tags: calculator, tkinter, notebook, chrome, lifecycle, placeholder, semantic-tone, correction
  memory_review: updated
  memory_reason: Chrome-before-allocation ordering and non-result placeholder tones correct the durable cross-profile Calculator presentation contract.
```

# Change Reason

Audit of the initial result and nested sizing change found that selected-child
allocation could be mutated before the first reliable notebook chrome measure.
An ISO default-to-Hong-Kong transition could therefore cache zero or undersized
chrome. The same audit found calculated presentation on non-result placeholders
and duplicate SASO scenario-label imports.

# Contract / Behavior Changed

The shared lifecycle now takes a side-effect-free measurement snapshot before
mutating nested Notebook client height. Measurement owns requested-size and
chrome calculation only; lifecycle orchestration owns `configure`, layout
settling, scrollregion refresh, and shell fit. The resulting requested height is
the selected child height plus preserved notebook chrome, including first Hong
Kong entry and return trips across ISO, EN, and AHRI siblings.

Initial placeholders use pending presentation, validation failures use invalid,
and successful values restore calculated or Brazil pass/fail presentation in
place. Logical rows, summaries, rules, final judgement, and status-only export
contracts remain unchanged. SASO placeholder and detail ordering now use one
canonical application-label import.

# Evidence And Verification

- Slice 1 lifecycle/measurement focused selection passed 46 tests.
- Slice 2 placeholder/result/export focused selection passed 96 tests.
- The final full Tk Calculator UI selection passed 677 tests.
- Python compilation, whitespace checks, and the structure guard passed; the
  ten warnings are unchanged soft-limit hotspots outside this correction.
- A visible macOS Tk launch confirmed the first ISO placeholder table, pending
  values, and input-waiting status. Tk internal controls were not exposed by
  macOS accessibility, so nested tab and invalid-input transitions use the
  real-widget automated evidence rather than coordinate-driven claims.

# Changed Files

- Shared visible-content measurement and lifecycle controller
- Shared ResultPanel and profile-local ISO/SASO/Brazil/Hong Kong/KS surfaces
- Focused measurement, lifecycle, tone, export, and sizing diagnostics
- Memory seed and report index

# Known Risks

Windows visual smoke was not available. macOS visible evidence covers initial
rendering only; automated Tk tests cover Hong Kong/EN/AHRI round trips, detail
and Batch geometry, status-only export, and invalid-to-valid recovery.

This record supersedes the lifecycle ordering and placeholder-tone portions of
`2026-07-13-calculator-initial-result-and-nested-sizing.md`; that earlier record
remains append-only historical evidence.
