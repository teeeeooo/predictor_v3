# Project Log
이 문서는 작업 과정의 시도, 실패, 성공, 중요 결정사항 및 반복 방지를 위한 기록용입니다.

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
- 현재 상태 요약은 `project_brief.md`.
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
