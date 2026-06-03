# 134 Standardize Project Memory Keywords Format

## Goal

`Project Memory Delta` 항목의 `keywords`가 일관된 YAML list 형식으로 작성되도록 report workflow 규칙을 보강한다.

## Scope

- `AGENT_TASK_ROUTER.md`의 `Project Memory Delta` 규칙에 `keywords` YAML list 형식과 예시 추가
- 이 Compact report 작성
- 기존 report, summary, archive, `project_log.md`, 코드, 테스트, config는 변경하지 않음

## Changed Files

- `AGENT_TASK_ROUTER.md` - `keywords` YAML list 작성 규칙, 예시, 기존 문자열 사례의 retroactive 수정 금지 추가
- `result_reports/active/134_standardize-project-memory-keywords-format.md` - 작업 결과 Compact report

## Verification

- `git diff --check` - 통과
- `rg -n "keywords|YAML list|Project Memory Delta|retroactive" AGENT_TASK_ROUTER.md result_reports/active` - 신규 작성 규칙과 기존 report 비수정 상태 확인
- `git diff --name-only` - report 작성 전 source/docs 변경 파일이 `AGENT_TASK_ROUTER.md`뿐임을 확인
- Scope compliance - 기존 report, summary, archive, `project_log.md`, 코드, 테스트, config를 수정하지 않음

## Known Risks

- `result_reports/active/133_add-project-memory-delta-workflow.md`의 기존 문자열형 `keywords`는 금지 범위와 retroactive 수정 금지 규칙에 따라 그대로 유지된다.
- inventory audit, backfill, memory seed report 생성은 이 작업에서 수행하지 않았다.

## Commit / Push

- Source/docs commit: `3bfd5ddba91b40d2148863b84d24beb4fb0f88b4` (`docs: require YAML list memory keywords`)
- Report commit: 이 파일을 포함하는 별도 `report: ...` 커밋으로 생성
- Push: report commit 생성 후 `origin/work/ui-ux-ssot-adoption`으로 push하고 최종 결과에서 확인

## Project Memory Delta

- type: `procedure`
  topic: `predictor_v3 Project Memory Delta keywords serialization`
  content: `predictor_v3 result reports serialize Project Memory Delta keywords as a YAML list instead of a comma-separated string.`
  keywords:
    - predictor_v3
    - result report
    - project memory delta
    - YAML list
  assertionStatus: `verified`
  source: `AGENT_TASK_ROUTER.md Project Memory Delta; source commit 3bfd5ddba91b40d2148863b84d24beb4fb0f88b4`
