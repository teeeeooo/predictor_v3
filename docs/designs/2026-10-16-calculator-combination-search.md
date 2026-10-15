# Calculator Combination Search — Implementation Specification

**Status:** Implemented for all currently exposed paths; native verification limits are listed in §10.
**Scope:** All currently exposed `app_calculator` standard/profile/product paths.
**Source baseline:** `cc96344c6a08205e754b0b0eb4a3c92e32e29b4f`.
**Execution state:** [Work Plan](../WORK_PLAN.md). This is a standalone Calculator
feature, independent of the held multi-point Predict → Calculate workstream.

## 1. Goal and confirmed decisions

Users enter several measured candidates for each test point, calculate every
combination, inspect results in descending seasonal-efficiency order, and export
them to CSV. For example, three STD candidates and five HALF candidates produce
15 calculations. One candidate contains a complete capacity/power pair from one
test; capacity and power must never be combined independently.

- Hard limit: **10,000 combinations per run**, inclusive. Reject 10,001 or more
  before calculation. Do not silently truncate, sample, or retain only top-K.
- A run uses one standard, profile, metric, climate, product variant, and set of
  common options. Different contexts have separate rankings.
- Include only active independent measured points in the Cartesian product.
  A fixed point has one included candidate. Derived, mapped, and disabled points
  are not independent axes. Common scalar settings are not candidate pools.
- Existing engines, formulas, configs, accepted goldens, and public result/API
  contracts remain authoritative. Calculator code stays pure Python.
- Calculation is explicit. Editing updates validation and the projected count;
  it does not start a combination run. Existing single/batch auto-calculation
  behavior remains unchanged.
- Use the existing Tkinter table and dialog foundations. Do not migrate to Qt.
- Complete the full coverage below; the initial ISO slice is an integration
  checkpoint, not the final feature scope.

## 2. Coverage and point semantics

The production operation inventory is defined by
[`build_builtin_capability_registry()`](../../core/calculators/capability/gateway.py)
and the actual tab/section composition in
[`CalculatorTkApp`](../../apps/calculator/ui/calculator_app.py).
There are 11 operation IDs; profile/product branches below also require coverage.
Point counts are current application inputs, not universal claims about standards.

| Current path | Operation / ranking context | Independent capacity/power pools |
| --- | --- | --- |
| ISO 16358-1 / India ISEER | `iso16358.cspf`; select ISO or India profile | 2: `35_full`, `35_half` |
| Hong Kong CSPF | `iso16358.cspf`; `hong_kong_cspf` | 2; declared capacity is common context |
| Hong Kong HSPF | `iso16358.hspf`; `hong_kong_hspf` | 2: `7_full`, `7_half` |
| SASO T3 | `iso16358.cspf`; `saso_t3_cspf` | 3 required; 4 when measured 35 Min is enabled |
| Brazil CSPF | `brazil.cspf_compliance` | 3: `35_full`, `35_half`, `29_half` |
| KS C 9306 CSPF | `ks_c9306.cspf` | 3 |
| KS C 9306 HSPF | `ks_c9306.hspf` | 5; rated cooling capacity is common context |
| EN14825 SEER | `en14825.seer`; Tested result | 4: A/B/C/D |
| EN14825 SCOP | `en14825.scop`; Tested result, selected climate | Up to 6: A/B/C/D/Tbiv/TOL, resolved by current point policy |
| AHRI Appendix M SEER | `ahri210240.seer` | 5 |
| AHRI Appendix M HSPF | `ahri210240.hspf` | 5 required + optional H12/H22 = up to 7 |
| AHRI Appendix M1 SEER2 | `ahri210240.seer2`; variable or dual-stage | Variable 5; dual-stage 4 |
| AHRI Appendix M1 HSPF2 | `ahri210240.hspf2`; variable, dual-stage, or Triple Northern | Variable up to 8; dual-stage up to 8; Triple Northern up to 9 |

Preserve every currently accepted system type and option within these paths;
the table does not enable unsupported metric/product combinations. Historical
AS/NZS compatibility code and core-only experimental profiles are outside the
currently exposed application scope.

### Rules that must be reused

- ISO/ISEER currently calculates two profiles in one comparison surface. The new
  dialog selects one profile per run; it must not mix the two scores in one rank.
- SASO selects required-only or measured-Min context before running. An omitted
  optional point uses the current owner rule, not an invented zero-valued test.
- EN14825 candidates represent **Tested capacity/power**. Declared capacity and
  EER/COP, Pdesign, auxiliary powers, temperatures, and climate remain common
  context. Never substitute a Declared score when Tested input is incomplete.
  Preserve existing W-to-core-unit conversion in the application adapter.
- SCOP calls `ScopAdapter.resolve_point_availability()`. At the probed warmer
  defaults, B/C/D are independent, Tbiv maps to B, A is inactive, and TOL is
  threshold-only. Changed Tbiv/TOL settings must resolve the policy again.
- AHRI Appendix M and M1 keep separate owners. Preserve Btu/h capacity and W
  power input handling, product defaults, measured-point flags, defrost, region,
  cut-in/out, and lockout/range settings through their current adapters.
- HSPF2 A2/AFull rated cooling capacity is a common scalar setting, not another
  candidate axis. Triple Northern declares ten point names, but H2Low is always
  excluded by the current application policy. H3Low is required when the low
  range reaches 37 °F or below; H2Boost follows its measured flag. Thus the
  maximum is **nine active pairs**, and the probed default has eight. Reuse
  `triple_h3_low_required()` and the existing optional-point policy.
- Brazil calls the composite capability once per combination. Rank by its
  public `three_point_exact_cspf`; retain two-point CSPF and Rule/Final outcomes.
  A Rule/Final NG is distinct from an execution failure and remains rankable.

## 3. Architecture and reuse boundary

| Responsibility | Owner / implementation direction |
| --- | --- |
| Formula, physical constraints, derived points, standard validation | Existing `core/calculators` engines, profiles, and config owners |
| Text parsing, units, optional-point resolution, request assembly, numeric result projection | Existing standard-specific `apps/calculator/application/` owners, extended with shared internal seams where necessary |
| Candidate/session model, count policy, run snapshot, iteration, error isolation, ranking | New toolkit-free `apps/calculator/application/combinations/` feature package |
| Widgets, page projection, event forwarding, Tk scheduling, dialog lifecycle, clipboard/file picker | New `apps/calculator/ui/combinations/`, consuming shared UI foundations |
| CSV row projection vs actual file I/O | Separate pure export-format adapter under `ui/combinations/`; existing UI export adapter writes the file |

Application dependency flow is UI → combination service → standard application
adapter → `execute_standard_calculation()`. Use typed requests from
[`requests.py`](../../core/calculators/capability/requests.py). The combination
service accepts an executor/adapter seam for tests; it never imports Tkinter,
UI table schemas, or filesystem dialogs.

Concrete reuse points:

- Standard application owners: `iso_iseer_2point/`, `hong_kong_cspf/`,
  `hong_kong_hspf/`, `saso_t3/`, `brazil_cspf/`, `korea/`, `en14825/`, `ahri_m/`,
  and `ahri/` under `apps/calculator/application/`. Several usecases return
  formatted strings. Extract their shared request construction/numeric mapping
  as needed and retain the existing presentation return contract. Do not parse
  displayed numbers back into scores or copy their standard rules into the UI.
- `core/calculators/adapters/result_adapter.py` currently normalizes a limited
  profile set; `ranking_adapter.py` builds a single ranking candidate envelope.
  Neither is an all-standards combination runner. Reuse compatible projections;
  do not expand an ML/persisted contract solely to store UI session data.
- Editable candidates reuse `ui/batch/case_table.py`, `ui/batch/models.py`,
  `ui/table/controller.py`, `ui/table/surface.py`, and shared visual policy where
  their shape fits. `BatchProfileSpec` requires an input column, so do not force
  read-only results through it using a fake editable column.
- Existing `ui/batch/controller.py` is synchronous and table-bound. A separate
  combination service is justified by lazy enumeration, pinned session state,
  cancellation, and reuse without widgets. Keep its existing callers intact.
- Use `ui/batch_dialogs/dialog_handle.py` and `shell.py` for open/focus/close and
  geometry. The shell's current snapshot annotation is `list[dict[str, str]]`;
  a typed combination session must not be squeezed into fake rows. Use a small
  compatible generic snapshot seam or an adapter over an external session store.
- Large ranked collections use the scrollable Treeview family and
  `ui/table/treeview_style.py`, with paging. `compact_result_grid.py` is for small
  fixed results and whole-table copy; it is not a large ranking table.
- `ui/table_csv_export.py` already owns UTF-8-BOM CSV writing and file picking.
  Pure application code must not import that Tk-bound module. CSV column names,
  ordering, and schema version belong to the export adapter, not the engine or
  application result model; the export projection itself needs no widgets/I/O.

Follow the [architecture boundary](../architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md)
and [table-family design](2026-07-12-calculator-table-architecture-design.md).
Keep new responsibilities within feature packages, including a focused test
package such as `tests/apps/calculator/combinations/`. Exact filenames/classes
are implementation choices; do not build a generic job framework or one adapter
class per trivial field. Do not put new feature files flat in broad directories.

## 4. Data contracts and ranking

These are internal feature contracts, not additions to public calculator JSON.

| Concept | Required information |
| --- | --- |
| Candidate draft | Stable candidate ID, user test label, inclusion flag, raw capacity/power text, cell issues; numeric values after validation |
| Point definition/pool | Stable point key, labels/units, ordered candidate IDs, required/optional/mapped/inactive role, mapping source if applicable |
| Common context | Capability/profile/metric identity, climate/product/system type, fixed inputs/options, score basis, unit interpretation |
| Run snapshot | Run ID, input revision, immutable context and candidate values/order, resolved point roles, planned count |
| Combination identity | Deterministic enumeration ordinal plus selected point→candidate IDs; labels and visible row numbers are not identity |
| Result summary | Combination identity, numeric score/basis/units, available raw/published values, execution status/error, standard-specific summary/Rule outcomes |
| Session | Draft, current run snapshot, progress counters, lightweight result summaries, stale flag; view selection/page state is separate |

- Unused fully blank placeholder rows do not become candidates. A partially
  entered included row is incomplete and blocks Calculate; report point/row/cell.
  Excluded rows may retain invalid drafts. Each active independent point needs at
  least one included complete candidate. Zero/non-finite/negative measurements
  receive the applicable existing validation, never silent removal or coercion.
- Identical measurements with different candidate IDs remain distinct tests.
- Count the product of included candidate counts before constructing requests.
  Enforce the same 10,000 limit in the application service, including direct
  headless calls. Any zero pool blocks execution; all single-candidate pools
  produce exactly one combination. Point count alone is not a limit.
- Sort descending by the actual numeric metric returned by the existing
  contract, never a formatted cell. Default to the normal reported/public metric;
  offer Raw/Published selection only when the current result exposes both, with
  the basis visible and pinned. Do not invent unavailable extra precision.
  ISO public results may already be rounded; preserve that precision.
- Equal numeric scores receive competition ranks (`1, 1, 3`) and deterministic
  enumeration order. Do not secretly break a Published-score tie using Raw.
  Error rows have no rank and follow successful rows in enumeration order.
- Retain candidate values and common context once per run plus O(combinations)
  compact summaries/selection references. Discard per-combination bin details
  after projection. Detail viewing rebuilds the request from the run snapshot
  and recalculates on demand through the same adapter/gateway, with a bounded
  cache if needed. Never read live edits when replaying an old result.

## 5. Run lifecycle, responsiveness, and stale data

1. On Calculate, commit the active editor using the table contract, validate
   included candidates/common inputs, resolve point policy, and check the count.
   A failed preflight leaves the previous run intact and makes no engine calls.
2. Freeze a new run snapshot and render progress before executing. Lock input,
   inclusion, context, and Calculate controls for that dialog while running.
3. Enumerate lazily with `itertools.product` or equivalent. The pure runner
   exposes bounded stepping; a Tk adapter schedules short chunks with `after()`.
   Check cancellation between cases and return control frequently. Start with a
   roughly 10–20 ms chunk budget and verify actual responsiveness; it is not a
   whole-run wall-clock assertion. Do not run a 10,000-case loop in one callback.
4. Per-combination domain/request errors create error rows and allow subsequent
   cases to run. Unexpected orchestration failures settle the run as failed,
   preserve completed rows, and release controls/callbacks. No blank success.
5. Settle as completed, completed-with-errors, cancelled, or failed. Counts expose
   planned/processed/succeeded/failed, where processed = succeeded + failed.
   On cancellation, rank completed successes as **partial results**, not a
   claimed global optimum. A cancelled run restarts from a new snapshot; resume
   checkpoints are not required.
6. Any later candidate/context/inclusion change marks the result stale. Keep its
   run provenance available; stale detail/export uses old pinned inputs and is
   labelled accordingly. Do not blend new inputs into old rows.

One active run per combination session is sufficient. Guard scheduled callbacks
with run/session identity, cancel pending callbacks on disposal, and ignore late
callbacks from a previous run. UI-only paging/selection does not stale a result.
Persistent jobs, multiprocessing, database storage, and background service APIs
are unnecessary for this limit.

## 6. UI and dialog behavior

- Add **조합 계산** beside the current Batch/action controls for every supported
  section. Open a modeless shared dialog, or focus its existing instance.
- Top: standard/profile/metric identity and common settings. Initialize from the
  invoking section; ISO/ISEER and other comparison surfaces expose an explicit
  ranking context selector. Reuse existing standard field definitions/defaults.
  On first open, seed each point with the invoking section's current measurement
  where present, preserving incomplete drafts instead of inventing sample data.
- Middle: point list with included/total counts and validation status; selecting
  a point shows its candidate grid. Columns: inclusion, test label, Capacity
  `[unit]`, Power `[W]`, optional read-only EER/COP, validation status. One test is
  one row. Provide row add/remove and selected-row include/exclude actions.
  Auto/mapped/inactive points show their source/status and cannot be edited.
- Show the count expression, e.g. `STD 3 × HALF 5 = 15 / 10,000`. Above the cap,
  disable Calculate and explain that candidates must be excluded or a point
  fixed to one candidate. Validate again on the application boundary.
- Bottom: Calculate/Cancel, progress and summary, ranked read-only results,
  selected-result detail, and **전체 결과 CSV 저장**. Result columns contain rank,
  metric/units/basis, selected test labels per point, and status. Candidate values
  and fixed settings remain inspectable through detail/export.
- Default result page size: 100. Export covers the whole run, not the visible
  page. Bound editable candidate rendering too; a legal 10,000×1 run must not
  create 10,000 Entry rows. Keep all drafts in the model and project a bounded
  page. Candidate input paging is a view concern, not a smaller candidate limit.
- Candidate grids use shared rectangular selection, TSV copy/paste, grouped
  edit/paste/clear undo, keyboard navigation, and read-only mutation protection.
  Scope paste to the visible page under the existing overflow rules and make
  that page boundary visible. Grow rows only within that bounded projection;
  never silently move overflow into another point/context. A page/point switch
  settles editing and resets page-local undo so it cannot affect different rows.
- Result tables support row selection, keyboard navigation, and selected-row TSV
  copy with read-only enforcement, per the scrollable-data family. Preserve
  selection by combination ID across safe refreshes. Shared table behavior and
  visuals belong in shared owners, not copied per standard.
- Preserve draft/results when closing and reopening within the application
  session. Keep the session outside disposable widgets and keyed by originating
  context. Reopening does not silently reload the parent inputs; provide an
  explicit reload/reset action. Switching standard/profile/climate/product or
  measurement mode stores the prior draft and selects a separate session; it
  does not relabel old pools. Editing common scalar values within that session
  retains the pools and marks its prior result stale.
- Closing a running dialog explicitly requests cancellation, settles partial
  state, then disposes callbacks/widgets and retains the session snapshot.
  Root shutdown disposes remaining runners. Merely hiding/repainting does not
  imply cancellation. Reuse existing geometry/focus helpers and visual tokens.

The [spreadsheet contract](../ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md) and
[Tkinter adapter](../ui_ux/adapters/TKINTER_TABLE_ADAPTER.md) govern interactions.
Current shared-controller gaps include no disjoint Ctrl selection, selection-mode
Esc retaining selection, and no separate double-click edit entry. Preserve the
documented temporary binding, report inherited gaps, and do not claim complete
Excel parity or expand this feature into a global table overhaul.

## 7. CSV contract

New combination export schema `calculator_combinations_v1`: UTF-8 with BOM,
standard CSV quoting, one processed combination per row in displayed rank order.
Completed runs include all successful and failed combinations. Cancelled/failed
runs export only processed rows and explicitly identify partial coverage.

Required fields:

- `schema_version`, `run_id`, `run_status`, `input_revision`, `stale`,
  `planned_count`, `processed_count`;
- `combination_id`, `rank`, `calculation_status`, `error_code`, `error_message`;
- capability/profile/metric, climate/product/system type when applicable,
  `score_basis`, `score`, `score_units`, and available raw/published metrics;
- one stable point-prefixed set of candidate ID, test label, numeric capacity,
  power, and unit fields per independent point;
- standard summary/Rule/Final fields where applicable, and deterministic
  `context_json` for fixed inputs/options and resolved point-source metadata.

Do not export formatted placeholders as numeric values or put bin traces in
every row. Auto-derived points are identified by policy/source metadata, not
invented candidate IDs. Export values must match the pinned run and numeric
ranking. Round-trip tests cover Unicode, commas/newlines in labels, ties, errors,
stale/partial runs, and all pages. File-picker cancel is a no-op; write failures
remain visible without destroying results. The new export is not a session
import/persistence format and does not modify existing CSV schemas.

## 8. Required verification and completion criteria

| Area | Required evidence |
| --- | --- |
| Enumeration and pair integrity | STD 3 × HALF 5 = 15 unique selections; capacity/power stay paired; duplicate-valued test IDs remain distinct; inputs are not mutated |
| Limit | 0/1/10,000/10,001 cases; 10^8 projected cases rejected before engine invocation; fixed/mapped/inactive axes counted correctly; direct service guard |
| Coverage | Every row of §2 through the real application adapter and gateway; every exposed profile/product, EN climate, and relevant optional-point branch |
| Numerical compatibility | Each synthetic combination equals a separately invoked existing single calculation with the same typed request/context; current golden suites remain unchanged |
| Ranking | Numeric order, current precision, competition ties/stable identity, explicit Raw/Published basis, no mixed contexts, Brazil NG distinct from error |
| Validation and isolation | Incomplete included candidate blocks preflight; excluded invalid candidate does not; non-finite/zero inputs handled; one combination error followed by valid success |
| Lifecycle | Cancel before first case and mid-run; completed-with-errors; unexpected failure; edit→stale; rerun isolation; close/reopen; parent context switch/disposal; no late callback writes |
| Table/UI | Rectangular/single-column paste, grouped undo, navigation, invalid draft retention, inactive/read-only mutation protection, page boundaries and stable selection |
| CSV | BOM/quoting/Unicode, all pages, errors, numeric scores and candidate values, fixed context, stale/partial provenance, write error and picker cancel |
| Integration/performance | Actual app entry → each section button → dialog → run → result/detail/export; bounded input/result widget count; visible progress/cancel during a 10,000-case run |

Add focused tests within a Calculator combination test package. Reuse nearby
fixtures and existing controller/shell tests. Run the affected calculator
application-boundary, standard golden, UI interaction, and entrypoint tests as
their owners change, then one final integrated pass. Use the repository's test
runtime/dependencies; a missing pytest environment is not passing evidence.
Do not assert the benchmark seconds below as a CI threshold. Report native
keyboard/window checks and Windows checks as unverified where not actually run.

### Existing exploratory evidence (not implementation acceptance)

At the source baseline above, a temporary stdlib probe exercised real application
adapters and `execute_standard_calculation()` using repository sample values.
Capacity stayed fixed; two point powers varied by `(0.97, 1, 1.03)` and
`(0.96, 0.98, 1, 1.02, 1.04)`. Other points/settings stayed fixed. Twelve sweeps
across eleven contexts completed 180 combinations, 180 separate gateway replays,
12 zero-power rejection/recovery checks, and a 180-row BOM CSV round trip.

| Context | Public score range observed |
| --- | --- |
| EN SEER | 8.958–9.248 |
| EN SCOP average / warmer / colder | 4.986–5.237 / 5.899–6.122 / 4.084–4.302 |
| AHRI M SEER / HSPF | 17.15–19 / 10.3–10.6 |
| M1 SEER2 variable / dual | 13.51–13.847 / 12.05–12.85 |
| M1 HSPF2 variable / dual | 6.75–6.925 / 8.2–8.3 |
| M1 HSPF2 Triple Northern | H1Full/H2Boost sweep tied at 9.75; H2Full/H3Boost sweep ranged 9.6–9.95 |

Reproduction seeds: `tests/standards_refactor/samples.py` (`EN_SEER_POINTS`,
`en_scop_points`), `tests/test_ahri_m_seer_hspf.py` (`SEER_POINTS`, `HSPF_POINTS`),
`tests/test_apps_calculator_ui_ahri_seer2.py` (`SAMPLE_VALUES`),
`tests/calculator_ui_sample_values.py` (`HSPF2_SAMPLE_VALUES`), and
`tests/test_ahri_multicapacity_2026.py` (`DUAL_SEER_POINTS`, `DUAL_HSPF_POINTS`,
`TRIPLE_POINTS`). Reuse application defaults and resolve optional points first.
The initial probe incorrectly expected inactive Triple H3Low to reach the core;
correcting the probe's expectation was necessary, with no production-code change.

Separately, four independent pools of ten candidates (power factors evenly
spaced from 0.99 to 1.01) produced 10,000 cases each, with zero errors:

| Context / varied points | Local compute | Sort |
| --- | --- | --- |
| EN SCOP colder / A,B,C,D | 3.4334 s | 0.0034 s |
| M1 HSPF2 variable / H01,H11,H1N,H2Int | 2.5525 s | 0.0031 s |
| M1 HSPF2 Triple / H0Low,H1Full,H1Low,H2Boost | 2.0361 s | 0.0017 s |

These are local headless observations with compact score retention. They exclude
GUI, CSV time, full-bin retention, and other hardware; they are neither formula
certification nor a UI performance guarantee. Temporary probe files are not
required handoff dependencies or committed acceptance tests. Convert useful
scenarios into maintainable tests of the implemented service.

## 9. Implementation slices and non-goals

1. Implement the toolkit-free candidate/session/count/run/ranking contracts and
   one ISO profile adapter. Verify pair integrity, the cap, and single-call parity.
2. Connect that path through the real app to the shared candidate/result dialog,
   progress/cancel, lifecycle, paging, and CSV. Verify the full user action path.
3. Extend the same mechanism to the remaining ISO profiles, Brazil, and KS.
4. Connect EN SEER/SCOP and all current AHRI M/M1 product branches, reusing their
   point/option owners. Verify context-specific coverage and input units.
5. Complete cross-standard regression, 10,000-case UI checks, export/detail
   provenance checks, and current-state documentation. Report remaining native
   verification gaps precisely; do not present a skipped path as complete.

These slices are implementation order, not repeated approval gates. Continue
through the agreed scope when ordinary implementation choices are reversible.
No formula rewrite, new standard, ML/Predict integration, general job system,
cross-run ranking, session-file import, XLSX export, automatic optimization,
arbitrary cap override, or global UI redesign is included.

## 10. Implementation and verification (2026-10-16)

- Application owner: `apps/calculator/application/combinations/` owns immutable
  candidate/run snapshots, preflight, a hard 10,000-case cap, lazy bounded steps,
  cancellation, per-case errors, competition ranking, and snapshot-only replay.
- Standard application owners now expose shared numeric request-building seams;
  single calculations and combinations use the same parsing, units and request
  assembly. EN requests explicitly use Tested inputs. No core engine, config,
  public result DTO, or golden fixture changed.
- UI owner: `apps/calculator/ui/combinations/` owns per-origin context sessions,
  candidate paging (100 rows), the shared spreadsheet binding, common settings,
  mode/session changes, scheduled progress, result paging (100 rows), detail,
  and pure `calculator_combinations_v1` projection. The existing CSV adapter
  retains BOM writing and file picking.
- `BatchDialogShell` accepts typed snapshots through a generic seam. The shared
  viewport gained an opt-in reserved vertical scrollbar gutter: without it,
  the stacked combination notebook reproducibly oscillated on macOS while
  opening SEER2 Dual Stage. Existing batch surfaces keep their default policy.
- `tests/apps/calculator/combinations/` covers 22 baseline contexts across all
  11 capabilities, paired 3×5 sweeps with separate gateway replays, SCOP policy,
  optional AHRI branches, raw/published values, and rankable Brazil Rule/Final
  outcomes. Real 10,000-case runs cover SCOP colder, variable HSPF2 and Triple
  Northern. Cap boundaries, excluded invalid rows, errors, cancellation, stale
  snapshots, full CSV, and request preflight are guarded separately.
- Actual `CalculatorTkApp` tests exercise all section actions through run,
  detail, export and reopen; they also cover mode/session separation, grouped
  paste/clear/undo, page overflow, a legal 10,000×1 candidate pool with bounded
  widgets, responsive progress/cancel, partial export and root disposal.
- The regression pass completed 1,313 tests with no skips; the subsequently
  strengthened feature suite completed 40 headless tests and 2 native Tk
  integration tests. Calculator regression spans standard/golden, application
  boundary, entrypoint, and shared Tk table/window tests. Native modules run in separate processes;
  new feature UI tests share one Tcl interpreter to avoid macOS Tk's known
  destroyed-root event-loop behavior.

Verification limits: native Windows, Linux desktop, OS-generated keyboard and
mouse interaction, multiple monitors and mixed DPI were not checked. The
computer-use screenshot service timed out, so no visual screenshot acceptance
is claimed. The existing shared-controller gaps (disjoint Ctrl selection,
selection-mode Esc, and dedicated double-click edit entry) remain inherited,
not claims of full Excel parity. File picker cancel and write errors were
exercised through the adapter seam, not a native OS save-panel interaction.

The existing Native Windows workstream and held Predict integration remain
independent; this implementation does not close or expand either workstream.
