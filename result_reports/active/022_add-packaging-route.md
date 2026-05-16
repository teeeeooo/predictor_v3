# 022 Add Packaging Route

## Goal
- 패키징 작업 요청 시 `docs/PACKAGING.md`가 active owner 문서로 연결되도록 workflow inbound를 보강한다.

## Scope
- `AGENTS.md` routing clue에 `Packaging / 배포 빌드`를 추가했다.
- `AGENT_TASK_ROUTER.md`에 Packaging route를 추가해 `docs/PACKAGING.md` 기본 참조, 조건부 참조, 금지 범위, 검증 보고 기준을 정의했다.
- root `README.md`와 `docs/README.md` 문서 맵에 `docs/PACKAGING.md`를 추가했다.
- `project_log.md`에 packaging route owner 연결 결정을 기록했다.

## Changed Files
- `AGENTS.md`
- `AGENT_TASK_ROUTER.md`
- `README.md`
- `docs/README.md`
- `project_log.md`
- `result_reports/active/022_add-packaging-route.md`

## Verification
- `rg -n "Packaging|PACKAGING|docs/PACKAGING.md" AGENTS.md AGENT_TASK_ROUTER.md README.md docs/README.md project_log.md`
  - expected inbound entries found in all target documents.
- `git diff --check`
  - passed.

## Known Risks
- Runtime tests were not run because this is a docs/router-only workflow change.
- No packaging command, `.spec`, or build script was added; packaging execution remains governed by `docs/PACKAGING.md` and future task evidence.
- Calculator, ML, UI, JSON schema, and public API files were not modified.

## Commit / Push
- Source change commit: `9796d3c docs: route packaging workflow`
- Report commit: pending.
- Push: pending.
