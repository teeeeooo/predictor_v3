```yaml
record:
  date: 2026-07-12
  topic: calculated-semantic-tone-correction
  tags: calculator, tkinter, semantic-tone, calculated, result, correction
  memory_review: no-change
  memory_reason: The existing table-family memory already separates shared visual binding from profile-local meaning; this correction applies that boundary consistently.
```

# Change Reason

Migrated calculation values used either neutral `DEFAULT` or compliance
`PASS`, conflating calculated read-only data with judgement outcomes.

# Contract / Behavior Changed

The shared Tk policy maps both `CALCULATED` and `PASS` to the approved existing
light-green background while retaining distinct semantic metadata. ISO/ISEER
numeric results, generic ResultPanel values, and Brazil CSPF/CSTL/CSEC values
declare `CALCULATED`. Brazil Rule outcomes alone use `PASS/FAIL`; identity and
description cells remain `DEFAULT`. Final judgement remains unchanged.

# Evidence And Verification

- 288 focused semantic, result, Brazil, ISO, dependent profile, lifecycle, and refit tests passed.
- Tests prove distinct enum meanings with the same approved background.
- Brazil Result/Rule/Final TSV and CSV, ISO text/copy/export, stable update,
  focus, and stale-result clearing remain guarded.
- Targeted compilation, whitespace, and structure checks passed with only
  unchanged legacy warnings.

# Changed Files

- shared Tk table visual policy
- ISO/ISEER compact result wrapper
- generic ResultPanel
- Brazil CSPF result surface
- focused semantic/result tests

# Known Risks

The two tones intentionally share a color today; future palette or
accessibility changes must continue to bind them separately rather than infer
meaning from the rendered color.
