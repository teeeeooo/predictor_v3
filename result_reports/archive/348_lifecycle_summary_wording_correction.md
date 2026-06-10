# Active Report 348: Lifecycle & Summary Wording Correction

## 목표 (Goal)

본 보고서의 목적은 Summary 346 및 active Report 347의 일부 문구를 프로젝트 문서화 가이드라인 및 lifecycle threshold 원칙에 맞추어 보정하고 기록하는 것이다.

## 346 Wording Correction 내용

Summary 346의 과도하게 확정적인 표현들을 evidence-based 표현으로 낮추어 보정하였다:
- `ui/` legacy PyQt boundary는 수정 없이 유지함.
- `train/predict` boundary는 변경하지 않음.
- `core/calculator` 변경 없이 경계를 유지함.
- 108 focused pytests와 check_code_structure.py를 통과하여 이번 relocation 범위의 import/structure 회귀를 방어함.

## 347 Exact Count Wording Correction 내용

Report 347 본문에서 exact active report count로 보일 수 있는 표현을 threshold wording으로 보정하였다:
- `Remaining Active: 본 보고서 (347) 단 1개만 active로 유지` 문구를 `Remaining Active: cleanup evidence report remains active as the next-action pointer`로 수정하여 durable report body 내에 exact count를 명시하지 않는 규칙을 충족함.

## 변경하지 않은 범위 (Non-goals)

- Python 프로덕션 소스 코드 및 테스트 코드는 절대 수정하지 않았습니다.
- `docs/WORK_PLAN.md`는 본 작업에서 수정하지 않고 보존하였습니다.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`, `PROJECT_CHARTER.md`, `docs/architecture/` 등 핵심 아키텍처 및 맵 문서는 본 작업에서 제외되었습니다.
- `result_reports/archive/`에 저장된 예전 archive 파일들은 수정하거나 이동하지 않았습니다.

## 검증 결과 (Verification Results)

- `python3 -B tools/check_code_structure.py` 검사 수행 완료 (code structure guard: OK)
- `git diff --check` 검사 수행 완료 (whitespace 에러 없음)
- `grep`을 통해 "고스란히", "완벽히", "100% 회귀", "clean warning", "단 1개" 등의 표현이 수정 대상 파일에서 완전히 제거되었음을 확인함.

## Next Action (차기 계획)

1. **Calculator PyQt reference retirement preflight**:
   - `apps/calculator`로의 Tkinter 이주가 완성됨에 따라 legacy PyQt 기반 계산기 UI 코드(`ui/calc_window.py` 등)의 안전한 은퇴 가능 여부를 preflight 진단합니다.

## Lifecycle Wording

- active report count is below lifecycle threshold
