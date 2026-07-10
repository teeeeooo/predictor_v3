# Calculator Window/Profile Lifecycle Compliance Audit

## Status

Active reference for the common lifecycle-controller design and migration
sequence in tasks 2–5.

## Purpose

Audit how the calculator shell and ISO16358, EN14825, and AHRI210240 profile
tabs currently compose visible-content measurement, scheduling, content-hugging
geometry, nested notebook changes, and detail visibility. This record classifies
the differences as justified policy variation or structural debt; it does not
change production behavior.

## Policy Baseline

The active window policy requires profile switches, nested tab switches, and
detail open/close to share a settled visible-content refit policy. Scheduling,
measurement, shell geometry, and view composition remain separate owners.
Profile/content switches preserve the current monitor and placement; overflow
stays inside the content viewport. Local fixed sizes, repeated synchronous
updates, and profile-local settle patches are not primary solutions.

## Current Owner Flow

```text
CalculatorTkApp top-level NotebookTabChanged
  -> selected tab preferred_initial_size()
  -> outer notebook content size
  -> selected tab fit_toplevel_to_current_content_once()
  -> optional on_parent_tab_selected()

Profile tab event/detail callback
  -> profile-local DynamicContentRefitScheduler
  -> profile-local fit callback
  -> profile-local TkContentHuggingForm
  -> shared TkContentHuggingShell geometry application
  -> profile-local scroll reset
```

The primitive owners are already separated correctly:

- `TkVisibleContentMeasurement`: requested-size snapshot and nested-notebook
  visible contribution replacement;
- `DynamicContentRefitScheduler`: idle settling, request coalescing, and
  measurement suppression;
- `TkContentHuggingShell`/form: snapshot-provider binding and one geometry
  mutation;
- `window_geometry.py`: caps, placement, parsing, and formatting;
- profile tabs: view composition and event binding.

The debt is the repeated assembly and lifecycle policy inside each profile tab,
not the primitive helper boundaries themselves.

## Profile Comparison

| Concern | ISO16358 | EN14825 | AHRI210240 |
| --- | --- | --- | --- |
| Scroll/content owner | `ScrollableFrame` | `ScrollableFrame` | `ScrollableFrame` |
| Measurement construction | profile-local | profile-local | profile-local |
| Shell/form construction | profile-local | profile-local | profile-local |
| Scheduler construction | profile-local | profile-local | profile-local |
| Nested notebook | Hong Kong metric notebook | SEER/SCOP notebook | SEER2/HSPF2 notebook |
| Nested measurement active | Hong Kong mode only | always | profile visible only |
| Nested switch refit | one cycle | one cycle | two cycles when visible |
| Detail refit | shared callback, one cycle | shared callback, one cycle | HSPF2 callback, default one cycle |
| Parent-selected refit | none | two cycles | none |
| After-fit policy | reset scroll position | reset scroll position | reset scroll position |
| Compatibility aliases | schedule/refit and scroll aliases | scroll aliases | minimal |

## Justified Policy Variation

- ISO enables nested-notebook measurement only in Hong Kong mode because its
  other modes use mutually exclusive non-notebook surfaces.
- AHRI checks outer-profile visibility before reacting to an inner metric change
  because hidden AHRI tabs must not mutate the main window.
- EN14825 currently requests a two-cycle parent-selected correction because a
  top-level return can expose a previously open detail surface after transient
  notebook undermeasurement.
- ISO mode changes may need two cycles when first entering Hong Kong because the
  mode surface is rendered/reused before its nested notebook contributes size.

These are controller configuration inputs or trigger policies, not reasons for
each profile to own the common lifecycle machinery.

## Structural Debt

1. Every profile tab constructs the same scheduler → measurement → shell/form
   graph and repeats the same fit method.
2. Public compatibility methods (`preferred_initial_size`, one-shot fit) and
   event callbacks delegate to differently named private methods, obscuring one
   common contract.
3. Settle-cycle values are selected at profile call sites without one owner for
   parent, nested-tab, and detail trigger policy.
4. Measurement suppression is wired manually through each profile scheduler.
5. The same after-fit scroll reset is repeated as an inline lambda.
6. A new profile can bypass the intended primitives or omit one lifecycle edge
   without a structural gate detecting the divergence.
7. `CalculatorTkApp` discovers optional capabilities dynamically, but the
   lifecycle capabilities are not represented by one profile-owned facade.

## Compliance Assessment

| Policy requirement | Current status | Assessment |
| --- | --- | --- |
| Shared measurement/geometry primitives | present | compliant foundation |
| Settled nested/detail refit | present per profile | behavior compliant, assembly duplicated |
| Profile-switch settled refit | EN only | incomplete common lifecycle |
| Measurement suppression | present per profile | compliant behavior, duplicated wiring |
| One coalesced geometry mutation | shell/form path | compliant |
| Preserve position/monitor | common geometry path | compliant |
| Profile tabs avoid lifecycle-owner construction | not enforced | structural debt |
| Stable cached profile surfaces | present | compliant |

## Controller Boundary Candidates For Task 2

The common controller should own construction and delegation for:

- `TkVisibleContentMeasurement`;
- `DynamicContentRefitScheduler`;
- `TkContentHuggingShell.register_content()`;
- preferred-size and one-shot fit methods;
- parent-selected, nested-tab, and detail-visibility refit triggers;
- measurement suppression and after-fit scroll reset;
- default and configurable settle-cycle policy.

Each profile should provide only its view-owned inputs:

- lifecycle owner widget and toplevel;
- content and scrollable frame;
- optional nested notebook and active predicate;
- parent/nested/detail settle policy overrides where evidence requires them;
- optional after-fit callback.

## Migration And Gate Implications

- Task 3 should establish the controller and migrate EN14825 first, preserving
  the three existing external tab capabilities and all SEER/SCOP callbacks.
- Task 4 should migrate AHRI and ISO, expressing visibility/mode predicates as
  configuration rather than controller branches.
- Task 5 should reject direct construction of measurement, shell, scheduler, or
  `register_content()` inside production `tabs/*.py` after all three migrations.
- The gate should allow the common controller owner and tests, and should not
  ban view-owned event binding or predicate definitions.

## Acceptance For The Next Design Slice

Task 2 must decide the controller name/location, constructor contract, public
delegation methods, policy defaults/overrides, migration sequence, compatibility
strategy, and hard-gate enforcement timing without modifying production code.
