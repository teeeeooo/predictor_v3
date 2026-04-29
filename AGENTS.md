# predictor_v3 Agent Rules (Lite)
전체 규칙: AGENTS_FULL.md 참조

## 절대 원칙
- Train/Predict 분리: app_train.py ↔ app_predict.py 병합 금지
- core/predictor.py에 optuna/sklearn/shap/matplotlib import 금지
- COLUMNS → core/constants.py, MODEL_REGISTRY → core/models.py 단일 소스 유지

## 계산기
- numpy/pandas 금지 (순수 Python only)
- calculate_hspf2_v2() / calculate_hspf2() 무단 수정 금지
- UI / ML 코드 수정 금지 / JSON 필드 삭제 금지
- ISO16358/KS C 9306 계산기 수정 시 `docs/iso16358/iso16358_dev_notes.md`와 `docs/iso16358/korea_ks_c_9306_notes.md`를 먼저 확인할 것

## ML
- model.fit()에 .values 변환 금지 (feature_names_in_ 보존)
- Cooling / Heating 완전 독립 모델 유지 (MultiOutput 금지)
- 물리 제약 > 통계 수치 (단조 제약 Monotone Constraints 유지)

## UI
- QTableWidget 금지 → QTableView + QAbstractTableModel만 허용
- setCellWidget 금지 → QStyledItemDelegate만 허용
- blockSignals는 반드시 try/finally로 감쌀 것

## 수정 범위
- 지정된 파일/함수만 수정, 관련 없는 코드 수정 금지
- 함수명/JSON key 변경 금지
- 구조 개선 및 리팩토링 예정 사항은 `docs/REFACTOR_PLAN.md`를 참조하라. 명시적인 지시가 없는 한 절대로 먼저 리팩토링을 수행하지 마라.

## 출력
- 코드만 출력, 작업 완료 시 [수정 파일] / [변경 내용] / [테스트 결과] 형식 유지
