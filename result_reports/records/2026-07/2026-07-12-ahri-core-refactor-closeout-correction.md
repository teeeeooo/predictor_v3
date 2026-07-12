```yaml
record:
  date: 2026-07-12
  topic: ahri-core-refactor-closeout-correction
  tags: ahri210240, seer2, hspf2, architecture, refactor, closeout, correction
  memory_review: no-change
  memory_reason: The memory seed already records the final private-owner structure, sibling-engine boundary, and golden-versus-characterization distinction.
```

# Change Reason

The R0 contract-lock record correctly preserves the baseline but remained written from the pre-extraction perspective. This correction records the completed R1–R5 outcome without mutating the committed append-only baseline record.

# Contract / Behavior Changed

R1–R5 are complete. The stable `ahri_hspf2.py` and `ahri_seer2.py` public facades now delegate to private owners under `core/calculators/standards/_ahri/`: HSPF2 config/context, point resolution, performance, variable seasonal engine, result assembly, and legacy v2 engine; SEER2 variable-capacity engine; and only the proven identical numeric primitives. Public APIs, formulas, golden expected values, diagnostics/result schemas, exceptions, and application seasonal scaling remain unchanged.

# Evidence And Verification

The final focused suite passed 180 tests covering contract fingerprints, HSPF2 branches/diagnostics, SEER2 HP/AC, dispatcher/capability, Calculator adapters and AHRI surfaces, plus ML/result/ranking envelopes. `tools/check_code_structure.py --verbose` reported no new AHRI warnings; its nine warnings were pre-existing and outside this workstream. `git diff --cached --check` and `tools/check_agent_change_gate.py --cached` passed for every slice commit; warning-first reuse/commonization evidence was reviewed, and R5 commonized only identical safe-division and linear-interpolation semantics.

# Changed Files

The completed workstream includes the stable AHRI facades, private `_ahri` implementation package, contract/owner tests, AHRI owner documents, implemented design status/index, project log, memory seed, the R0 baseline record, and this closeout correction.

# Known Risks

The strict deep-result fingerprints remain intentionally sensitive to observable floating-point or nested mapping drift. Future two-stage and triple-capacity work still requires a separate design and sibling engines; it must not add product branches to the current variable-capacity formula bodies.
