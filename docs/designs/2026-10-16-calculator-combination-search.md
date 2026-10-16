# Calculator Combination Search — Implementation Specification

**Status:** Implemented for all current paths, including the confirmed candidate-column UI (§6.1); verification limits are listed in §10.
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
- Editable candidates reuse `MetricInputTable`, `ui/table/controller.py`,
  `ui/table/surface.py`, batch viewport and shared visual policy. The batch
  matrix's complete-case model does not represent independent point pools;
  a feature-local candidate-column adapter projects those existing pools.
  Common settings retain `ui/batch/case_table.py`. Read-only results do not
  acquire a fake editable column to fit an input schema.
- Existing `ui/batch/controller.py` is synchronous and table-bound. A separate
  combination service is justified by lazy enumeration, pinned session state,
  cancellation, and reuse without widgets. Keep its existing callers intact.
- Use `ui/batch_dialogs/dialog_handle.py` and `shell.py` for open/focus/close and
  geometry. The shell's current snapshot annotation is `list[dict[str, str]]`;
  a typed combination session must not be squeezed into fake rows. Use a small
  compatible generic snapshot seam or an adapter over an external session store.
- Ranked results use a feature-local read-only page adapter over
  `compact_result_grid.py`, `TkTableController` and `BatchTableViewport`. Only
  100 rows are rendered at once. The original Treeview choice is superseded:
  native row selection cannot provide the requested rectangular cell copy.
  Rendering, selection and scrolling stay with their existing shared owners.
  Refresh must reuse event bindings on existing cells: Tcl callback registrations
  must stay bounded across page changes, including temporarily hidden widgets.
  Resolve cell addresses at dispatch time and release owned callbacks on destroy.
- `ui/table_csv_export.py` already owns UTF-8-BOM CSV writing and file picking.
  Pure application code must not import that Tk-bound module. CSV column names,
  ordering, and extra-result selection belong to the export adapter, not the engine or
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
| Combination identity | Deterministic enumeration ordinal plus selected point→candidate IDs; labels and visible column numbers are not identity |
| Result summary | Combination identity, numeric score/basis/units, available raw/published values, execution status/error, standard-specific summary/Rule outcomes |
| Session | Draft, current run snapshot, progress counters, lightweight result summaries, stale flag; view selection/page state is separate |

- Unused fully blank placeholder columns do not become candidates. A partially
  entered included candidate is incomplete and blocks Calculate; report point/column/field.
  Excluded candidates may retain invalid drafts. Each active independent point needs at
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
- Middle: vertically stacked test-point blocks, each with candidate columns and
  Capacity/Power rows, as fixed in §6.1. All points share the input viewport;
  there is no point-selection dropdown. Auto/mapped/inactive blocks show their
  source/status and cannot be edited.
- Show the count expression, e.g. `STD 3 × HALF 5 = 15 / 10,000`. Above the cap,
  disable Calculate and explain that candidates must be excluded or a point
  fixed to one candidate. Validate again on the application boundary.
- Bottom: Calculate/Cancel, progress and summary, ranked read-only results,
  selected-result detail, and **전체 결과 CSV 저장**. Result columns contain rank,
  metric/units/basis, selected test labels per point, and status. Candidate values
  remain inspectable through detail/export; fixed settings remain in detail.
- Default result page size: 100. Export covers the whole run, not the visible
  page. Bound editable candidate rendering too; a legal 10,000×1 run must not
  create 10,000 Entry columns. Keep all drafts in the model and project a bounded
  page. Candidate input paging is a view concern, not a smaller candidate limit.
- Candidate grids use shared rectangular selection, TSV copy/paste, grouped
  edit/paste/clear undo, keyboard navigation, and read-only mutation protection.
  Scope paste to the visible page under the existing overflow rules and make
  that page boundary visible. Grow columns only within that bounded projection;
  never silently move overflow into another point/context. A page switch
  settles editing and resets page-local undo so it cannot affect different candidates.
- Result tables support rectangular cell drag selection, keyboard navigation,
  Ctrl/Cmd+C and an explicit selected-range copy action, with read-only enforcement.
  Preserve selection by combination ID/column and scroll across unchanged refreshes;
  reset selection when moving to a page without those results. Shared table behavior and
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

### 6.1 Confirmed candidate-column revision (2026-10-16)

The user confirmed this layout after reviewing the first implementation. This
supersedes the original point-selector / candidate-per-row UI, including its
later row-height adjustment. It applies to every standard/profile/product.

```text
STD              #1       #2       #3       ...
Capacity [W]     3600     3700     3800
Power [W]         900      920      950

HALF             #1       #2       ...
Capacity [W]     1800     1900
Power [W]         400      420
```

- Each point has its own candidate count and numbering. One column is one
  stable candidate ID and a complete capacity/power pair. STD #1 and HALF #1
  are independent choices, not a pre-paired case. Three by two gives six runs.
- Results show the original candidate column as `#n`, followed by its test name
  when supplied. Pin that number before exclusions so the result table/detail can identify
  the source column even after later input edits or deletions.
- Keep both measurement rows adjacent. Candidate names remain editable through
  an optional test-information row; inclusion and validation appear in column
  headers and block summaries. Add/delete/include/exclude act on whole selected
  candidate columns within that block. A header click selects the whole pair.
- Default blocks expose the two measurement rows together, without selecting a
  point first. Many points scroll vertically in one contained input viewport;
  candidate columns scroll horizontally. Common settings/options stay separate.
- Put each test-point name (e.g. STD/HALF) in the table's top-left corner cell.
  Show valid/total counts with the candidate-range/page caption below the table;
  place column actions below that caption. Page controls are labelled 이전 페이지
  and 다음 페이지 because each step changes a 100-column page.
- Select calculation profiles/climates/products through explicit top tabs, not
  an unlabeled dropdown. Tab switches preserve the window geometry and each
  session's draft/results; other tabs are disabled during a run. Option variants
  with the same base title receive distinct setting numbers, with exact flags
  in 실행 옵션. The main-input reload action is labelled 메인 입력으로 초기화,
  explains that the current tab's candidates/results are reset, and is disabled
  when no matching context exists in the invoking main section.
- Paste a 2×N TSV rectangle starting at Capacity #1 without transposition.
  Pasting grows candidate columns within a bounded 100-column page. Overflow
  never writes to the next point, metadata row, or next page. Invalid included
  drafts remain visible; excluded invalid drafts remain retained. One paste or
  clear is one undo operation; pair identities survive edits and undo.
- Each point pages independently by 100 columns; full pools remain in session
  state, including a legal 10,000×1 input. Page changes reset that block's undo
  history and preserve other blocks. Ordinary edits preserve selection/scroll.
- Preserve the existing runner, active-point resolution, 10,000 limit, ranking,
  progress/cancel, stale/partial provenance, CSV and pinned detail contracts.
  Do not transpose the existing batch complete-case model or alter its behavior.
- Verify paired paste/copy/undo, column actions, page boundaries, inactive points,
  close/reopen and all existing actual section entry paths. Inspect ISO's two
  blocks visually and exercise many-point/resize paths with native Tk tests.

## 7. CSV contract

The user-approved concise export replaces the initial metadata-heavy
`calculator_combinations_v1` projection. UTF-8 with BOM and standard CSV quoting
remain unchanged. Export every processed combination in numeric rank order,
including errors, across all pages.

Columns, in order:

- `순위`, `값`, `지표`;
- each independent test point's `성능 [capacity unit]` and `전력 [W]`, in point
  order, using the run's selected capacity/power pair (`STD`, `HALF` for ISO);
- available standard-specific additional results: cooling/energy totals for
  ISO/HK/KS/SASO; Brazil Two Point/Rule/Final; EN SEER `seer_on`, `qc_kwh`;
  EN SCOP `scop_on`, `qh_kwh`, active/standby/total energy; AHRI M seasonal
  load/energy sums; M1 EER2 values and canonical load/energy totals;
- a single `오류` column only when the run has failed combinations. Failed rows
  retain their test pairs and metric, with blank rank/value/additional results.

Do not include run IDs, candidate IDs/numbers/names, revisions, repeated context,
JSON, duplicate metric aliases, interpolation coefficients or bin traces.
Use stored score summaries and immutable run inputs without recalculation.
Input units are in headers, not repeated columns. Fixed settings, source policy,
original candidate numbers and full provenance remain available in detail.

Cancelled/failed runs export only processed rows. The screen and proposed
filename explicitly distinguish `_partial` and `_stale`, independently; a
non-public score basis adds `_raw` or `_published` to the filename. Metadata is
not repeated on every row. Users can rename the file in the save dialog.

Round-trip tests cover BOM, Unicode/CSV quoting in errors, all pages, original
pairs after input edits, and additional fields for every supported context.
Picker cancel is a no-op; write failures preserve results. This is a result
export, not an import/session archive, and other CSV contracts are unchanged.

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
| CSV | BOM/quoting/Unicode, all pages, errors, numeric scores and candidate values, per-standard additional results, stale/partial filename, pinned detail context, write error and picker cancel |
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
  candidate paging (100 columns per point), the shared spreadsheet binding, common settings,
  mode/session changes, scheduled progress, result paging (100 rows), detail,
  and a pure CSV projection (revised to the concise §7 contract). The existing CSV adapter
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
  strengthened feature suite completed 43 headless tests and 2 native Tk
  integration tests. Calculator regression spans standard/golden, application
  boundary, entrypoint, and shared Tk table/window tests. Native modules run in separate processes;
  new feature UI tests share one Tcl interpreter to avoid macOS Tk's known
  destroyed-root event-loop behavior.
- A follow-up macOS screenshot review found that the initial candidate viewport
  showed only one or two rows. The first layout correction used a proportional
  2:1 allocation independent of candidate count, with a 480-pixel minimum dialog
  height. The corrected ISO completion screen was visually inspected. All 3
  native integration tests passed, including resize checks for at least 5 input
  rows at 640×590, 8 at 800×720, and 3 at 640×480, with result rows and action
  buttons remaining visible. The row-based layout and row-count acceptance were
  subsequently superseded by §6.1.
- Candidate-column revision: `candidate_columns.py` projects bounded pool pages
  through `MetricInputTable` and the shared controller; `candidate_block.py`
  owns point-level column actions; `candidates.py` composes all blocks in the
  existing batch viewport. No shared table/window behavior or calculation owner
  was modified. A small controller extension guards measurement-paste metadata
  boundaries and preserves undo history while input is locked.
- Follow-up verification: 43 headless feature tests and 4 native Tk integration
  tests passed. These cover all 22 baseline contexts, 3×5 pair paste/run, optional
  names, whole-column inclusion/deletion, IDs/undo, page boundaries, independent
  point pages, unchanged-widget selection/scroll retention, 10,000×1 bounded
  rendering/cancel, resize, root disposal, detail/CSV and source reopen. A real
  Triple Northern common-setting edit switches H3Low inactive→active→inactive
  while retaining its pool. The many-point viewport reaches the last block.
- Shared metric/batch/controller/dialog regression: 170 tests passed across 14
  modules. A macOS screenshot confirmed STD 3 candidate columns and HALF 5
  candidate columns together, both Capacity/Power rows, the 15-case completion
  count, ranking and action buttons.
- Header/control revision: point names now use the metric grid's optional corner
  label (blank by default for existing callers). Counts and column controls sit
  below each table. Context tabs replace the dropdown; the batch shell can swap
  session content without replacing or repositioning its window. Main-input
  reload is explicitly labelled as resetting the current tab's candidates and
  results. Five native combination tests and 90 focused shared table/window
  regression tests passed; macOS ISO screenshots confirmed the new arrangement.
- Main integration review corrected unnamed result candidates showing internal
  ID prefixes: results now show their pinned column numbers, with optional test
  names; the initial CSV also included those numbers (superseded by §7). Excluded columns and later input
  deletion retain the original run's numbering. The focused feature/application
  boundary suite passed 65 tests, and all 4 native Tk integration tests passed.
  A fresh macOS ISO 3×5 completion screenshot confirmed the numbered results.

- Result-copy/export revision: the bounded result page now adapts the shared
  cell renderer, viewport and rectangular controller. Dragging selects cells;
  Ctrl/Cmd+C or the copy button exports only that rectangle. Data stays read-only,
  unchanged refreshes retain selection/scroll, and page changes clear selections
  absent from the new page. The concise CSV contract in §7 replaces metadata
  columns while retaining pinned measurements and stored additional results.
  Verification passed 68 headless combination tests, 21 application boundary
  tests, 6 native Tk integration tests and 30 shared controller/viewport checks.
  The native tests include generated drag/key events, reverse selection,
  read-only mutation protection, 101-result paging, all 22 baseline contexts,
  partial/stale export, picker cancel, write failure and root disposal.
  At the minimum 640×480 size one full result row remains visible; normal sizes
  show more rows, with the remainder scrollable. A fresh macOS ISO 3×5 screenshot
  confirmed the shared result-cell layout and copy/detail/CSV buttons.

- Result-rendering resource correction: repeated controller refreshes previously
  replaced Tk binding scripts but retained their registered Python/Tcl callbacks.
  Ten ISO page changes grew interpreter commands from 51,428 to 531,428 and the
  measured process peak from about 276 to 708 MiB. The controller now tracks bound
  widgets weakly, registers once per live widget, and resolves the current address
  at event dispatch. Hidden/reused cells retain bindings without retaining dead
  widgets. Existing selection, edit and read-only policies remain authoritative.
  After correction the same 10,000-result ISO probe retained 53,028 commands;
  process peak stayed near 279 MiB. Mean page transition fell from about 250 to
  94 ms; an eight-point HSPF2/14-column probe fell from 487 to 208 ms.
  These are local macOS/Python 3.14/Tk 8.6 observations, not platform guarantees.
  ISO first rendering remained approximately 0.5 seconds for both 100 and 10,000
  results: the table creates at most 100 rows, while only data/ranking spans the run.
  Regression covers all 100 pages of a real 10,000-result run with nine independent
  points (15 result columns), fixed widget/command counts, selection/copy after
  paging and callback release on close. Seven feature UI tests and 101 focused
  controller/input/caller checks passed. No formula, result or CSV schema changed.

Verification limits: native Windows, Linux desktop, OS-generated keyboard and
mouse interaction, multiple monitors and mixed DPI were not checked. The
initial screenshot attempt timed out; the follow-up inspected the ISO candidate
and completed-ranking screen only, not every profile or the detail dialog.
The existing shared-controller gaps (disjoint Ctrl selection,
selection-mode Esc, and dedicated double-click edit entry) remain inherited,
not claims of full Excel parity. File picker cancel and write errors were
exercised through the adapter seam, not a native OS save-panel interaction.

The existing Native Windows workstream and held Predict integration remain
independent; this implementation does not close or expand either workstream.
