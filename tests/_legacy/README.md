# tests/_legacy

This directory is still collected by pytest. The `_legacy` name does not mean
the tests are safe to delete.

The tests here are active diagnostic/reference tests for historical
workbook-oracle and AS/NZS investigation context. Their xfail markers are not
production ISO16358-2 HSPF official-exact failures. The production official
exact path is covered separately by `tests/test_iso16358_hspf_official_exact_golden.py`.

Do not remove xfail markers, update expected values, change fixtures, or change
core calculator behavior from this folder without a separate design decision.
Decommissioning this folder, or moving these diagnostics to a different owner,
must be handled as its own design-gated cleanup.
