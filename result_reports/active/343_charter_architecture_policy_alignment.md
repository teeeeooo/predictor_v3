# Report 343: Charter and Architecture Policy Alignment

## Goal (목표)

- 342 calculator-first apps package architecture audit 결과를 반영하여, `PROJECT_CHARTER.md`와 `docs/architecture/project_architecture.md`의 예전 UI 정책 표현을 수정 및 보정함으로써 현재의 아키텍처 방향과 미래 이주 계획을 명확히 동기화한다.

## 확인한 기준 문서 (References)

- `PROJECT_CHARTER.md` (프로젝트 목적, 핵심 아키텍처 원칙, 장기 마일스톤)
- `docs/architecture/project_architecture.md` (파일 구조, UI 및 데이터 흐름, Calculator Boundary)
- `result_reports/active/342_calculator_first_apps_package_architecture_audit.md` (Tension 해소 방안 및 slice 제안)
- `docs/WORK_PLAN.md` (Next Actions 및 Recent History)

## PROJECT_CHARTER.md 보정 내용

- **UI 툴킷 정책 (UI Toolkit Policy) 추가**: 기존의 "PyQt5 유지" 규칙을 현재 로드맵에 맞추어 보정함.
  - Calculator UI 전환은 현재 Tkinter 마이그레이션이 active direction임을 명시.
  - Train/Predict의 기존 legacy PyQt5 경로는 재작성 전까지 유지함을 명시하고 PyQt6로의 전환은 차단함.
  - 향후 Train/Predict의 신규 재작성은 별도 Design Gate를 거쳐 PySide6를 타겟으로 할 수 있음을 장기적으로 선언함.
- **UI 분리 및 경계 (UI Separation & Boundary) 추가**:
  - Calculator, Train, Predict 애플리케이션의 화면 및 비즈니스 로직 책임을 구분하여 작업을 서로 섞지 않음을 명문화함.
  - 장기적인 애플리케이션 패키지 경계는 `apps/{calculator,train,predict}/` 구조를 지향함을 선언함.
- **장기 마일스톤 (Phase 2) 보정**:
  - Phase 2 Calculator UI v1이 Tkinter 기반 마이그레이션 방향임을 명시함 (`Phase 2 — Calculator UI v1 (Tkinter Migration)`).

## project_architecture.md 보정 내용

- **Section 1. 파일 구조 (File Structure) 보정**:
  - `ui/` 패키지를 `app_calculator.py`, `app_train.py`, `app_predict.py`가 공유하는 레거시 PyQt5 multi-app UI 경로로 재정의함.
  - `ui_tk/` 패키지를 calculator-only Tkinter 기반 마이그레이션 소스로 규정하고, generic `ui`로 이름을 변경하지 않도록 가이드라인 명문화함.
  - `apps/` 패키지 경계를 명문화하여 `apps/calculator` 하위에 Tkinter UI가 들어올 것이며, `apps/train` 및 `apps/predict`는 향후 PySide6 재작성 시점에 생성할 reserved boundary로 개념화함.
- **Section 3.3 UI Model/View Guardrails 보정**:
  - 기존 PyQt-specific table guardrail 내용들이 legacy PyQt UI(`ui/` 패키지 하위의 train/predict 화면)에만 국한되는 규칙임을 분명히 기술하여 신규 Tkinter UI(`ui_tk/`)와의 혼동을 원천 차단함.
- **Section 5. UI / calc_window.py routing contract 보정**:
  - `calc_window.py` 및 관련 PyQt5 코드가 read-only reference이며 `apps/calculator` 구조화 완료 시 은퇴(retire)할 예정임을 명시하여, future apps 마이그레이션 흐름과 혼동되지 않도록 보정함.

## PyQt5 / Tkinter / PySide6 Policy 정렬 결과

- **Calculator**: Tkinter가 활성 개발(active migration) 및 이주 타겟임.
- **Train/Predict (Legacy)**: PyQt5 기반으로 현행 유지하며, 함부로 PyQt6 등으로의 전환을 시도하지 않음.
- **Train/Predict (Future)**: 향후 재개발 시에는 PySide6로 새로이 작성하여 현대적인 아키텍처와 toolkit 표준을 충족함.

## apps/{calculator,train,predict}/ Boundary 정리

- 장기 지향적으로는 `apps/` 아래 세 개의 도메인 패키지가 위치하게 됨.
- 단기적으로는 calculator 이주만을 apps 하위에서 물리적으로 취급함 (`apps/calculator/ui/`).
- train/predict는 future PySide6 rewrite 전까지 reserved boundary로만 개념적으로 분류함.

## Train/Predict를 지금 Migration 대상에서 제외한 이유

- train/predict의 경우, 현재 마이그레이션할 즉각적인 요구가 없고 PyQt5 기반으로 안정적으로 동작하고 있음. 향후에 PySide6 기반으로 새롭게 재작성할 계획이 확정되어 있으므로, 불필요하게 현재 stable 상태의 코드를 건드리지 않음으로써 regression 위험을 방지하고 calculator Tkinter 이주 마무리에 개발 자원을 집중하기 위함임.

## WORK_PLAN 업데이트 여부

- `docs/WORK_PLAN.md`에 본 문서 보정 (343) 완료를 추가하고, 차기 Next Actions의 최상단을 `Apps package skeleton creation and calculator entrypoint handover`로 정렬함.

## 제외 범위 (Excluded Scope)

- **물리적 소스/파일 변경 없음**: `apps/` 폴더 생성 및 python 소스 파일 이동, import path 갱신 없음.
- **실행 금지**: calculator entrypoint handover, PyQt calculator retire, train/predict rewrite 등의 실제 구현은 전혀 수행하지 않음.
- **공통/핵심 모듈 변경 없음**: `calculator/core` 및 profile/region config, tests/fixtures의 수정 없음.
- **기타 문서 변경 없음**: `docs/code_map/CODEBASE_REFERENCE_MAP.md` 수정 또는 재생성 없음. `project_brief.md`, `project_log.md` 및 `result_reports/memory/project_memory_seed.md` 파일은 전혀 수정하지 않음 (unchanged).

## 검증 결과 (Verification Results)

- `python3 -B tools/check_code_structure.py` 통과 (OK)
- `git diff --check` 상의 whitespace 문제 없음 (OK)
- `git status --short` 확인 결과 허용된 3개 문서 파일(`PROJECT_CHARTER.md`, `docs/architecture/project_architecture.md`, `docs/WORK_PLAN.md` 및 본 active report) 외의 변경 사항 없음 확인 (OK)

## Project Memory Delta

- none

## Lifecycle Note

- active report count is below lifecycle threshold

## Next Action suggested (차기 과제)

1. **Apps package skeleton creation and calculator entrypoint handover**
