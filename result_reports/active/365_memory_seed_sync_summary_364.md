# Active Report 365: Project Memory Seed Sync after Summary 364

## 목표 (Goal)
* Summary 364의 Project Memory Seed Sync Judgment 지침에 따라, 이번 마일스톤에서 확정된 핵심 decision들을 `result_reports/memory/project_memory_seed.md`에 Stage 1 entries로 최소 반영한다.
* 이번 작업은 memory seed 갱신 및 기록 전용이며, source code 및 tests는 수정하지 않는다.

## 범위 (Scope)
* **갱신 대상**: `result_reports/memory/project_memory_seed.md`
* **추가 내용**: Source File Owner Boundary Policy 및 EN14825 defaults prefill hierarchy에 관한 2개 entry 신규 추가, 그리고 Source Summaries 리스트에 summaries 334, 346, 364 추가.
* **비대상**: 기존 memory seed의 대량 삭제/수정/재작성 배제.

## 수정 파일 (Changed Files)
* [project_memory_seed.md](../memory/project_memory_seed.md)

## Added Memory Seed Entries
YAML 형식으로 추가된 2개의 entries 세부사항은 다음과 같습니다:

1. **`predictor_v3 source file owner boundary policy`** (`decision`):
   * **내용**: 신규 소스 파일 생성 전에 소유 패키지 경계를 명시적으로 결정해야 하며, broad folder에 flat file을 직접 추가하는 것을 차단합니다. 여러 파일로 확장될 calculator UI 피처는 `apps/calculator/ui/<feature>/` 형태의 패키지 디렉토리로 격리하고, `check_code_structure.py` 정적 검사기를 통해 이를 강제(error/warning)합니다.
   * **Keywords**: `predictor_v3`, `source owner boundary`, `feature package`, `check_code_structure`, `flat file guard`
2. **`EN14825 GUI prefill defaults hierarchy`** (`decision`):
   * **내용**: EN14825 UI prefill defaults는 config의 validation 한계와 분리된 사용자 편집 가능한 UI prefill 값이며, core 계산 엔진은 config default가 아니라 현재 UI에서 resolve된 현재 편집 값을 전달받아 계산합니다. `declared_power`는 내부 core 입력용 값으로 row 노출을 차단합니다.
   * **Keywords**: `predictor_v3`, `EN14825`, `prefill defaults`, `UI input`, `adapter boundary`

## 중복/스킵 후보 (Duplicate/Skipped Candidates)
* 기존 entries에 동일한 도메인/피처의 정책이 존재하지 않음을 topic/keyword 단위로 확인하였으며, 스킵되거나 누락된 후보는 없습니다.

## 검증 결과 (Verification Results)
* `python3 -B tools/check_code_structure.py`: **code structure guard: OK (no findings)** (정적 가드 정상 작동 및 위반 사항 없음)
* `git diff --check`: whitespace 에러 없음.
* `git status --short`: `project_memory_seed.md` 수정 및 새 active report 생성 상태 확인 완료.

## Known Risks
* Memory seed entries가 누적되어 50개 임계치에 도달하는 경우, 추후 memory maintenance task를 제안하여 seed 정리 및 indexing preflight를 수행해야 하는 장기적 과제가 있습니다. (현재는 threshold 미만이므로 cleanup 보류)

## Project Memory Seed Sync Judgment
* Summary 364 마일스톤에 대한 memory seed sync를 완료하여 memory seed의 최신성을 동기화하였습니다. 향후 GUI section integration 작업 시 이 entries 정보가 참고자료로 자동 활용됩니다.

## Next Suggested Action
* **EN14825 SEER section integration with real-time updates** (GUI 조립 및 실시간 이벤트 바인딩)
