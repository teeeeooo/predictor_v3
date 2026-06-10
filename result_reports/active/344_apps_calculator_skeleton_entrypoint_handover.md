# Report 344: Apps Calculator Package Skeleton and Entrypoint Handover

## Goal (목표)

- 343 Charter/architecture policy alignment 결과에 따라 calculator app package skeleton을 생성하고, root entrypoint들의 실행 대상을 PyQt에서 Tkinter calculator-only (`apps.calculator.app`) 방향으로 핸드오버를 완료한다.

## 기준으로 사용한 Reports (References)

- [342_calculator_first_apps_package_architecture_audit.md](342_calculator_first_apps_package_architecture_audit.md)
  - Candidate A/B 권장 방향 및 슬라이스 계획을 참조함.
- [343_charter_architecture_policy_alignment.md](343_charter_architecture_policy_alignment.md)
  - UI toolkit 정책(Tkinter active direction, legacy PyQt5 train/predict 유지, PySide6 future rewrite) 및 `apps/` 패키지 경계 명문화 내용을 참조함.

## 생성한 apps/calculator skeleton

- 다음 3개 파일을 생성하여 `apps.calculator` 패키지 구조를 갖춤:
  - `apps/__init__.py`: 상위 `apps` 패키지 초기화 파일.
  - `apps/calculator/__init__.py`: `calculator` 하위 패키지 초기화 파일.
  - `apps/calculator/app.py`: thin app entrypoint로, `ui_tk.calculator_app.main`을 호출하여 Tkinter 계산기 화면을 실행함. PyQt에 대한 어떠한 의존성도 포함하지 않음.

## app_calculator.py Handover 내용

- root `app_calculator.py`를 PyQt 실행 코드에서 `apps.calculator.app.main()`을 호출하는 thin wrapper로 전면 전환함.
- root level에서 PyQt QApplication 및 `ui.calc_window`를 직접 import/execute하던 레거시 동작을 배제함.

## app_calculator_tk.py Compatibility/Deprecated Wrapper 보정 내용

- root `app_calculator_tk.py`를 임시 compatibility/deprecated wrapper로 갱신하여 동일하게 `apps.calculator.app.main()`을 위임 호출하도록 변경함.
- 기존의 "NOT a replacement for app_calculator.py" 또는 feasibility-spike 성격을 나타내던 오래된 문구 및 경고 주석을 제거하고, `apps.calculator.app`이 정식 entrypoint임을 주석으로 명시함.

## Legacy PyQt Calculator Source를 수정하지 않은 이유

- `ui/calc_window.py`를 포함한 기존 PyQt5 기반 계산기 소스 코드는 마이그레이션이 완료되고 완전히 안정화될 때까지 안정적인 read-only reference로서 보존해야 하므로 이번 작업에서 변경을 배제함.

## Train/Predict를 건드리지 않은 이유

- `app_train.py` 및 `app_predict.py`와 `ui/` 하위의 legacy PyQt train/predict 전용 코드들은 현재 이주 대상이 아니며, 차후 PySide6 재개발 시점에 다루어지도록 reserved boundary로 남겨두었기 때문임.

## Tests 및 Validation 결과

- `tests/test_apps_calculator_entrypoints.py`를 추가하여 아래 사항들을 철저히 검증 완료함:
  - `apps.calculator.app`, `app_calculator`, `app_calculator_tk`는 import 시 GUI 메인루프를 실행하여 테스트를 블로킹하지 않음 (Side-effect-free import).
  - `apps.calculator.app.main` 호출 시 underlying Tkinter `main`이 정상 호출됨 (monkeypatch 검증).
  - `app_calculator.main` 및 `app_calculator_tk.main`이 canonical `apps.calculator.app.main`과 동일한 함수 개체를 참조 및 위임함.
- `python3 -B -m pytest tests/test_apps_calculator_entrypoints.py` 유닛 테스트 패스 (4/4 passed).
- `python3 -B tools/check_code_structure.py` 통과 (OK).

## CODEBASE_REFERENCE_MAP.md Regeneration 결과

- `apps/` 패키지 신설 및 entrypoint 변경에 따라 `docs/code_map/CODEBASE_REFERENCE_MAP.md`를 재생성하였으며, `freshness` 검증(FRESH)을 통과 완료함.

## WORK_PLAN 업데이트 여부

- `docs/WORK_PLAN.md`에 본 마이그레이션 및 핸드오버 (344) 완료를 추가하고, 차기 우선순위를 `ui_tk relocation to apps/calculator/ui`로 갱신함.

## 제외 범위 (Excluded Scope)

- **UI 코드 이주 제외**: `ui_tk/` 하위 파일들을 `apps/calculator/ui/`로 실제 이동하거나 import path를 갱신하는 작업은 다음 슬라이스에서 수행함.
- **물리적 폴더 생성 제한**: `apps/train` 및 `apps/predict` 폴더는 생성하지 않음.
- **기타 core 및 config 수정 제외**: `calculator/core`, profile/region configs, golden/fixtures의 변경 사항 없음.
- **Project log 및 memory seed 유지**: `project_log.md` 및 `result_reports/memory/project_memory_seed.md` 파일은 전혀 수정하지 않음 (unchanged).

## Project Memory Delta

- none

## Lifecycle Note

- active report count is below lifecycle threshold

## Next Action suggested (차기 과제)

1. **ui_tk relocation to apps/calculator/ui**
