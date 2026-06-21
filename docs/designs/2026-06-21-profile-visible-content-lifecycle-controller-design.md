# Profile Visible-Content Lifecycle Controller Design

## Status

Approved implementation contract for calculator lifecycle tasks 3–5.

## Decision

Create a feature-owned package at `apps/calculator/ui/lifecycle/` with a
`ProfileVisibleContentLifecycleController` in `controller.py`. The package owns
reusable Tk profile lifecycle orchestration; profile tabs remain views that
compose widgets and forward lifecycle triggers.

This placement avoids another broad-folder flat helper and leaves room for a
future protocol or policy module only if a later approved slice requires one.
Task 3 creates only `__init__.py` and `controller.py`.

## Responsibility Boundary

### Controller owns

- construction of `DynamicContentRefitScheduler`;
- construction of `TkVisibleContentMeasurement`;
- construction/registration of `TkContentHuggingShell` and its content form;
- preferred visible-content size;
- immediate one-shot fit;
- coalesced visible-lifecycle refit requests;
- parent-selected, nested-tab, and detail-visibility trigger methods;
- measurement suppression through the scheduler;
- after-fit scroll reset;
- default and profile-configured settle-cycle policy.

### Profile tab owns

- `ScrollableFrame`, content widgets, notebooks, sections, and event binding;
- the optional nested notebook instance;
- the predicate that says whether nested measurement is active;
- evidence-based settle-cycle configuration;
- forwarding profile events to controller trigger methods;
- existing public tab compatibility methods.

### Existing primitive owners remain unchanged

- measurement arithmetic stays in `window_measurement.py`;
- idle/coalescing mechanics stay in `window_refit.py`;
- shell fitting stays in `window_shell.py`;
- geometry math stays in `window_geometry.py`.

The controller composes these owners; it does not copy or absorb their logic.

## Constructor Contract

```python
ProfileVisibleContentLifecycleController(
    *,
    owner: tk.Widget,
    content: tk.Widget,
    scrollable: ScrollableFrame,
    nested_notebook: ttk.Notebook | None = None,
    nested_notebook_active: Callable[[], bool] | None = None,
    parent_selected_settle_cycles: int | None = None,
    nested_tab_settle_cycles: int = 1,
    detail_visibility_settle_cycles: int = 1,
    after_fit: Callable[[ContentFitResult], None] | None = None,
)
```

Policy:

- `owner` supplies idle scheduling and settled layout updates.
- `content`, `scrollable`, notebook, and active predicate are measurement inputs.
- omitted `after_fit` defaults to `scrollable.reset_scroll_position()`.
- `parent_selected_settle_cycles=None` means the controller exposes no-op parent
  selection behavior; a tab should only publish `on_parent_tab_selected()` when
  it already has or explicitly adopts that external capability.
- cycle values are positive integers validated by the controller.
- profile call sites choose only named trigger policy, never scheduler internals.

## Public Controller Interface

```python
preferred_initial_size() -> tuple[int, int]
fit_toplevel_to_current_content_once() -> None
request_visible_lifecycle_refit(*, settle_cycles: int | None = None) -> bool
on_parent_tab_selected() -> bool
on_nested_tab_changed() -> bool
on_detail_visibility_changed() -> bool
vertical_overflow_delta() -> int
snapshot() -> VisibleContentSnapshot
```

`request_visible_lifecycle_refit()` is the narrow compatibility escape hatch for
existing event paths that require an explicit evidence-based cycle count. New
ordinary parent/nested/detail paths use the named trigger methods.

The controller may expose read-only diagnostic/test properties for pending state
or primitive instances only when existing tests cannot assert behavior through
the public trigger contract. Production profile tabs must not use those
properties to bypass named lifecycle methods.

## Compatibility Strategy

Profile tab public interfaces remain stable:

- `preferred_initial_size()` delegates to the controller;
- `fit_toplevel_to_current_content_once()` delegates to the controller;
- EN14825 `on_parent_tab_selected()` delegates to the controller.

Existing section callbacks keep their current signatures. Profile-local private
aliases may temporarily delegate to the controller during a migration commit if
tests or section constructors already reference them, but they must not construct
or manipulate scheduler/measurement/shell primitives. Task 4 should remove
unneeded aliases where focused tests can move to the controller contract.

## Profile Configuration

| Profile | Nested active predicate | Parent cycles | Nested cycles | Detail cycles |
| --- | --- | ---: | ---: | ---: |
| EN14825 | always true | 2 | 1 | 1 |
| AHRI210240 | outer profile is visible | none | 2 | 1 |
| ISO16358 | current mode is Hong Kong | none | 1 | 1 |

ISO retains the existing explicit two-cycle request when entering Hong Kong for
the first time. This is a mode-render trigger, not the ordinary nested-tab
default, and uses the compatibility request method.

## Migration Sequence

### Task 3: foundation and EN14825

- create the lifecycle package and controller;
- add controller unit tests using fake owner/measurement-facing widgets where
  practical;
- replace EN14825 direct primitive construction;
- retain its three public methods and section callback signatures;
- preserve one-cycle detail/nested and two-cycle parent behavior.

### Task 4: AHRI then ISO

- migrate AHRI, preserving its outer visibility predicate and two-cycle inner
  metric behavior;
- migrate ISO, preserving Hong Kong-only nested measurement, mode rendering,
  compatibility schedule method, and detail callbacks;
- update tests to assert named controller triggers rather than scheduler internals
  where feasible.

### Task 5: enforcement

- add a structure rule only after all production profile tabs are migrated;
- reject forbidden constructor/call AST patterns in
  `apps/calculator/ui/tabs/*.py`;
- allow imports/type references only when they do not instantiate the primitive;
- allow `apps/calculator/ui/lifecycle/` and tests;
- document the hard rule in workflow owners.

## Hard-Gate Design

The structure checker is the preferred owner because the rule is a persistent
source architecture invariant, not staged-report policy. The rule should inspect
production tab files and reject calls to:

- `TkVisibleContentMeasurement(...)`;
- `TkContentHuggingShell(...)`;
- `DynamicContentRefitScheduler(...)`;
- `.register_content(...)`.

The initial rule is intentionally syntactic and conservative. It does not ban
view event binding, controller construction, measurement diagnostics requested
through the controller, or test code.

## Invariants

- One event path produces at most one pending settled refit.
- Measurement-side tab events are suppressed through the same scheduler used by
  the controller.
- Immediate top-level sizing remains available and behavior compatible.
- Geometry application continues through one registered content form.
- Detail/nested triggers do not call geometry directly.
- Profile-specific predicates and cycle policies are injected, not encoded as
  profile-name branches in the controller.
- No core, result, detail-payload, or calculation dependency enters the package.

## Verification Contract

- controller unit tests: delegation, defaults, policy validation, coalescing
  handoff, named trigger cycles, suppression wiring, and after-fit reset;
- task 3: EN14825 profile-switch and SEER/SCOP detail suites;
- task 4: AHRI/ISO lifecycle/detail suites plus EN profile-switch regression;
- task 5: focused structure-rule pass/fail fixtures and the live structure guard;
- relation assertions over platform-specific exact pixels.

## Rejected Alternatives

- **One base tab class:** couples view inheritance to lifecycle policy and makes
  profile composition less explicit.
- **Move primitives into `CalculatorTkApp`:** the app does not own profile-local
  content, nested predicates, or detail triggers.
- **Keep profile-local assembly with a shared factory:** reduces constructor
  repetition but leaves trigger policy and compatibility delegation scattered.
- **Add another flat `ui/profile_lifecycle.py`:** violates the new-source owner
  preflight and offers no feature package boundary.
