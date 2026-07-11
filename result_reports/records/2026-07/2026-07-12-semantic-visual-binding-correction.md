```yaml
record:
  date: 2026-07-12
  topic: semantic-visual-binding-correction
  tags: calculator, tkinter, semantic-tone, calculated, pass, result-panel
  memory_review: no-change
  memory_reason: The existing table-family and semantic-tone records already contain the durable owner and meaning boundaries.
```

# Change Reason

Calculated and pass tones had distinct enum values but shared one resolution
branch, while ResultPanel applied calculated color only to the inner Label and
left its cell container neutral.

# Contract / Behavior Changed

The Tk policy now owns independent calculated/pass background bindings that
currently resolve to the same approved light green. ResultPanel creates both
the value cell container and Label with the calculated binding. Same-shape
updates retain widget identity, tone metadata, background, status, and copy
text.

# Evidence And Verification

- 288 focused semantic, result, profile, export, lifecycle, and refit tests passed.
- A custom policy with different calculated/pass values proves independent resolution.
- ResultPanel tests prove container/Label background and metadata parity before
  and after stable update.
- Targeted compilation, whitespace, and structure checks completed with only
  unchanged legacy warnings.

# Changed Files

- `apps/calculator/ui/table/visual_policy.py`
- `apps/calculator/ui/result_panel.py`
- focused visual-policy and ResultPanel tests

# Known Risks

Calculated and pass bindings intentionally remain the same concrete color.
Future visual divergence must change the appropriate binding without merging
their semantic branches again.
