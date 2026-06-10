# Active Report 350: Report 349 Local Link Correction

## 목표 (Goal)

* [Report 349](349_calculator_pyqt_reference_retirement_preflight.md) 본문에 포함된 로컬 절대경로 링크(`file:///Users/sunjaekim/Downloads/태우 작업/...`)들을 repo-relative 상대경로 링크로 보정하여 타 환경에서의 링크 깨짐을 방지하고 로컬 사용자 절대경로 노출을 제거한다.

## 발견된 local absolute link 문제 (Problem)

* `result_reports/active/349_calculator_pyqt_reference_retirement_preflight.md` 파일 생성 시, 기준 문서, 런타임 파일, 테스트 파일 링크들이 로컬 개발 환경의 절대경로를 가리켜 외부 환경 가독성 및 이식성에 문제가 발견되었습니다.

## 보정 방식 (Correction method)

* `result_reports/active/` 디렉토리에 위치한 Report 349 기준의 상대경로 링크로 일괄 수정하였습니다:
  * 루트 레벨 파일(예: `AGENT_TASK_ROUTER.md`, `app_calculator.py` 등): `../../` 접두사 사용
  * 아카이브 레포트(예: `154_pyqt-calculator-retirement-audit.md` 등): `../archive/` 접두사 사용
  * 요약 레포트(예: `346_summary-batch-foundation-apps-calculator-relocation-closeout.md` 등): `../summaries/` 접두사 사용
  * 액티브 레포트(예: `347_active_report_lifecycle_cleanup_after_apps_calculator_relocation.md` 등): 접두사 없이 파일명 직접 지칭

## 변경하지 않은 범위 (Non-goals / Unchanged scope)

* PyQt retirement preflight의 감사 내용 및 판단(readiness judgment, reference inventory, next slices)을 변경하지 않았습니다.
* [docs/WORK_PLAN.md](../../docs/WORK_PLAN.md)를 수정하지 않았습니다.
* `project_log.md` 및 `result_reports/memory/project_memory_seed.md`는 수정하지 않고 보존하였습니다.
* Python 프로덕션 소스 코드 및 테스트 코드는 본 작업에서 제외되었습니다.

## 검증 결과 (Verification)

* `python3 -B tools/check_code_structure.py` 검사 수행 완료 (findings 없음).
* `git diff --check` 검사 수행 완료 (whitespace 오류 없음).
* `grep`을 통해 Report 349 본문에서 `file:///Users`, `Downloads`, `태우 작업` 키워드가 완전히 제거되었음을 확인하였습니다.
* active report count가 lifecycle threshold 이하임을 확인하였습니다.

## Next Action

* **Slice 1: Mixed ISO table test split or retirement** 실행을 추천합니다.
