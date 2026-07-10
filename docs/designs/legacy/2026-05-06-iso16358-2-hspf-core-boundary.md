# Design Gate Summary

## Goal

ISO16358-2 HSPF 구현에서 `global core`와 `region handler/config/profile`의 경계를 검증한다. 코드 수정은 하지 않는다.

## Confirmed Decisions

- `global core`는 ISO16358-2 본문에서 지역과 무관한 canonical HSPF 계산 구조만 담당한다.
- region/profile 선택, alias, unit normalization, optional matrix, 지역별 rounding, test/golden/production 구분은 core 밖에서 처리한다.
- core input contract는 canonical-only로 고정한다.
- metadata는 audit/debug/result trace 전용이며 계산 분기 조건으로 사용할 수 없다.
- core 내부 분기는 ISO 표준 equipment/operating-case branch만 허용한다.
- ML predictor core에도 같은 boundary rule을 적용한다.

## Core vs Handler Boundary

Core 포함:

- heating bin loop
- building load 산정
- fixed/two-stage/multi-stage/variable operating case 분류
- capacity/power interpolation 또는 extrapolation
- per-bin COP/efficiency 계산
- ISO 공통 backup/make-up heat 구조
- HSTL, HSEC, HSPF 집계
- `bin_details` / intermediate result 생성
- ISO standard fallback

Handler/config/profile 책임:

- KS C 9306 rounding
- Korea-specific test point 보정
- SASO T3 등 climate/profile 선택
- optional matrix 채택 여부
- production bin/profile 값
- UI 표시용 편의 계산
- local alias/local naming
- golden/sample/test 전용 값

## Data Shape / API Boundary

Canonical heating input schema는 세 그룹으로 둔다.

- `required_calculation_inputs`: HSPF 계산 필수값
- `standard_options`: ISO 공통 계산 선택값
- `trace_metadata`: 계산에 쓰지 않는 추적 정보

Forbidden fields는 `trace_metadata`를 제외한 전체 input tree에서 recursive validation한다.

- `region`, `country`, `profile`
- `local`, `raw`, `alias`
- `ks`, `korea`, `saso`
- `golden`, `sample`
- `selector`
- `rounding_policy`, `optional_matrix_policy`, `bin_profile_selector`

Validation 실패 시 core는 `CanonicalInputValidationError` 같은 명시적 exception으로 즉시 중단한다. Public wrapper/UI adapter만 이를 structured error result로 변환할 수 있다.

## Required Tests

- ISO common fallback test
- region/profile fallback test
- top-level forbidden key rejection
- nested forbidden key rejection
- `trace_metadata.source_region` 허용
- trace metadata 변경이 계산 결과를 바꾸지 않음
- missing required field -> validation exception
- wrapper 호출 시 structured error result 변환
- validation 실패 시 HSPF/HSEC/HSTL/bin_details 미생성
- ML predictor core에서도 raw/local/experiment-only feature 거부

## Migration / Refactor Path

- 기존 public API가 dict result를 강제한다면 wrapper에서만 error dict를 만든다.
- core calculation function은 success result와 failure state를 섞지 않는다.
- region fallback trace는 가능하면 metadata namespace로 전달하되, core 계산은 이를 읽지 않는다.
- schema guard는 명시적 denylist와 테스트로 시작하고 필요 시 확장한다.

## Risks

- forbidden pattern이 과도하면 정상 canonical field를 막을 수 있다.
- trace metadata가 나중에 계산 분기 조건으로 오용될 수 있다.
- wrapper가 validation exception을 너무 넓게 잡으면 core boundary 위반이 숨겨질 수 있다.
- region handler가 canonical normalization 책임을 불완전하게 수행하면 core가 실패하게 된다.

## Non-goals

- 코드 수정 없음
- public API 변경 없음
- UI/ML/계산기 리팩토링 없음
- KS/SASO 특정 로직 구현 없음
- golden/sample/test 값 production config 반영 없음

## Next Codex Implementation Prompt

ISO16358-2 HSPF implementation must preserve the Design Gate boundary: implement only canonical ISO common logic in the global core, accept canonical-only heating input, reject forbidden raw/region/profile/policy fields recursively outside trace metadata, keep trace metadata calculation-neutral, and route all region/profile fallback or normalization through explicit handler/config/profile layers.
