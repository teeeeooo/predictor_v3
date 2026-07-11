```yaml
record:
  date: 2026-07-11
  topic: brazil-cspf-compliance
  tags: calculator, brazil, cspf, capability, profile, golden, tkinter, batch
  memory_review: updated
  memory_reason: Preserve the Brazil composite capability boundary, exact-rule policy, and single/batch caller ownership for future calculator work.

change_gate:
  new_source: justified
  hotspot_delta: accepted-for-slice
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
```

# Change Reason

Add Brazil CSPF compliance on top of the existing ISO 16358 T1 core without
copying the seasonal calculation loop or changing existing ISO result schemas.
The feature requires one canonical composite capability for 3-point/2-point
comparison, exact Rule 1/Rule 2 evaluation, a Brazil production profile/config,
and matching single and batch calculator surfaces.

# Contract / Behavior Changed

- Added the enabled `brazil_cspf_compliance` ISO/CSPF/cooling profile with a
  `brazil.cspf_compliance` capability allowlist and Brazil-only production bins.
- Added frozen Brazil request/result contracts. The operation preserves both
  ISO raw result mappings and computes exact CSPF values from raw bin
  diagnostics before evaluating Rule 1, Rule 2, and the OR final decision.
- Added Brazil-owned finite-positive input and diagnostic-integrity validation;
  missing or duplicate 29°C bins fail fast with `BrazilCspfComplianceError`.
- Added the independent Brazil mode to the existing ISO tab, a six-cell input
  matrix, comparison/rule/final result surface, and a shared batch matrix/dialog
  that calls the same capability through the application usecase.
- Added profile-level capability allowlists while preserving unrestricted
  legacy profiles with `capability_ids=None`; generic `iso16358.cspf` cannot
  execute the Brazil profile.

# Evidence And Verification

- Read-only core evidence reproduced the supplied golden: 3-point exact CSPF
  `6.0230584487`, 2-point exact CSPF `4.5500136808`, exact CSTL/CSEC values,
  measured 29°C EER `5.5573770492`, calculated 29°C EER `5.7524453055`, and
  2080 total bin hours.
- Focused Brazil/core/profile/application/UI/config suite passed: `125 passed`,
  followed by final Brazil contract tests passing `29 passed` after the last
  exact-rounding and raw-identity guards.
- Final full active suite passed: `1664 passed, 2 xfailed` in 49.02 seconds.
- `python3 -B tools/check_code_structure.py`, `python3 -m py_compile` for the
  calculator/application/UI tree, and `git diff --check` passed. The structure
  guard reported only the existing ten soft warnings; no new hard warning was
  introduced.
- Automated Tk focused smoke passed (`4 passed`), including Brazil mode
  composition, two-row result/rule rendering, stale-result clearing, and batch
  dialog snapshot preservation.
- Computer Use manual interaction was attempted. The Tk window rendered, but
  its widgets were absent from the accessibility tree and coordinate clicks
  were not delivered to controls; manual mode/input/batch interaction is
  therefore recorded as skipped due to a platform/input-injection gap.

# Changed Files

- `core/calculators/capability/` and `core/calculators/profiles.py`
- `data/region_configs/brazil.json`
- `apps/calculator/application/brazil_cspf/`
- `apps/calculator/application/profile_resolver.py`
- `apps/calculator/ui/sections/brazil_cspf_*`
- `apps/calculator/ui/batch_dialogs/profiles/brazil_cspf.py`
- `apps/calculator/ui/profile_resolver.py` and `apps/calculator/ui/tabs/iso16358_tab.py`
- Brazil fixture and focused calculator/application/UI tests
- `docs/WORK_PLAN.md`

# Known Risks

The final GUI smoke remains automated rather than manually operated because
the current Computer Use path cannot inject events into this Tk application.
Packaging, deployment, and `main` merge were intentionally not performed.
