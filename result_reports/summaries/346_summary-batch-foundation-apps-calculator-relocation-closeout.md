# Summary 346: Batch Foundation & Apps Calculator Relocation Closeout

## Summary Scope (범위)

본 문서는 `result_reports/active/`에 등록되어 있던 335번부터 345번까지의 보고서를 종합하고 마치는 문서이다. 본 개발 주기는 Tkinter 계산기의 batch foundation 폴더링 정리에서 시작하여, 루트 entrypoint 구조 개편 및 `apps/calculator` 패키지 구조로의 최종 이주(relocation)까지를 범위로 다룬다.

## 대상 보고서 (Covered Active Reports)

- **335**: Active report lifecycle cleanup before batch foundation audit
- **336**: Active report lifecycle remaining-active wording correction
- **337**: Batch foundation foldering audit
- **338**: Batch foundation foldering implementation - Slice 1 (models/specs 이주)
- **339**: 338 report reference link typo correction
- **340**: Batch foundation foldering implementation - Slice 2 (widgets/viewports/controllers 이주)
- **341**: Align post-batch-foldering next action with apps package audit
- **342**: Calculator-first apps package architecture audit before entrypoint handover
- **343**: Charter/architecture policy alignment doc update
- **344**: Apps calculator skeleton creation and entrypoint handover
- **345**: Relocate ui_tk to apps/calculator/ui

## Major Decisions (주요 결정 사항)

1. **관심사 격리(SoC)를 위한 batch foundation 패키지화**: 루트에 흩어져 있던 batch-related widgets, models, controllers를 단일 소스 패키지인 `ui_tk/batch/`로 격리 통합함.
2. **장기 지향적 `apps/` 패키지 구조 확정**: 루트의 calculator-only entrypoint를 `apps.calculator`로 질서 있게 진입하도록 보장함.
3. **PyQt5 preservation 원칙과의 tension 해소**: `PROJECT_CHARTER.md` 및 `project_architecture.md`를 보정하여, 계산기 UI는 Tkinter로 이주하고 legacy PyQt는 train/predict용으로 유지하되, 향후 PySide6로 새로이 작성하는 방향으로 toolkit 로드맵 정책을 동기화함.
4. **Direct Import 갱신 및 Shim 배제**: 레거시 임포트 경로 호환용 shim을 남기지 않고, 소스 및 테스트 전 영역에 걸쳐 direct import 경로를 원스텝으로 갱신하여 패키지 구조의 청결함을 극대화함.

## Implemented Changes by Arc (아크별 변경 사항)

1. **Batch Foundation Foldering**:
   - `batch_case_table.py`, `batch_matrix_table.py`, `batch_table_viewport.py`, `batch_controller.py`, `batch_table_controller.py`, `batch_table.py`, `batch_models.py`, `batch_matrix_models.py` 등 8개 파일을 `ui_tk/batch/` 패키지로 이동 완료.
2. **Apps Package Architecture Alignment**:
   - `PROJECT_CHARTER.md` 및 `project_architecture.md`를 갱신하여 PyQt5, Tkinter, PySide6 툴킷 정책과 `apps/{calculator,train,predict}/` 패키지 경계를 명문화함.
3. **Calculator Entrypoint Handover**:
   - `apps/` 및 `apps/calculator/` 패키지 skeleton을 신설하고 entrypoint인 `apps/calculator/app.py`를 작성함.
   - 루트 `app_calculator.py`를 `apps.calculator.app:main` 위임 wrapper로 전면 전환함. `app_calculator_tk.py`를 deprecated compatibility wrapper로 보정함.
4. **Calculator Tk UI Relocation**:
   - 기존 `ui_tk/` 패키지 하위의 53개 파일 전체를 `apps/calculator/ui/` 하위로 `git mv` 이동 처리하고, 소스 및 테스트 전역의 모든 임포트 경로를 `apps.calculator.ui.*`로 원스텝 교정함.

## MVC/SoC/Clean Architecture Alignment

- **View**: 마이그레이션된 Tkinter UI 위젯들이 `apps/calculator/ui/` 패키지 하위로 응집됨.
- **Controller/Orchestration**: batch case/matrix controller와 `table_controller` 등이 `apps/calculator/ui/batch/`로 깔끔하게 정돈됨.
- **Model**: toolkit-neutral models/specs가 `ui/` 하위의 PyQt legacy와 격리되어 `apps/calculator/ui/batch/models.py` 등으로 온전히 분리됨.

## 보존된 경계 (Retained Boundaries)

- **ui/**: `app_train.py`, `app_predict.py` 및 legacy PyQt calculator reference 등이 사용하는 legacy PyQt multi-app UI로서 어떠한 수정 없이 원본 상태를 고스란히 보존함.
- **train/predict**: 현행 PyQt 구조를 온전히 유지하며, `apps/train` 및 `apps/predict` 패키지는 실제 생성하지 않고 future PySide6 reserved boundary 상태로 유지함.
- **core/calculator**: 계산 공식, region config schema, dispatcher 등의 core 계산 엔진 및 constants는 전혀 수정하지 않고 경계를 완벽히 보호함.

## 검증 하이라이트 (Validation Highlights)

- 마이그레이션 진행 중 어떠한 비즈니스 로직, 레이아웃, 계산 동작, 컨트롤러 바인딩의 변경도 없음을 검증함.
- `apps.calculator.ui` 이주 완료 후, 총 108개의 focused pytests 및 `check_code_structure.py` 검사를 수행하여 100% 회귀 방어(regression-free) 및 구조적 깨끗함(clean warning)을 검증함.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`를 최종 재생성하여 변경 사항을 명문화하고 Freshness 상태를 충족함.

## 정리 후 남은 Active Reports (Remaining Active Reports)

- 본 summary arc 닫힘에 따라 active report 하위의 모든 레거시 보고서(335~345)를 archive로 이동 완료함.
- 본 정리 실행 결과 보고서(`347_active_report_lifecycle_cleanup_after_apps_calculator_relocation.md`)만 active에 잔류함.

## Lifecycle Wording

- active report count is below lifecycle threshold

## 차기 과제 추천 (Next Action Recommendation)

1. **Calculator PyQt reference retirement preflight**
   - Tkinter calculator UI 및 `apps/calculator` 이주가 안전하게 완성됨에 따라, legacy PyQt calculator 코드(`ui/calc_window.py` 등)의 안전한 은퇴(retirement) 가능 여부를 preflight 진단하고 pre-cleanup 준비 절차를 수립한다.
