# Packaging Guide

## Purpose
- `predictor_v3`의 로컬/배포 패키징 원칙을 관리한다.
- Packaging task procedure는 repository-local `.agents/skills/packaging/SKILL.md`가 제공하고, runtime dependency policy는 `docs/development/dependencies.md`가 소유한다.
- 이 문서는 packaging policy owner이며, 과거 milestone/failure context가 필요할 때만 `project_log.md`를 reference evidence로 조회한다.

## Current status
- 현재 프로젝트에 완전 자동화된 packaging workflow나 전용 빌드 스크립트는 존재하지 않는다.
- 명확히 확정된 build command나 `.spec` 파일은 없으므로, 아래 원칙은 패키징 파이프라인 구축 시의 가이드라인으로 작용한다.
- Train 애플리케이션의 주 지원 환경은 Windows다. Data Definition runtime
  generation state는 `%LOCALAPPDATA%\\predictor_v3\\data_definition`에 저장하며,
  tracked bootstrap seed는 `config/data_definition/manifest.json`에 유지한다.
  POSIX 개발 환경은 `$XDG_STATE_HOME/predictor_v3/data_definition` 또는
  `~/.local/state/predictor_v3/data_definition`을 사용한다.

## Packaging principles
- **클린 배포 환경**: 일반 개발 환경과 섞이지 않도록, 배포용 빌드는 반드시 독립된 깨끗한 환경에서 수행한다.
- **전용 가상환경 사용**: PyInstaller 빌드는 `venv_deploy` 또는 그에 준하는 별도 배포용 가상환경 생성을 권장한다.
- **의존성 최소화**: 패키징 시 불필요한 개발용 라이브러리가 포함되지 않도록 관리한다.
- **앱별 requirements 기준**: `app_train.py` 패키징은 `requirements/train.txt`,
  `app_predict.py` 패키징은 `requirements/predict.txt`,
  `app_calculator.py` 패키징은 `requirements/calculator.txt`를 dependency
  baseline으로 삼는다. `requirements/dev.txt`는 명시 승인 없는 packaged
  runtime 기본 source가 아니다.
- **Excel dependency 분리**: generated XLSX write/export는 `openpyxl`,
  기존 사용자 Excel read workflow는 Windows 사용자 환경의 `xlwings` 정책을
  따른다.
- **작업 분리**: 패키징 작업 시 계산기, ML, UI 등의 핵심 코드/로직 변경을 동시에 진행하지 않는다.

## PyInstaller considerations
- **DLL 런타임 방어**: XGBoost, scikit-learn, NumPy 등의 라이브러리 사용 시 DLL 파일 누락 에러가 발생하기 쉬우므로 주의한다. Predict packaging도 real `model.pkl` inference를 위해 XGBoost/scikit-learn runtime을 고려해야 한다.
- **binaries 매핑**: 누락 방지를 위해 `.spec` 파일 생성 시 `binaries` 항목에 해당 동적 라이브러리들을 명시적으로 매핑해야 한다.
- **spec 파일 관리**: 자동 생성된 `.spec` 파일에만 의존하지 않고, 검증 후 버전 관리 대상에 포함할지 고려한다.
- **배포 형태**: onefile 또는 onedir 선택은 실제 사용자 배포 및 업데이트 요구사항에 따라 추후 결정한다.

## Crash logging
- **글로벌 에러 로깅**: GUI 애플리케이션 특성상 콘솔 출력이 가려지므로 `sys.excepthook` 또는 동등한 글로벌 핸들러를 배치한다.
- **로그 파일 생성**: 강제 종료 또는 치명적 에러 발생 시 `crash_log.txt`와 같은 형태로 사용자 환경에 로그를 남기도록 설계한다.
- **에러 추적성**: 사용자 환경에서 발생한 failure report가 유실되지 않도록 보존 정책을 마련한다.

## Do not
- 일반 개발용 `venv`와 배포용 `venv_deploy` 환경 혼용 금지.
- Packaging 작업 브랜치나 커밋에서 계산 로직/UI 구조 무단 수정 금지.
- 검증 없이 용량이 큰 외부 dependency 임의 추가 금지.
- 아직 동작 확인이 되지 않은 추측성 build command를 canonical 가이드로 문서화 금지.

## Open questions
- PyInstaller 배포 최적 형태 (onefile vs onedir 성능/로딩 속도 트레이드오프).
- XGBoost/scikit-learn/NumPy 외에 명시적 매핑이 필요한 실제 binary dependency 목록.
- 생성된 crash log의 저장 위치(AppData 등) 및 보존 주기(retention policy).
