# Project Log
이 문서는 작업 과정의 시도, 실패, 성공, 중요 결정사항 및 반복 방지를 위한 기록용입니다.

## 2026-05-04
- **Validation 안정화 완료:** Validation smoke 및 golden 테스트 안정화가 완료되었습니다.
- **Hong Kong HSPF:** Hong Kong HSPF smoke/golden validation을 완료했습니다.
- **아카이브 이동:** 루트 디렉토리에 있던 임시/레거시 ISO16358 reverse engineering 파일들을 `docs/archive` 폴더로 이동 완료했습니다.
- **결정 (문서 리팩토링):** `project_context.md`가 비대해짐에 따라 역할 분리를 위한 문서 리팩토링 시작을 결정했습니다.

### [반복 방지 및 레슨런]
- **반복 실수:** ISO16358 계열 계산식 작업 시, 공통 엔진 구조보다 지역별 하드코딩을 먼저 시도하여 재작업이 발생했습니다.
- **결정 (Logic 수정 방향):** 앞으로 Logic 수정 시에는 지역별 하드코딩을 배제하고, 반드시 **공통 엔진 / profile / config / handler** 구조로 표현/수용이 가능한지를 먼저 검토해야 합니다.
