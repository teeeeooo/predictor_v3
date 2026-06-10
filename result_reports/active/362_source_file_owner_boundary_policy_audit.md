# Active Report 362: Source File Owner Boundary Policy and Guard Audit

## 목표 (Goal)
* 신규 source file 생성 시 broad folder에 flat하게 파일이 분산 및 방치되는 문제를 repo-wide 정책으로 정립하고, 정적 검사기(guard)에 반영할 수 있는 규칙 후보군을 설계 및 문서화한다.
* 이번 작업은 policy/audit slice이며, 실제 guard 구현 및 source 이동/rename은 수행하지 않는다.

## 기준으로 확인한 docs/reports (Reference Sources)
* [AGENT_TASK_ROUTER.md](../../AGENT_TASK_ROUTER.md): Architecture / Coding / Documentation Sync / Structure Guard / Result Report Workflow 섹션
* [PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md](../../docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md): MVC 및 UI/UX 책임 경계 규칙
* [docs/architecture/project_architecture.md](../../docs/architecture/project_architecture.md): 파일 및 패키지 구조 설명
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md): Recent History 및 Next Actions
* [result_reports/active/361_en14825_seer_model_adapter_correction.md](361_en14825_seer_model_adapter_correction.md): EN14825 패키지 경계 보정 결과

## Policy Gap 분석 (Policy Gaps)
* **Preflight 부재**: 신규 소스 파일 생성 전에 소유주(owner) 및 패키지 경계를 명시적으로 질의하는 preflight 절차가 부재했습니다.
* **Sections 오용 위험**: `apps/calculator/ui/sections/` 폴더가 개별 피처의 model, adapter, table model 등을 무분별하게 추가하는 dumping ground로 오용될 위험이 상존했습니다.
* **Core flat 부채**: `core/` root 폴더에 신규 calculator 규격 외에 보조용 flat helper/misc 파일들이 쌓일 우려가 있었습니다.
* **Tests 구조 불명확**: 소스 코드의 패키지 구조를 반영한 focused test naming 및 mapping 기준이 정리되지 않았습니다.
* **Guard 미지정**: `check_code_structure.py` 등 자동화 도구로 탐지할 수 있는 파일 생성 차단/경고 규칙이 공식 문서화되어 있지 않았습니다.

## 수정 파일 (Modified Files)
* [PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md](../../docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md)
* [AGENT_TASK_ROUTER.md](../../AGENT_TASK_ROUTER.md)
* [docs/architecture/project_architecture.md](../../docs/architecture/project_architecture.md)
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md)

## 확정한 Repo-wide Source File Owner Boundary Policy
* **Owner Boundary First**: 모든 신규 소스 파일 생성 전 파일의 도메인/피처 소유주를 먼저 확정합니다.
* **Flat File dumping 방지**: `apps/calculator/ui/`, `core/`, `tests/`, `tools/` 등 root급 broad folder에 개별 피처 전용 flat file을 추가하는 것을 금지합니다.
* **독립 패키지 지향**: 데이터 모델, 어댑터, 테이블 모델, 뷰, 컨트롤러 등으로 파일 확장성이 예상되는 경우, `apps/calculator/ui/en14825/`와 같이 독립된 피처 패키지 디렉토리를 신설하여 응집도를 높입니다.
* **Halt and Report**: 패키지 경계 설계나 신설 작업이 현재 배정된 task 범위를 넘어서는 경우, 임시 flat file을 broad folder에 뿌리지 않고 작업을 멈추고 논의합니다.
* **No New Flat Debt**: 기존 레거시 flat 구조는 별도 refactor 작업이 배정될 때까지 임시 유지할 수 있으나, 신규 flat 부채 추가는 철저히 배제합니다.

## AGENT_TASK_ROUTER Preflight 보정 요약
* 모든 코딩 작업에서 **신규 source file을 생성할 때**에만 선택적으로 강제되는 **New Source File Owner Preflight** 절차를 `AGENT_TASK_ROUTER.md`에 추가하였습니다.
* 파일 생성 전: (1) 소유 도메인 확인, (2) 기존 소유 패키지 유무 확인, (3) 다중 파일 확장성 판단, (4) 피처 패키지 지향, (5) 범위 초과 시 중단 및 보고 질문을 순서대로 수행합니다.

## Architecture Doc 보정 요약
* `docs/architecture/project_architecture.md` 파일의 파일 구조 설명 영역을 보정하였습니다:
  * **`apps/calculator/ui/`**: 공용 Reusable UI/Common Shell 컴포넌트 파일들과 개별 `en14825/`, `batch/` 와 같은 Feature Package 디렉토리로 구조적 역할을 구분합니다.
  * **`sections/`**: 얇은 Glue/Routing/Registration 용도로만 사용을 제한하고 dumping ground로 사용하지 않습니다.
  * **`core/`**: 기존 flat calculator들을 legacy public surface로 유지하되, 신규 flat calculator/helper 추가는 설계 심사 없이 금지합니다.
  * **`tests/`**: 소스 코드 패키지 구조를 정직하게 반영한 focused tests 구성을 최우선 정책으로 삼습니다.

## Guard 후보군 설계 (Guard Candidates)
향후 `tools/check_code_structure.py`에 구현할 정적 검사 규칙 후보군은 다음과 같습니다:

1. **UI Root Flat File 가드**:
   * 대상 디렉토리: `apps/calculator/ui/`
   * 규칙: 허용된 공용 쉘/컴포넌트 파일 목록(allowlist) 외에 피처 종속적인 접두사(예: `en14825_*.py`, `saso_*.py`)를 가진 flat file 추가 감지 시 오류 발생.
2. **Sections Flat File 가드**:
   * 대상 디렉토리: `apps/calculator/ui/sections/`
   * 규칙: 섹션 폴더 내부에는 오직 UI glue/view 성격만 허용하며, `*_adapter.py`, `*_models.py`, `*_table_model.py` 등의 파일 추가 감지 시 오류 발생.
3. **Core Root Flat Helper 가드**:
   * 대상 디렉토리: `core/`
   * 규칙: `calculator_*.py` 규격 엔진 본체 외에 `*_helper.py`, `*_misc.py`, `*_utils.py` 등 보조용 flat file 생성 시 경고/오류 발생.
4. **Tests Naming & Mapping 가드**:
   * 대상 디렉토리: `tests/`
   * 규칙: `test_*_everything.py` 또는 `test_*_all.py` 형태의 mega-test 파일명 사용을 경고하고, 테스트 대상 소스 경로를 1:1로 매핑하는 naming (`test_apps_calculator_ui_<package>.py`)을 강제.
5. **Allowed Package Registry 검증**:
   * 규칙: UI 하위의 허용된 패키지 목록(`en14825/`, `batch/` 등) 외의 새로운 하위 디렉토리가 감지될 경우 모니터링/경고.

## 구현하지 않은 범위 (Non-goals in this slice)
* `tools/check_code_structure.py`에 실제 guard 검사 코드 구현.
* 기존 flat 파일들의 패키지 이동 및 rename refactor.
* EN14825 section integration 및 batch, SCOP 구현.

## 검증 결과 (Verification Results)
* `git status --short`: 수정 대상 4개 문서 및 신규 362 report 외 clean 상태 확인.
* `python3 -B tools/check_code_structure.py`: **code structure guard: OK (no findings)**
* `git diff --check`: whitespace 에러 없음.

## Next Action
* **Source file owner boundary guard implementation** (정적 검사기 가드 구현 및 ruleset 적용).
