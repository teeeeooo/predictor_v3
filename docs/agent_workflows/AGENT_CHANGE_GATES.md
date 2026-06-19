# Agent Change Gates

## Role

This document owns change-focused agent gates for:

- pre-write source boundary decisions;
- compact read-budget evidence;
- staged report association and structured gate metadata;
- local no-report exceptions and commit metadata;
- future pre-commit, commit-msg, pre-push, and CI enforcement.

It complements `DIFF_READ_BUDGET.md`, `RESULT_REPORT_WORKFLOW.md`, and
`check_code_structure.py`. It does not replace their owner responsibilities.

The owner policy is active. The automated gate tool and hooks described below
are not implemented yet and must be added in separate slices.

## Applicability

Use this workflow for:

- new source modules, helpers, adapters, controllers, profiles, dialogs,
  tables, shells, sessions, policies, or tools;
- structure-impacting source moves, splits, merges, or owner changes;
- additions to an existing soft-limit hotspot;
- report-backed source, test, tool, config, or code-map changes;
- follow-ups where broad or repeated reads were previously identified.

Docs-only wording, report lifecycle work, commit/push-only follow-ups, and
simple status checks do not require the full workflow unless they modify this
workflow or its enforcement.

## Required Stages

1. Run the pre-write boundary check before creating source files.
2. Read targeted ranges and keep a Read Ledger when required.
3. Implement within the declared owner boundaries.
4. Add a structured `change_gate` block to the associated active report.
5. Validate the staged change against this policy.
6. Run hooks and CI enforcement after those surfaces are implemented.

## Pre-write Boundary Gate

Before source edits, answer these questions:

| Question | Required action when yes |
| --- | --- |
| New source likely exceeds 220 LOC? | Record a split plan. |
| New source likely exceeds 250 LOC? | Split first or justify it. |
| One file owns two or more responsibilities? | State the owner boundary. |
| State, view, shell, calculation, or I/O are mixed? | Split by responsibility. |
| Reference implementation is already 200 LOC or larger? | Decide the split before adapting it. |
| Existing target exceeds a soft limit? | Keep it wiring-only or run a split audit. |
| Task introduces three or more responsibility areas? | Separate interface/skeleton and implementation slices. |

Prefer feature-local state/view/wrapper splits over premature generic
framework extraction. Do not split a cohesive owner solely to reduce LOC.

Allowed `new_source` decisions:

- `none`
- `small`
- `split`
- `justified`

Allowed `hotspot_delta` decisions:

- `none`
- `wiring-only`
- `accepted-for-slice`
- `split-audit-required`
- `split-required`

`justified`, `accepted-for-slice`, and either split-required value need one
short reason in the report.

## Read Ledger

Include a compact Read Ledger when:

- creating a source module or UI/tool surface;
- changing architecture-sensitive ownership;
- modifying a dialog, table, profile, window, result, or export surface;
- a prior review identified read-budget problems;
- any broad or repeated read occurred.

Follow `DIFF_READ_BUDGET.md`: locate symbols first, start with 30-80 lines,
and require a blocker before reading more than 100 lines from one file at once.

Report format:

```text
Read Ledger:
- <path>: lines <start>-<end>, reason: <short reason>
- broad read: none | <path + blocker>
- repeated read: none | <path + reason>
```

Accepted broad-read blockers are unclear method/owner boundaries after symbol
search, explicit full-file inventory, truncated target output, or generated
structure that cannot be inspected narrowly. "Might be useful" is not a
blocker.

## Structured Change Gate

Every associated active report for source, test, tool, config, or code-map
changes must contain this exact block:

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: not_required
  report_exemption: none
  read_ledger: not_required
```

Allowed `code_map_check` values:

- `not_required`
- `checked`
- `skipped`
- `regenerated`
- `no-change`

Allowed `report_exemption` values:

- `none`
- `user-approved-docs-only`
- `user-approved-formatting-only`
- `commit-push-only`
- `status-only`

Allowed `read_ledger` values:

- `not_required`
- `included`
- `skipped`

The future gate tool must parse only this structured block for pass/fail. It
must not infer gate state from ordinary report prose. Add one short reason for
`new_source: justified`, nontrivial hotspot decisions, `code_map_check:
skipped`, non-`none` exemptions, and `read_ledger: skipped`.

## Staged Report Association

In `--cached` mode, only staged files under `result_reports/active/` can satisfy
the report requirement.

| Staged state | Decision |
| --- | --- |
| Relevant change plus exactly one staged active report | Parse that report. |
| Relevant change plus no staged active report | Fail unless a valid local exemption exists. |
| Relevant change plus multiple staged active reports | Fail unless the manifest selects one `report_path`. |
| Existing active report is not staged | Do not recognize it. |

When a manifest selects `report_path`, that path must itself be a staged active
report. The tool must read its index blob, not its working-tree content.

## No-report Exceptions

No-report approval is narrow and must not use `--no-verify` as the normal path.

Allowed reasons:

- `user-approved-docs-only`
- `user-approved-formatting-only`
- `commit-push-only`
- `status-only`

No-report exemption is forbidden for behavior changes, calculator logic,
schema/public API changes, expected/golden changes, or new workflow/tool source.

### Local Manifest

The future local hook may read a task manifest resolved through:

```bash
git rev-parse --git-path agent_task_manifest.yml
```

Minimum schema:

```yaml
allowed_paths:
  - docs/agent_workflows/AGENT_CHANGE_GATES.md
report_path: null
report_exemption:
  reason: user-approved-formatting-only
  scope: formatting-only
  approved_by_user: true
```

Rules:

- `allowed_paths` is required, nonempty, and contains literal repository paths;
- every staged path must be listed;
- glob patterns are not accepted in the initial implementation;
- `report_path`, when set, must identify one staged active report;
- reason and scope must be allowed and compatible;
- `approved_by_user` must be exactly `true`.

`user-approved-docs-only` accepts docs/report text paths only.
`user-approved-formatting-only` accepts existing files only and requires the
future gate's formatting-only classifier to confirm no semantic change.
`commit-push-only` and `status-only` cannot authorize staged content changes.

### Commit Trailer And CI

Local manifests are not available to CI. A locally exempted commit must carry:

```text
Agent-Report-Exemption: user-approved-formatting-only
```

A future `commit-msg` hook must validate the trailer against the local manifest
and reject unsupported or behavior-changing exemptions. Branch-diff CI must
recognize only the same allowlisted trailer values and independently verify
that the diff is eligible. The trailer alone is never sufficient evidence.

## Staged Change Gate

The future command surfaces are:

```bash
python3 -B tools/check_agent_change_gate.py --cached
python3 -B tools/check_agent_change_gate.py --base <merge-base> --head HEAD
```

`--cached` must inspect the index:

- inventory: `git diff --cached --name-status`;
- staged content: `git show :<path>`;
- staged delta: `git diff --cached --numstat`;
- whitespace: `git diff --cached --check`.

It must remain correct with partially staged files.

Minimum staged checks:

| Check | Policy |
| --- | --- |
| Whitespace errors | Hard fail. |
| New production Python source over 350 LOC | Hard fail. |
| New production Python source 251-350 LOC | Require `new_source: split` or `justified`. |
| New production source over 5 classes | Warning. |
| New production source over 5 classes and over 250 LOC | Also require `new_source: justified`. |
| New production source over 8 classes | Strong warning, not hard fail. |
| Existing hotspot with net +40 LOC or more | Require an accepted hotspot decision. |
| Relevant change without associated staged report | Fail unless valid exemption. |
| Structural source change without code-map judgment | Fail. |
| Staged path outside manifest `allowed_paths` | Fail. |

Production source roots are `core/`, `ui/`, `apps/`, and `scripts/`. Tool source
under `tools/` is report-relevant even though it is not evaluated as production
runtime source by the LOC policy.

A hotspot is an existing source already over a structure soft limit,
allowlisted as known-large, or over that limit in staged content. Use net LOC
delta between the base/index blobs, not raw diff additions, for the +40 rule.

Structural changes include new/moved/deleted source, new helpers or surfaces,
owner/commonization changes, and source splits or merges.

## Hook And CI Policy

Future `.githooks/pre-commit`:

```bash
git diff --cached --check
python3 -B tools/check_agent_change_gate.py --cached
```

Do not run pytest or regenerate the code map in pre-commit.

Future `.githooks/commit-msg` validates exemption trailers against the local
manifest. Pre-push may run `check_code_structure.py` and code-map `--check`
after the staged gate is stable; it must not run full pytest by default.

CI must rerun branch-diff gates because hooks can be bypassed. It must handle
merge-base and shallow-clone setup explicitly and fail clearly when the base is
unavailable. CI checks generated artifacts; it does not regenerate them.

## Implementation Status And Slices

Current status after this owner document lands:

- policy owner: implemented;
- router links: pending;
- `check_agent_change_gate.py`: pending;
- pre-commit/commit-msg hooks: pending;
- pre-push and CI branch mode: pending.

Implementation order:

1. Add minimal links from `AGENTS.md` and `AGENT_TASK_ROUTER.md`.
2. Implement and test `tools/check_agent_change_gate.py --cached`.
3. Add pre-commit and commit-msg hooks.
4. Add branch-diff mode and CI/pre-push integration after the cached gate is
   stable.

Do not duplicate this policy text into routing documents.
