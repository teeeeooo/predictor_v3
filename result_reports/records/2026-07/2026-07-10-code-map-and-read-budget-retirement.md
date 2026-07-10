# Code-map And Read-budget Retirement

record:
  date: 2026-07-10
  topic: code-map and read-budget retirement
  tags: agent-harness, code-map, read-budget
  memory_review: updated
  memory_reason: active architecture/source-owner memory still named reference-map evidence and must point to targeted owner/reuse search after retirement

change_gate:
  new_source: none
  hotspot_delta: none
  ui_literal_exemption: none
  reuse_commonization: checked

## Reason And Evidence

- The tracked map was stale and dirty-generated, with 110 historical map
  commits, including 81 in the recent approximately 20 days.
- Its maintenance surface was 265 map lines, 917 generator-subsystem lines, and
  397 dedicated-test lines, yet no CI or hook generated it and the gate emitted
  only a stale warning.
- Direct exact-symbol search plus bounded sibling/owner review is more precise
  for changed behavior and ownership.

## Change

- Deleted the tracked map, all of `tools/code_checker/`, its dedicated test, and
  the standalone diff/read-budget workflow.
- Removed map-freshness coupling and the `code_map_check` field and warning.
- Folded targeted changed-path/owner review and owner-matched validation rules
  into the task router.

## Preserved Behavior

- Preserved `check_code_structure.py` hard/soft behavior, the
  reuse/commonization warning, UI literal exemption, manifest scoping, and
  record/index/memory checks.
- Preserved targeted `AGENTS.md` first-read discipline and bounded UI
  validation.

## Verification

- 66 focused tests passed with `PYTHONPATH=.`.
- `py_compile` passed.
- Structure guard completed with 0 errors and only 9 pre-existing hotspot
  warnings.
- `git diff --check` passed.
- Active reference scan was clean except for the parser rejection test.
