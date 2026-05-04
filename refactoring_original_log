## 2026-05-04 — Calculator UI 기본 구조 안정화 방향 결정

### Tried
- ISO/CSPF Calculator UI를 단건 입력 중심의 `single-input-first` 구조로 전환하는 방향을 검토했다.
- 기존 batch-first 화면에서 벗어나, 메인 화면은 1개 시험 데이터 입력과 규격/profile별 결과 비교에 집중하도록 방향을 잡았다.
- `QTableView + QAbstractTableModel` 기반을 유지하면서, 메인 입력부도 스프레드시트처럼 2행 x N열 TSV 붙여넣기를 지원하는 `ProfileInputGridModel / ProfileInputGridView` 구조로 정리하기로 했다.
- PyQt5 기반에서 UI 구현을 계속 진행할지, PyQt6 또는 웹 UI로 전환할지 검토했다.
- `matplotlib`, `pyqtgraph` 등 신규 그래프 의존성 추가 여부를 검토했으나, 배포 용량과 패키징 리스크 때문에 보류했다.
- QPainter 기반 단순 graph와 QTableView 기반 trace table을 유지하는 방향을 선택했다.

### Result
- PyQt5를 유지하기로 결정했다.
- PyQt6 전환은 금지하기로 했다.
- core 계산 로직, calculator public API, Train/Predict UI는 이번 UI 작업에서 건드리지 않기로 했다.
- EN14825, AHRI210240, Korea CSPF 실제 UI 구현은 아직 진행하지 않기로 했다.
- ISO16358/CSPF UI는 다음 profile 구조로 정리하기로 했다.
  - ISO / ISEER 2점식
  - Hong Kong CSPF
  - SASO T3
- 메인 입력부는 `QLineEdit` 나열 방식이 아니라 `QTableView + QAbstractTableModel` 기반의 `ProfileInputGrid`로 유지하기로 했다.
- `ProfileInputGrid`는 2행 x N열 구조를 기본으로 한다.
  - row 0 = `Capacity [W]`
  - row 1 = `Power [W]`
  - column = profile별 test point
- 메인 입력부도 다중 셀 paste가 필수 UX라는 점을 확정했다.
- 1행 x 2N pair paste는 유지보수 복잡도 때문에 지원하지 않기로 했다.
- Multi 입력 dialog는 당분간 ISO/ISEER 2점식 전용으로 유지하고, Hong Kong Multi / SASO T3 Multi는 후속으로 남겼다.
- ISO16358-2 HSPF 계산기 구현은 별도 대화창에서 진행하고, 계산 엔진과 golden 검증이 끝난 뒤 UI profile로 연결하기로 했다.

### Failed / Risk
- 초기 UI 구현에서 기존 legacy ISO UI와 새 UI가 섞여 `[계산하기]`, `"결과 대기 중..."`, `lbl_result`, `combo_region_iso` 같은 요소가 남는 문제가 있었다.
- batch-first UI는 실제 사용 패턴과 맞지 않았다. 사용자는 대부분 1개 데이터에 대해 여러 규격 결과를 비교하므로, 메인 화면에 여러 No. 행을 펼치는 방식은 과했다.
- Hong Kong CSPF는 Rated/Declared Capacity 입력이 필요하므로 ISO/ISEER 2점식 결과표에 그대로 섞으면 안 된다.
- SASO T3는 35 Full/Half 2점식이 아니라 `46_full / 35_full / 35_half` 3점식 또는 optional `35_min` 포함 4점식 구조라 별도 profile 분리가 필요하다.
- UI 디자인을 먼저 덮는 방식은 `delegate paint`, selection, editor, paste, undo, repaint 타이밍이 얽혀 복잡도가 높다.
- 기능이 안정되기 전에 rounded input box, card-like UI, custom table skinning을 적용하면 입력 UX와 계산 연결이 꼬일 위험이 있다.
- `matplotlib`은 graph 구현은 쉽지만 배포 용량 증가와 PyInstaller 패키징 리스크가 있다.
- `pyqtgraph`도 신규 의존성이라 경량 계산기 배포 목표와 맞지 않는다.

### Decision
- 현재 단계에서는 “예쁜 UI”보다 “정확하고 빠르게 쓸 수 있는 엔지니어링 계산 UI”를 우선한다.
- UI 작업 순서는 다음으로 정한다.
  1. ISO16358-2 HSPF 계산기 구현
     - 공식 규격서 / 공식 계산기 / golden case 교차검증 가능할 때 구현
     - 구현 완료 후 UI profile로 연결
  2. Calculator UI 기본 기능 구현
     - 우선 ISO 계열부터 안정화
     - CSPF / HSPF profile 선택 구조 정리
     - input grid, result table, detail trace/graph 기본 UX 확정
  3. EN14825, AHRI210240 UI 연결
     - 계산 엔진이 안정된 것부터 UI에 연결
     - 규격별 입력 grid 구조를 맞춤
  4. UI 디자인 다듬기
     - 모든 주요 규격 UI 연결 후 QSS / delegate paint / rounded input / card layout 적용
- 메인 입력부는 반드시 스프레드시트 UX를 지원한다.
- `QTableView + QAbstractTableModel` 기반은 유지한다.
- `ProfileInputGridModel / ProfileInputGridView`를 Calculator UI의 장기 입력 패턴으로 사용한다.
- 디자인 skinning은 모든 규격 UI 구조가 안정화된 뒤 별도 턴에서 진행한다.
- 신규 그래프 라이브러리 없이 QPainter graph를 유지한다.
- `matplotlib`, `pyqtgraph`, `QTableWidget`, `setCellWidget`, PyQt6는 사용하지 않는다.

### Lesson
- 계산기 UI의 핵심 가치는 “예쁜 화면”보다 “엑셀/성적서 데이터를 빠르게 붙여넣고 정확히 검산하는 흐름”이다.
- 사용자가 값을 하나씩 타이핑해야 한다면 이 프로그램을 쓸 이유가 약해진다.
- 메인 단건 입력도 스프레드시트처럼 paste/undo/navigation이 가능해야 한다.
- region/profile마다 required input point가 다르므로, 단일 flat UI에 모든 규격을 억지로 섞으면 안 된다.
- Hong Kong, SASO처럼 입력 구조가 다른 규격은 별도 profile로 분리해야 한다.
- UI 디자인은 기능 구조가 안정된 뒤 마지막에 하는 것이 안전하다.
- PyQt5에서도 스프레드시트 기능과 디자인 개선은 양립 가능하지만, QSS/custom delegate skinning은 별도 작업으로 분리해야 한다.
- 기능 안정화 전 custom paint를 적용하면 editor, selection, paste, undo, repaint가 꼬일 수 있다.
- 앞으로 Codex 작업 지시 시에는 “기능 안정화 턴”과 “디자인 skinning 턴”을 명확히 분리한다.

## 2026-05-04 — Calculator UI v1 기본 구조 안정화

### Tried
- ISO16358/CSPF 계산 결과를 UI에서 입력·실행·확인할 수 있도록 Calculator UI 기본 기능을 정리했다.
- UI 입력부를 single-input-first 구조로 전환했다.
- `ProfileInputGridModel` / `ProfileInputGrid` 기반으로 입력 테이블 구조를 구성했다.
- `QTableView` + `QAbstractTableModel` 기반을 유지하면서 스프레드시트형 입력 UX를 우선했다.
- 계산 연결이 먼저 동작하도록 하고, 디자인 skinning은 후순위로 미뤘다.

### Result
- Calculator UI는 우선 ISO16358/CSPF 입력과 계산 연결을 안정화하는 방향으로 정리했다.
- 기능이 동작하는 테이블 구조를 먼저 확보하는 것이 디자인을 먼저 덮는 것보다 안전하다고 판단했다.
- PyQt5 기반을 유지하기로 했다.
- `QTableView` + `QAbstractTableModel` 구조는 유지하기로 결정했다.
- UI는 스프레드시트 UX와 정확한 계산 연결을 우선하는 방향으로 정했다.

### Failed / Risk
- 디자인을 먼저 덮는 방식은 현재 계산 입력 구조가 완전히 안정화되기 전에는 복잡도를 크게 올릴 수 있다.
- skinning을 먼저 진행하면 입력 모델, 계산 handler, 결과 표시 구조가 뒤섞여 유지보수가 어려워질 위험이 있다.
- PyQt6 전환은 기존 PyQt5 기반 UI와 호환성 문제를 만들 수 있으므로 금지했다.
- `matplotlib`, `pyqtgraph` 등 신규 그래프 의존성을 추가하면 UI 안정화보다 의존성 관리와 배포 리스크가 커질 수 있다.
- core 계산 로직, calculator public API, Train/Predict UI를 함께 건드리면 Calculator UI 작업 범위가 불필요하게 커질 위험이 있다.

### Decision
- PyQt5를 유지하고 PyQt6 전환은 하지 않는다.
- `QTableView` + `QAbstractTableModel` 기반을 유지한다.
- ISO16358/CSPF UI는 single-input-first 구조로 우선 안정화한다.
- `ProfileInputGridModel` / `ProfileInputGrid` 기반 입력부를 유지한다.
- 기능 동작과 계산 연결을 먼저 안정화하고, 디자인 skinning은 별도 후속 턴에서 진행한다.
- core 계산 로직, calculator public API, Train/Predict UI는 이번 UI 작업에서 수정하지 않는다.
- `matplotlib`, `pyqtgraph` 등 신규 그래프 의존성은 추가하지 않는다.
- EN14825, AHRI210240, Korea CSPF 실제 UI 구현은 아직 진행하지 않는다.
- ISO16358-2 HSPF 구현은 별도 대화창에서 진행하고, 완료 후 UI 작업으로 넘긴다.

### Lesson
- Calculator UI는 예쁘게 보이는 것보다 먼저 “정확한 입력 → 정확한 handler 호출 → 정확한 결과 표시”가 안정화되어야 한다.
- UI skinning은 구조가 확정된 뒤에 해야 한다.
- 계산기 UI는 일반 폼보다 스프레드시트 UX에 가깝기 때문에, `QTableView` 기반 모델 구조가 더 적합하다.
- 계산 엔진과 UI를 동시에 흔들면 디버깅 범위가 커지므로, UI 작업 중에는 core/API/Train/Predict를 보호해야 한다.
- 신규 그래프 의존성은 기능 요구가 명확해진 뒤 추가 여부를 판단한다.

## 2026-05-03 — Calculator UI v1 기본 기능 안정화

### Tried
- ISO16358/CSPF UI의 기본 기능을 우선 구현하고, 디자인 개선은 후순위로 미루는 방향을 검토했다.
- 기존 입력 UI를 한 번에 여러 계산기를 모두 구현하는 방식이 아니라, ISO16358/CSPF를 먼저 안정화하는 single-input-first 구조로 전환했다.
- 입력부는 `ProfileInputGridModel` / `ProfileInputGrid` 기반으로 구성했다.
- 테이블 UI는 `QTableView` + `QAbstractTableModel` 기반을 유지하는 방향으로 정했다.
- 스프레드시트처럼 입력값을 확인하고 수정할 수 있는 UX를 우선했고, 계산 연결의 정확성을 디자인보다 우선했다.
- `EN14825`, `AHRI210240`, `Korea CSPF` 실제 UI 구현은 아직 진행하지 않기로 했다.
- `ISO16358-2 HSPF` 구현은 별도 대화창에서 계산 엔진을 먼저 안정화한 뒤, 완료 후 Calculator UI 작업으로 넘기기로 했다.

### Result
- ISO/CSPF UI는 기본 입력/표시 구조를 우선 안정화하는 방향으로 정리되었다.
- `QTableView` + `QAbstractTableModel` 기반이 현재 단계에서 가장 안전한 구조로 판단되었다.
- `ProfileInputGridModel` / `ProfileInputGrid`를 중심으로 입력부 구조를 유지하기로 했다.
- UI 작업 범위가 ISO16358/CSPF 기본 기능 안정화로 좁혀졌다.
- 디자인 skinning, 그래프 추가, 다른 규격 UI 확장은 후속 작업으로 분리되었다.
- PyQt5 유지, PyQt6 전환 금지 방침을 확정했다.
- `core` 계산 로직, calculator public API, Train/Predict UI는 이번 UI 작업에서 건드리지 않기로 했다.

### Failed / Risk
- 기능이 안정화되기 전에 디자인을 먼저 덮으면 UI 구조와 계산 연결이 동시에 흔들릴 위험이 있다.
- `QSS` skinning, custom delegate, 그래프 위젯 등을 먼저 넣으면 디버깅 범위가 커지고 원인 추적이 어려워질 수 있다.
- `matplotlib`, `pyqtgraph` 등 신규 그래프 의존성을 추가하면 배포/환경 리스크가 생긴다.
- PyQt6 전환은 기존 PyQt5 기반 UI와 호환성 문제를 만들 수 있다.
- `core` 계산 로직이나 calculator public API를 UI 작업 중 함께 수정하면, 계산 regression과 UI bug가 섞일 위험이 있다.
- `EN14825`, `AHRI210240`, `Korea CSPF` UI까지 동시에 구현하면 범위가 커져 ISO/CSPF 기본 기능 안정화가 지연될 수 있다.

### Decision
- Calculator UI v1은 ISO16358/CSPF 기본 기능 안정화를 우선한다.
- UI 테이블은 `QTableView` + `QAbstractTableModel` 기반을 유지한다.
- 입력부는 `ProfileInputGridModel` / `ProfileInputGrid` 기반으로 유지한다.
- PyQt5를 유지하고 PyQt6로 전환하지 않는다.
- `core` 계산 로직, calculator public API, Train/Predict UI는 이번 UI 작업 범위에서 제외한다.
- 신규 그래프 의존성(`matplotlib`, `pyqtgraph` 등)은 추가하지 않는다.
- 디자인 skinning은 기능/구조가 확정된 뒤 별도 턴에서 진행한다.
- `EN14825`, `AHRI210240`, `Korea CSPF` 실제 UI 구현은 후순위로 둔다.
- `ISO16358-2 HSPF`는 별도 엔진 구현 작업에서 완료한 뒤 Calculator UI에 연결한다.

### Lesson
- UI는 먼저 예쁘게 만드는 것보다, 입력값이 정확히 계산기로 전달되고 결과가 안정적으로 표시되는 구조를 먼저 고정해야 한다.
- 테이블형 계산 UI에서는 스프레드시트 UX와 계산 연결 정확성이 skinning보다 우선이다.
- 큰 UI 변경과 계산 로직 변경을 같은 턴에서 섞으면 regression 원인 추적이 어려워진다.
- 신규 의존성은 기능상 꼭 필요해진 시점까지 미루는 편이 안전하다.
- 여러 규격 UI를 동시에 확장하기보다, ISO16358/CSPF처럼 하나의 대표 경로를 먼저 안정화한 뒤 반복 적용하는 방식이 낫다.

## 2026-05-04 — 규격 문서 유산화 구조 수립 및 EN14825/AHRI 문서화

### Tried
- EN14825, AHRI210/240, ISO16358 규격 구현 경험을 향후 재사용 가능한 문서 자산으로 남기는 방향을 검토했다.
- `notes`, `dev_notes`, `design_notes`의 역할을 분리하는 문서 구조를 설계했다.
- `docs/DOCS_GUIDELINES.md`, `docs/STANDARD_DOC_TEMPLATE.md`, `docs/FORMULA_REFERENCE_GUIDE.md`를 기준 문서로 사용하기로 했다.
- EN14825 문서는 `docs/en14825/` 하위에 `en14825_notes.md`, `en14825_dev_notes.md`, `en14825_design_notes.md`로 작성했다.
- AHRI210/240 문서는 HSPF2 중심으로 먼저 유산화하고, SEER2는 별도 보강 대상으로 남겼다.
- 문서 작성 시 PDF를 Primary로 삼지 않고, 기존 검증된 notes와 calculator 코드/test를 Primary Source로 삼는 참조 전략을 정했다.
- design_notes에는 제품 설계 관점 설명을, dev_notes에는 코드 구현/버그/테스트 노하우를 담도록 역할을 분리했다.

### Result
- EN14825 유산화 문서 3종 작성이 완료되었다.
- AHRI HSPF2 유산화 문서 작성이 완료되었다.
- 문서 작성 기준은 “규격 설명 + 구현 노하우 + 설계 노하우”의 3계층 구조로 정리되었다.
- design_notes는 현업 설계자가 참고할 수 있도록 코드 언급을 배제하고, 효율 측정값에 영향을 주는 규격 기반 설계 포인트 중심으로 작성하기로 했다.
- dev_notes는 실제 발견된 버그, 구현 실수, 테스트 전략, 디버깅 체크리스트 중심으로 작성하기로 했다.
- PDF는 Clause/Table/Equation 근거 확인용 Secondary Source로 제한하고, 계산 구조 해석은 검증된 notes/code/test 기준으로 작성하기로 했다.

### Failed / Risk
- PDF를 Primary Source로 사용하면 파싱 오류나 오해석으로 인해 문서 내용이 흔들릴 위험이 있었다.
- dev_notes와 design_notes에 용어 설명, 코드 설명, 설계 해석이 섞이면 문서 목적이 불명확해질 수 있었다.
- 문서 폴더 구조를 지금 당장 `glossary/`, `notes/`, `design_notes/`, `dev_notes/`로 재편하면 링크 수정과 가이드 수정 범위가 커져 현재 작업 흐름이 깨질 위험이 있었다.
- 현업 배포를 고려하면 design_notes의 가독성이 중요하지만, 전체 문서 구조 리팩토링까지 동시에 진행하면 ISO16358 및 ML 작업 진입이 지연될 수 있다.

### Decision
- 지금은 문서 폴더 구조 전체 리팩토링은 보류하고, 각 design_notes에 `Quick Glossary`를 추가하는 방식으로 가독성을 개선한다.
- dev_notes에는 상세 glossary를 넣지 않고, 코드 구현/버그/테스트 중심 문서로 유지한다.
- 향후 문서 구조 리팩토링은 별도 작업으로 관리한다.
- `REFACTOR_PLAN.md`를 만들어 docs 구조 리팩토링, ML pipeline 리팩토링 등 프로젝트 전반의 향후 구조 개선 항목을 기록한다.
- `docs/DOCS_GUIDELINES.md`에는 Future Refactor Notice를 추가한다.
- `AGENTS.md` Lite에는 `REFACTOR_PLAN.md` 참고 규칙을 짧게 추가하고, `AGENTS_FULL.md`에는 상세 설명을 추가한다.
- context/roadmap 또는 TODO에도 “유산용 docs 작성 및 구조 리팩토링 예정”을 남긴다.

### Lesson
- 문서화도 코드처럼 구조와 책임 분리가 필요하다.
- 규격 문서 작성 시 PDF 원문보다 검증된 구현 notes/code/test를 기준으로 삼는 편이 안정적이다.
- design_notes는 현업 설계자가 바로 읽을 수 있어야 하므로, Quick Glossary처럼 문서 내부에서 이해를 돕는 장치가 필요하다.
- dev_notes는 신입 교육용 개념서가 아니라 구현 실수 방지용 문서로 유지해야 한다.
- 구조 리팩토링은 중요하지만, 계산기/ML 핵심 작업 흐름을 막을 정도로 앞당기면 안 된다.
- 나중에 까먹을 가능성이 높은 작업은 기억에 의존하지 말고 `REFACTOR_PLAN.md` 같은 backlog 문서에 강제로 남겨야 한다.

## 2026-05-04 — AHRI SEER2 미사용 입력 P_W_off 제거

### Tried
- `calculator_ahri_seer2.py`와 AHRI SEER2 UI 입력 구조를 검토했다.
- UI에서 `P_W_off`를 입력받고 calculator로 전달하지만, 실제 SEER2 계산에는 사용되지 않는다는 점을 확인했다.
- 사용자가 off-mode power가 SEER2에 반영된다고 오해할 수 있어 UI와 결과 dict에서 제거하는 방향을 잡았다.

### Result
- `ui/calc_window.py`에서 AHRI SEER2 추가 파라미터의 `P_W_off (W)` 입력칸, placeholder, 위젯 등록이 제거되었다.
- `calculate_ahri()`에서 `P_W_off` 값을 더 이상 읽지 않도록 정리했다.
- `calculate_seer2()` 호출 시 `p_w_off` 인자를 전달하지 않도록 수정했다.
- 외부 호출 호환성을 위해 `calculate_seer2(..., p_w_off=0.0, ...)` 함수 시그니처는 유지했다.
- 계산 결과 dict에서는 미사용 `p_w_off` 항목을 제거했다.
- `p_w_off` 미전달 값과 `p_w_off=999.0` 전달 값을 비교해 `SEER2`, `EER2_A_Full`, `EER2_B_Low`, `total_cooling_Btu`, `total_energy_Wh` 결과가 동일함을 확인했다.

### Failed / Risk
- 계산에 사용되지 않는 입력값이 UI에 남아 있으면 사용자가 해당 값이 SEER2에 반영된다고 오해할 수 있다.
- 결과 dict에 미사용 입력값이 남아 있으면 계산 결과의 의미가 불명확해질 수 있다.
- 함수 시그니처를 즉시 제거하면 외부 호출부 호환성이 깨질 수 있다.

### Decision
- UI와 호출부에서는 `P_W_off`를 제거한다.
- `calculate_seer2()` 함수 시그니처는 당장 제거하지 않고 호환성을 위해 유지한다.
- 계산 결과 dict에서는 미사용 `p_w_off`를 제거한다.
- SEER2 계산식 자체는 변경하지 않는다.
- HSPF2, EN14825 파일은 이번 작업에서 수정하지 않는다.

### Lesson
- UI 입력값은 실제 계산에 반영되는 항목만 노출해야 한다.
- 계산에 사용되지 않는 값은 사용자의 신뢰를 떨어뜨리는 혼동 요소가 된다.
- public API에 가까운 함수 시그니처는 즉시 삭제보다 단계적 정리가 안전하다.
- 미사용 파라미터 제거 작업은 계산 결과 비교로 “영향 없음”을 반드시 확인해야 한다.

## 2026-05-04 — Git 정리 및 로컬 PDF/backup 파일 관리 기준 정리

### Tried
- 규격 PDF를 로컬 루트 폴더에 두고 문서 작업에 사용했지만, GitHub에는 push하지 않는 방향을 검토했다.
- `*_backup.py`, `backup.json` 같은 임시/백업 파일을 정리하는 방법을 논의했다.
- `git status`, PDF 삭제, `git add -A`, commit/push 순서를 안전하게 점검했다.
- 로컬 폴더를 완전히 삭제한 뒤 `git pull`하는 방식의 위험성을 검토했다.

### Result
- 규격 PDF는 GitHub에 올리지 않고 로컬에서 삭제 후 별도 클라우드에 보관하기로 했다.
- PDF가 untracked 상태라면 삭제 후 `git add -A`를 진행해도 push 대상에 포함되지 않는다는 점을 확인했다.
- backup 파일은 구현 완료 후 별도 정리 대상으로 남기기로 했다.
- 로컬 루트 폴더 전체를 삭제한 뒤 `git pull`하는 방식은 사용하지 않기로 했다.
- 로컬을 원격 상태로 강제 동기화해야 할 때는 `git fetch`, `git reset --hard origin/main`, `git clean -fd` 같은 Git 명령을 신중히 사용하기로 했다.

### Failed / Risk
- `git add .` 또는 `git add -A` 전에 PDF 상태를 확인하지 않으면 원하지 않는 규격서 PDF가 GitHub에 올라갈 수 있다.
- 로컬 파일을 무작정 삭제하면 Git이 이를 삭제 변경사항으로 인식해 실수로 삭제 커밋할 수 있다.
- 술을 마신 상태나 피곤한 상태에서 Git 정리를 하면 불필요한 파일 push, 삭제 커밋, 작업 손실 위험이 커진다.

### Decision
- PDF는 GitHub에 올리지 않고 별도 클라우드에 보관한다.
- backup 파일은 당장 급하게 지우지 않고, 다음 정리 턴에서 확인 후 삭제한다.
- 루트 폴더를 수동으로 통째 삭제한 뒤 `git pull`하는 방식은 금지한다.
- Git 정리 전에는 항상 `git status`로 변경사항을 확인한다.
- 불안한 상태에서는 commit/push 전에 변경 대상 파일 목록을 한 번 더 확인한다.

### Lesson
- Git 정리는 “삭제 후 push”보다 “상태 확인 → 삭제 → add → 상태 재확인 → commit/push” 순서가 안전하다.
- untracked 파일과 tracked 파일의 차이를 알고 정리해야 한다.
- 루트 폴더 수동 삭제는 Git 작업 방식이 아니며, 프로젝트 손상 위험이 크다.
- 규격 PDF처럼 라이선스/용량/공개 문제가 있는 파일은 `.gitignore` 또는 별도 보관 정책이 필요하다.

## 2026-05-04 — 자동화 Agent Loop 도입 여부 검토

### Tried
- Gemini API, Codex CLI, Python script를 연결해 AI 간 자동화 루프를 만드는 구조를 검토했다.
- 사람이 프롬프트와 결과를 복사/전달하는 현재 구조를 자동화할 수 있는지 논의했다.
- predictor_v3 현재 단계에 해당 자동화 루프를 적용하는 것이 적절한지 평가했다.

### Result
- Python orchestrator가 Gemini API를 호출하고, Codex CLI에 명령을 전달하고, 결과를 다시 LLM에 전달하는 구조는 기술적으로 가능하다고 판단했다.
- 다만 현재 predictor_v3는 계산기 LOCK, ISO16358 완료, predictor/trainer 안정화 전 단계이므로 완전 자동 루프 도입은 비효율적이라고 판단했다.
- 지금은 자동화 루프보다 테스트 자동화, 검증 스크립트, 프롬프트 템플릿화가 더 높은 ROI를 가진다고 정리했다.
- 향후 데이터가 쌓이고 predictor/trainer가 안정화되면 자동 탐색/검증 루프에 활용할 수 있다고 판단했다.

### Failed / Risk
- 현재 단계에서 AI 자동 루프를 도입하면 Gemini와 Codex가 범위를 과도하게 확장해 사람이 수습해야 할 가능성이 크다.
- 규격 계산기처럼 정확성이 중요한 영역에서는 테스트 통과만으로 정답을 보장하기 어렵다.
- 자동 루프는 토큰 사용량이 크고, 상태 관리와 검증 체계가 없으면 오히려 생산성을 떨어뜨릴 수 있다.

### Decision
- 현재 predictor_v3에는 완전 자동 Agent Loop를 도입하지 않는다.
- 우선순위는 계산기 LOCK, ISO16358 완료, predictor/trainer 진입으로 유지한다.
- 자동화는 나중에 `auto_eval.py`, `auto_compare.py`, `auto_regression_check.py` 같은 검증 자동화부터 단계적으로 도입한다.
- 장기적으로는 계산기 + ML predictor + 열역학 제약 + design space exploration 구조로 확장할 수 있다.

### Lesson
- 자동화 루프는 프로젝트 초반 개발보다 검증/탐색/운영 단계에서 가치가 크다.
- 지금 필요한 것은 AI 간 완전 자동화가 아니라, 사람이 방향을 잡고 Codex가 실행하는 반자동 협업 구조다.
- 자동화를 도입하려면 먼저 안정적인 평가 함수, 테스트 세트, 로그, 실패 복구 기준이 있어야 한다.
- 열역학 경계와 규격 계산기가 고정된 뒤에야 자동 탐색 루프가 의미 있는 후보를 만들 수 있다.

## 2026-05-04 — ISO16358 / KS C 9306 CSPF 계산기 및 문서 구조 정리

### Tried

* `calculator.py`를 ISO16358 공통 계산기로 유지할지, KS C 9306 전용 계산기로 분리할지 검토
* 파일명을 `calculator_iso16358.py`로 정리하는 방향 검토
* KS C 9306 CSPF 계산 경로에서 다음 로직 검토

  * 시험값 `ROUND_HALF_UP` 정수 반올림
  * `power_interpolation_method = "ks_intersection"` 분리
  * 29/35°C 외삽 처리
  * `BL > max_cap` 구간에서 냉방량 cap 처리
  * `declared_capacity` 기반 building load 유지
* KS C 9306 golden sample 복구 및 검증 기준 정리
* `recommend_35_half_capacity()` helper의 위치와 config 기반 분리 방향 검토
* ISO16358 / KS C 9306 문서 구조를 `DOCS_GUIDELINES.md` 기준으로 재설계
* `notes / dev_notes / design_notes / glossary` 역할 분리 기준 재정의
* KS C 9306 design notes에 `ta / tb / tc`, PLF/CD, bin hour 설계 노하우를 별도로 담는 방향 검토
* ISO16358-2 HSPF 작업은 새 대화창에서 별도 시작하기로 논의

### Result

* ISO16358 계산기는 공통 엔진으로 유지하고, KS C 9306은 region-specific 확장으로 관리하기로 결정
* 파일명은 `calculator_iso16358.py` 방향이 적절하다고 판단
* KS C 9306 CSPF golden sample 기준 재확인

  * `declared_capacity = 6000 W`
  * `35_full = 6035.8 W / 1641.4 W`
  * `35_half = 3420.4 W / 679.4 W`
  * `29_min = 1759.6 W / 201.7 W`
  * `CSPF = 6.504`
  * `cooling_output = 1943798 Wh`
  * `cooling_power ≈ 298852 Wh`
* `round_test_values`는 시험값/파생값 반올림 전용으로 두고, KS 교점 전력 보간은 `power_interpolation_method`로 분리하는 구조가 맞다고 정리
* `recommend_35_half_capacity()`는 CSPF 본계산과 분리된 보조 설계 helper로 유지하되, `half_capacity_recommendation` config 기반으로 하드코딩을 줄이는 방향 확정
* 문서 구조는 ISO 공통과 KS 확장을 다음처럼 분리하는 방향으로 정리

  * `docs/iso16358/`
  * `docs/iso16358/regions/ks_c_9306/`
* 문서 역할 기준 정리

  * `notes.md`: 규격 개요, 계산 구조, 수식 ↔ 코드 매핑, 검증 결과
  * `dev_notes.md`: 구현 지침, 디버깅, 테스트 전략, Agent 프롬프트
  * `design_notes.md`: 제품 설계 엔지니어용 해석, 코드 언급 금지
  * `glossary.md`: 용어 SSOT
* KS C 9306의 `ta / tb / tc` 중간점 설계 논리는 `ks_c_9306_design_notes.md`에 별도 명시하기로 결정

### Failed / Risk

* ISO16358 공통 문서와 KS C 9306 전용 문서를 한 폴더에 뭉뚱그리면 지역별 확장 시 혼선 발생 가능
* `design_notes`에 코드 구현 내용이 섞이면 열설계 엔지니어용 문서 역할이 흐려질 위험
* `dev_notes`에 설계 노하우가 섞이면 Agent가 구현 세부와 설계 해석을 혼동할 수 있음
* `recommend_35_half_capacity()`에 `23.0`, `35.0`, `29.0`, `1.077`, `0.077` 같은 KS 전용 상수를 하드코딩하면 다른 ISO16358 지역 확장 시 기술 부채 발생
* KS C 9306 design notes에서 `tc = (ta + tb) / 2`를 “항상 전역 최적”으로 단정하면 과장된 문서가 될 수 있음
* HSPF는 CSPF보다 defrost, auxiliary heat, heating bin 처리 등이 복잡하므로 같은 대화창에서 이어가면 컨텍스트 혼선 가능

### Decision

* ISO16358은 공통 엔진, KS C 9306은 region-specific 확장으로 문서와 코드 관점을 분리
* `calculator_iso16358.py`는 ISO16358 공통 계산기 파일명으로 유지
* KS C 9306 전용 동작은 `data/region_configs/korea.json` 같은 region config에서 제어
* `round_test_values`와 `power_interpolation_method`는 반드시 분리
* KS C 9306 design 노하우는 `ks_c_9306_design_notes.md`에만 작성
* golden sample과 검증 결과는 `notes.md` 또는 `dev_notes.md`에 두고, `design_notes.md`에는 넣지 않음
* `design_notes.md`에는 코드 파일명/함수명/변수명 언급 금지
* `dev_notes.md`에는 glossary 본문을 쓰지 않고 링크만 둠
* ISO16358-2 HSPF 구현은 새 대화창에서 별도 작업으로 시작

### Lesson

* 공통 규격과 국가별 확장은 처음부터 문서 폴더 구조로 분리해야 나중에 꼬이지 않는다
* 계산 옵션은 의미별로 분리해야 한다: 반올림 여부와 보간 방식은 별도 설정이다
* golden sample은 계산기 리팩토링의 기준점이므로 반드시 로그와 문서에 남겨야 한다
* 설계 문서와 개발 문서는 독자가 다르므로 같은 내용을 섞어 쓰면 재사용성이 떨어진다
* KS C 9306의 `ta / tb / tc` 논리는 구현 설명이 아니라 제품 설계 인사이트로 관리해야 한다
* “수학적 최적” 같은 표현은 실제 규격/제품 제약을 고려해 engineering heuristic으로 제한해서 작성하는 것이 안전하다
* CSPF와 HSPF는 같은 ISO16358 계열이라도 복잡도가 다르므로 작업 대화창과 문서를 분리하는 것이 좋다


## 2026-05-04 — ISO16358-1 T1 CSPF region config 확장 및 공식 툴 검증

### Tried
- ISO16358-1 CSPF region config 확장 작업을 시작했다.
- 기존 `thailand.json` 구조와 사용자 제공 `temp_bin/golden_data`를 비교했다.
- ISO T1 기본 2점식 공통 config 방향을 검토했다.
- `tests/fixtures/iso16358_cspf_golden_fixtures.json`에 ISO T1, India, SASO, Hong Kong fixture 초안을 정리했다.
- ISO T1 default 2-point control sample 4개를 정리했다.
  - user ISO T1 CSPF 4.665
  - ASEAN Table 7 CSPF 4.760
  - JATL slide CSPF 4.860
  - JATL tool CSPF 4.930
- `20181107 ISO16358-1_AMD1 Calculation_tool_FINAL.xlsm` 공식 계산 툴을 `openpyxl`로 read-only audit했다.
- `Variable Capacity unit` 시트의 T1 bin table 수식을 확인했다.
- `CH/CI/CJ`, `CL/CM/CN`, `CZ`, `CW/CX/CY`, `CS/CT/CU`, `CK5/CK6/CK7` 수식을 추적했다.

### Result
- 기존 `thailand.json`은 ISO T1 기준과 맞지 않는 2397h 임시/불일치 config로 판단했다.
- 태국/베트남/말레이시아/필리핀/인도네시아는 별도 국가 config가 아니라 `iso_t1_default_2point.json` 공통 profile을 쓰는 방향으로 확정했다.
- 공식 xlsm audit 결과, low-load branch 자체는 현재 엔진과 동일한 구조임을 확인했다.
- mismatch 원인은 low-load branch가 아니라 half < Lc <= full 구간의 power 산정 방식 차이로 좁혀졌다.
- 공식 xlsm은 해당 구간에서 capacity-linear power interpolation이 아니라 boundary EER 보간 후 `P(tj)=Lc/EER` 방식으로 계산하는 것으로 판단했다.
- `core/calculator_iso16358.py`에 `power_interpolation_method="iso_boundary_eer"`를 추가했다.
- 적용 범위는 CSPF cooling path의 half < Lc <= full 구간으로 제한했다.
- low-load branch, default `capacity_linear`, Korea `ks_intersection`, HSPF path는 유지했다.
- `data/region_configs/iso_t1_default_2point.json` production config를 추가했다.
- `data/region_configs/thailand.json`을 삭제했다.
- ISO T1 bin total 1817 검증과 production config 기반 CSPF 4.665 1-sample control regression을 추가했다.
- 최종 테스트는 `71 passed`로 통과했다.
- Korea CSPF 6.504 regression은 유지됐다.
- 최종 커밋/푸시 완료:
  - `ee40545f5ca2d0e39073d916194927b40aa1a0e0`
  - `config: add ISO T1 default CSPF region profile`

### Failed / Risk
- 처음에는 2점식이라 단순히 region config만 추가하면 끝날 것으로 예상했지만, 공식 계산 방식과 sample provenance 확인이 필요해 작업 범위가 커졌다.
- xlsm 파일은 VBA/selector/cached output 상태가 불일치할 수 있어 cached CSPF/CSEC 값을 그대로 golden으로 신뢰할 수 없었다.
- user golden, ASEAN, JATL sample은 control regression으로는 유용하지만 certification-grade golden은 아니다.
- `Cd=0`, hidden factor, derived coefficient 조정으로 golden에 맞추는 방식은 잘못된 방향으로 판단했다.
- 공통 CSPF path를 직접 수정하면 Korea CSPF 6.504 regression이 깨질 위험이 있었다.
- `iso_boundary_eer` 적용 범위를 넓히면 KS C 9306, HSPF, 기존 profile에 회귀 위험이 있다.

### Decision
- ISO T1 default 2-point는 `iso_t1_default_2point.json` production config로 관리한다.
- Thailand 전용 config는 두지 않고 ISO T1 default 공통 config를 사용한다.
- `thailand.json`은 삭제한다.
- ISO T1 2점식의 half~full 구간 power 계산은 `power_interpolation_method="iso_boundary_eer"`로 명시적으로 분리한다.
- Korea config는 `ks_intersection` 경로를 유지한다.
- user ISO T1 CSPF 4.665는 “1-sample control regression, not certification-grade validation”으로 남긴다.
- xlsm cached output은 golden으로 쓰지 않고, 공식 수식 구조 확인용으로만 사용한다.
- 다음 region 확장은 Hong Kong, India, SASO 순서로 custom bin/profile을 분리해 진행한다.

### Lesson
- region config 확장은 단순 JSON 추가처럼 보여도, 공식 계산식과 sample provenance를 먼저 확인해야 한다.
- xlsm 계산 툴은 openpyxl로 수식은 확인할 수 있지만, VBA/cached output은 신뢰하지 말아야 한다.
- golden mismatch가 나오면 계수 조정부터 하지 말고, 공식 worksheet 수식과 현재 엔진의 분기 차이를 먼저 찾아야 한다.
- 공통 엔진을 직접 고치기보다 `power_interpolation_method` 같은 명시적 profile 분기로 격리하는 것이 안전하다.
- 기존 Korea CSPF 6.504 같은 검증된 regression은 region 확장 중 반드시 보호해야 한다.
- control sample은 provenance 수준에 따라 certification-grade golden과 구분해서 기록해야 한다.

## 2026-05-04 — ISO16358 CSPF profile path Phase R1 구현 및 문서 정리

### Tried
- ISO16358 CSPF 계산기를 공식 xlsm 구조 기준으로 다시 점검했다.
- 기존 35/29 hard-code 기반 flat config 방식만으로는 T3/SASO, optional minimum, required_only 분기를 표현하기 어렵다고 판단했다.
- T1/T3 공식 시트 구조를 역추적했다.
  - T1 result: `Y15`
  - T1 calculation rows: `18~48`
  - T1 CSTL/CSEC: `CK49` / `CZ49`
  - T3 result path: `Y40 → CF112 → CK163/CZ163`
  - T3 calculation rows: `132~162`
  - T3 segment: `tj > 35`는 `46↔35`, `tj <= 35`는 `35↔29`
- `cspf_test_profile` opt-in path를 추가하는 방향으로 정리했다.
- `core/calculator_iso16358.py`에 profile resolver 및 T1 `required_only` 계산 path를 추가했다.
- 신규 테스트를 추가했다.
  - `tests/test_iso16358_cspf_profile_resolver.py`
  - `tests/test_iso16358_cspf_profile_calculation.py`
- legacy ISO T1 default path와 profile path의 parity audit을 진행했다.
- 임시 audit/debug/trace 파일을 정리했다.

### Result
- `cspf_test_profile` 기반 resolver 구현 완료.
  - `_has_cspf_test_profile()`
  - `_resolve_cspf_profile_points()`
  - `_get_cspf_profile_cd()`
  - `_get_cspf_temperature_segments()`
  - `_get_active_load_levels()`
- T1 `required_only` profile calculation path 구현 완료.
  - `_calculate_cspf_profile()`
  - `_profile_capacity_power_at()`
- T1 `required_only`에서 legacy ISO T1 default path와 CSTL/CSEC/CSPF parity를 확보했다.
- 기존 production regression은 유지됐다.
  - ISO T1 default CSPF `4.665`
  - Korea CSPF `6.504`
  - India ISEER xlsx-compatible
  - Hong Kong current engine
- 최종 테스트 상태는 `85 passed, 2 xfailed`.
- 커밋 단위는 아래로 정리했다.
  - `feat: add ISO16358 CSPF variable profile resolver and T1 path`

### Failed / Risk
- 초기에 T1 profile path와 legacy path 간 CSPF 약 `0.088` 차이가 발생했다.
- 원인은 profile path가 legacy config의 `power_interpolation_method=iso_boundary_eer`를 동일하게 따르지 않고 단순 power 보간을 사용한 점이었다.
- Codex가 중간에 `app_calculator.py --help`를 실행하면서 PyQt UI가 뜨는 등 작업 범위가 UI 쪽으로 새는 일이 있었다.
- `tests/test_trace_divergence.py`, `tests/test_debug.py`, `tests/test_audit_bin.py`, `scripts/audit_divergence.py`, `audit_log.txt` 같은 임시 산출물이 남을 뻔했다.
- `0.088` 차이를 “small discrepancy”로 넘기려는 보고가 있었지만, regression 기준에서는 parity failure로 봐야 한다.

### Decision
- ISO16358 CSPF profile path는 variable-capacity / inverter-only 범위로 고정한다.
- Fixed / two-stage / multi-stage는 프로젝트 scope 밖으로 둔다.
- 기존 flat config path는 유지하고, `cspf_test_profile`이 있을 때만 새 profile path로 진입한다.
- T1 `required_only`에서는 minimum point를 생성하지 않는다.
  - `35_full`, `35_half`만 measured required
  - `29_full`, `29_half`는 default 생성
  - half를 lowest continuous operating point로 사용
- T1 `with_optional_test`에서만 minimum branch를 활성화한다.
- T3는 SASO 전용 구현이 아니라 ISO16358 T3 generic profile path로 구현한다.
  - 이후 `saso.json`은 region config + golden/control regression으로 추가한다.
- `REFACTOR_PLAN.md`의 “SASO T3 구현” 표현은 “ISO16358 T3 profile path 및 SASO config 추가”로 바꾸는 것이 적절하다.
- `AGENTS_FULL.md`는 보류하고, `project_context.md`, `REFACTOR_PLAN.md`, `iso16358_notes.md`, `iso16358_dev_notes.md` 중심으로 최신화한다.

### Lesson
- “bin별 P_tj가 맞다”만으로 parity가 확보된 것이 아니다.
  - 반드시 CSTL, CSEC, CSPF까지 비교해야 한다.
- CSPF `0.088` 차이는 작은 차이가 아니라 regression failure로 취급해야 한다.
- 새 계산 path는 기존 legacy path와 같은 fixture에서 parity를 먼저 확보한 뒤 확장해야 한다.
- 임시 audit/debug 파일은 작업 종료 전에 반드시 삭제해야 한다.
- Codex 작업 프롬프트에는 UI 실행 금지, T3/optional 구현 금지 등 범위를 명확히 고정해야 한다.
- region-specific 구현으로 밀어붙이지 말고, ISO16358 common profile path를 먼저 만들고 region config를 얹는 방식이 맞다.

## 2026-05-04 — ISO16358 CSPF SASO T3 공식 xlsm 정합화

### Tried
- SASO T3 golden sample을 기준으로 `core/calculator_iso16358.py`의 `cspf_test_profile` 경로를 검증했다.
- 공식 `20181107 ISO16358-1_AMD1 Calculation_tool_FINAL.xlsm`의 T3 계산 블록을 역추적했다.
- `t_100_load`, `reference_point`, `power_interpolation_method`, `boundary temperature` 계산 방식이 CSPF 결과에 미치는 영향을 비교했다.
- `_iso_boundary_eer_power()`가 T3 `min-half` 구간과 35↔46°C 고온 구간을 처리하지 못하는 문제를 확인했다.
- T3 전용 helper `_iso_boundary_eer_t3_piecewise()`를 추가하는 방향으로 작업을 진행했다.

### Result
- SASO T3 공식 경로는 `t_100_load=46.0`, `reference_point="46_full"`임을 확정했다.
- `power_interpolation_method="iso_boundary_eer"` 기준으로 SASO T3 golden을 맞췄다.
- `_iso_boundary_eer()` 기존 T1/legacy 동작은 유지하고, T3 profile guard 안에서만 `_iso_boundary_eer_t3_piecewise()`를 사용하도록 정리했다.
- SASO T3 결과가 공식값에 근접했다.
  - CSPF: 4.955
  - CSTL: 21547.386 kWh
  - CSEC: 4349.020 kWh
- 전체 테스트는 `97 passed, 1 xfailed`까지 통과했다.
- 커밋 완료: `8f83f64`  
  - `feat: align SASO T3 CSPF profile with ISO16358 AMD1 tool`

### Failed / Risk
- 중간에 `t_100_load=35.0`, `reference_point="35_full"` 가설과 `t_100_load=46.0`, `reference_point="46_full"` 가설이 혼재되어 CSTL/CSEC 해석이 흔들렸다.
- 일부 bin trace와 final total을 서로 다른 계산 블록에서 가져오면 잘못된 결론으로 이어질 수 있음을 확인했다.
- `29_full`은 신규 추가인지 기존 구현 유지인지 혼동이 있었고, 문서에는 “신규 추가”가 아니라 “동작 확인/유지/테스트 커버”로 표현하기로 했다.

### Decision
- SASO T3는 `t_100_load=46.0`, `t_0_load=20.0`, `reference_point="46_full"`을 사용한다.
- T3 profile에서만 `_iso_boundary_eer_t3_piecewise()`를 사용한다.
- 기존 `_iso_boundary_eer()`와 legacy/T1 경로는 변경하지 않는다.
- T3에서는 `{min, half}`와 `{half, full}` bracket 모두 처리한다.
- hidden 보정계수나 golden fitting용 factor는 추가하지 않는다.

### Lesson
- 공식 xlsm 분석 시 반드시 “최종 합계에 실제 연결된 row/column”을 확인해야 한다.
- 대표 bin 몇 개가 맞아도 전체 CSEC가 맞는 것은 아니므로 full-bin trace가 필요하다.
- 계산 가설이 흔들릴 때는 코어 수정 전에 xlsm row trace와 engine trace를 먼저 맞춰야 한다.
- T1/legacy 보호를 위해 신규 규격 분기는 guard 안에 격리해야 한다.

## 2026-05-04 — Hong Kong HSPF 후속 작업 범위 분리

### Tried
- Hong Kong HSPF 계산 구조를 KS C 9306 HSPF와 비교했다.
- heating load line, 2°C 외삽 계수, frost/non-frost 분기, boundary temperature 필요성을 정리했다.
- Hong Kong HSPF를 단독 patch로 처리할 수 있는지 검토했다.

### Result
- Hong Kong HSPF는 단순한 Hong Kong 전용 patch보다 ISO16358-2 HSPF profile path 완전 구현으로 접근하는 것이 맞다고 판단했다.
- 현재까지 확인한 후보/관찰값을 문서에 preliminary note로 남기기로 했다.
  - `Lh(tj) = cap_0 × (12.75 - tj) / 12.75`
  - `cap_0 = 7°C full heating capacity × 0.82`
  - `t_limit = 12.75°C`
  - `Cd_heating = 0.25`
  - full non-frost / full frost / half frost-only 2°C 외삽 계수 후보
- Hong Kong HSPF golden 후보값은 Measure #1 3.643, Measure #2 4.572로 기록했다.

### Failed / Risk
- Hong Kong HSPF는 KS C 9306 HSPF와 구조가 비슷해 보이지만 계수, frost 분기, half 처리 방식이 다르다.
- KS HSPF 엔진에 홍콩 계수만 끼워 넣으면 KS regression을 깨뜨릴 위험이 있다.
- half non-frost가 없고 half frost-only로 보이는 구조는 기존 데이터 모델과 맞지 않을 수 있다.

### Decision
- Hong Kong HSPF는 이번 작업에서 구현하지 않는다.
- ISO16358-2 HSPF 완전 구현 Phase로 별도 추적한다.
- 구현 전 `pitfalls / calculation order` 문서를 먼저 작성한다.
- AHRI HSPF2 구현은 reference design으로만 참고하고, 계수와 계산 순서는 ISO16358-2 기준으로 별도 검증한다.
- 기존 KS C 9306 HSPF regression 보호를 최우선으로 한다.

### Lesson
- HSPF는 CSPF보다 frost/non-frost, auxiliary heat, boundary temperature가 얽혀 있어 단기 patch로 처리하면 위험하다.
- regional patch보다 ISO16358-2 profile resolver/handler 구조를 먼저 설계해야 한다.
- 확인된 값도 최종 구현 전까지는 “확정”이 아니라 “preliminary notes”로 기록하는 것이 안전하다.

## 2026-05-04 — ISO16358 문서 및 project_context 동기화

### Tried
- SASO T3 완료 상태와 Hong Kong CSPF golden 전환 내용을 문서에 반영했다.
- `docs/REFACTOR_PLAN.md`, `project_context.md`, `docs/iso16358/iso16358_notes.md`, `docs/iso16358/iso16358_dev_notes.md`를 업데이트했다.
- 작업 문서에는 완료된 내용과 보류된 내용을 구분해 기록했다.

### Result
- Phase R2를 “SASO T3 official xlsm alignment complete” 상태로 정리했다.
- SASO T3 final config, golden result, boundary diagnostic, pytest 결과를 문서화했다.
- Hong Kong CSPF는 source golden regression으로 전환된 상태로 정리했다.
- 남은 Hong Kong HSPF는 후속 ISO16358-2 대형 작업으로 분리했다.
- `project_context.md`와 `REFACTOR_PLAN.md`가 현재 구현 상태와 일치하도록 업데이트되었다.

### Failed / Risk
- 문서에 “29_full 신규 추가”처럼 실제 git diff와 다른 표현이 들어갈 수 있는 위험이 있었다.
- SASO T3 중간 가설이 여러 번 바뀌었기 때문에 잘못된 가설이 문서에 남을 위험이 있었다.
- 완료된 항목과 보류 항목을 구분하지 않으면 다음 대화창에서 작업 방향을 다시 혼동할 수 있다.

### Decision
- `29_full`은 “신규 추가”가 아니라 “동작 확인/유지/테스트 커버”로 표현한다.
- Hong Kong HSPF는 “확정 구현안”이 아니라 “preliminary notes / future ISO16358-2 phase”로 기록한다.
- 문서 업데이트 후 테스트 결과와 커밋 상태를 함께 확인한다.
- UI 작업으로 넘어가기 전에 계산 handler와 문서를 먼저 clean 상태로 고정한다.

### Lesson
- 계산 구현이 끝난 뒤 바로 문서를 맞춰야 다음 작업에서 길을 잃지 않는다.
- 중간 가설은 rejected hypothesis 또는 preliminary note로 구분해 기록해야 한다.
- project_context는 다음 대화창의 출발점이므로 “현재 완료/보류/다음 단계”를 짧고 정확하게 유지해야 한다.

아래 그대로 **project_log.md에 붙여넣으면 되는 로그 초안**이야.

---

## 2026-05-04 — EN14825 SCOP Cd 적용 조건 해석 정리

### Tried

* `_scop_pl_at_declared_point()`의 Cd 적용 조건 검토
* 조건식: `capacity > load and load_gap_ratio > 0.10`
* EN14825 Clause 7.4.2.2의 “±10% closest capacity control step” 개념과 비교 검토
* 코드 수정 vs 주석 보강 방향 의사결정

### Result

* 현재 조건은 계산 결과(golden)와 정합성 유지
* 다만 규격 원문의 “capacity control step 선택 로직”과 완전히 동일하지는 않음
* 현재 구현은 **declared point 기반 근사 로직**으로 판단됨

### Failed / Risk

* raw capacity-control step 입력 없이 closest-step을 정확히 구현할 수 없음
* 단순 조건 변경 시 규격 해석 왜곡 및 golden mismatch 위험
* 코드만 보고 규격 구현으로 오해될 가능성 존재

### Decision

* 코드 수정하지 않고 주석으로 명확히 의도와 한계를 기록
* 해당 조건은 다음과 같이 해석하기로 결정:

  * load 대비 capacity가 10% 이내 초과 → closest step으로 간주 (Cd 미적용)
  * 10% 초과 → cycling 발생으로 간주 (Cd 적용)
* 추후 **raw capacity-control step schema 도입 시 로직 교체** 예정

### Lesson

* 규격 로직을 단순 입력 구조에 맞춰 “암묵적 해석”으로 구현하면 반드시 주석으로 근거를 남겨야 함
* 계산 정확성(golden match)과 규격 충실도는 별개이며, 둘을 구분해서 관리해야 함
* 구조적 한계(API/입력 스키마)가 있는 상태에서 로직을 확장하면 오히려 위험함 

아래는 이번 대화에서 진행한 **AHRI HSPF2 v3 golden case 추가 검증 작업** 기준으로 정리한 `project_log.md`용 초안이다.
(바로 붙여넣기 가능 형태)

---

## 2026-05-04 — AHRI HSPF2 v3 추가 golden case 검증

### Tried

* HSPF2 v3 엔진에 대해 추가 golden case 3종 검증 수행

  * H22 tested 경로
  * H12 tested 경로
  * h1n_same_speed_as_h3=True (Eq.11.183) 경로
* AHRI 공식 계산기 기대값을 직접 입력하여 비교 (CSV 미사용)
* test_hspf2_v3_smoke.py 기반으로 inline 실행 검증
* 출력 항목 통일:

  * raw_hspf2 / rounded_hspf2
  * total capacity / total power
  * metadata trace (h12/h22 source, anchor)
  * COP_Int-Bin (32/27/22/17F)

### Result

* 3개 케이스 모두 AHRI 기대값과 고정밀 일치 (diff ≈ ±0.005 이내)
* COP_Int-Bin 값도 모든 온도 구간에서 거의 완전 일치
* metadata trace 확인 결과:

  * H22 tested → 정상 분기 (source=tested)
  * H12 tested → H22 fallback (eq_11_44_11_50) 정상 동작
  * h1n_same_speed=True → eq_11_183 경로 정상 적용
* H1Full_calc anchor 및 H22 anchor 모두 기대 경로와 일치

### Failed / Risk

* 현재 검증은 golden case 기반이므로 edge case coverage 부족 가능성 있음
* COP_Int 기반 경로는 정상이나, 향후:

  * 다른 region 조건
  * compressor limit variation
    에서 오차 발생 가능성 존재
* AHRI 계산기는 내부 rounding/hidden rule 존재 가능성 있음 (black box 리스크)

### Decision

* AHRI HSPF2 v3 엔진은 **golden case 기준 완료 상태로 판단**
* 다음 단계로 진행 가능:

  * predictor 연동
  * 추가 region 확장
* 이후 검증은:

  * random case fuzz test
  * boundary condition test
    로 확장

### Lesson

* AHRI 계열 검증은 반드시 **golden case + COP_Int-Bin까지 함께 확인**해야 안정성 확보됨
* 단순 HSPF2 값 일치만으로는 분기 오류를 놓칠 수 있음
* metadata trace 출력은 디버깅 및 검증에서 필수
* “tested vs fallback vs eq-based 경로”는 항상 명시적으로 검증해야 함

## 2026-05-04 — AHRI 210/240 HSPF2 v3 규격 정합성 검증 및 수정

### Tried

* `core/calculator_ahri_hspf2.py`의 AHRI HSPF2 v3 경로를 실제 AHRI 공식 계산기 CSV 결과와 비교했다.
* `H12 tested: No`, `H22 tested: No`, `H42 tested: Yes`, `Region IV`, `Cd=0.25`, `fdef_override=1.0`, `t_on/t_off=-40` 조건의 golden case 2개를 기준으로 검증했다.
* `H12`, `H22`를 optional test point로 처리하도록 단계별로 수정했다.
* `H12` 미실시 시 `h1n_same_speed_as_h3=True`는 Eq.11.183, 기본은 Eq.11.185~11.186 경로로 처리했다.
* `H22` 미실시 시 초기에는 17°F~47°F 단순 보간 fallback을 적용했으나, 이후 AHRI 문구 확인을 통해 Eq.11.44 / Eq.11.50 기반 fallback으로 교체했다.
* `t_off=-40.0`, `t_on=-40.0`, `fdef_override=1.0` 기본값을 추가했다.
* `Fdef` 처리에서 `f_def_seasonal=1.03`이 최종 HSPF2에 중복 곱해지는 문제를 추적했다.
* `does_comp_limit_min_spd=True` 조건에서 minimum-speed-limiting 경로 Eq.11.189~11.194를 연결했다.
* AHRI 공식 CSV의 `ratioTotalHeating`, `ratioTotalPower`, `ratioTotalResistHeating`, `M_Q`, `M_E`, `heatCapacity35full`, `powerConsumption35full`를 기준으로 bin-level 비교를 수행했다.
* `summary["metadata"]`에 `h12_source`, `h22_source`, `t_off_used`, `t_on_used`, `defrost`, `minimum_speed_limited`, `case_i_low_source`, `h22_capacity`, `h22_power` 등 trace 정보를 추가했다.
* CSV 파일은 검증 참고용으로만 사용하고 commit 대상에서 제외했다.

### Result

* `H12` optional 처리 완료:

  * `tested`
  * `eq_11_183`
  * `eq_11_185`
    경로를 metadata로 추적 가능하게 됐다.
* `H22` optional 처리 완료:

  * 최종적으로 `h22_source = "eq_11_44_11_50"` 경로로 정리했다.
  * Case #2 기준 `H2Full capacity = 26275.792968`, `H2Full power = 3190.51390385`가 AHRI CSV와 일치했다.
  * `M_Hq`, `M_HE`도 CSV의 `M_Q`, `M_E`와 일치했다.
* `fdef_override=1.0` 경로에서 seasonal defrost multiplier 중복 적용을 제거했다.

  * 변경 전: `raw_hspf2 = raw_hspf2_base * f_def_seasonal * fdef_override`
  * 변경 후: `raw_hspf2 = raw_hspf2_base * fdef_override`
* `does_comp_limit_min_spd=True`일 때 Case I low-speed bin이 Eq.11.189~11.194 경로를 타도록 연결했다.
* Case II bin인 27°F, 22°F, 17°F는 CSV와 power/heat/COP가 사실상 일치함을 확인했다.
* Case #1은 최종적으로 `rounded_hspf2 ≈ 9.45`로 AHRI 공식값과 일치 수준까지 도달했다.
* Case #2는 A2 capacity를 CSV 기준 `22420.0`으로 정정한 뒤 heating은 일치했으며, 남은 차이는 Case III 저온 full branch로 좁혀졌다.
* 주요 commit:

  * `ccb54ad feat: implement optional H12 fallback per AHRI 210/240-2026`
  * `0fca67a chore: add HSPF2 v3 metadata trace for AHRI validation`
  * `ca45edf fix: route minimum-speed-limiting HSPF2 bins through AHRI path`
  * `bd24058 fix: use calculated H1Full anchor for H22 fallback`
  * `2854e1b fix: avoid duplicate seasonal defrost multiplier when Fdef override is used`
  * `27db19f fix: use Eq.11.44 and Eq.11.50 for missing H22 fallback`

### Failed / Risk

* 처음에는 `H22` 미실시 fallback을 `H3Full`~`H1Full_calc`의 17°F~47°F 단순 보간으로 해석했으나, AHRI 공식 CSV와 불일치했다.
* `H22` fallback 값이 틀리면서 `M_Hq/M_HE`가 과대 산출되고, 35°F 이하 intermediate slope가 틀어졌다.
* `f_def_seasonal=1.03`이 최종 HSPF2에 중복 곱해져 AHRI 공식값보다 HSPF2가 높게 나오는 문제가 있었다.
* Case #2의 A2 입력값을 CSV와 다르게 넣어 building load 전체가 낮게 잡히는 혼선이 있었다.
* Case III 저온 bin에서 `q_full/p_full`이 CSV보다 높게 계산되어 resistance heat가 낮게 산출되는 문제가 아직 남았다.
* `_cert_full_capacity_power_at_temp()`의 `temp_f <= 5°F` branch가 CSV와 맞지 않으며, 이 부분은 별도 재검토가 필요하다.
* AHRI HSPF2 수식은 SEER2 섹션 수식을 준용하는 부분이 있어, equation 번호만 보고 HSPF2 내부 보간식으로 추정하면 오해가 생길 수 있다.

### Decision

* `H12`, `H22`는 required point가 아니라 optional point로 유지한다.
* `H12` 미실시:

  * `h1n_same_speed_as_h3=True` → Eq.11.183
  * 기본 → Eq.11.185~11.186
* `H22` 미실시:

  * Eq.11.44 / Eq.11.50 사용
  * 기존 `"fallback_interp_17_47"` 경로는 폐기하고 `"eq_11_44_11_50"`로 추적한다.
* `fdef_override=1.0`일 때는 최종 HSPF2에 `f_def_seasonal`을 추가 곱하지 않는다.
* `does_comp_limit_min_spd=True`는 반드시 Eq.11.189~11.194 경로로 연결한다.
* CSV 검증 파일은 commit하지 않고, 코드 수정 파일만 commit한다.
* 다음 수정 대상은 `_cert_full_capacity_power_at_temp()`의 `h4_point is not None and temp_f <= 5°F` branch로 한정한다.

### Lesson

* optional test point는 코드에서도 optional이어야 하며, missing case는 규격 fallback 수식으로 처리해야 한다.
* AHRI 공식 계산기 CSV의 중간 컬럼(`M_Q`, `M_E`, `heatCapacity35full`, `ratioTotalPower`, `ratioTotalResistHeating`)은 단순 최종값보다 훨씬 강력한 검증 기준이다.
* HSPF2 오차는 최종 HSPF2만 비교하지 말고, 반드시 bin-level heat/power/resistance로 분해해야 원인을 찾을 수 있다.
* `raw_hspf2_base`와 `raw_hspf2`를 분리해두면 defrost 중복 적용 같은 오류를 빠르게 찾을 수 있다.
* `metadata` trace는 규격 계산기 검증에서 필수다. `h12_source`, `h22_source`, `case_i_low_source`, `defrost mode`가 없으면 오차 원인 추적이 어려워진다.
* Codex 작업은 한 번에 크게 맡기기보다 defaults → optional point → metadata → golden case → bin diff처럼 작은 단계로 나누는 것이 안전하다.
* 규격 equation 번호가 다른 섹션 수식을 준용하는 경우가 있으므로, “HSPF2 섹션 안의 보간식”이라고 추정하지 말고 원문 문구를 확인해야 한다.
* 입력값 검증 전에 golden case의 A2, H2v power 같은 원본 입력 오타를 먼저 확인해야 한다.

## 2026-05-04 — AHRI HSPF2 v3 strict 계산 경로 및 UI 연결 정리

### Tried
- `calculate_hspf2_v3()`의 AHRI 210/240-2026 Variable Capacity Heating 경로를 CODEX로 점검/수정했다.
- 초기에는 H2Int 입력을 기존 full/low 보간 경로에 연결하는 방식으로 접근했으나, 이후 규격 구현 원칙을 재정의했다.
- `H2Int`, `H01`, `H11`, `H12`, `H1N`, `H22`, `H32`, `A2`, `t_off`, `t_on`, `defrost_t_test_minutes`, `defrost_t_max_minutes`를 strict 필수 입력으로 검증하도록 정리했다.
- Case I / Case II / Case III bin 분기, `q_low/P_low`, `q_int/P_int`, `q_full/P_full`, `delta_j`, auxiliary heat 분리 집계 경로를 추가/정리했다.
- 기존 SEER2 UI 연결 방식을 참고하여 HSPF2 v3 strict 계산 경로를 기존 PyQt window에 연결하도록 CODEX 작업을 진행했다.
- Codex 작업 시 전체 리팩토링/대형 파일 전체 탐색이 토큰을 크게 소모한다는 점을 다시 확인했다.

### Result
- `core/calculator_ahri_hspf2.py`에서 v3 공개 경로는 AHRI 210/240-2026 strict 경로만 실행하도록 정리되었다.
- legacy v3 fallback block과 ratio projection helper가 제거되었다.
- H2Int power 변경 시 HSPF2 결과가 변하는 것을 테스트로 확인했다.
  - base `raw_hspf2`: `10.187003`
  - H2Int power changed `raw_hspf2`: `9.822598`
- Case 분기 테스트에서 Case I / II / III bin이 분리되어 확인되었다.
  - Case I: `[3, 4, 5, 6]`
  - Case II: `[7, 8, 9, 10]`
  - Case III: `[11, 12, 13, 14, 15]`
- 실행된 주요 테스트는 모두 pass 했다.
  - `python3 -B test_hspf2_v3_h2int.py`
  - `python3 -B test_hspf2_v3_smoke.py`
  - `python3 -B test_hspf2_v3_low_cases.py`
  - `python3 -B test_hspf2_v3_bincheck.py`
  - `python3 -B test_hspf2_smoke.py`
  - `python3 -B -m py_compile core/calculator_ahri_hspf2.py`
- UI 연결 작업은 코드 수준에서는 진행되었으나, CODEX 환경에 `PyQt5`가 없어 오프스크린 위젯 실행 검증은 실패했다.
  - 실패 사유: `ModuleNotFoundError: No module named 'PyQt5'`
  - 이는 코드 오류가 아니라 CODEX/headless 환경 제약으로 판단했다.

### Failed / Risk
- 초기에 `certification-grade / fallback` 같은 표현과 `ratio fallback` 유지 방향을 검토했으나, 프로젝트 원칙과 맞지 않았다.
- 규격 계산기에서 fallback으로 숫자를 내면 “그럴듯하지만 틀린 값”이 될 위험이 크다.
- “규격서대로 싹 뜯어고치기” 방식은 방향은 맞지만 CODEX 토큰/잔고 소모가 매우 크다.
- PyQt UI 실행 검증은 CODEX 환경에서 신뢰하기 어렵고, 로컬 PC에서 직접 클릭 테스트가 필요하다.
- `app_trainer`, `app_predictor` 정상 동작 검증은 아직 진행하지 않았다.
- CSPF/HSPF 계산 결과를 Predictor feature/result output에 연결하는 작업은 아직 남아 있다.

### Decision
- 규격 계산기는 앞으로도 fallback/추정/임의 보간을 허용하지 않는다.
- 규격에서 필요한 입력값이 없으면 계산하지 않고 즉시 에러를 띄운다.
- AHRI HSPF2 v3는 strict 입력 검증과 strict 계산 경로만 유지한다.
- UI는 계산 로직을 포함하지 않고, 입력값 수집 → canonical input mapping → calculator 호출 → 결과 표시 역할만 담당한다.
- CODEX에는 앞으로 “대규모 리팩토링”보다 작업 범위를 명확히 제한하되, 규격 계산 로직 자체는 애매하게 구현하지 않도록 지시한다.
- 내일 출근 후 우선 `app_trainer`와 `app_predictor` 정상 동작 검증을 진행한다.
- 이후 주말 동안 만든 CSPF/HSPF 계산 결과를 Predictor에 연결하는 작업으로 넘어간다.

### Lesson
- 규격 구현에서는 결과가 두 가지뿐이어야 한다: 정확한 계산값 또는 에러.
- fallback, approximate, internal validation mode 같은 우회 경로는 규격 계산기에서 장기적으로 위험하다.
- CODEX에게 “싹 뜯어고쳐”라고 하면 빠르게 정리될 수 있지만 토큰/잔고 소모가 크므로, 실행 전 범위와 산출물을 명확히 제한해야 한다.
- GUI 검증은 CODEX보다 로컬 환경에서 직접 확인하는 것이 맞다.
- 이미 있는 SEER2 UI 연결 패턴처럼 검증된 흐름을 재사용하는 것이 안전하다.
- 문서화 시에는 시행착오도 남겨야 같은 fallback 논쟁과 토큰 낭비를 반복하지 않는다.
