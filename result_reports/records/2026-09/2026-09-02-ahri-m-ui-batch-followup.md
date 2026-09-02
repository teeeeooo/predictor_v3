```yaml
record:
  date: 2026-09-02
  topic: ahri-m-ui-batch-followup
  tags: calculator, ahri210240, appendix-m, batch, ui, defrost, terminology
  memory_review: no-change
  memory_reason: Existing memory already captures the durable M/M1 owner split; this follow-up changes presentation and adds a bounded batch surface without changing that invariant.
change_gate:
  new_source: small
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Post-implementation UI review found M HSPF point labels inconsistent with the existing M1 surface, no M batch entry point, Korean SEER seasonal aggregate headers, and no visible confirmation of the automatically calculated demand-defrost credit.

# Contract / Behavior Changed

- M HSPF displays `H2v` and `H1N(STD)` while preserving canonical domain keys `H2V` and `H1N`.
- M SEER displays seasonal aggregates as `CSTL [Btu/h]` and `CSEC [W]`.
- M SEER/HSPF now expose the shared `일괄 입력` workflow through existing batch matrix/dialog/lifecycle owners and M-specific row handlers that continue to call M application adapters/capabilities.
- HSPF `Defrost Credit` is read-only: non-demand defrost displays `1.000`; demand defrost is calculated from Defrost Test/Max by the Appendix M domain and displayed after calculation.

# Evidence And Verification

- Main M SEER/HSPF UI regression covers the revised headers, standard batch button text, golden outputs, and read-only Defrost Credit display (`1.000` default; `1.026` for 180/720 minute timing).
- M batch row handlers reproduce the same SEER `18.05` and HSPF `10.45` goldens as the single surfaces; HSPF half-filled H12 is rejected and batch point labels match the single surface.
- Batch button regression opens the shared dialog shell and proves each metric is bound to its Appendix M matrix spec.

# Changed Files

- `apps/calculator/ui/ahri_m/`: UI point labels, batch specs/handlers/dialog access, and revised single surfaces.
- `apps/calculator/application/ahri_m/hspf_adapter.py`: exposes core-computed `f_def` in the UI summary model.
- Focused Appendix M UI tests and active design follow-up amendment.

# Known Risks

- Batch remains limited to the same initial M product/region scope as the single surfaces; it does not add M1 product classes, H42, or additional HSPF regions.
- The original 2026-09-02 implementation record remains append-only and describes the initial no-batch scope; this follow-up record supersedes only that UI-scope decision.
