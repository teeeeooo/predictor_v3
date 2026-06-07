# 280 MetricInputTable Clipboard Protocol Compatibility Check

## Goal

Verify whether `MetricInputTable` already satisfies the `TkTableSurface` clipboard
protocol (`clipboard_clear`, `clipboard_append`, `clipboard_get`) needed by
`TkTableController._copy()` / `._paste()`, and avoid adding unnecessary or buggy
wrappers.

## Scope

- Runtime verification of `MetricInputTable` clipboard method availability.
- Signature compatibility check against `TkTableController` usage.
- Add focused roundtrip test.
- No production code changes unless a real gap is found.

## Excluded Scope

- Controller switch implementation.
- `MetricInputTable` production code changes (unless a gap is found).
- `ExcelLikeTableController` / `TkTableController` / `interaction_core.py` changes.
- Map regeneration.

## 279 Correction

An earlier version of 279 incorrectly identified clipboard methods as "missing"
from `MetricInputTable" and provided a buggy recursive wrapper example:

```python
def clipboard_clear(self) -> None:
    self.clipboard_clear()  # infinite recursion!
```

This report corrects that finding.

## Clipboard Compatibility Result

**Finding: `MetricInputTable` already fully satisfies the clipboard protocol.**

Evidence:

1. `MetricInputTable` inherits from `ttk.Frame` (verified via `__bases__` and MRO).
2. `ttk.Frame` provides:
   - `clipboard_clear(self, **kw)`
   - `clipboard_append(self, string, **kw)`
   - `clipboard_get(self, **kw)`
3. `TkTableController` calls these methods as:
   - `self.table.clipboard_clear()` — no args ✓
   - `self.table.clipboard_append(text)` — one positional string arg ✓
   - `self.table.clipboard_get()` — no args, returns str ✓
4. `hasattr(MetricInputTable, "clipboard_clear")` returns `True`.

**No production code changes needed.**

## Tests

Added `test_clipboard_roundtrip` to
`tests/test_ui_tk_metric_input_table_adapter.py`:

```python
def test_clipboard_roundtrip(self, sample_table: MetricInputTable) -> None:
    sample_table.clipboard_clear()
    sample_table.clipboard_append("test_value")
    result = sample_table.clipboard_get()
    assert result == "test_value"
```

All 25 tests in the file skipped (headless environment, matching existing
pattern). No failures.

## Validation

| Check | Command | Result |
|-------|---------|--------|
| Adapter tests | `pytest tests/test_ui_tk_metric_input_table_adapter.py` | 25 skipped, 0 failures |
| Compile check | `py_compile ui_tk/metric_input_table.py` | OK |
| Structure guard | `python3 -B tools/check_code_structure.py` | No new violations |
| Git diff check | `git diff --check` | Clean |

## Modified Files

- `tests/test_ui_tk_metric_input_table_adapter.py`

## Next

- Controller switch parity test foundation (focused tests for
  `MetricInputTable` + `TkTableController` behavior parity).

## Risks

- None. The clipboard protocol is already satisfied.
- Headless environment skips Tk tests; real clipboard roundtrip will be
  verified during Windows GUI smoke before any controller switch.
