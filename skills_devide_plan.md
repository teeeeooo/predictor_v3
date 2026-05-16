1차: data/skills.md inventory / owner mapping

각 section을 owner로 나눠야 해.

1. PyQt5 dropdown delegate
   → docs/architecture/project_architecture.md 또는 UI section
   → 단, QTableWidget 기반 코드는 deprecated example로만 보존

2. cascading autofill pattern
   → docs/architecture/project_architecture.md UI guardrails

3. dropdown target mapping
   → docs/architecture/project_architecture.md 또는 core/constants 관련 architecture note

4. xgboost_rfe_pipeline
   → docs/knowledge/hvac_ml_feature_engineering.md
   → docs/architecture/project_architecture.md ML training guardrails

5. ml_safety_patterns
   → docs/knowledge/hvac_ml_data_quality.md
   → docs/architecture/project_architecture.md ML artifact/preprocess guardrails

6. model_registry_pattern
   → docs/architecture/project_architecture.md

7. test_harness_pattern
   → docs/knowledge/hvac_ml_data_quality.md 또는 별도 test strategy section
2차: owner docs에 이미 반영됐는지 audit

바로 옮기지 말고, “이미 반영됨 / 부분 반영 / 미반영”으로 나눠야 해.

예상은 이럴 것 같아.

이미 반영 가능성 높음:
- .values 금지
- feature_names_in_
- MODEL_REGISTRY SSOT
- model.pkl 단일 artifact
- preprocess_version guard
- QTableView / QStyledItemDelegate
- blockSignals try/finally

부분 반영 가능성:
- UI paste 경로 주의
- QTimer.singleShot one-click UX
- cascading autofill 3단계
- feature snapshot candidates/selected
- test harness 4단계

미반영 가능성:
- 구체적인 V2 시행착오 설명
- model.pkl 구조 변경 시 SHAP 호환성 우려
- optimization harness optuna 실행 조건

3차: 이관 후 data/skills.md 처리

docs/archive/skills_v2_patterns.md 로 이동


