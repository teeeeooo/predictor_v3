```yaml
record:
  date: 2026-09-02
  topic: ahri-m-documentation-sync
  tags: calculator, ahri210240, appendix-m, appendix-m1, documentation, ui, traceability
  memory_review: no-change
  memory_reason: The existing memory already captures the M/M1 owner split; this record makes recent M UI/batch behavior and its documentation correction discoverable without changing that decision.
```

# Change Reason

The recent Appendix M UI/batch follow-up changed visible point labels, HSPF aggregate labels, and demand-defrost batch presentation. The active design spec recorded the decision, but the standard owner documents still described only the M1 HSPF2/SEER2 scope and the UI adapter named a retired controller. This append-only record closes that traceability gap without rewriting prior records.

# Contract / Behavior Changed

- Appendix M and Appendix M1 remain separate contracts: standard edition, metric name, test-point schema, region/bin config, fallback behavior, and golden values are not interchangeable.
- M canonical keys remain `EV`, `H2V`, and `H1N`; the current display aliases are `Ev`, `H2v`, and `H1N(STD)`.
- M HSPF presents `Heating Load [Btu/h]`, `Compressor Input [W]`, and `Auxiliary Input [W]`; M SEER presents `CSTL [Btu/h]` and `CSEC [W]`.
- M HSPF demand-defrost timing is conditional: disabled timing fields are read-only `N/A` and credit is `1.0`; enabled timing fields are editable and the calculated credit remains read-only.
- The current common Tk table owner is `TkTableController`; the adapter documentation no longer points to the retired controller name.

# Evidence And Verification

- Existing Appendix M UI/batch regression evidence covers the labels, aggregate result fields, shared batch surface, H12/H22 pair semantics, and defrost credit behavior.
- The Appendix M project golden remains published SEER `18.05` and published HSPF `10.45`; the M1 official-calculator golden set is kept separate.
- The documentation update was checked against the active design spec, M application/config owners, Result Record workflow, and the current Tk table controller owner.
- No source or test file is changed by this documentation-sync slice; focused M UI/table evidence is reused from the recent validation, while the current AHRI-filtered regression remains green (`PYTHONPATH=. pytest -q -k ahri`: 208 passed).

# Changed Files

- `docs/ahri210240/README.md`
- `docs/ahri210240/ahri210240_notes.md`
- `docs/ahri210240/ahri210240_dev_notes.md`
- `docs/ahri210240/ahri210240_design_notes.md`
- `docs/ahri210240/ahri210240_glossary.md`
- `docs/ui_ux/adapters/TKINTER_TABLE_ADAPTER.md`
- `docs/designs/2026-09-02-ahri-documentation-sync-plan.md`

# Known Risks

- This record provides traceability and owner-document parity; it does not independently re-prove the calculator formulas or UI behavior.
- M standard references and project goldens are documented as separate paths, but any future M1 standard expansion still requires its own design gate and golden evidence.
