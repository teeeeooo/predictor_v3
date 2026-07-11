```yaml
record:
  date: 2026-07-11
  topic: Brazil CSPF final interaction correction
  tags: calculator, brazil, cspf, tkinter, interaction, batch, audit-correction
  memory_review: no-change
  memory_reason: Existing Brazil presentation/export and shared table owners already encode the durable boundaries; this record adds guarded correction evidence.

change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Close the final audit gaps where semantic batch repaint could hide selection,
single result Copy had no user interaction path, and heading-fit evidence did not
measure the rendered Tk font.

# Contract / Behavior Changed

- `BatchMatrixTable` repaints semantic base backgrounds before the attached
  `TkTableController` reapplies its selected and active-cell overlays.
- Result clearing, pending, and error transitions reset stale pass/fail colors;
  Brazil-specific judgement keys remain in the Brazil presentation policy.
- The existing single action row exposes Copy through the unchanged sectioned
  Result/Rule/Final document and Status fallback.
- Batch heading fit uses the actual Tk header font, label padding, and unchanged
  production width tokens. No heading text or result-column width changed.

# Evidence And Verification

- Automated Tk tests cover active/selected persistence, semantic backgrounds,
  OK-to-NG, NG-to-OK, valid/pending/error/valid, and `clear_results()` transitions.
- Copy-button `invoke()` covers both sectioned valid output and invalid Status
  fallback; all nine Brazil result headings pass font-pixel fit assertions.
- Focused Brazil/shared regression passed `114 passed`; the full active suite
  passed `1672 passed, 2 xfailed`.
- Structure and compile/import checks passed. The structure guard reported only
  ten pre-existing warnings outside the changed source.

# Changed Files

- Shared Tk matrix/controller repaint and header measurement boundaries
- Brazil single action-row composition
- Focused Brazil/shared Tk interaction tests
- Current work plan

# Known Risks

Manual GUI smoke was skipped because the current session did not expose the
`node_repl` runtime required by the Computer Use skill. Automated Tk tests use
real widgets, clipboard interaction, backgrounds, and font metrics as acceptance
evidence. Core formulas, goldens, schemas, highlight policy, and export content
remain unchanged.
