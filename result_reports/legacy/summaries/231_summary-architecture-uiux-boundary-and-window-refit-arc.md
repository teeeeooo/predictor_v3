# 231 Summary — Architecture/UI-UX Boundary and Window Refit Arc

## Covered Reports

Archived by this summary:

- `221c_dynamic-content-refit-loop-stabilization.md`
- `222_result-report-lifecycle-cleanup.md`
- `223_common-dynamic-content-refit-owner-preflight.md`
- `224_common-dynamic-content-refit-owner-first-slice.md`
- `225_hong-kong-profile-switch-sizing-closeout.md`
- `226_content-hugging-window-sizing-redesign-preflight.md`
- `227_toolkit-neutral-content-hugging-window-shell-preflight.md`
- `228_tk-content-hugging-shell-first-slice.md`
- `230a_project-wide-clean-architecture-boundary-policy.md`
- `230b_clean-architecture-boundary-wording-neutralization.md`
- `230c_ui-ux-portable-document-neutralization-audit.md`
- `230d_ui-ux-portable-document-neutralization.md`

Active context intentionally not archived by this summary:

- `229_tk-content-hugging-shell-template.md`

## Arc Result

The dynamic refit/window-shell arc stabilized the Windows resize loop caused by
local nested notebook refit scheduling, then moved sizing responsibility toward
common owners:

- `window_refit.py` owns scheduling, guards, settled refit, and suppress
  behavior.
- `window_geometry.py` remains the primitive geometry helper.
- `window_shell.py` became a reusable Tk content-hugging form/shell template.
- `Iso16358Tab` is now a consumer/provider rather than the sole owner of
  scheduling and geometry application.

The Hong Kong CSPF lower blank space is still unresolved. The current likely
next boundary is extracting an `Iso16358Tab`-specific visible content
measurement adapter/provider that the shell can consume.

The architecture/UI-UX documentation arc promoted the repeated sizing lesson
into project-wide responsibility boundaries and portable UI/UX rule ownership:

- Clean Architecture / MVC boundaries are owned by
  `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`.
- Concrete project, interface, and implementation names are evidence, not
  scope boundaries.
- `docs/ui_ux/` is a portable UI/UX rule set.
- `docs/ui_ux/README.md` is the navigation/adoption index; `00` remains the
  root SSOT, `01` through `07` are portable principle/policy owners,
  `adapters/` are interface-framework-specific, and `_source/` is historical
  evidence.

## Major Decisions

- Repeated smoke failures of the same class should trigger owner-boundary
  judgment before more local patches.
- Local tab-level refit scheduling is not enough for nested/dynamic content.
- Content-hugging window/form behavior should be expressed as a shell/form
  contract: content/provider registration, visible-content measurement,
  overflow provider, after-fit hook, and one geometry apply where possible.
- UI/UX principle documents must stay portable. Concrete examples such as
  project names, standards, screens, or interface frameworks are allowed only
  as examples, evidence, or adoption notes.
- Adapter documents may keep specific framework names because their job is
  implementation mapping, not portable principle ownership.

## Completed Work

- Stabilized the 221B Windows refit loop by disabling direct metric tab-change
  refit and tightening scheduler guard behavior.
- Confirmed the remaining Hong Kong lower blank space is a dynamic content
  owner-boundary issue rather than a simple settle-cycle issue.
- Added the first common dynamic content refit owner slice.
- Added the first Tk content-hugging shell owner slice.
- Promoted the Tk shell into a reusable form template with provider
  registration and after-fit hooks.
- Added project-wide Clean Architecture / MVC boundary policy and router/agent
  gates.
- Neutralized the architecture boundary wording to keep concrete names as
  evidence rather than scope.
- Audited and neutralized the first portable UI/UX document slice (`04`, `05`,
  `07`) and added `docs/ui_ux/README.md`.

## Known Remaining Issues

- Hong Kong CSPF lower blank space remains unresolved after profile switch.
- The next implementation should extract visible content measurement from
  `Iso16358Tab` into an adapter/provider boundary consumed by `window_shell.py`.
- Windows smoke is still needed after the measurement adapter extraction.
- Common table foundation is not migrated to the main calculator table.
- Batch dialog sizing was explicitly out of scope for this arc.

## Current Active Report Kept

`229_tk-content-hugging-shell-template.md` stays active because it is the direct
implementation-state evidence for the next code slice:

- shell public API shape;
- provider/overflow/after-fit contract;
- current lower blank/flicker status;
- Windows manual smoke items.

## Next Action

Extract Tk visible content measurement adapter.
