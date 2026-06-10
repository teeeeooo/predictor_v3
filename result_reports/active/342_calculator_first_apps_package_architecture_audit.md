# Report 342: Calculator-First Apps Package Architecture Audit

## Goal (목표)

- calculator entrypoint handover 전에 app package boundary를 먼저 audit하여, 향후 `apps/{calculator,train,predict}/` 패키지 아키텍처로 나아가기 위한 안전한 구조적 합의와 이주(migration) 계획을 확립한다.

## 확인한 기준 문서 (References)

- `AGENT_TASK_ROUTER.md` (Documentation Sync, Result Report Workflow, Architecture, UI)
- `PROJECT_CHARTER.md` (프로젝트 목적, UI 분리 원칙, 장기 마일스톤)
- `project_brief.md` (현재 상태, 실행 로드맵 관리 원칙)
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` (클린 아키텍처 책임 경계)
- `docs/architecture/project_architecture.md` (파일 구조, UI/데이터 흐름, UI/calc_window.py 라우팅 계약)
- `docs/WORK_PLAN.md` (Next Actions 및 Recent History)

## 현재 app/UI ownership inventory

- **루트 Entrypoint 분류**:
  - `app_calculator.py`: legacy PyQt calculator entrypoint. `ui.calc_window` 모듈을 로드하여 실행.
  - `app_calculator_tk.py`: current Tkinter calculator migration entrypoint (feasibility spike). `ui_tk.calculator_app` 모듈을 로드하여 실행.
  - `app_train.py`: legacy PyQt train entrypoint. `ui.train_window` 모듈을 로드하여 실행. 현 시점의 migration 대상이 아님 (Reserved future boundary).
  - `app_predict.py`: legacy PyQt predict entrypoint. `ui.predict_window` 모듈을 로드하여 실행. 현 시점의 migration 대상이 아님 (Reserved future boundary).
- **UI 패키지 소유 분류**:
  - `ui/`: legacy PyQt multi-app UI. `app_calculator.py`, `app_train.py`, `app_predict.py`에서 공유 중.
  - `ui_tk/`: calculator-only Tkinter UI migration source.

## PROJECT_CHARTER / project_architecture Tension

- `PROJECT_CHARTER.md` 제3항에는 "PyQt5 유지: PyQt5를 표준으로 유지하며, PyQt6로의 전환은 금지합니다."라고 명시되어 있음.
- 그러나 현재 실제 로드맵 및 memory seed 상의 방향은 다음과 같음:
  1. **Calculator**: PyQt5 기반 UI를 Tkinter(`ui_tk/`)로 완전히 전환 중이며, 완료 시 PyQt5 calculator-only 코드는 은퇴(retire) 가능함.
  2. **Train/Predict**: 현재 PyQt5 상태를 유지하며 calculator와 물리적으로 결합하지 않고 분리하되, 향후 PyQt5를 버리고 PySide6 기반으로 새로 작성(rewrite)할 장기 방향을 가짐.
- **Tension 해소 방안**: Charter의 "PyQt5 유지" 문구는 legacy multi-app 및 future PySide6 전환 방향을 모두 포괄하도록 갱신이 필요함. 다음 문서 갱신 slice(Charter/architecture policy alignment)를 제안하여 이 tension을 합리적으로 해소하도록 함.

## 후보 구조 비교 (Candidate Structures Comparison)

### Candidate A. Calculator-only package first
- **구조**:
  ```text
  apps/
    calculator/
      app.py
      ui/
  ```
  - `app_train.py`, `app_predict.py`와 `ui/` legacy PyQt는 루트 및 현 위치를 그대로 유지.
- **판단**:
  - *장점*: calculator 이주 영역을 가장 좁게 유지하여 short-term 리스크가 없음. train/predict를 건드리지 않아 regression 위험 차단.
  - *단점*: train/predict의 reserved boundary가 폴더 구조상으로 즉시 드러나지 않음.

### Candidate B. Full apps skeleton reserved only
- **구조**:
  ```text
  apps/
    calculator/
      app.py
      ui/
    train/
      (reserved only)
    predict/
      (reserved only)
  ```
  - 단, 이번 audit 단계에서는 실제 apps 폴더 및 skeleton 파일을 물리적으로 생성하지 않고 설계상으로만 지정함.
- **판단**:
  - *장점*: 장기 구조 방향성이 가장 명확하고 깨끗하게 드러남.
  - *단점*: 실제 파일/폴더 작성 시 불필요한 empty directory 관리 비용 발생 가능. (물리적 생성 없이 개념적 reserved boundary로 두는 편이 더 우수함)

### Candidate C. Keep ui_tk name and only handover app_calculator.py
- **구조**:
  - `app_calculator.py` -> `ui_tk.calculator_app`으로 리다이렉트만 수행.
  - `ui_tk/` 및 `ui/` 폴더는 명칭 변경 없이 루트에 유지.
- **판단**:
  - *장점*: 파일 이동이나 패키지 구조 신설이 없어 단기 안정성은 극대화됨.
  - *단점*: `ui_tk`라는 명칭이 generic UI처럼 오해받을 수 있으며, 장기 `apps/{calculator,train,predict}/` 목표 구조로의 전환을 지연시킴.

## 권장 구조 (Recommended Candidate)

- **선택**: **Candidate B 개념적 reserved 구조를 포괄하는 Candidate A 방식**
- **이유**:
  - **관심사 격리**: calculator migration을 우선 타겟팅하되, 현재 정상 작동 중인 `app_train.py` / `app_predict.py` 및 `ui/` legacy PyQt를 전혀 침범하지 않음.
  - **오해 방지**: `ui_tk/`는 calculator-only UI이므로 generic UI로 인식되지 않도록 `apps/calculator/ui/` 하위로 숨기고, 기존 `ui_tk/` 루트 구조는 이주 완료 후 완전 정리함.
  - **확장성**: `apps/train` 및 `apps/predict`를 문서상 reserved future boundary로 규정하여, 향후 PySide6 rewrite 작업 시 apps 패키지 하위에서 충돌 없이 질서 있게 구현할 수 있음.

## Train/Predict를 지금 제외하는 이유

- 사용자가 현재 train/predict를 마이그레이션할 즉각적인 요구가 없으며, 향후 PyQt5 legacy 코드를 버리고 PySide6 기반으로 새로 작성하기로 확정하였기 때문임. 따라서 불필요한 과행동을 방지하고 calculator 안정화에 집중하기 위해 train/predict는 reserved future boundary로만 선언하고 마이그레이션 대상에서 배제함.

## Next Implementation/Documentation Slice 설계

실제 구현 리스크와 이주(churn)를 최소화하기 위해 아래와 같이 단계별 슬라이스로 구현을 전개할 것을 추천함.

### Slice 1: Charter/architecture policy alignment doc update (추천)
- **목표**: `PROJECT_CHARTER.md` 및 `project_architecture.md` 문서를 갱신하여 PyQt5 유지 원칙과의 tension을 해소하고, `apps/{calculator,train,predict}/` 장기 지향점 및 Reserved boundary를 명문화함.
- **수정 대상**: `PROJECT_CHARTER.md`, `docs/architecture/project_architecture.md`
- **금지 대상**: 소스 코드 수정, apps 폴더 생성 등 모든 물리적 변경 금지.
- **검증**: `git diff`, document freshness.
- **위험**: 없음 (순수 문서 동기화).

### Slice 2: Apps package skeleton creation and calculator entrypoint handover
- **목표**: `apps/calculator/` 폴더를 생성하고 패키지를 초기화한 후, 루트 `app_calculator.py`가 Tkinter calculator-only entrypoint를 얇은 wrapper 형태로 바라보고 시작하도록 핸드오버함.
- **수정 대상**: `apps/calculator/__init__.py`, `apps/calculator/app.py`, 루트 `app_calculator.py`
- **금지 대상**: `ui_tk/` 폴더의 직접적인 파일 이동/삭제 금지.
- **검증**: `app_calculator.py` offscreen 실행 및 헬프 동작 테스트.
- **위험**: Tcl/Tk loading mismatch.

### Slice 3: ui_tk relocation to apps/calculator/ui
- **목표**: `ui_tk/` 내부 파일들을 `apps/calculator/ui/` 패키지로 실제 이동하고, 내부 import 경로들을 신규 경로로 일괄 갱신함. 루트 `app_calculator_tk.py`는 deprecated 처리 후 삭제함.
- **수정 대상**: `ui_tk/` 하위 전체 파일 이동, 관련 테스트 파일 및 `apps/calculator/` 내부 import path 일괄 수정.
- **금지 대상**: `ui/` legacy PyQt 및 train/predict logic 변경 금지.
- **검증**: `python3 -B tools/check_code_structure.py`, 모든 batch/matrix/controller/profile focused pytests 실행.
- **위험**: 대규모 import path 수정으로 인한 reference 깨짐. Mitigation: regex replace 및 build_reference_map freshness check 활용.

## WORK_PLAN 업데이트 여부

- `docs/WORK_PLAN.md`에 본 audit (342) 완료를 추가하고, 차기 우선순위를 `Slice 1: Charter/architecture policy alignment doc update`로 갱신함.

## 제외 범위 (Excluded Scope)

- **물리적 파일/폴더 변경 없음**: `apps/` 폴더 생성 및 python 소스 파일 이동, import path 갱신 없음.
- **실행 금지**: calculator entrypoint handover, PyQt calculator retire, train/predict rewrite 등의 실제 구현은 전혀 수행하지 않음.
- **공통/핵심 모듈 변경 없음**: `calculator/core` 및 profile/region config, tests/fixtures의 수정 없음.
- **기타 문서 변경 없음**: `docs/code_map/CODEBASE_REFERENCE_MAP.md` 수정 또는 재생성 없음. `project_log.md` 및 `result_reports/memory/project_memory_seed.md` 파일은 전혀 수정하지 않음 (unchanged).

## 검증 결과 (Verification Results)

- `python3 -B tools/check_code_structure.py` 통과 (OK)
- `git diff --check` 상의 whitespace 문제 없음 (OK)
- `git status --short` 확인 결과 허용된 2개 파일(`docs/WORK_PLAN.md` 및 본 audit report) 외의 변경 사항 없음 확인 (OK)

## Project Memory Delta

- none

## Lifecycle Note

- active report count is below lifecycle threshold

## Next Action suggested (차기 과제)

1. **Charter/architecture policy alignment doc update**
