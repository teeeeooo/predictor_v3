# predictor_v3 ISO separation audit 결과
## 결론

전체적으로 ISO / KS / AS/NZS 책임 분리는 성공한 상태로 보인다. PROJECT_CHARTER.md의 “계산식 신뢰성 → 테스트 → 입력 구조 → UI → Predictor” 순서도 대체로 지켰고, docs/architecture/project_architecture.md의 calculator boundary 기준에도 거의 맞는다.

다만 **“ML 및 app_calculator.py 구현 가능 상태”**로 보면 아직 완성은 아니다.
현재 상태는 계산기 core 분리는 완료, UI/ML 연결을 시작할 수 있는 기반은 생김, 하지만 UI resolver 정리와 calculator→ML adapter 설계는 아직 필요한 단계다.

## 확인한 기준
AGENTS.md
PROJECT_CHARTER.md
project_brief.md
docs/architecture/project_architecture.md
docs/designs/*
iso_seperation_plan.md
iso_separation_result.md
iso_remaining_work_completion.md
active_documents_workflow_audit_result.md
result_reports/summaries/054_summary-calculator-ui-iso-separation.md
관련 core / UI / tests 실제 코드

참고로 사용자가 말한 project_architecture.md는 root에는 없고, 실제 기준 파일은 docs/architecture/project_architecture.md에 있다.

검증 결과

##직접 실행한 검증:

python3 -B -m py_compile \
  core/calculator_iso16358.py \
  core/calculator_ks_c9306.py \
  core/calculator_asnzs_hspf_excel.py \
  core/calculator_dispatcher.py \
  core/calculator_profiles.py \
  app_calculator.py \
  ui/calc_window.py \
  ui/calculators_2point.py

결과: 통과

python3 -B -m pytest -q \
  tests/test_calculator_profiles.py \
  tests/test_calculator_dispatcher.py \
  tests/test_iso16358_cspf_iso_t1_default_golden.py \
  tests/test_iso16358_hspf_formula_micro.py \
  tests/test_iso16358_hspf_hong_kong_config.py \
  tests/test_asnzs_hspf_excel_compat_workbook_current_exact_match.py \
  tests/test_asnzs_cspf_excel_compat_workbook_current_exact_match.py \
  tests/test_region_config_integrity.py

결과: 70 passed

python3 -B -m pytest -q

결과: 288 passed, 23 xfailed

테스트 상태는 iso_remaining_work_completion.md에 적힌 결과와 일치한다.

## 잘 된 부분
1. ISO / KS / AS/NZS 계산기 분리

docs/architecture/project_architecture.md는 다음 구조를 요구한다.

core/calculator_iso16358.py: ISO 16358 common calculator
core/calculator_ks_c9306.py: KS C 9306 special calculator
core/calculator_asnzs_hspf_excel.py: AS/NZS workbook compatibility calculator

실제 코드도 이 구조를 대체로 따른다.

core/calculator_iso16358.py 안에 KSC9306Calculator, ASNZS, workbook helper 직접 import가 없다.
core/calculator_ks_c9306.py는 KSC9306Calculator.from_config_path()를 통해 korea.json을 직접 해석한다.
core/calculator_asnzs_hspf_excel.py는 REFERENCE_TYPE = "ASNZS_EXCEL_COMPAT"로 opt-in compatibility 경계를 둔다.
production-ish 파일에서 core._legacy.calculator_iso16358_legacy import는 발견되지 않았다.

이건 이번 분리 작업의 가장 중요한 성공 지점이다.

2. profile / dispatcher 기반이 생김

core/calculator_profiles.py에 ISO, KS, AHRI, AS/NZS compatibility profile이 등록되어 있고, core/calculator_dispatcher.py가 calculator_id 기준으로 lazy import한다.

특히 다음 경계가 잘 지켜졌다.

ks_c9306 → KSC9306Calculator
iso16358 → ISO16358Calculator
asnzs_excel_hspf → ASNZSExcelHSPFCompatibilityCalculator
AS/NZS compatibility profile은 enabled=False

즉, standard=ASNZS 같은 메타값만으로 compatibility mode가 자동 노출되지 않는다. 이건 architecture 문서의 opt-in 원칙과 맞다.

3. Calculator UI 일부는 이미 dispatcher를 사용함

ui/calculators_2point.py의 ISO CSPF 단건 UI는 create_calculator_for_profile()로 ISO / India / Hong Kong / SASO 계산기를 만든다.

즉, ISO CSPF UI는 더 이상 legacy direct instantiation 구조가 아니다. 이 부분은 app_calculator 쪽 다음 작업의 기반으로 쓸 수 있다.

4. 문서 lifecycle 정리는 대체로 잘 됨

ACTIVE_DOCUMENTS.md가 생겼고, AGENT_TASK_ROUTER.md, README.md, docs/README.md에서 이 문서를 참조한다.
result_reports/active/034~053을 result_reports/archive/로 이동하고, result_reports/summaries/054_summary-calculator-ui-iso-separation.md로 요약한 흐름도 맞다.

## 발견한 문제 / 남은 위험
1. core/calculator_iso16358.py 상단 docstring이 오래됨

현재 파일 상단에 다음 취지의 문구가 남아 있다.

Step 3a implements the ISO 16358-1 CSPF path only.
HSPF remains a Step 3b contract and intentionally raises NotImplementedError here.

하지만 실제로는 calculate_hspf_iso16358_common()과 calculate_hspf()가 구현되어 있다.

이건 계산 결과를 깨는 문제는 아니지만, 다음 작업자가 보면 “HSPF가 아직 미구현인가?”라고 오해할 수 있다. 바로 고치는 게 좋다.

2. tests/test_iso16358_hspf_golden.py가 active 위치에 있는데 legacy calculator를 import함

현재 이 파일은 root-level active test인데, 상단에서 다음을 import한다.

from core._legacy.calculator_iso16358_legacy import ISO16358Calculator

파일 내부 reason에는 “archived legacy workbook diagnostics”라고 설명되어 있지만, 파일 위치와 이름은 여전히 active golden처럼 보인다.

이건 당장 실패를 만들지는 않는다. 실제 full suite도 통과한다.
하지만 앞으로 ISO HSPF golden을 볼 때 active ISO common golden인지, legacy workbook diagnostic인지 혼동될 가능성이 크다.

정리 방향은 둘 중 하나가 좋다.

이 파일을 tests/_legacy/로 이동하고 이름도 diagnostic 성격으로 바꾼다.
또는 active ISO common golden 부분과 legacy workbook diagnostic 부분을 분리한다.

다만 테스트 파일 이동/rename/split은 영향 범위가 있으니 문서 오타 수정과 섞지 말고 별도 작업으로 하는 게 맞다.

3. ui/calc_window.py는 아직 완전히 resolver-backed가 아님

ui/calculators_2point.py의 ISO CSPF UI는 dispatcher를 쓰지만, ui/calc_window.py에는 아직 다음 흐름이 남아 있다.

scan_configs()가 data/region_configs/*.json을 직접 스캔함
AHRI SEER2는 AHRICalculator(path)를 직접 생성함
EN tab은 아직 실질 연결이 약함
on_region_changed_iso()는 pass 상태

따라서 app_calculator.py 관점에서는 실행 가능성은 있지만, architecture 문서의 “UI resolver-backed config selection” 완료 상태는 아니다.

즉, 다음 단계에서 app_calculator를 키우려면 먼저 calc_window.py의 남은 direct config scan / direct calculator construction 경로를 audit하는 게 좋다.

4. iso_separation_result.md의 report 경로가 현재 상태와 어긋남

iso_separation_result.md에는 reports가 result_reports/active/044~053에 있다고 되어 있다.
하지만 이후 문서 lifecycle 작업으로 실제 파일은 result_reports/archive/044~053로 이동했고, 요약은 result_reports/summaries/054_summary-calculator-ui-iso-separation.md에 있다.

이건 큰 문제는 아니지만, root result doc만 보고 따라가면 경로가 틀린다.
active_documents_workflow_audit_result.md에는 이 이동이 잘 기록되어 있으므로, iso_separation_result.md에 “이후 054 summary에서 archive로 이동됨” 정도를 덧붙이면 좋다.

5. docs/REFACTOR_PLAN.md 일부가 완료 상태와 살짝 안 맞음

docs/REFACTOR_PLAN.md의 Calculator series reset 항목에서 Next work order 번호가 1, 2, 5, 6, 7처럼 남아 있고, 이미 일부 완료된 profile/dispatcher/UI 연결이 “나중 작업”처럼 보이는 문장이 있다.

큰 문제는 아니지만 다음 대화창/다음 Codex가 이 문서를 보면 완료된 작업을 다시 제안할 위험이 있다.

기준별 판정
PROJECT_CHARTER 기준

판정: 대체로 OK

계산식 신뢰성 확보 → 테스트 보호 → 입력 구조/profile → UI 연결 순서로 진행됐다.
다만 Predictor 연동 단계로 넘어가기 전에는 calculator result를 ML/inverse-search 입력으로 변환하는 adapter boundary가 아직 필요하다.

project_brief 기준

판정: OK

project_brief.md의 현재 상태는 ISO HSPF / AS/NZS 경계 분리 상태를 잘 요약하고 있다. 현재 full suite 결과도 문서에 적힌 방향과 충돌하지 않는다.

project_architecture 기준

판정: core boundary는 OK, UI boundary는 partial

Core calculator module boundary는 잘 맞는다.
하지만 UI는 아직 완전히 resolver-backed가 아니다. 특히 ui/calc_window.py가 direct config scan과 direct AHRI constructor를 유지하고 있다.

docs/designs 기준

판정: 대체로 OK

ISO common path에 AS/NZS workbook convention을 섞지 않았다.
AS/NZS compatibility는 opt-in 전용으로 분리했다.
historical case3 full-dump parity를 Z-phase로 둔 판단도 문서와 맞다.
active production caller가 legacy를 import하지 않는 것도 지켜진다.

단, active test 이름/위치에 legacy golden diagnostic이 남아 있는 점은 정리 필요하다.

ML 및 app_calculator.py 구현 가능성

판정: 기반은 생겼지만, 바로 ML/inverse-search 본구현으로 들어가긴 이르다

가능해진 것:

calculator별 책임 경계가 정리됨
profile resolver / dispatcher가 생김
ISO CSPF UI는 profile 기반으로 calculator를 생성함
계산기 result schema와 ML schema를 섞지 않는 방향이 문서화됨

아직 필요한 것:

calc_window.py의 남은 direct config scan 정리
calculator result envelope / adapter 설계
ML output → calculator input adapter 설계
candidate HW input과 region config가 섞이지 않도록 별도 schema 정의
app_calculator interactive smoke

## 지금 당장 할 수 있는 다음 작업
다음 작업 1: 문서/주석 정합성 cleanup

이 작업은 코드 동작을 바꾸지 않는 범위로 먼저 하는 게 좋다.

수정 대상:

core/calculator_iso16358.py
iso_separation_result.md
docs/REFACTOR_PLAN.md
필요 시 docs/WORK_PLAN.md

할 일:

core/calculator_iso16358.py 상단 docstring에서 “HSPF 미구현 / NotImplementedError” 문구 제거
iso_separation_result.md의 result_reports/active/044~053 경로가 이후 result_reports/archive/와 result_reports/summaries/054...로 정리되었다는 후속 상태 반영
docs/REFACTOR_PLAN.md의 Next work order 번호와 완료/미완료 표현 정리
docs/WORK_PLAN.md는 현재 내용이 대체로 맞으니, 필요하면 “다음은 UI resolver audit → adapter design” 정도만 보강

금지:

계산 로직 수정
golden expected 수정
테스트 파일 이동/rename
UI 동작 변경

다음 작업 2: legacy HSPF golden diagnostic 위치 정리

이건 별도 작업으로 분리하는 게 맞다.

수정 후보:

tests/test_iso16358_hspf_golden.py
tests/_legacy/
관련 report / work plan 문구

목적:

active ISO HSPF golden과 legacy workbook diagnostic의 혼동 제거
legacy calculator import가 root active test처럼 보이지 않도록 정리

금지:

ISO HSPF 계산 로직 수정
expected 값 수정
xfail 해제
fixture 구조 대규모 변경

다음 작업 3: app_calculator.py / calc_window.py UI resolver audit

그 다음으로 이 작업을 해야 ML/app_calculator 연결로 넘어가기 편하다.

확인 대상:

ui/calc_window.py
ui/calculators_2point.py
core/calculator_profiles.py
core/calculator_dispatcher.py

목적:

calc_window.py에 남은 direct JSON scan / direct calculator construction 경로 확인
현재 유지할 경로와 resolver로 옮길 경로 분리
app_calculator 실행 smoke에서 확인할 최소 범위 정의

다음 작업 4. UI resolver audit 결과에 따른 구현