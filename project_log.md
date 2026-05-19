# Project Log
이 문서는 작업 과정의 시도, 실패, 성공, 중요 결정사항 및 반복 방지를 위한 기록용입니다.

## 2026-05-19 — ISO16358-2 HSPF -7_ext fix + golden update

### Tried
- 099에서 `_iso_hspf_extended_minus7_default()`의 -7_ext default factor 적용
  대상을 정정 (2°C frost → 2°C non-frost ×1.12/×1.06 → -7°C ×0.734/×0.877
  2-step).
- 100에서 ISO16358-2 HSPF official exact 16-case fixture expected를 원문
  audit + 099 기준값으로 갱신하고 `XFAIL_CASE_IDS`를 빈 frozenset으로 정리.

### Result
- case 3/4/9/10/11이 099 fix만으로 자연 pass.
- case 8/12/13/14/15/16의 expected를 원문 audit 기준값으로 갱신해 16/16 case
  모두 pass.
- frost trace / boundary COP / extended default focused test 그대로 pass.
- full suite: 425 passed, 4 skipped, 23 xfailed (XPASS strict 실패 0).

### Failed-Risk
- 091 시점에서는 case 12/15/16 large Δ를 external reference script의 frost/
  non-frost 동일 주입 해석 오류로 추정했으나, 원문 audit 결과 repo 구현이
  frost endpoint 정책 / -7 multi-measured / Formula 50 적용 / saturated 모두
  원문 준수임이 확인됐고, 실제 원인은 -7_ext default factor 적용 대상 오류
  (099) 였음.

### Decision
- ISO16358-2 HSPF 16-case mismatch hold 상태는 종료.
- official exact fixture expected는 원문 audit + 099 fix 기준값을 single
  source of truth로 둔다.
- 잔여 follow-up은 ISO table UI / TSV / unit adapter / ML 복귀 순으로 진행.

### Lesson
- factor 자체의 출처가 맞아도 적용 대상 (frost vs non-frost) 이 어긋나면
  대표적인 case에서 큰 mismatch가 발생한다. 0.734/0.877 같은 derived factor를
  볼 때는 derivation 시점의 baseline (여기서는 2°C non-frost) 을 항상 함께
  점검한다.

## 2026-05-18 — ISO16358-2 HSPF reference diagnostic hold

### Tried
- 083 diagnostic의 16-case mismatch 원인을 부분 점검함.
- bin_hours, total bin hours, HSTL expected, fixture 입력, repo의 measured
  `2_full` / `2_half` → frost reference point `2_full_f` / `2_half_f` 보존
  동작을 ISO16358-2 규격 원문 해석에 비추어 확인함.
- 사용자가 비교 기준으로 사용한 external reference script의 입력 처리
  방식도 함께 확인함.

### Result
- bin_hours는 ISO16358-2 default bin과 일치하고, total bin hours는 2866 h로
  확인됨.
- HSTL expected 4885.4 kWh는 맞는 값으로 확인됨.
- repo fixture와 external reference script의 입력 fixture는 동일함.
- repo fixture의 measured `2_full` → `2_full_f`, `2_half` → `2_half_f` 매핑은
  ISO16358-2 frost reference point 처리상 정상으로 확인됨.
- repo calculator는 measured `2_full` / `2_half`를 frost reference point인
  `2_full_f` / `2_half_f`로 보존하고, non-frost `2_full` / `2_half`는 -7~7 line
  계산값으로 유지한다. 현재 규격 원문 해석상 이 방식이 맞는 것으로 판단됨.
- external reference script는 measured `2_full`을 `2_full`과 `2_full_f` 모두에
  동일하게 넣고 `2_half`도 동일하게 처리한 것으로 확인됨.

### Failed-Risk
- 083 report의 "official exact" 표현이 사실상 single external reference 결과를
  authority로 취급할 위험이 있어, 후속 작업이 reference script 출력에 맞춰
  repo 계산식을 임의로 수정하는 방향으로 흘러갈 수 있음.

### Decision
- ISO16358-2 HSPF 16-case mismatch는 hold 상태로 둔다.
- `core/calculator_iso16358.py`, `tests/fixtures/iso16358_hspf_official_exact_cases.json`,
  `tests/test_iso16358_hspf_official_exact_golden.py`, expected 값, xfail
  목록은 이번 작업에서 수정하지 않는다.
- case 12/15/16의 큰 mismatch는 repo calculator bug보다 external reference
  script의 frost/non-frost 동일 주입 해석 오류 가능성이 크다고 본다.
- 나머지 mismatch case는 사용자가 별도 분석 중이므로 hold한다.
- 083 report는 historical diagnostic snapshot으로 다루고, 정정/보류 상태는
  091 신규 report에 명시한다.

### Lesson
- single external reference script 결과를 "official exact" authority로 굳히지
  않는다. 비교 기준은 규격 원문 + repo calculator + external script의 입력
  해석을 모두 evidence로 보고, calculator 변경은 명시적 standard decision이
  있을 때만 진행한다.
- frost reference point (`2_full_f` / `2_half_f`)와 non-frost line (`2_full`
  / `2_half`)을 동일 measured 값으로 채우면 frost/non-frost 분리가 무너진다
  — reference 비교 도구가 이 분리를 따르는지 먼저 확인해야 한다.

---

## 2026-05-17 — ISO16358-2 HSPF official exact golden verification

### Tried
- 사용자가 제공한 ISO16358-2 HSPF 공식 원문 exact expected 16개 case를
  현행 `core/calculator_iso16358.py` public schema에 맞춰 diagnostic golden
  fixture/test로 추가함.
- `2_full_f` / `2_half_f` measured 조건은 현행 입력 schema의 `2_full` /
  `2_half` measured point로 매핑했고, `-7_*` measured/default 조건은 optional
  input 포함/제외 경로로 검증함.
- case #13/#14의 중복 설명과 동일 expected는 임의 해석 없이 그대로 보존함.

### Result
- 현재 계산기 actual 기준 16개 중 5개 case가 expected와 rounded match:
  case 1, 2, 5, 6, 7.
- 11개 case는 mismatch:
  case 3, 4, 8, 9, 10, 11, 12, 13, 14, 15, 16.
- 신규 테스트는 mismatch case를 `xfail(strict=True)`로 보존하여 전체 pytest를
  깨뜨리지 않는 active diagnostic anchor로 동작함.

### Failed-Risk
- 공식 원문 exact expected 기준의 active passing golden anchor는 아직 확보되지
  않았음.
- 큰 delta는 `2_full` / `2_half` measured frost/extended 경로가 포함된 case
  12, 15, 16에서 집중되고, 나머지는 extended mode 및 `-7_*` measured/default
  조합에서 소규모 delta가 발생함.

### Decision
- 이번 작업에서는 expected 값과 `core/calculator_iso16358.py` 계산식을 수정하지
  않는다.
- mismatch 분석을 다음 blocking task로 두고, calculator table-input UI design
  audit / UI redesign / table-input 구현은 mismatch 분석 뒤로 둔다.

### Lesson
- 공식 원문 exact expected 기준과 현재 계산기 actual 검증 결과는 문서와 report에서
  명확히 분리해야 한다.
- 현행 public schema에서 measured `2_full_f` / `2_half_f`는 입력 key
  `2_full` / `2_half`를 통해 resolver가 `_f` reference point로 보존한다.

---

## 2026-05-17 — Audit 5 next actions completion (074 ~ 080)

### Result
- audit_5의 6개 next action을 단계별 source/report 분리 커밋으로 완료함.
  최종 reference report는 `reference_files/audit_5_next_actions_completion.md`.
- 074: active 문서 (`project_log.md`, `docs/WORK_PLAN.md`,
  `project_brief.md`) 를 audit_4 completion 상태로 동기화.
- 075: `CalculatorInputEnvelope` shape을 design doc과 정렬.
  `{calculator_profile_id, standard, region, mode, metric, measured_inputs,
  options}` 구조로 잠그고 source vocabulary는
  `manual_candidate / ml_prediction / fixture` 로 고정. `measured_inputs`는
  dict, extra key는 fail-fast. `measured_inputs_as_test_points()` helper로
  calculator public API 보존.
- 076: `en14825_seer` profile 추가 (SCOP config 재사용). EN tab은 metric-aware
  로 `calculate_seer` / `calculate_scop` 분기. SCOP 경로 동작은 변경 없음.
- 077: AHRI HP 모드 + SEER2 + HSPF2 v3 결과가 result label에 함께 출력되는
  happy-path smoke 추가.
- 078: `core/calculator_prediction_adapter.py` 신설 — AHRI SEER2 한정
  `PredictedPointsEnvelope` validator/helper + CalculatorInputEnvelope 변환.
  단위 변환은 의도적으로 envelope 밖.
- 079: `core/calculator_ranking_adapter.py` 신설 — CalculatorResultEnvelope →
  RankingCandidateEnvelope 최소 smoke (score 기본값은 metric value).

### Decision
- Envelope adapter chain `PredictedPoints → CalculatorInput →
  CalculatorResult → RankingCandidate`는 모두 adapter-owned이고 calculator
  public API와 region config 의미는 변경하지 않는다.
- 단위 변환은 adapter chain 안에 포함하지 않는다. caller가 일관된 단위
  (AHRI SEER2: Btu/h capacity, W power) 로 미리 정규화해야 한다.
- 첫 slice는 `ahri_usa_seer2` profile 단일 지원. EN / KS / ISO profile
  확장은 후속 slice로 분리한다.
- RankingCandidateEnvelope은 `raw_result` / `diagnostics`를 노출하지 않는다.
  ranking layer는 envelope fields만 소비한다.
- EN14825 SEER profile은 SCOP의 region config JSON을 재사용한다 (SEER
  path가 SCOP 정적 키를 읽지 않음).

### Verification
- `python3 -B -m pytest -q` → `364 passed, 23 xfailed`.
- Source commits: `3acc966, 614dfd6, 80ef665, 223192b, f4e9d84, dd283dc`.
- Report commits: `0759744, 9fe1097, 01b6909, 73180d2, 379f4e3, 754dd94,
  1704f1d`.

---

## 2026-05-17 — Audit 4 next actions completion (069 ~ 073)

### Result
- `reference_files/audit_4.md`가 제시한 4개 next action을 단계별 source/report
  분리 커밋으로 완료함. 최종 reference report는
  `reference_files/audit_4_next_actions_completion.md`에 작성.
- 069: HSPF2 UI 중복 row guard. `ui/calc_window.py`에는 실제 중복이 없었고,
  `tests/test_app_calculator_ui_smoke.py`에 회귀 방지 smoke 2건만 추가.
- 070: EN14825 UI → `calculate_scop()` 연결. EN tab에 TOL/Tbiv/p_design_h/
  climate/standby 입력을 추가하고 placeholder `calculate_en()`을 실제 SCOP
  계산 경로로 교체. standby power는 W → kW 변환을 UI 어댑터에서 수행.
- 071: `core/calculator_input_adapter.py` 신설 (AHRI SEER2 한정 첫 slice).
  Tuple/Dict 입력, Btu/h·W 단위만 허용, fail-fast로 8건 테스트.
- 072: `tests/test_calculator_schema_boundaries.py`의 banned region key 및
  adapter-owned term 가드 확장. 9개 production region config 모두 통과 확인.

### Decision
- Calculator boundary는 계속 result adapter + input adapter의 두 축으로 유지.
  ML caller 도입 전에 schema 정합성 (`source` vocabulary, envelope shape) 을
  먼저 고정하기로 한다 (다음 audit_5 task 2~3).
- region config는 정적 standard/region data로 유지하고, 모든 runtime/ML/ranking
  관련 key는 가드 테스트로 차단.

### Verification
- `python3 -B -m pytest -q` → `312 passed, 23 xfailed` (PyQt5 사용 가능 환경
  기준). PyQt5가 없는 sandbox에서는 UI smoke 7개가 skip되어 `305 passed,
  1 skipped, 23 xfailed`.
- Source commits: `e35ea2f, b673293, f7c7527, 2a3b680`.
- Report commits: `afa9e13, 798be75, 30c0d9c, 7819a50, e3f37f6`.

---

## 2026-05-17 — Calculator series reset direction

### Decision
- 기존 `core/calculator_iso16358.py`의 부분 cleanup 누적(037~043 사이클)으로는 ISO / KS / ASNZS boundary가 정렬되지 않음을 확인하고, 점진 cleanup 방향을 중단함.
- 기존 파일은 legacy/reference로 격하하고, ISO / KS / ASNZS 3개 축의 새 calculator 파일을 명확한 책임으로 재작성하기로 결정함.
  - 새 `core/calculator_iso16358.py` — ISO 16358 CSPF/HSPF common standard logic 전용.
  - `core/calculator_ks_c9306.py` — KS C 9306 전용 special calculator (`data/region_configs/korea.json` 직접 해석).
  - `core/calculator_asnzs_hspf_excel.py` — AS/NZS workbook oracle compatibility 전용 (Z-phase / 별도 compatibility phase).
- tests 정책 정정: legacy implementation behavior를 고정하는 테스트는 그대로 유지하지 않는다. 필요한 regression만 새 calculator contract 기준으로 이전하고, diagnostic / workbook-mixed 테스트는 삭제 또는 legacy/archive로 격리.
- profile resolver / dispatcher / UI 연결은 새 calculator series가 안정화된 뒤 재개.
- 상세 실행 순서는 `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md` 및 `docs/architecture/project_architecture.md` Calculator module boundary 섹션 참조.

---

## 2026-05-10 — ISO16358-2 HSPF golden provenance correction

### Result
- `tests/fixtures/iso16358_hspf_golden_fixtures.json`의 case 1~8 출처를 'ISO 16358 mode workbook golden'으로 정정함.
- 기존에 AS/NZS reference 또는 Z-phase compatibility로 분류했던 표현을 정정하고, 해당 goldens는 AS/NZS-mode가 아닌 ISO 16358-mode workbook oracle임을 명시함.
- `tests/test_iso16358_hspf_golden.py`의 xfail 사유를 GEMS/ZERL/ASNZS 대신 workbook oracle의 optional/frost/boundary routing 미구현으로 정정함.
- `docs/iso16358/iso16358_dev_notes.md`에 'ISO 16358 Workbook Golden Tolerance Calibration Plan'을 추가함.

### Decision
- Pure ISO Track A는 branch 수식 단위 검증 보조 fixture로 역할을 고정함.
- AS/NZS HSPF calculator(Z-phase) 논의는 이번 ISO 16358 workbook golden과 엄격히 분리함.
- 워크북 골든의 오차 범위를 감이 아닌 캘리브레이션 계획에 따라 체계적으로 정하기로 함.

---

## 2026-05-10 — Phase H-6: 문서 체계 재정의 및 라우터 손상 사고 기록

### Tried
- `docs/WORK_PLAN.md`를 신규 생성하여 현재 우선순위 및 실행 순서를 분리 관리.
- `docs/REFACTOR_PLAN.md`를 리팩토링 후보 및 가드레일 전용 문서로 축소.
- `project_brief.md`를 새 세션 handoff 허브로 복구하고 `WORK_PLAN` 연결 보강.
- `AGENTS.md`를 Lite가 아닌 Active Working Rules로 격상.

### Failed / Risk
- **AGENT_TASK_ROUTER.md 손상 사고**: `write_file` 도구 사용 중 파일 뒷부분 약 150라인이 유실되고 깨진 문자(`tor`)가 남는 현상 발생.
- **무승인 복구 수행**: 에이전트가 손상 발견 후 사용자 승인 없이 `git checkout` 복구 및 의도했던 `WORK_PLAN` 관련 diff 재적용을 독단적으로 수행함.

### Decision
- **Option A 선택**: 현재의 `AGENT_TASK_ROUTER.md` diff가 의도했던 문서 역할 분리(WORK_PLAN/REFACTOR_PLAN)와 일치하므로 복구 및 수정 상태를 유지하기로 함.
- **인수인계 강화**: `project_brief.md`와 `README.md`에 세션 시작 시 브리프 확인 규칙을 명시적으로 추가.

### Lesson
- **질문은 수정 승인이 아님**: 사용자의 질문이나 진단 요청을 파일 수정 승인으로 확대 해석하지 않는다.
- **복구 전 보고 필수**: 파일 손상이나 과거 오류 발견 시 즉시 보고하고 복구 방법 및 재적용 여부에 대해 승인을 받는다.
- **복구와 재적용 분리**: 시스템 파일 복구와 원래 의도했던 변경 사항 적용은 별도의 단계로 나누어 승인을 획득한다.
- **대형 문서 수정 후 검증**: `write_file` 등 대형 파일 수정 도구 사용 후에는 반드시 `tail` 또는 파일 구조 확인을 통해 뒷부분 손상 여부를 체크한다.

---

## 2026-05-10 — Phase H-2b: ISO HSPF KS oracle cycling / nonzero Cd extension 완료

### Result
- `tests/test_iso16358_hspf_ks_oracle.py`에 cycling 및 $C_d > 0$ 케이스 검증 테스트 추가 완료.
- ISO common path와 KS path가 cycling ($load < min\_capacity$) 영역에서 동일한 $PLF$ 공식을 공유함을 neutralized fixture를 통해 실증함.
- $C_d=0.35, CR=0.4$ 조건에서 $heat\_pump\_energy$가 소수점 10자리 이상 일치함을 확인.

### Decision
- **AS/NZS row-level exact reconstruction 보류**: AS/NZS Excel component row subset extraction 및 exact matching 작업은 현재 ISO16358-2 common HSPF 마무리 단계에서 제외하고, 향후 별도 호환 계산기 구현 단계인 **Z-phase**로 보류함.
- 현재 우선순위를 ISO16358-2 common HSPF 엔진 마무리 및 UI 연결로 집중함.

### Verification
- `pytest tests/test_iso16358_hspf_ks_oracle.py` -> `2 passed`.
- `pytest tests/test_iso16358_hspf_formula_micro.py` -> `7 passed`.
- 전체 테스트 `250 passed, 9 xfailed`. (AS/NZS 미구현분 xfail 유지)

---

## 2026-05-04 — Validation smoke/golden 안정화

### Result
- Validation smoke 및 golden 테스트 안정화 완료.
- Hong Kong HSPF smoke/golden validation 완료.
- 전체 테스트 기준: `109 passed`.

### Decision
- 문서 리팩토링 전 필수 코드/테스트 수정 항목은 없음.

---

## 2026-05-04 — ISO16358 초기 리버스 엔지니어링 파일 archive 이동

### Result
- 루트 디렉토리의 초기 ISO16358 reverse engineering 파일을 `docs/archive/iso16358_initial_reverse_engineering/`로 이동.
- `temporary.txt`는 로컬 scratch 파일이므로 제외.

### Verification
- `pytest tests/` → `109 passed`.

---

## 2026-05-04 — 문서 리팩토링 시작 결정

### Tried
- `project_context.md`의 역할 비대화를 검토.

### Decision
- 장기 방향은 `PROJECT_CHARTER.md`.
- 단기 상태 요약은 `project_brief.md`.
- 작업 기록은 `project_log.md`.
- 살아있는 계획은 `docs/REFACTOR_PLAN.md`.

### Lesson
- ISO16358 계열 작업에서 공통 엔진 구조보다 지역별 하드코딩을 먼저 시도해 재작업이 발생했다.
- 앞으로 Logic 수정 시 공통 엔진 / profile / config / handler 구조로 표현 가능한지 먼저 검토한다.

---

## 2026-05-04 — Calculator UI v1 기본 구조 안정화 방향 결정

### Tried
- ISO/CSPF Calculator UI를 기존 batch-first 방식에서 단건 입력 중심의 `single-input-first` 구조로 전환하는 방향을 검토함.
- `QTableView + QAbstractTableModel` 기반을 유지하며, `ProfileInputGridModel / ProfileInputGrid`를 통해 스프레드시트와 유사한 입력 UX(TSV 붙여넣기 등)를 제공하는 방안을 시도함.
- PyQt6 전환, 웹 UI 도입, `matplotlib` 또는 `pyqtgraph` 등 신규 그래프 라이브러리 추가 여부를 검토함.

### Result
- Calculator UI v1은 ISO16358/CSPF 기본 기능 안정화를 최우선으로 하기로 함.
- PyQt5를 유지하고 PyQt6 전환은 진행하지 않기로 확정함.
- `QTableView`와 `QAbstractTableModel` 기반의 아키텍처를 유지하며 `ProfileInputGrid`를 입력 표준으로 채택함.
- 신규 그래프 의존성 없이 기존 `QPainter` 기반 graph와 `QTableView` 기반 trace table을 유지함.

### Failed / Risk
- 기능이 안정되기 전에 디자인(QSS skinning, custom delegate)을 먼저 적용할 경우, 입력 모델과 계산 handler 간의 연결이 꼬이고 디버깅 리스크가 커질 위험이 확인됨.
- `matplotlib` 등 대형 라이브러리 추가 시 배포 용량 증가 및 PyInstaller 패키징 리스크가 있음.
- Core 계산 로직이나 Train/Predict UI를 동시에 수정할 경우 Calculator UI 작업 범위가 불필요하게 커지고 regression 위험이 발생할 수 있음.

### Decision
- **디자인보다 기능 우선:** "예쁜 UI"보다 "엑셀 데이터를 빠르게 붙여넣고 정확히 검산할 수 있는 엔지니어링 UI"를 우선함.
- **범위 제한:** core 계산 로직, calculator public API, Train/Predict UI는 이번 UI 작업에서 일절 건드리지 않음.
- **순차적 확장:** EN14825, AHRI210240, Korea CSPF 실제 UI 구현은 후순위로 미루고 ISO 계열부터 안정화함.
- **HSPF 공통화:** ISO16358-2 HSPF는 별도 엔진 구현 및 golden 검증을 완료한 뒤 UI profile로 연결함.
- **디자인 후순위:** 디자인 skinning은 기능 구조가 확정된 뒤 별도 턴에서 진행함.

### Lesson
- 계산기 UI의 가치는 타이핑 편의성보다 "데이터 붙여넣기(Paste)와 정확한 결과 확인"에 있음.
- UI skinning은 구조가 확정된 뒤에 수행해야 editor, selection, repaint 타이밍 이슈를 방지할 수 있음.
- 여러 규격을 동시에 구현하기보다 하나의 대표 경로(ISO16358/CSPF)를 먼저 안정화한 뒤 반복 적용하는 것이 효율적임.

---

## 2026-05-04 — V2 주요 시행착오 정리

### Tried
- V2 개발 과정에서 `QTableWidget` 사용, 모델 파일 분리 저장, `.values`를 통한 데이터 학습 등을 시도함.
- `constants.py`에 설정 로드 로직(파일 I/O)을 포함하고, `EXCLUDED_FEATURES`를 별도로 관리함.

### Result
- V3 설계의 기초가 되는 다양한 아키텍처적 교훈을 얻음.
- UI는 `QTableView`로, 모델은 통합 저장 구조로, 데이터 파이프라인은 `feature_names_in_` 보존 방식으로 개선됨.

### Failed / Risk
- **UI/UX**: `QTableWidget`과 `blockSignals` 미사용으로 인한 이벤트 루프 꼬임 및 유지보수 어려움 발생.
- **ML/Data**: `.values` 변환으로 피처 이름 정보가 소실되거나, 데이터 누수(Leakage) 관리 미흡으로 타겟별 성능 왜곡 발생.
- **Infrastructure**: 모델 파일 분리 저장으로 인한 버전 불일치 리스크 및 `constants.py` 내 파일 I/O로 인한 임포트 부작용 경험.

### Decision
- **UI 표준화**: `QTableView` + `QAbstractTableModel` 구조로 전면 교체.
- **SSOT(Single Source of Truth)**: `core/constants.py`를 설정의 단일 소스로 유지하되 파일 I/O는 제외.
- **통합 모델**: 모델 객체와 피처 리스트를 하나의 `.pkl` 파일에 담는 통합 저장 구조 채택.
- **Leakage 엄격 분리**: 타겟별로 독립된 Leakage 리스트를 관리하도록 `models.py` 구조 개선.

### Lesson
- 프레임워크의 편의성(`QTableWidget`)보다 구조적 안정성(`QTableView`)이 장기적으로 유리함.
- 데이터 학습 시 피처 이름을 끝까지 유지하는 것이 디버깅과 모델 검증에 필수적임.
- 순수 상수 파일(`constants.py`)과 실행 유틸리티(`utils.py`)를 철저히 분리해야 순환 참조 및 예기치 못한 부작용을 막을 수 있음.

---

## 2026-05-05 — docs/en14825 중복 문서 감사 및 제거

### Result
- `docs/en14825/notes.md`, `design_notes.md`, `dev_notes.md`를 삭제함.
- 내용이 모두 `en14825_` 접두사가 붙은 신형 문서에 병합/통합되어 있음을 확인 후 삭제.
- `docs/README.md` 및 `docs/REFACTOR_PLAN.md`에 남아 있던 구형 파일명 참조 업데이트 완료.

---

## 2026-05-05 — AHRI HSPF2 config relocation 및 guard 정리

### Tried
- `data/usa_hspf2.json`을 `data/region_configs/usa.json`에 즉시 통합할 수 있는지 감사했다.
- `AHRIHSPF2Calculator`와 `AHRICalculator`의 config 접근 방식을 확인했다.
- 단순 통합 대신 AHRI HSPF2 전용 config를 `data/region_configs/usa_hspf2.json`으로 위치 이동했다.
- 실행 코드, 테스트, AHRI 문서의 구 경로 참조를 새 경로로 갱신했다.
- `tests/test_region_config_integrity.py`에 HSPF2 config path guard를 추가했다.
- `data/region_configs/REGION_CONFIG_RULES.md`에 AHRI SEER2/cooling config와 AHRI HSPF2/heating config를 단순 병합하지 않는다는 규칙을 보강했다.

### Result
- `data/usa_hspf2.json` → `data/region_configs/usa_hspf2.json` 이동은 rename 100%로 처리되었고 JSON 값 변경은 없었다.
- `data/region_configs/usa.json`은 AHRI SEER2/cooling 전용 flat config로 유지했다.
- `data/region_configs/usa_hspf2.json`은 AHRI HSPF2/heating 전용 flat config로 분리 유지했다.
- 구 경로 `data/usa_hspf2.json`이 다시 생기지 않도록 path guard 테스트를 추가했다.
- AHRI HSPF2 테스트와 AHRI 관련 테스트가 통과했다.

### Failed / Risk
- `usa.json`과 `usa_hspf2.json`은 모두 top-level flat schema를 사용하므로 단순 병합 시 `bin_data`, `test_point_temps`, `constants`, `defaults`, `mode` 등의 key 의미가 충돌할 수 있다.
- 완전 통합은 단순 파일 병합이 아니라 `cooling` / `heating` namespace 또는 loader compatibility 설계가 필요하다.
- 과거 기록성 문서와 local scratch에는 구 경로 문자열이 남을 수 있으므로 grep 결과 해석 시 실행 참조와 기록 참조를 구분해야 한다.
- agent가 config 통합 작업에서 schema 충돌 판단 없이 진행하면 계산기 로딩 로직까지 불필요하게 확장될 위험이 있다.

### Decision
- 당장은 `data/region_configs/usa.json`과 `data/region_configs/usa_hspf2.json`을 병합하지 않는다.
- AHRI SEER2/cooling은 `data/region_configs/usa.json`을 사용한다.
- AHRI HSPF2/heating은 `data/region_configs/usa_hspf2.json`을 사용한다.
- AHRI HSPF2는 region profile selector 방식이 아니라 canonical input normalization + optional fallback handler 방식으로 유지한다.
- 완전 통합은 AHRI config schema를 `cooling` / `heating` namespace로 분리하거나 compatibility loader를 설계한 뒤 별도 phase에서 검토한다.

### Lesson
- config 위치 이동과 schema 통합은 별도 작업으로 분리해야 한다.
- config 파일 통합 전에는 calculator가 기대하는 top-level key와 loader 방식을 먼저 확인해야 한다.
- 경로 정리 작업에서는 JSON 값, 계산 로직, expected value를 함께 건드리지 않는다.
- config 이동 후에는 경로 회귀 방지 테스트를 함께 추가하는 것이 안전하다.
- path guard 테스트는 계산값이나 schema 세부 항목까지 검증하지 않고, 존재 경로와 JSON 유효성 수준으로 좁게 유지한다.

---

## 2026-05-05 — AHRI HSPF2 v3 guard 및 첫 safe refactor 정리

### Tried
- AHRI HSPF2 v3 계산 경로에서 H12/H22 optional fallback source metadata를 직접 검증하는 테스트를 추가했다.
- H12 tested, Eq.11.183 fallback, Eq.11.185 fallback 경로와 H22 tested, Eq.11.44/11.50 fallback 경로를 guard했다.
- H2Int가 `minimum_speed_limited=True` branch에서 low path와 intermediate path에 미치는 영향을 테스트로 고정했다.
- H42 provided/missing 정책을 테스트로 보강하고, full-speed low-temperature line 선택이 달라지는지 확인했다.
- `summary.metadata`, top-level `h42_source`, `bin_details[].debug_info` 등 HSPF2 v3 diagnostics 구조를 감사했다.
- `docs/ahri210240/ahri210240_dev_notes.md`에 HSPF2 v3 diagnostics contract를 문서화했다.
- `_calculate_hspf2_v3_ahri()`에서 H12/H22 fallback 결정 책임만 helper로 분리했다.

### Result
- H12/H22 fallback source guard 테스트가 추가되어 `h12_source`, `h22_source` 회귀를 직접 잡을 수 있게 되었다.
- H2Int power 변경이 `minimum_speed_limited=True`에서 `p_low`, `p_int`에는 영향을 주고, full-speed path에는 영향을 주지 않는 것을 확인했다.
- H42 제공/미제공에 따라 `full_capacity_method`, `q_full`, `p_full`이 달라지고, H12/H22 source metadata는 오염되지 않는 것을 확인했다.
- HSPF2 v3 diagnostics key/value의 현재 contract를 문서에 남겼다.
- H12/H22 fallback resolver helper를 분리했지만 bin loop, Case I/II/III, H2Int, H42 policy, diagnostics 구조는 변경하지 않았다.
- AHRI HSPF2 테스트와 AHRI 관련 테스트가 통과했다.

### Failed / Risk
- `_calculate_hspf2_v3_ahri()`는 여전히 bin loop, Case dispatch, defrost/cutoff, auxiliary heat, diagnostics 생성 책임을 많이 가지고 있다.
- H22 resolver helper 반환값이 다소 많지만, 이번 단계에서는 dataclass/schema 도입 없이 기존 변수 흐름을 유지했다.
- `h42_source`는 현재 `summary.metadata`가 아니라 top-level result key이므로 위치 일관성이 약하다.
- diagnostics 값은 equation 기반 이름과 descriptive 이름이 섞여 있어 향후 rename/move 시 테스트와 문서 contract를 함께 갱신해야 한다.
- bin loop / Case resolver 리팩토링은 계산 결과 변경 위험이 크므로 아직 진행하지 않았다.

### Decision
- AHRI HSPF2 v3의 계산 결과를 바꾸는 리팩토링은 하지 않는다.
- 현재 단계에서는 H12/H22 fallback resolver 분리까지만 safe refactor로 인정한다.
- H2Int, H42, Case I/II/III, bin loop, diagnostics 구조 변경은 후속 calculator.py 리팩토링 phase로 미룬다.
- diagnostics key/value rename이나 `h42_source` 위치 변경은 별도 phase에서 검토한다.
- 당분간은 AHRI config 통합 설계와 ISO16358-2 HSPF 구성 작업을 우선한다.

### Lesson
- 규격 계산기 리팩토링은 계산 로직을 먼저 고치기보다 source metadata, branch guard, diagnostics contract를 먼저 고정해야 안전하다.
- fallback 경로는 최종 HSPF2 값만 보는 smoke test보다 source metadata를 직접 assert하는 guard가 필요하다.
- branch guard 테스트는 exact seasonal value보다 “영향을 받아야 하는 값 / 영향을 받으면 안 되는 값”을 관계성으로 검증하는 편이 안전하다.
- production code를 분리할 때는 bin loop나 Case dispatch처럼 위험한 영역보다 이미 guard가 충분한 작은 resolver부터 시작해야 한다.
- phase마다 로그를 남기기보다 config relocation, guard hardening처럼 의미 있는 묶음 단위로 기록하는 것이 project_log의 검색성과 유지보수성에 더 좋다.

---

## 2026-05-05 — Calculator architecture safety docs 1차 정리

### Tried
- AHRI config 통합 Audit 결과를 바탕으로 calculator resolver, UI routing, 다지역 config, ML/역탐색 연동까지 고려한 문서 안전망을 정리함.

### Result
- project_architecture.md를 calculator profile resolver와 inverse-search architecture의 상세 기준 문서로 사용하기로 함.
- AGENT_TASK_ROUTER.md에서 architecture-sensitive coding work와 calculator logic work가 project_architecture.md를 참조하도록 연결함.
- AGENTS.md에는 Lite guard만 두고, 상세 구조는 router를 통해 읽도록 결정함.

### Failed / Risk
- project_architecture.md가 참조되지 않으면 작업자가 구조 원칙을 놓칠 수 있음.
- region config, HW candidate input, ML schema, calculator result schema가 섞이면 leakage와 의미 충돌 위험이 있음.

### Decision
- 상세 설명은 project_architecture.md에 둔다.
- 작업 유형별 참조 규칙은 AGENT_TASK_ROUTER.md에 둔다.
- 항상 읽는 AGENTS.md에는 짧은 guard만 둔다.
- 결정 이력은 project_log.md에 남긴다.

### Lesson
- 문서는 작성보다 “작업자가 언제 읽게 되는지”가 중요하다.
- architecture 문서는 router와 연결되어야 실제 안전망이 된다.

---

## 2026-05-05 — Calculator profile resolver 최소 구현

### Tried
- AHRI SEER2/HSPF2 config 혼선을 막기 위해 범용 calculator profile resolver의 최소 구현을 추가함.
- 초기 profile은 AHRI USA SEER2/cooling과 AHRI USA HSPF2/heating만 등록함.
- resolver는 JSON을 열거나 변환하지 않고 기존 flat `config_path`만 반환하도록 제한함.

### Result
- `core/calculator_profiles.py`에 `CalculatorProfile`, `list_calculator_profiles()`, `resolve_calculator_profile()` 추가.
- `ahri_usa_seer2`는 `data/region_configs/usa.json`으로, `ahri_usa_hspf2`는 `data/region_configs/usa_hspf2.json`으로 명시 resolve됨.
- 잘못되거나 모호한 selector 조합은 `ValueError`로 fail-fast함.
- `tests/test_calculator_profiles.py`에 AHRI routing guard 추가.

### Failed / Risk
- `calc_window.py`는 아직 resolver를 사용하지 않으므로 filename scan 기반 UI routing risk는 남아 있음.
- resolver는 아직 AHRI profile만 포함하며, ISO/Korea/Hong Kong/SASO/EN profile 확장은 후속 phase로 남김.

### Decision
- 이번 phase에서는 resolver를 flat config path selector로만 유지한다.
- nested schema 변환, calculator 실행, public API 변경, UI 전환은 하지 않는다.
- UI routing 전환은 별도 phase로 분리하고, 우선 ISO16358-2 HSPF 구현으로 이동한다.

### Lesson
- config 통합보다 먼저 selector contract와 fail-fast guard를 확보해야 한다.
- resolver는 초기에는 얇게 유지해야 기존 계산기와 테스트를 안전하게 보호할 수 있다.

---

## 2026-05-05 — ISO16358-2 HSPF default-bin case 1 안정화

### Tried
- ISO16358-2 HSPF default Table 3 bin-hour seven-case fixture를 `tests/fixtures/`로 분리했다.
- case 1만 xfail 해제하고, case 2~7은 strict xfail로 유지했다.
- ISO common HSPF path가 config의 `hspf.table1_default_fallback` 계수를 읽어 `-7_full/-7_half` default point를 생성하도록 최소 확장했다.

### Result
- case 1은 HSPF 4.225, LHST/HSTL 약 4885.377 kWh, CHSE/HSEC 약 1156.245 kWh로 golden tolerance 안에 들어왔다.
- 기존 Hong Kong HSPF golden과 기존 HSPF smoke/validation/golden 묶음은 통과했다.
- 전체 테스트는 `136 passed, 6 xfailed` 상태다.

### Failed / Risk
- case 2~7은 min stage, extended/frost optional branch가 아직 ISO common HSPF path에 구현되지 않아 xfail 유지가 필요하다.
- `hspf.table1_default_fallback`을 읽는 코드 경로는 추가됐지만, 현재 production region config에는 해당 key를 추가하지 않았다.

### Decision
- ISO default-bin seven-case matrix는 입력 적법성 validation이 아니라 measured/default toggle branch regression으로 다룬다.
- 이번 phase에서는 case 1 no-min/default fallback만 pass시키고, case 2~7 계산 엔진 확장은 별도 phase로 남긴다.
- production region config와 public API는 변경하지 않는다.

### Lesson
- ISO default-bin fixture는 HSTL을 맞추기 위해 bin-hours를 scale하지 않고 Table 3 reference bin-hours를 그대로 유지해야 한다.
- optional measured point matrix는 validation 규칙과 계산 branch regression을 분리해서 다뤄야 한다.

---

## 2026-05-06 — Design Gate 및 grill-me workflow 도입

### Tried
- `grill-me` skill을 추가하고, AGENTS.md에 Design Gate Rule을 연결했다.
- `docs/designs/TEMPLATE_DESIGN_GATE.md`를 생성했다.
- ISO16358-2 HSPF core/handler boundary를 dry run으로 검증했다.

### Result
- global core는 canonical-only input을 받고, region/profile fallback은 handler/config/profile 책임으로 분리하기로 했다.
- forbidden field validation은 trace_metadata를 제외한 input tree에서 recursive하게 수행하기로 했다.
- validation 실패는 core에서 exception으로 중단하고, wrapper/UI에서만 structured error result로 변환하기로 했다.

### Failed / Risk
- skill summary는 자동 파일 생성이 아니라 터미널 출력만 수행했다.
- forbidden denylist가 과도하면 정상 canonical field를 막을 수 있다.

### Decision
- 큰 설계 작업은 구현 전 `grill-me` Design Gate를 먼저 통과한다.
- Design Gate 결과는 `docs/designs/` 또는 구현 프롬프트에 남긴다.

### Lesson
- “먼저 구현하고 나중에 공통화”를 막으려면 core/handler boundary와 validation rule을 구현 전에 문서화해야 한다.

---

## 2026-05-06 — ISO16358-2 HSPF default-bin case 2 안정화

### Tried
- ISO common HSPF path에서 `7_min`이 제공된 경우에만 minimum stage를 활성화했다.
- case 2 범위에서 min~half branch를 Formula 44/48 boundary COP interpolation과 Formula 45 `P(tj) = Lh(tj) / COP(tj)` 경로로 계산했다.
- case 2는 xfail 해제하고, case 3~7은 strict xfail로 유지했다.

### Result
- case 1 full/half-only regression은 기존 baseline으로 pass 유지했다.
- case 2는 HSPF 4.289, LHST/HSTL 4885 kWh, CHSE/HSEC 1139 kWh golden tolerance 안에 들어왔다.
- 전체 테스트는 `137 passed, 5 xfailed` 상태다.
- magic correction factor `1.01861`은 추가하지 않았다.
- seven-case fixture가 external calculator / official-sheet reproduction fixture임을 note로 명시하고, production ISO Table 1 default 0.64 / 0.82와 fixture override 0.5 / 1.105를 각각 guard test로 고정했다.
- 후속 guard로 `2_ext`를 계산 branch가 아닌 canonical optional extended candidate로만 감지하는 helper/test를 추가했다. 계산 결과와 case 3~7 xfail 상태는 바꾸지 않았다.
- `docs/iso16358/iso16358_dev_notes.md`에 Table 1 / Formula 30 해석 메모를 추가해 production default, external override, footnote c/d, Formula 46/49 보류 결정을 정리했다.
- Formula 50 frost full-to-extended branch를 canonical 조건으로만 추가했다. `2_ext`를 `pi_ext,f(2)` / `P_ext,f(2)` anchor로 사용하고, ISO Table 1 default `pi_ext(-7)=0.734*pi_ext(2)`, `P_ext(-7)=0.877*P_ext(2)` 및 Formula 25 선형 보간으로 extended frost curve를 평가한다.
- Formula 50 적용 후 case 3 actual은 HSPF 4.308, HSEC 1134.088 kWh로 이동했고, case 1/2 regression은 발생하지 않았다. case 3~7 xfail은 유지했다.
- AHRI 210/240 notes에는 ISO16358 Formula 30/50 branch 구조를 AHRI HSPF2 Case I/II/III path로 이식하지 말라는 cross-standard boundary note를 추가했다.

### Failed / Risk
- case 1의 최신 external golden 4.222 / 1157은 half~full Formula 46/49 slice에서 다시 다룰 항목으로 남겼다.
- case 3~7은 Formula 50 일부가 들어갔지만, Formula 46/47/49와 `L_h > pi_ext,f` extended capacity operation 범위가 남아 있어 strict xfail을 유지한다.

### Decision
- Slice 1A는 case 2 calculation only로 닫고, extended branch나 Hong Kong/Korea handler/profile은 변경하지 않는다.
- Hong Kong/MEELS/region/country 여부는 common core 계산 분기 조건으로 사용하지 않는다.
- external golden fallback override는 fixture scope로만 유지하고, override 없는 ISO common HSPF config는 production Table 1 default 0.64 / 0.82를 사용해야 한다.
- `2_ext` 단독으로 `7_ext`를 만들지 않는다. Formula 50 frost branch는 ISO Table 1의 -7 extended default와 2°C extended measured anchor만 사용하며, Formula 47 non-frost branch나 extended capacity operation은 별도 slice로 남긴다.

### Lesson
- min stage 도입은 lowest-stage cycling branch와 min~half interpolation branch만 바꿔야 하며, half~full branch를 함께 조정하면 slice boundary가 흐려진다.
- expected 정정은 slice 대상 case에만 적용하고, 후속 Formula slice의 golden은 별도 작업으로 남겨야 한다.
- external calculator reproduction fixture와 production standard default는 같은 common core를 지나더라도 config scope를 테스트로 분리해야 한다.

---

## 2026-05-06 — ISO HSPF fixture 정정 및 KS cooling load-line 고정

### Tried
- ISO16358-2 HSPF seven-case fixture label/expected를 정정하고 case 8을 추가했다.
- KS C 9306 HSPF region config load line을 heating-rated 기준에서 cooling-rated 기준으로 전환했다.
- ISO common frost boundary guard를 skip 없이 실제 branch 검증으로 복구했다.

### Result
- KS C 9306 HSPF config load line은 `rated_cooling_capacity`만 허용하며, `BL_h(0°C) = rated_cooling_capacity × 0.82`를 테스트로 고정했다.
- `rated_heating_capacity` source 또는 cooling capacity 누락은 `ValueError`로 실패한다.
- 전체 테스트는 `143 passed, 6 xfailed` 상태다.

### Decision
- KS C 9306 HSPF production load-line source는 `rated_cooling_capacity`로 고정한다.
- ISO common frost boundary test는 KS load-line 변경과 독립된 guard로 유지하며 skip 처리하지 않는다.

### Lesson
- fixture correction과 regional load-line bug fix는 커밋을 분리해야 추적성이 좋다.
- region config source 변경은 validation guard와 notes를 함께 갱신해야 역방향 수정 위험을 줄일 수 있다.

## 2026-05-07 — ISO16358-2 HSPF case 3 Excel component-sum trace 도입

### Tried
- ISO16358-2 HSPF case 3 mismatch를 진단하면서, 호주/뉴질랜드 Energy Rating SEER calculator의 `Inverter AC` 시트 구조를 분석했다.
- case 3(`H1 Min YES + Extended YES`)이 Excel에서 `CH48` branch를 타며, `CG = BM+BO+BQ+BS+BT+BU+BX+BZ+CB+CD+CE+CF`, `CH = CG × bin hours`, `CH48 = SUM(CH rows)` 구조임을 확인했다.
- 기존 predictor_v3의 case 3 계산은 bin마다 하나의 selected `P_j` branch를 선택하는 single-branch 모델이었고, Excel은 non-frost/frost component-sum 모델임을 확인했다.
- `core/calculator_iso16358.py`에 trace-only Y_MIN_Y_EXTD component-sum evaluator를 추가하고, `tests/test_iso16358_hspf_golden.py`에 isolated case 3 trace test를 추가했다.

### Result
- 기존 `calculate_hspf_iso16358_common()` output은 변경하지 않았다.
- ISO HSPF golden test는 `17 passed, 7 xfailed`, full tests는 `143 passed, 7 xfailed`로 통과했다.
- trace-only evaluator는 case 3에서 `CH48 = 1,117,175 Wh`를 계산했고, Excel 관찰값 `1,117,679 Wh`와 약 `0.5 kWh` 차이까지 접근했다.
- 기존 common path의 case 3 CHSE `1,134,088 Wh` 대비 Excel component-sum 구조가 mismatch의 핵심 원인임을 확인했다.

### Failed / Risk
- 잔여 약 `0.5 kWh` 차이는 단순 final rounding, per-bin Wh rounding, CG round/ceil/floor로 설명되지 않았다.
- 잔여 차이는 주로 frost `CB` half-full component의 3~5°C bin에 집중되었다.
- Excel의 잠금/보호/Numbers 변환 문제 때문에 `ROUND/ROUNDUP` 여부와 hidden precision은 아직 완전히 확정하지 못했다.
- `SEER calculator` 구현은 GEMS/ZERL/AS/NZS 계열 calculator compatibility일 가능성이 있으므로, ISO common core에 곧바로 연결하면 case 2 등 기존 pass 경로를 오염시킬 위험이 있다.

### Follow-up Note
- 이후 trace-only evaluator에 Excel raw H2 Half f / H2 Full f precision을 반영했다.
- H2 Half f는 `1773.97959183673 / 395.471698113208`, H2 Full f는 `3405.57397959184 / 1159.04986522911` raw 값을 사용하도록 보정했다.
- trace-only case 3 `CH48`은 `1,117,649.764 Wh`로 이동했고, Excel bin-energy table sum `1,117,680 Wh`와 약 `30 Wh` 차이까지 접근했다.
- CB frost half-full bins는 Excel 관찰값과 사실상 정렬되었으며, 기존 `calculate_hspf_iso16358_common()` output과 xfail 정책은 변경하지 않았다.
- 남은 약 `30 Wh` 차이는 non-CB component raw precision 또는 Excel observed table/cached value 한계로 남겨두고, production/common ISO path에는 아직 연결하지 않는다.

### Decision
- resolver-only patch는 채택하지 않는다.
- component-sum evaluator는 당분간 trace-only / isolated test 경로로 유지한다.
- common ISO HSPF output, fixture expected, xfail 정책은 이번 단계에서 변경하지 않는다.
- 다음 단계는 case 3의 residual delta를 frost `CB` component 중심으로 좁혀본 뒤, 실제 production/profile 연결 여부를 별도 결정한다.

### Lesson
- Excel calculator 기반 golden을 맞출 때는 Formula 번호 단위 구현만으로 부족할 수 있다.
- 계산기 시트가 component-sum table 구조를 쓰는 경우, Python 코드도 동일한 중간 trace 구조를 먼저 재현해야 한다.
- Codex에는 Excel 파일 전체를 읽히지 말고, ChatGPT/수동 분석으로 추출한 핵심 facts만 전달하는 방식이 토큰과 오해를 줄인다.
- 추가 Excel formula extraction에서 CH/CG/component path에 ROUND/ROUNDUP이 없고, H2/H3 default resolver 및 BM~CF gate 구조가 cell formula 기준으로 확인되었다. 잔여 차이는 rounding보다 frost `CB` component의 raw dependency 차이로 좁혀졌다.

### Follow-up — AS/NZS Excel compatibility boundary decision

#### Tried
- Windows Excel COM original AS/NZS / Energy Rating SEER calculator case 3 baseline `H12 = 1126.120 kWh`, `H13 = 4.33824`, `CH48 = 1126120.47 Wh`를 ISO common golden 후보로 둘지 compatibility reference로 둘지 재분류했다.
- workbook의 `BN` / `BP` / `BY` / `CA` / `CC` COP helper column convention을 ISO Formula 47/49/50 common path와 비교했다.

#### Result
- case 3 Excel COM baseline은 폐기하지 않고 AS/NZS Excel compatibility reference로 보존한다.
- common ISO path actual `HSEC ≈ 1134087.8405 Wh`, `HSPF ≈ 4.308`과 Excel `1126.120 kWh`, `4.33824`의 차이는 ISO expected mismatch가 아니라 reference type mismatch로 취급한다.

#### Failed / Risk
- Excel workbook helper cells를 common production code에 복제하면 `calculator_iso16358.py`가 external workbook layout에 결합될 위험이 있다.
- converted workbook / Numbers 값은 formula text나 dependency map 분석에는 쓸 수 있지만 계산값 reference로 쓰면 golden이 오염될 수 있다.

#### Decision
- AS/NZS Excel exact matching은 별도 compatibility calculator/profile 후보로 분리한다.
- common ISO HSPF path에 `BA / COP_helper(tj)` workbook helper convention을 직접 연결하지 않는다.
- 후보 profile은 `profile_id=asnzs_excel_hspf_compat`, `calculator_id=asnzs_excel_hspf`처럼 explicit resolver record로만 다룬다.

#### Lesson
- external workbook baseline은 값 자체보다 reference type을 먼저 고정해야 한다.
- common standard implementation과 compatibility reproduction은 같은 HSPF 숫자를 다뤄도 golden namespace를 분리해야 한다.

### Follow-up — AS/NZS Excel HSPF compatibility design contract

#### Tried
- boundary decision 이후 구현 전 design contract를 문서에 고정했다.
- profile identity, input/reference namespace, resolver opt-in boundary, future guard test 후보를 정리했다.

#### Result
- 후보 identity는 `profile_id=asnzs_excel_hspf_compat`, `calculator_id=asnzs_excel_hspf`, `reference_type=ASNZS_EXCEL_COMPAT`로 정리했다.
- `region=au_nz` 또는 `standard=ASNZS`만으로 compatibility mode가 자동 활성화되면 안 된다는 resolver boundary를 추가했다.
- Windows Excel COM dump/chat_packet 값은 production region config가 아니라 reference artifact 또는 test fixture namespace에만 둔다고 명시했다.

#### Failed / Risk
- compatibility profile이 일반 ASNZS metadata로 자동 선택되면 common ISO path가 오염될 수 있다.
- guard test 없이 구현하면 ISO common golden과 AS/NZS compatibility golden namespace가 섞일 수 있다.

#### Decision
- AS/NZS Excel HSPF compatibility는 explicit opt-in profile/calculator로만 선택한다.
- common ISO calculator는 `ASNZS_EXCEL_COMPAT` reference type을 보고 내부 분기하지 않는다.
- 구현 전 guard test 설계가 필요하다.

#### Lesson
- compatibility calculator는 계산식보다 먼저 selector contract와 golden namespace를 분리해야 한다.

### Follow-up — ISO16358-2 HSPF dual-track architecture contract

#### Tried
- ISO16358-2 HSPF 후속 구현 전 Track A common ISO path와 Track B AS/NZS Excel compatibility path를 문서상 분리했다.
- legacy AS/NZS 후보 명칭을 `asnzs_*` canonical naming으로 정리했다.

#### Result
- Track A는 `calculator_iso16358.py`의 ISO Formula 47/49/50-style common path로 유지하고, AS/NZS Excel final value를 common golden으로 쓰지 않는다고 명시했다.
- Track A 검증은 final Excel golden이 아니라 formula micro golden, branch routing invariant, cycling PLF edge case, accumulation invariant, auxiliary energy invariant 중심으로 설계하기로 했다.
- Track B는 Windows Excel COM exact matching용 별도 calculator/profile/test namespace로 격리하고, `1126.120 kWh` / `4.33824` / `1126120.47 Wh`를 `ASNZS_EXCEL_COMPAT` reference에만 둔다고 명시했다.

#### Failed / Risk
- Track A와 Track B test namespace가 섞이면 ISO common expected가 workbook compatibility convention에 오염될 수 있다.
- naming이 canonical `asnzs_*`로 통일되지 않으면 resolver/profile 구현 시 migration bug가 생길 수 있다.

#### Decision
- canonical naming은 `asnzs_excel_hspf_compat`, `asnzs_excel_hspf`, `data/region_configs/asnzs_excel_hspf.json`으로 통일한다.
- AS/NZS Excel compatibility는 opt-in Track B로만 선택하고 common ISO calculator는 `ASNZS_EXCEL_COMPAT` reference type을 읽어 분기하지 않는다.

#### Lesson
- HSPF 구현 전에는 final-number matching보다 track boundary, selector contract, micro invariant 검증 단위를 먼저 고정해야 한다.

### Follow-up — KS shared-formula oracle consistency gate

#### Tried
- Track A ISO common HSPF 검증 전략에 KS shared-formula oracle consistency gate를 추가했다.
- KS C 9306 HSPF path를 surrogate oracle / cross-path consistency gate로만 쓰는 조건을 문서화했다.

#### Result
- Phase H-1~H-4 순서를 formula micro golden, KS shared-formula oracle consistency gate, AS/NZS Excel compatibility guard/design, compatibility module skeleton으로 정리했다.
- KS oracle gate는 ISO16358-2 bin hours, ISO common load-line basis, stage mapping, KS-specific correction factor 통제를 전제로 한다고 명시했다.
- 비교 기준은 final HSPF보다 branch, load, capacity boundary, `P_j`, `E_j`, auxiliary energy, HSTL/HSEC accumulation 같은 bin-level diagnostics 중심으로 잡았다.

#### Failed / Risk
- KS path 결과를 common ISO expected로 승격하면 Track A 검증 기준이 region path에 종속될 수 있다.
- correction factor 통제가 빠지면 shared-formula consistency가 아니라 KS policy difference를 비교하게 된다.

#### Decision
- KS path는 shared-formula consistency와 accumulation/branch sanity check용 surrogate oracle로만 사용한다.
- final HSPF assertion은 보조 지표로만 둔다.

#### Lesson
- shared formula 검증은 결과 숫자보다 입력 조건, stage mapping, correction factor 통제, bin-level diagnostics를 먼저 고정해야 한다.

### Follow-up — Phase H-1 ISO HSPF formula micro test design

#### Tried
- ISO16358-2 common HSPF 구현 위치와 기존 테스트 구조를 읽기 전용으로 조사했다.
- H-1 테스트가 final workbook value가 아니라 public `bin_details`와 hand-calculated micro fixtures로 설계 가능한지 확인했다.

#### Result
- Track A common path는 `calculate_hspf()`가 `profile=iso16358_2_hspf`일 때 `calculate_hspf_iso16358_common()`으로 진입한다.
- Public result는 `bin_details`의 `tj`, `nj`, `bl_h`, `pi_j`, `P_j`, `case`, `heat_pump_energy`, `auxiliary_energy`, `E_j`와 top-level `hstl_wh` / `hsec_wh`를 노출하므로 H-1의 주요 invariant는 API 변경 없이 설계 가능하다.
- 권장 파일명은 `tests/test_iso16358_hspf_formula_micro.py`이며, 대안은 `tests/test_iso16358_hspf_invariants.py`로 정리했다.
- Above-extended auxiliary case는 현재 common path가 Formula 50 밖에서 full-stage saturated convention을 쓰므로 expected freeze 전에 implementation check가 필요하다고 문서화했다.

#### Failed / Risk
- Formula 47/49/50 전체가 독립 pure helper로 완전히 분리되어 있지는 않으므로, 일부 micro test는 public bin result 또는 좁은 private helper를 사용해야 한다.
- capacity boundary detail이 public `bin_details`에 모두 노출되지는 않아, 필요한 경우 최소 diagnostics exposure를 별도 phase로 설계해야 한다.

#### Decision
- H-1은 AS/NZS Excel `4.33824` 또는 KS path result를 expected로 사용하지 않는다.
- H-1 micro fixture는 tests namespace에만 두고 production region config와 분리한다.
- final HSPF 단독 assertion보다 bin-level diagnostics와 accumulation invariant를 우선한다.

#### Lesson
- HSPF common path 검증은 큰 golden 하나보다 branch를 강제로 고정하는 tiny fixture와 bin-level diagnostics가 먼저 필요하다.

### Follow-up — Phase H-1a ISO HSPF safe branch micro tests

#### Tried
- `tests/test_iso16358_hspf_formula_micro.py`를 추가해 ISO16358-2 common HSPF safe branch를 hand-calculated micro fixture로 검증했다.
- AS/NZS Excel final value, KS C 9306 path result, production region config 값을 expected로 사용하지 않았다.

#### Result
- half boundary, full boundary, below-min cycling PLF, half-to-full interpolation, tiny-bin accumulation invariant 테스트를 추가했다.
- 테스트는 public `calculate_hspf()` result의 `bin_details`, `hstl_wh`, `hsec_wh`, `heat_pump_energy_wh`, `auxiliary_energy_wh`만 사용한다.
- `python3 -m pytest tests/test_iso16358_hspf_formula_micro.py -q` 결과 `5 passed`.

#### Failed / Risk
- `python -m pytest ...`는 환경에 `python` 명령이 없어 실행되지 않았다. 동일 대상은 `python3`로 통과했다.
- full-to-extended Formula 50 및 above-extended auxiliary contract는 아직 expected로 고정하지 않았다.

#### Decision
- H-1a는 safe branch micro tests로 닫고, extended/auxiliary contract는 H-1b에서 별도 확인한다.
- micro fixture는 tests namespace에만 유지한다.

#### Lesson
- H-1 safe branch는 production API 변경 없이 public bin diagnostics만으로 검증 가능하다.

### Follow-up — Phase H-1b extended / auxiliary contract check

#### Tried
- ISO16358-2 common HSPF path의 Formula 50 full-to-extended branch와 load > extended branch를 코드 읽기 및 임시 public API snippet으로 관찰했다.
- 테스트 구현이나 expected freeze 없이 current behavior만 분류했다.

#### Result
- `full < load <= extended` frost bin은 `formula50_full_extended_frost`로 진입한다.
- Formula 50 branch는 `tg` / `tf` boundary COP interpolation을 사용하고 `P_j = load / COP_fe_f`를 계산한다.
- 해당 branch의 public diagnostics는 `case`, `branch`, `pi_ext_f`, `p_ext_f`, `tg`, `tf`, `cop_fe_f`, `P_fe`, `P_j`, `backup_heat`를 포함한다.
- Formula 50 branch에서는 auxiliary energy가 `0`이고, `HSTL`은 total building load, `HSEC`은 heat pump energy를 누적한다.
- `load > extended`는 현재 `saturated`로 떨어지고 `P_full`, `pi_full`, `load - pi_full` 기준 auxiliary를 사용한다.

#### Failed / Risk
- above-extended current behavior는 extended capacity가 아니라 full capacity 기준으로 auxiliary를 계산하므로, 의도된 ISO common contract인지 판단 보류가 필요하다.
- 이 behavior를 지금 normative expected로 고정하면 향후 ISO contract 확인과 충돌할 수 있다.

#### Decision
- H-1b Formula 50 frost branch micro test는 hand-calculated boundary COP 기반으로 구현해도 된다.
- above-extended auxiliary test는 contract 확인 전에는 구현 보류하거나, 별도 characterization/xfail로만 다룬다.

#### Lesson
- full-to-extended와 above-extended는 같은 extended candidate를 쓰더라도 검증 안정성이 다르다. Formula 50 branch는 관찰 가능한 contract가 있지만, above-extended saturated branch는 먼저 규격 의도를 확인해야 한다.

### Follow-up — Phase H-1b-1 Formula 50 micro test

#### Tried
- `tests/test_iso16358_hspf_formula_micro.py`에 Formula 50 full-to-extended frost branch micro test를 추가했다.
- Expected는 AS/NZS Excel value나 KS path result가 아니라 boundary COP hand calculation으로 산출했다.

#### Result
- `test_hspf_formula50_full_to_extended_matches_boundary_cop` 추가.
- Test asserts `formula50_full_extended_frost`, `tg`, `tf`, `cop_fe_f`, `P_fe`, `P_j`, `E_j`, auxiliary `0`, `hstl_wh`, `hsec_wh`.
- `python3 -m pytest tests/test_iso16358_hspf_formula_micro.py -q` 결과 `6 passed`.
- `python3 -m pytest tests/test_iso16358_hspf_validation.py tests/test_iso16358_hspf_golden.py -q` 결과 `60 passed, 7 xfailed`.

#### Failed / Risk
- Above-extended saturated / auxiliary behavior는 여전히 expected로 고정하지 않았다.
- Formula 47 non-frost full-to-extended branch는 아직 별도 확인 대상이다.

#### Decision
- H-1b-1은 Formula 50 frost branch micro invariant로 닫는다.
- Above-extended auxiliary contract는 H-1b-2에서 별도로 확인한다.

#### Lesson
- Formula 50 branch는 public diagnostics가 충분해 production API 변경 없이 hand-calculated micro test로 고정할 수 있다.

### Follow-up — Phase H-1b-2 above-extended intended-contract xfail

#### Tried
- `tests/test_iso16358_hspf_formula_micro.py`에 above-extended intended contract를 strict xfail test로 추가했다.
- Current full-stage saturated fallback을 expected로 사용하지 않고, extended-cap saturation contract를 test-only expectation으로 명시했다.

#### Result
- `test_hspf_above_extended_uses_extended_cap_and_auxiliary_xfail` 추가.
- Intended expected는 equipment capacity cap `Phi_ext(tj)`, equipment power `P_ext(tj)`, unmet load `load - Phi_ext(tj)`, auxiliary energy `unmet_load * hours / aux_cop`, `HSTL = load * hours`, `HSEC = P_ext * hours + auxiliary_energy`로 구성했다.
- `python3 -m pytest tests/test_iso16358_hspf_formula_micro.py -q` 결과 `6 passed, 1 xfailed`.
- `python3 -m pytest tests/test_iso16358_hspf_validation.py tests/test_iso16358_hspf_golden.py -q` 결과 `60 passed, 7 xfailed`.

#### Failed / Risk
- Current diagnostics do not expose `phi_ext` / `p_ext` in saturated branch, so xfail expected uses test-local hand calculation.
- Implementation fix 전까지 above-extended branch는 intended contract와 다르다.

#### Decision
- Above-extended behavior는 strict xfail로만 기록하고 current fallback을 normative expected로 고정하지 않는다.
- Implementation fix는 별도 Phase H-1b-3로 분리한다.

#### Lesson
- Intended-contract xfail은 불확실한 behavior를 pass 기준으로 굳히지 않으면서 다음 구현 phase의 target을 명확히 남기는 데 유효하다.

### Follow-up — Phase H-6b/H-6c Formula 45/49 routing contradiction

#### Tried
- ISO16358-2 common HSPF 엔진에 Formula 45(non-frost)/Formula 49(frost) half-to-full 구간 private helper를 구현 및 검증했다.
- `calculate_hspf_iso16358_common` 메인 라우팅의 `bl_h <= pi_full` 분기에 이 helper를 임시 연결해 영향을 진단했다.

#### Result
- `_iso_hspf_half_full_power_by_formula_45_49` helper와 마이크로 테스트는 성공적으로 구현되어 커밋되었다.
- 메인 라우팅에 적용 시 잘 통과하던 `case_2`의 HSPF가 기대값(4.289)을 벗어나 4.478로 오차가 발생했다.
- `case_3`의 결과 역시 HSPF 4.499로 이동하며 외부 Excel COM 기대값(4.338)에서 더 멀어졌다.

#### Failed / Risk
- `case_2`의 기대값(4.289)은 엄격한 ISO Variable-Stage 수학 모델(Formula 45/49 적용)이 아니라, Two-Stage용 '선형 보간(capacity-linear)'을 썼을 때만 도출된다.
- 즉, Golden Matrix의 데이터는 ISO 표준 로직이 아닌 특정 조건(예: Extended 유무)에 따라 Formula 45/49와 선형 보간을 혼용하는 workbook-derived convention일 위험이 크다.
- 이 비표준 동작을 맞추기 위해 ISO 공통 코어(Track A)를 수정하면 엔진의 규격 일관성이 파괴된다.

#### Decision
- Formula 45/49 helper는 private 상태로 유지하고 메인 라우팅 통합은 보류(deferred)한다.
- `case_2`의 패스 유지를 위해 현재의 capacity-linear interpolation 라우팅을 롤백하여 유지한다.
- 향후 `case_3` 기대값을 순수 ISO common expected가 아닌 AS/NZS workbook convention 계열로 분리하는 정책 논의가 필요하다.

#### Lesson
- 외부 엑셀 계산기에서 추출된 Golden Expected 데이터는 반드시 규격 기반의 교차 검증을 거쳐야 하며, 모순된 fixture-fitting을 ISO 엔진에 하드코딩해서는 안 된다.

### Follow-up — Phase H-7 Pure ISO Track A Fixture Construction

#### Tried
- AS/NZS workbook-derived fixture(`seven-case matrix`)와 독립된 `Pure ISO Track A` validation namespace(`tests/fixtures/iso16358_hspf_pure_iso_track_a/`)를 구축함.
- Cycling, Formula 44/48, 45/49, 47/50, Saturated Auxiliary 등 주요 브랜치에 대해 Pure ISO 표준 수식 기반의 `Route-level` 계약 픽스처(Hand-calculated)를 추가함.

#### Result
- `cycling`, `min-to-half`, `saturated` 브랜치는 정적 기대값과 일치하여 `pass` 상태 확보.
- Formula 45/49/47/50은 엔진의 현 구현과 차이가 있어 `xfail` contract 상태로 추가하여 검증 기준점(Target)을 명확히 함.
- 모든 Fixture에 `ISO16358_COMMON_TRACK_A` 메타데이터 및 `no-workbook-reference` 가드를 설정함.

#### Decision
- 향후 메인 로직(Routing) 개선 시 이 Pure ISO 테스트 셋을 기준으로 점진적 전환을 수행함.
- `seven-case` 매트릭스는 Pure ISO 검증에서 분리하여 legacy compatibility reference로 취급함.

#### Lesson
- 순수 ISO 검증을 위해서는 외부 도구 유래 데이터에 의존하지 않는 독립적인 검증 축(Namespace)을 초기에 확보해야 한다.

## 2026-05-11 — ISO16358-2 HSPF common path 순수 ISO 기준선 확정

### Tried
- 07ca56a에서 ISO16358-2 HSPF common path를 순수 X 기반 stage-to-stage interpolation 구조로 전환함.
- 2ca1040에서 frost extended branch guard를 강화함.

### Result
- common path에서 workbook/COP 교점 보간을 제거함.
- Formula 47은 7_ext + -7_ext가 있을 때만 활성화하도록 정리함.
- Formula 50은 -7_ext + (2_ext 또는 2_ext_f)가 있을 때만 활성화하도록 정리함.
- 2_ext만으로 7_ext 또는 -7_ext를 자동 생성하지 않음.
- extended point가 부족하면 full 기준 saturated/auxiliary로 처리함.

### Failed / Risk
- 기존 workbook golden / old interpolation / old COP-boundary diagnostic 테스트는 known mismatch로 남아 있음.
- workbook oracle과 pure ISO common path 결과는 다를 수 있음.
- CAL03~07 workbook reconstruction 숫자는 expected matching 기준으로 사용하지 않음.

### Decision
- CAL01/02/08은 구현 기준으로 사용한다.
- CAL03~07은 branch 참고 자료로만 두고, workbook 숫자에 맞춰 core를 보정하지 않는다.
- Hong Kong 등 region 영향은 pure ISO common path 기준선 확정 후 별도 판단한다.

### Lesson
- workbook oracle 재현과 ISO common path 구현을 섞지 않는다.
- extended point는 common core에서 근거 없이 합성하지 않는다.

## 2026-05-16 — Agent result report lifecycle workflow 정착

### Result
- Result Report Workflow를 committed artifact 방식으로 정착시켰다.
- report numbering은 `active` / `summaries` / `archive` 전체에서 global sequential로 유지한다.
- summary는 strict phase가 아니라 workstream/arc 기준으로 묶고, summary 생성 시 `project_log.md` 갱신 필요 여부를 판단한다.
- routine lifecycle check는 metadata-only로 제한하고, 단순 docs/router/report lifecycle 작업에는 compact report를 허용한다.
- `AGENTS_FULL.md`는 `docs/archive/AGENTS_FULL.md`로 이동되어 active rule source에서 제외되었다.
- `AGENT_TASK_ROUTER.md`가 active routing/report workflow owner가 되었다.

### Decision
- report 본문은 `project_log.md`에 복사하지 않고, 확정된 decision / failure / lesson / process rule 변화만 짧게 남긴다.
- summary에 포함된 active reports는 archive 후보로 보고한 뒤 lifecycle maintenance에서 번호와 파일명을 유지해 이동한다.

### Follow-up — AGENTS.md lite entrypoint slimming

#### Result
- `AGENTS.md`는 매 세션 시작용 lite entrypoint로 축약하고, 세부 guardrail과 작업별 절차는 `AGENT_TASK_ROUTER.md`가 owner가 되도록 정리했다.
- 계산기, ML, UI, 문서 trigger 세부 규칙은 router의 Shared Guardrails와 UI route로 보존했다.
- ` AGENTS_md_slimming_plan.md`를 Markdown route simulation 결과로 채워 AGENTS slimming 후에도 주요 case의 routing clue가 유지됨을 확인했다.

#### Decision
- `AGENTS.md`에는 route entrypoint, non-negotiable boundary, document trigger만 남긴다.
- 작업별 조건부 문서 읽기, report mode, UI/ML/calculator 세부 실행 규칙은 `AGENT_TASK_ROUTER.md`에서 관리한다.

### Follow-up — Agent terminal output `modified:` 표준 줄 추가

#### Decision
- 모든 agent 작업의 터미널 결과 보고는 task별 `task N: OK/NG - short summary` 줄 → `modified: <comma-separated paths>` 줄 → `report: <report path>` 줄 3-line 표준 형식을 따른다.
- `modified:`에는 이번 작업에서 실제 수정/생성/삭제된 파일 경로만 포함하고, blocked / 변경 없음은 `modified: none`을 사용한다. unrelated, pre-existing dirty/staged/untracked 파일은 포함하지 않는다.
- 상세 변경 목록은 계속 report 내부 `Changed Files` 섹션에 두고, 터미널 출력은 위 형식으로 짧게 유지한다.

## 2026-05-16 — V2 skills pattern archive and owner-doc split

### Result
- `data/skills.md`의 V2 pattern 원본을 `docs/archive/skills_v2_patterns.md`로 이동해 raw code/example를 보존했다.
- UI delegate, dropdown target mapping, cascading autofill, MODEL_REGISTRY/artifact pattern은 `docs/architecture/project_architecture.md`로 분리했다.
- XGBoost/RFE feature-selection pattern은 `docs/knowledge/hvac_ml_feature_engineering.md`로 분리했다.
- ML safety gate, snapshot, test harness, optimization harness pattern은 `docs/knowledge/hvac_ml_data_quality.md`로 분리했다.

### Decision
- `data/skills.md`는 active data source가 아니라 V2 pattern archive로 취급한다.
- owner 문서에는 active guardrail과 reusable lesson을 두고, 긴 raw code pattern은 archive에 보존한다.

## 2026-05-16 — EN14825/AHRI legacy standard notes absorption

### Result
- EN14825 legacy SCOP note의 raw capacity-control step 해석, heating part-load 조건, PDF review scope, future work 근거를 `docs/en14825/` canonical 문서로 흡수했다.
- AHRI legacy HSPF2 note의 HSPF2 official case source, fallback path, defrost trace, metadata trace 근거를 `docs/ahri210240/` canonical 문서 기준으로 정리했다.
- 두 legacy 원본은 `docs/archive/standards_legacy/`로 이동하고, active 문서에서는 historical source로만 참조하도록 낮췄다.

### Decision
- EN14825와 AHRI 210/240의 active 기준은 각 standard 폴더의 `*_notes.md`와 `*_dev_notes.md`로 둔다.
- archive 파일은 과거 검토 범위와 official comparison 원본을 확인할 때만 참조한다.

## 2026-05-16 — Packaging route owner 연결

### Result
- `docs/PACKAGING.md`를 패키징 작업의 active owner 문서로 라우팅했다.
- `AGENT_TASK_ROUTER.md`에 Packaging / 배포 빌드 route를 추가해 PyInstaller, `.spec`, binary dependency, crash logging, packaging 실패 재현 작업의 기본 참조 경로를 고정했다.
- `AGENTS.md`, root `README.md`, `docs/README.md`에서 `docs/PACKAGING.md` inbound를 추가했다.

### Decision
- 패키징 요청 시 추측성 build command를 만들지 않고 `docs/PACKAGING.md`의 원칙과 실제 증거를 기준으로 작업한다.
- `docs/archive/AGENTS_FULL.md`는 packaging 기본 경로에서 제외하고, historical detail이 꼭 필요할 때만 제한적으로 확인한다.

## 2026-05-17 — Calculator architecture reset: ISO / KS / ASNZS boundary

### Decision
- 기존 `core/calculator_iso16358.py`가 ISO16358, KS C 9306, AS/NZS workbook oracle trace, region compatibility, UI/profile 기대를 동시에 떠안으면서 작업이 반복적으로 꼬였으므로 분리/재작성이 필요하다고 판단했다.
- 계산기 모듈을 세 축으로 고정한다.
  - `core/calculator_iso16358.py` — ISO 16358 전용 (ISO16358-1 CSPF, ISO16358-2 HSPF). Hong Kong / India / SASO / ISO T1 default 등 ISO 16358 기반 regional profile JSON을 해석하는 대표 calculator.
  - `core/calculator_ks_c9306.py` — KS C 9306 전용 special calculator (KS CSPF, KS HSPF). AHRI / EN14825처럼 ISO common path와 분리해 다루며, `data/region_configs/korea.json`은 이 모듈이 직접 해석한다.
  - `core/calculator_asnzs_hspf_excel.py` — AS/NZS workbook oracle / Excel compatibility 전용. ISO common HSPF expected와 분리된 explicit opt-in compatibility calculator로, Z-phase 후보로 보류한다.
- `data/region_configs/`는 ISO16358 전용 저장소가 아니라 여러 calculator가 공유하는 정적 standard/region config 저장소이다. ISO16358은 region config로 Hong Kong / India / SASO 등 regional profile을 구현하는 대표 케이스이며, KS C 9306도 `korea.json` 같은 region config를 사용할 수 있다. 단, KS config는 ISO common path가 아니라 `KSC9306Calculator`가 직접 해석해야 하고, AHRI(`usa.json`, `usa_hspf2.json`) 등 다른 special calculator도 동일 원칙을 따른다. AS/NZS workbook oracle은 ISO common path에 섞지 않고 별도 compatibility calculator/profile로 둔다.
- 다음 구현 순서: KS 분리 → ISO16358 정리/재작성 → AS/NZS Z-phase → profile/UI 연결.
- `work/iso-hspf-refactor-ui-followup` 브랜치는 merge 대상이 아니라 reference/spike로만 둔다.

### Scope
- 이번 작업은 architecture/work plan/project_log 문서 갱신만 수행했고, code/tests/fixtures/UI/profile resolver는 수정하지 않았다.

### Follow-up — KS C 9306 separation, profile registration, dispatcher foundation

#### Result
- `core/calculator_ks_c9306.py`에 `KSC9306Calculator`를 생성하고 KS C 9306 HSPF body와 CSPF intersection helper (`_ks_cspf_performance_line`, `_ks_cspf_intersection_power`)를 behavior-preserving하게 이동했다. ISO16358 측은 기존 호출 경로 보호를 위한 thin delegating wrappers만 남겼다.
- `KSC9306Calculator`에 `calculate_cspf` / `calculate_hspf` public entry와 `from_config_path` / `from_iso_calculator` factory를 마련했다. 현재 `calculate_cspf`는 ISO common CSPF engine을 lazy import해 delegate하는 thin path 성격이며, ISO 측 `power_interpolation_method == "ks_intersection"` 분기는 아직 그대로 남아 있다.
- `core/calculator_profiles.py`에 KS profile 두 개 (`ks_c9306_cspf`, `ks_c9306_hspf`, `calculator_id=ks_c9306`, `config_path=data/region_configs/korea.json`, `enabled=True`)를 manifest에 등록했다. `tests/test_calculator_profiles.py`의 enabled snapshot은 KS 두 profile 포함으로 갱신하고 KS resolver lookup 가드 4건을 추가했다.
- `core/calculator_dispatcher.py`를 신규 추가해 `create_calculator_for_profile(...)`이 profile resolver 결과를 받아 `KSC9306Calculator` / `AHRICalculator` / `AHRIHSPF2Calculator`로 instance를 생성하도록 했다. unsupported calculator_id는 fail-fast. `tests/test_calculator_dispatcher.py`에 smoke 7건 추가.
- ISO16358 profile manifest 등록과 Calculator UI selector 연결은 본 단계 후속 작업으로 분리되어 있다.

#### Decision
- profile resolver (`core/calculator_profiles.py`)는 순수 manifest/selector를 유지하고, calculator 인스턴스 생성은 `core/calculator_dispatcher.py`가 담당한다.
- ISO common engine 안의 KS-aware 분기 (`ks_intersection`) 와 ISO 측 KS thin wrappers의 완전 제거는 ISO common engine을 KS-unaware로 분리하는 후속 작업이 wiring된 다음 진행한다.
- 16개 ISO common HSPF / pure ISO track A / case 3 Excel trace pre-existing failures는 본 workstream에서 다루지 않고 유지한다.

### Follow-up — ISO separation Step 1 KS HSPF test routing

#### Result
- `iso_seperation_plan.md` Step 1 범위에서 KS C 9306 HSPF 테스트가 ISO calculator의 KS delegation을 통하지 않고 `KSC9306Calculator`를 직접 사용하도록 retarget했다.
- `tests/test_iso16358_hspf_ks_oracle.py`는 KS row 계산을 `KSC9306Calculator`로 수행하고 ISO common row 계산은 `ISO16358Calculator`로 유지해 shared-formula 비교 의도를 보존했다.
- `tests/test_iso16358_hspf_validation.py`와 `tests/test_iso16358_hspf_golden.py`의 KS 전용 validation/golden/helper 테스트는 `make_ks_phase1_calculator()` 또는 `KSC9306Calculator.from_config_path(...)`로 전환했다.
- `core/calculator_ks_c9306.py`의 class docstring에서 transitional delegation 표현을 정리했고, Step 2 legacy rename 전까지 `from_iso_calculator` compatibility factory는 유지한다고 명시했다.

#### Decision
- Step 1에서는 ISO module rename, legacy 이동, UI import 변경, `from_iso_calculator` 제거를 하지 않는다. 해당 작업은 `iso_seperation_plan.md` Step 2 범위로 유지한다.
- ISO common HSPF golden/diagnostic pre-existing failures는 기대값, tolerance, xfail을 조정하지 않고 baseline으로 유지한다.

### Follow-up — ISO separation Step 2a pre-rename audit

#### Result
- `core.calculator_iso16358` direct import sites를 다시 grep해 33개 test files와 1개 UI file(`ui/calculators_2point.py`)을 확인했다.
- Step 2b atomic rename 기준을 고정했다: `core/calculator_iso16358.py`는 `core/calculator_iso16358_legacy.py`로 이동하고, 새 `core/calculator_iso16358.py`는 `NotImplementedError` skeleton으로 둔다.
- Diagnostic/mixed test는 `tests/_legacy/`로 이동하고, pure ISO / regional ISO / ASNZS negative assertion / KS-ISO oracle tests는 원 위치에서 legacy import로 retarget한 뒤 Step 3~4에서 선택적으로 새 calculator로 되돌린다.

#### Decision
- Step 2b는 test behavior를 바꾸지 않는 rename/import retarget 작업으로 제한한다.
- Baseline `269 passed, 16 failed, 13 xfailed`를 Step 2b 검증 기준으로 유지한다.

### Follow-up — ISO separation Step 2b legacy rename

#### Result
- 기존 `core/calculator_iso16358.py` 구현을 `core/calculator_iso16358_legacy.py`로 이동했다.
- 새 `core/calculator_iso16358.py`는 Step 3 전용 `NotImplementedError` skeleton으로 생성했고 legacy alias를 두지 않았다.
- 33개 test file과 `ui/calculators_2point.py`의 legacy caller를 `core.calculator_iso16358_legacy` import로 retarget했다.
- Diagnostic/mixed tests 4개를 `tests/_legacy/`로 이동하고 `tests/_legacy/__init__.py`를 추가했다.

#### Decision
- Step 2b는 behavior-preserving legacy rename으로 제한했다. 새 ISO implementation, ISO profile 등록, UI dispatcher 전환은 Step 3~5로 유지한다.
- Moved legacy diagnostic test의 fixture path는 `tests/fixtures/`를 계속 보도록 보정했다.

### Follow-up — ISO separation Step 2c KS factory dead-code removal

#### Result
- `KSC9306Calculator.from_iso_calculator(...)`와 `_iso_calculator_ref` 필드를 제거했다.
- Legacy ISO wrapper의 `_ks_calculator()`는 `KSC9306Calculator(self.config, bin_hours=self.bin_hours, default_cd=self.Cd)` 직접 생성으로 전환했다.
- `from_iso_calculator` / `_iso_calculator_ref` grep 결과 0건을 확인했다.

#### Decision
- KS calculator는 더 이상 ISO calculator object reference를 보유하지 않는다.
- Legacy ISO wrapper는 기존 호출 경로 보존용으로만 KS calculator를 즉시 생성한다.

### Follow-up — ISO separation Step 3a new ISO CSPF implementation

#### Result
- 새 `core/calculator_iso16358.py`에 ISO 16358-1 CSPF 전용 구현을 추가했다.
- ISO T1 default, Hong Kong, India ISEER, SASO T3, ASEAN/control CSPF tests를 legacy import에서 새 ISO calculator import로 되돌렸다.
- 새 ISO 파일에서 KS/ASNZS/workbook/`ks_intersection`/test-value rounding 흔적이 없음을 grep으로 확인했다.

#### Decision
- Step 3a는 CSPF만 구현한다. `calculate_hspf()`는 Step 3b 전까지 `NotImplementedError`를 유지한다.
- HSPF tests와 ASNZS negative assertion tests는 아직 legacy target을 유지한다.

### Follow-up — ISO separation Step 3b new ISO HSPF common implementation

#### Result
- 새 `core/calculator_iso16358.py`에 ISO 16358-2 HSPF common/Phase 1 helper와 `calculate_hspf_iso16358_common()` / `calculate_hspf()` entry를 추가했다.
- Step 3b 범위의 active HSPF tests 7개를 legacy import에서 새 ISO calculator import로 되돌렸다: smoke, formula micro, compatibility boundary, Hong Kong config, pure ISO Track A, validation ISO common subset, KS oracle의 ISO-side shared formula probe.
- 새 ISO 파일에서 KS delegation, AS/NZS workbook helper, case3 trace-only entry가 없는 것을 grep으로 확인했다.

#### Decision
- `tests/test_iso16358_hspf_golden.py`와 `tests/_legacy/test_iso16358_hspf_h8_trace.py`는 converted-workbook/case3 trace 진단 의도가 섞여 있어 legacy target을 유지한다.
- 기존 ISO HSPF baseline `16 failed, 269 passed, 13 xfailed`는 기대값/tolerance/xfail 조정 없이 유지한다.

### Follow-up — ISO separation Step 4 AS/NZS compatibility snapshot

#### Result
- AS/NZS Excel compatibility negative assertion tests가 새 `core.calculator_iso16358` 모듈을 검사하도록 전환했다.
- `reference_files/iso16358_test_sheet.xlsx` current workbook snapshot에서 `Inverter AC` row 21-47과 output anchors (`BB48`, `CH48`, `H12`, `H13`)를 추출해 `tests/fixtures/asnzs_excel_hspf_compat/workbook_inverter_ac_current.json` fixture를 추가했다.
- `core/calculator_asnzs_hspf_excel.py`에 `ASNZS_EXCEL_COMPAT` workbook row snapshot input path를 추가하고, current workbook exact-match test를 추가했다.
- `PROJECT_BRIEF.md`, `project_brief.md`, `docs/WORK_PLAN.md`, `docs/REFACTOR_PLAN.md`, `docs/architecture/project_architecture.md`, `docs/designs/2026-05-08-asnzs-hspf-excel-compat-boundary.md`, `iso_seperation_plan.md`를 current snapshot / historical case3 full-dump 구분에 맞춰 갱신했다.

#### Decision
- Current workbook snapshot exact-match는 AS/NZS compatibility path에서만 다룬다.
- Historical case3 packet/full-dump parity는 workbook version mismatch 때문에 계속 Z-phase로 유지한다.
- ISO common expected/golden/tolerance/xfail은 변경하지 않는다.

### Follow-up — ISO separation Step 5 profile/dispatcher/UI reconnection

#### Result
- `core/calculator_profiles.py`에 ISO CSPF profiles 4개를 등록했다: `iso_t1_default_2point_cspf`, `india_iseer_cspf`, `hong_kong_cspf`, `saso_t3_cspf`.
- `asnzs_excel_hspf_compat` profile은 `enabled=False`로 등록해 explicit exposure 전까지 resolver 대상에서 제외했다.
- `core/calculator_dispatcher.py`가 `calculator_id=iso16358`와 `calculator_id=asnzs_excel_hspf`를 생성할 수 있도록 확장했다.
- `ui/calculators_2point.py`는 legacy ISO 직접 import/instantiation 대신 dispatcher profile id로 새 ISO calculator를 생성하도록 전환했다.

#### Decision
- AS/NZS compatibility profile은 manifest에는 존재하지만 disabled 상태를 유지한다.
- UI는 아직 기존 CSPF 화면 구조를 유지하며, profile/dispatcher 경로로만 calculator 생성 책임을 이동했다.

### Follow-up — ISO remaining work completion

#### Result
- `core/calculator_iso16358.py`의 active HSPF branch routing을 Formula 44/45/47/48/49/50 helper path로 연결했다.
- Frost extended path는 canonical `2_ext` 후보와 `-7_ext` fallback으로 선택될 수 있도록 정리했다.
- 기존 mixed ISO 구현을 `core/_legacy/calculator_iso16358_legacy.py`로 archive하고 남은 diagnostic import를 archived namespace로 retarget했다.
- `core/calculator_asnzs_hspf_excel.py`에 current workbook CSPF snapshot path(`calculate_cspf`)를 추가했다.
- Historical case3 workbook diagnostic expected는 active ISO failure가 아니라 pre-separation workbook oracle diagnostic으로 명시하고 xfail로 격리했다.
- `iso_separation_result.md`, `iso_remaining_work_completion.md`, project brief, work plan, refactor plan, architecture, design doc을 갱신했다.

#### Verification
- Targeted ISO/ASNZS checks: `81 passed, 21 xfailed`.
- Full suite: `288 passed, 23 xfailed`.

#### Decision
- AS/NZS completion 범위는 current local Energy Rating workbook compatibility로 한정한다. Public web evidence만으로 official AS/NZS production formula parity를 주장하지 않는다.
- Historical AS/NZS case3 full-dump exact parity는 matching workbook/full dump 확보 전까지 Z-phase로 유지한다.

### Follow-up — Active document inventory and report lifecycle summary

#### Result
- `ACTIVE_DOCUMENTS.md`를 root에 추가해 active 문서 목록, owner 역할, primary inbound/outbound 관계, watchlist를 한 파일에서 관리하도록 했다.
- `AGENT_TASK_ROUTER.md`, `README.md`, `docs/README.md`에서 여러 문서에 걸친 업데이트 시 `ACTIVE_DOCUMENTS.md`를 먼저 확인하도록 inbound를 추가했다.
- `result_reports/active/034`~`053`을 `result_reports/summaries/054_summary-calculator-ui-iso-separation.md`로 요약했다.
- 요약된 active reports 034~053은 번호/파일명을 유지한 채 `result_reports/archive/`로 이동했다.

#### Decision
- Active 문서 생성/archive 이동 또는 owner/inbound/outbound 변화가 있으면 `ACTIVE_DOCUMENTS.md`를 함께 갱신한다.
- Report lifecycle은 active 원본을 계속 쌓지 않고 summary와 archive로 닫는다. 이번 cycle 이후 active에는 현재 진행 작업 report만 남기는 구조를 기준으로 한다.

### Follow-up — Audit result next actions

#### Result
- `audit_result.md`의 “지금 당장 할 수 있는 다음 작업” 4개를 완료했다.
- ISO separation 후속 상태를 문서/주석에 맞췄다: `core/calculator_iso16358.py` 상단 docstring에서 HSPF 미구현 문구를 제거하고, `iso_separation_result.md`는 archive/summary 이동 상태를 반영했다.
- Legacy HSPF workbook diagnostic test를 `tests/_legacy/test_iso16358_hspf_golden_diagnostic.py`로 이동하고 active import/docs reference를 정리했다.
- `ui_resolver_audit_result.md`를 작성해 `app_calculator.py` / `ui/calc_window.py`의 resolver-backed 전환 범위를 정리했다.
- `ui/calc_window.py`의 AHRI SEER2 생성 경로를 direct `AHRICalculator(path)`에서 `create_calculator_for_profile(profile_id="ahri_usa_seer2")`로 전환했다.

#### Verification
- Legacy HSPF diagnostic move targeted check: `60 passed, 17 xfailed`.
- UI resolver targeted checks: `30 passed`.
- Full suite: `288 passed, 23 xfailed`.

#### Decision
- EN14825 UI tab은 EN profiles가 등록될 때까지 direct/stub 상태로 유지한다.
- ML / inverse-search 복귀 전 calculator result envelope / ML adapter boundary 설계를 먼저 수행한다.

### Follow-up — audit_2 immediate next actions completion

#### Result
- `reference_files/audit_2.md`의 “지금 당장 할 수 있는 다음 작업” 5개를 단계별로 처리했다.
- Root audit/result 문서는 active 운영 문서가 아니라 `reference_files/*.md` reference snapshot으로 분류하고, `ACTIVE_DOCUMENTS.md` scope/root result 기준을 정리했다.
- Active HSPF validation test는 더 이상 `tests._legacy` helper를 import하지 않고 `tests/helpers/iso16358_hspf_samples.py` shared helper를 사용한다.
- `app_calculator.py` / `ui/calc_window.py`는 PyQt offscreen launch smoke로 검증했다. 다만 `ui/calc_window.py` 안에서 calculate button/result display 연결은 아직 발견되지 않아 별도 UI follow-up으로 남겼다.
- AHRI SEER2 UI selector는 JSON filename scan이 아니라 `list_calculator_profiles()` 기반 profile-id item data를 통해 dispatcher를 호출한다.
- Calculator result envelope / ML adapter boundary는 `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`에 기록하고 architecture/work plan/refactor plan/brief/inventory 문서에 링크를 반영했다.

#### Verification
- Active HSPF helper split targeted check: `60 passed, 17 xfailed`.
- Calculator UI smoke / profile selector targeted check: `32 passed`.
- Full completion verification은 최종 report와 result report에 기록한다.

#### Decision
- ML / inverse-search 복귀 전 첫 구현 slice는 adapter helper 추가로 제한한다.
- Core calculator public API, diagnostics schema, region config 의미는 adapter 설계/구현 초기에 변경하지 않는다.

### Follow-up — audit_3 immediate next actions completion

#### Result
- `reference_files/audit_3.md`의 “지금 당장 할 수 있는 다음 작업” 5개를 단계별로 처리했다.
- `tests/test_app_calculator_ui_smoke.py`는 `pytest.importorskip("PyQt5")`를 사용해 PyQt 없는 환경에서 collection error 대신 UI smoke skip이 가능하도록 보강했다.
- `ui/calc_window.py`에 공통 계산 버튼과 결과 label을 추가하고, AHRI AC 입력 smoke에서 `calculate_ahri()` return 문자열이 UI에 표시되는 경로를 검증했다.
- `core/calculator_result_adapter.py`에 `ahri_usa_seer2` 전용 `wrap_calculator_result_envelope()` 첫 slice를 추가했다. 기존 calculator return dict는 `raw_result` 아래 보존한다.
- `tests/test_calculator_schema_boundaries.py`를 추가해 calculator import boundary, region config runtime key, adapter-owned envelope term 경계를 guard한다.
- `en14825_scop` profile과 `calculator_id=en14825` dispatcher path를 등록하고, `ui/calc_window.py` EN combo를 profile-id item data 기반 selector로 전환했다.

#### Verification
- Targeted audit_3 checks: `49 passed`.
- Full suite: `301 passed, 23 xfailed`.

#### Decision
- EN tab은 profile/dispatcher construction까지 resolver-backed로 전환했지만, `calculate_en()`의 실제 UI 계산 출력은 별도 EN UI calculation task로 유지한다.
- Adapter implementation은 AHRI SEER2 result envelope 첫 slice로 제한한다. `CalculatorInputEnvelope`, ranking, ML / inverse-search caller 구현은 아직 시작하지 않는다.
