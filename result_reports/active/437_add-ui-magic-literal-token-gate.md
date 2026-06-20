# 437 Add UI Magic Literal Token Gate

## Goal

Prevent newly staged production UI sizing/color literals from bypassing token
owners without attempting a legacy migration.

## Scope

- Document project-wide UI presentation literal/token policy and legacy
  grandfathering.
- Add an index-only Phase 1 detector to the existing cached gate.
- Add a structured report exemption field.
- Add focused temp-repository tests and synchronize the work-plan pointer.

## Non-goals

- No AHRI sizing/A2/source or batch-label work, UI layout/token migration,
  common table/window refactor, core/config/fixture/golden, pre-push, CI, or
  unrelated cleanup.

## Changed Files

- `docs/agent_workflows/AGENT_CHANGE_GATES.md`
- `tools/agent_change_gate.py`
- `tools/agent_change_gate_git.py`
- `tools/agent_change_gate_models.py`
- `tools/agent_change_gate_ui_literals.py`
- `tests/test_tools_check_agent_change_gate.py`
- `tests/test_tools_check_ui_magic_literals.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/437_add-ui-magic-literal-token-gate.md`

## Task Results

- The policy distinguishes UI presentation literals from domain/regulation
  constants and explicitly grandfathers untouched legacy.
- The detector reads only staged/index blobs and added index line numbers.
- Phase 1 covers numeric table character widths, numeric-pair `min_size`, fixed
  geometry strings, and six-digit color strings in production UI Python.
- `layout_constants.py` and `*token*.py` owners are allowed; tests and non-UI
  domain code are not scanned.
- The existing cached gate invokes the detector, so the existing pre-commit
  hook gains enforcement without another process or hook edit.
- Only `ui_literal_exemption: approved-for-slice` in the associated structured
  report can bypass the detector; manifest/trailer report exemptions do not.

## Verification

- `python3 -B -m pytest tests/test_tools_check_ui_magic_literals.py tests/test_tools_check_agent_change_gate.py tests/test_githooks.py`
  — 35 passed.
- `python3 -B tools/check_code_structure.py` — passed with only two pre-existing
  EN14825 soft-LOC warnings.
- Code-map `--check` reported stale as expected for the new tool module;
  regenerated once with `build_reference_map.py`.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed with the new
  UI literal detector active on this staged slice.

## Known Risks

- Phase 1 intentionally does not detect every spacing/font/minsize expression;
  widening patterns requires evidence and focused false-positive tests.
- Token-owner filename exemption trusts owner review; it does not validate token
  naming or detect duplicate semantic values.
- Existing reports staged in future source slices must adopt the new structured
  field before the closed schema will accept them.

## Scope Compliance

- Prompt-supplied policy targets, staged-only boundary, exemption owner, and
  tests were sufficient for Design Gate.
- New policy logic is split from Git index access and the existing CLI shell.
- `.githooks/pre-commit` is unchanged because it already invokes the integrated
  cached checker.
- `project_log.md` remains outside the approved paths; this report and the
  active work-plan owner capture the slice and next action.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENT_TASK_ROUTER.md`: workflow/source/report route ranges only; reason:
  applicable coding, report, and commit gates.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: structured gate, staged gate,
  hook, and implementation-status ranges; reason: policy owner.
- cached gate CLI/policy/Git/model modules: complete small files or targeted
  methods; reason: index access, integration, and closed schema.
- existing checker/hook tests: temp-repo and invocation ranges only; reason:
  focused test parity.
- `.githooks/pre-commit`: complete small script; reason: confirm integration is
  inherited through the existing cached command.
- `docs/WORK_PLAN.md`: current-slice range; reason: next-action sync.
- broad read: none
- repeated read: none

## Next Action

Common visible-content notebook measurement design.
