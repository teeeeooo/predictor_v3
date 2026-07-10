# Goal

- Remove the stale ISO 16358 HSPF XLSM audit artifact.
- Update active ISO/KS calculator docs that still pointed at the retired
  `core/calculator_iso16358.py` path.

# Scope

- Deleted `reference_files/audit_iso16358_hspf_xlsm.md`.
- Updated active workflow/architecture/design/ISO/KS documentation to point to
  `core/calculators/standards/iso16358.py` and
  `core/calculators/standards/ks_c9306.py`, and to the current AS/NZS
  compatibility path where that boundary is mentioned.
- Left archive reports and historical project logs unchanged because their old
  paths describe historical state.

# Verification

- `grep` over active docs/reference areas, excluding archive history, for
  `core/calculator_iso16358.py` / `calculator_iso16358.py`: OK, no remaining
  matches.
- `git diff --check`: pending final validation.
- pytest not run because this is docs/reference cleanup only.

# Known Risks

- Historical archive/report files still contain old paths by design.

# Commit / Push

- Commit and push requested; final hash and remote match are reported in the
  terminal output.

# Project Memory Delta

- none
