# core/ml/training.py — 학습 파이프라인 및 하이퍼파라미터/피처 최적화
import os
import joblib
import pandas as pd
import numpy as np
import optuna
import datetime
from xgboost import XGBRegressor
from sklearn.model_selection import KFold
from sklearn.feature_selection import RFECV
from sklearn.metrics import mean_squared_error, r2_score

from core.ml.artifacts import TRAIN_DATA_FILE
from core.ml.catalog_fingerprint import attach_catalog_fingerprint
from core.ml.feature_catalog import load_feature_catalog, validate_feature_catalog
from core.ml.feature_catalog_projection import validate_training_headers
from core.ml.registry import compatibility_registry_snapshot
from core.data_definition.target_registry.runtime import (
    ModelRegistrySnapshot,
    apply_target_policy,
)
from core.ml.preprocessing import load_and_preprocess, prepare_pipeline
from core.utils import save_train_log_to_excel

def optimize_and_train(X, y, mandatory_features, use_rfe, log_callback=None):
    """RFE 피처 선택 및 Optuna 하이퍼파라미터 튜닝을 수행합니다."""
    def custom_log(msg):
        if log_callback: log_callback(msg)
        else: print(msg)

    selected_cols = list(X.columns)

    if use_rfe:
        custom_log("       🔍 [RFE] 최적의 피처 개수와 조합 탐색 중...")
        base_model = XGBRegressor(random_state=42, n_jobs=-1)
        rfecv = RFECV(estimator=base_model, step=1, cv=5, scoring='neg_root_mean_squared_error', n_jobs=-1)
        rfecv.fit(X, y)
        selected_cols = [col for col, sel in zip(X.columns, rfecv.support_) if sel]

        for mf in mandatory_features:
            if mf in X.columns and mf not in selected_cols:
                selected_cols.append(mf)
        custom_log(f"       ✅ [RFE 완료] 총 {X.shape[1]}개 중 {len(selected_cols)}개 피처 생존")
        X = X[selected_cols]

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "max_depth": trial.suggest_int("max_depth", 3, 7),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "random_state": 42, "n_jobs": -1
        }
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        rmses = []
        for train_idx, val_idx in kf.split(X):
            model = XGBRegressor(**params)
            model.fit(X.iloc[train_idx], y.iloc[train_idx])
            preds = model.predict(X.iloc[val_idx])
            rmses.append(np.sqrt(mean_squared_error(y.iloc[val_idx], preds)))
        return np.mean(rmses)

    def optuna_callback(study, trial):
        if trial.number % 5 == 0 or trial.number == 29:
            custom_log(f"       ⏳ [Optuna] Trial {trial.number+1}/30 완료 (Best RMSE: {study.best_value:.4f})")

    custom_log("       ⚙️ [Optuna] 하이퍼파라미터 튜닝 시작 (총 30 Trials)...")
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=30, callbacks=[optuna_callback])

    best_params = dict(study.best_params)
    best_params["random_state"] = 42
    best_params["n_jobs"] = -1

    custom_log("       📊 최종 모델 성능 검증 중 (5-Fold CV)...")
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    final_rmses, final_r2s = [], []
    for train_idx, val_idx in kf.split(X):
        eval_model = XGBRegressor(**best_params)
        eval_model.fit(X.iloc[train_idx], y.iloc[train_idx])
        preds = eval_model.predict(X.iloc[val_idx])
        final_rmses.append(np.sqrt(mean_squared_error(y.iloc[val_idx], preds)))
        final_r2s.append(r2_score(y.iloc[val_idx], preds))

    cv_rmse = np.mean(final_rmses)
    cv_r2 = np.mean(final_r2s)
    custom_log(f"       🏆 [성능 요약] R² Score: {cv_r2:.4f} | RMSE: {cv_rmse:.4f}")

    final_model = XGBRegressor(**best_params)
    final_model.fit(X, y)

    importances = final_model.feature_importances_
    feature_ranking = sorted(zip(selected_cols, importances), key=lambda x: x[1], reverse=True)
    top_n = min(5, len(feature_ranking))
    top_features_str = ", ".join([f"{f} ({imp*100:.1f}%)" for f, imp in feature_ranking[:top_n]])
    custom_log(f"       🌟 [Top 피처] {top_features_str}")

    return final_model, selected_cols, cv_r2, cv_rmse, feature_ranking

def train_all_models(
    data_path=None, log_callback=None, model_output_path=None,
    *, registry_snapshot: ModelRegistrySnapshot | None = None,
):
    if not model_output_path:
        raise ValueError("Training caller must provide a staging model_output_path.")

    def custom_log(msg):
        if log_callback: log_callback(msg)
        else: print(msg)

    file = data_path or TRAIN_DATA_FILE
    custom_log(f"📦 데이터 로드 및 전처리 시작... ({os.path.basename(file)})")
    df = load_and_preprocess(file)
    snapshot = registry_snapshot or compatibility_registry_snapshot()
    validate_training_input_headers(df.columns, registry_snapshot=snapshot)

    model_data = attach_catalog_fingerprint(
        {
            "models": {}, "features": {},
            "preprocess_version": snapshot.preprocessing_version,
            "training_contract": {
                "generation_id": snapshot.generation_id,
                "registry_fingerprint": snapshot.registry_fingerprint,
                "ordered_ml_fingerprint": snapshot.ordered_ml_fingerprint,
                "derived_semantics_fingerprint": snapshot.derived_semantics_fingerprint,
                "one_hot_fingerprint": snapshot.one_hot_fingerprint,
            },
        }
    )
    summary_report = "📊 [최종 학습 모델 성능 요약]\n\n"
    all_results_for_excel = []

    for group in snapshot.groups:
        config = {
            "name": group.name,
            "targets": [item.ml_name for item in group.targets],
            "use_rfe": group.use_rfe,
        }
        if not group.targets:
            continue
        custom_log(f"\n==============================================")
        custom_log(f"🚀 [{config['name']}] 학습 준비 중...")

        X_full, y_full = prepare_pipeline(df, config, registry_snapshot=snapshot)
        mandatory_features = config.get("mandatory_features", [])
        use_rfe = config.get("use_rfe", False)

        for target_definition in group.targets:
            target = target_definition.ml_name
            custom_log(f"\n🎯 Target: {target}")
            y_target = y_full[target]

            # --- [핵심 추가] 피처 격리 (Data Leakage 차단) 로직 ---
            selected_columns = apply_target_policy(X_full.columns, target_definition)
            X_target = X_full.loc[:, list(selected_columns)].copy()
            custom_log(
                f"       {'⚪ 화이트리스트 적용' if target_definition.policy_mode == 'allowed' else '🚫 제외 정책 적용'}: "
                f"{X_target.shape[1]}개 학습 피처"
            )
            # --------------------------------------------------

            final_model, final_features, r2, rmse, feature_ranking = optimize_and_train(
                X_target, y_target, mandatory_features, use_rfe, log_callback=log_callback
            )


            model_data["models"][target] = final_model
            model_data["features"][target] = final_features

            top_3 = ", ".join([f[0] for f in feature_ranking[:3]])
            summary_report += f"✅ {target}\n   - R²: {r2:.4f} | RMSE: {rmse:.4f}\n   - 주요 피처: {top_3}\n\n"

            all_results_for_excel.append({
                "Target": target, "R2_Score": round(r2, 4), "RMSE": round(rmse, 4),
                "Selected_Features_Count": len(final_features),
                "Top_1_Feature": feature_ranking[0][0] if len(feature_ranking) > 0 else "",
                "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    output_path = model_output_path
    output_dir = os.path.dirname(output_path) or "."
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    joblib.dump(model_data, output_path)
    saved_path = save_train_log_to_excel(all_results_for_excel)
    custom_log(f"💾 학습 로그 저장 완료: {saved_path}")
    custom_log(f"\n🎉 모든 모델 학습이 완료되었습니다!")

    return summary_report


def validate_training_input_headers(headers, *, registry_snapshot=None):
    """Fail fast when raw training columns do not match catalog ml_name values."""
    if registry_snapshot is not None:
        observed = {str(header).strip() for header in headers if str(header).strip()}
        required = set(registry_snapshot.training_headers)
        known = set(registry_snapshot.known_ml_names)
        errors = []
        unknown = sorted(observed - known)
        missing = sorted(required - observed)
        if unknown:
            errors.append(f"unknown training header(s): {', '.join(unknown)}")
        if missing:
            errors.append(f"missing required training header(s): {', '.join(missing)}")
        if errors:
            raise ValueError("Training data header contract violation: " + "; ".join(errors))
        return
    catalog = load_feature_catalog()
    catalog_errors = validate_feature_catalog(catalog)
    if catalog_errors:
        joined = "; ".join(catalog_errors)
        raise ValueError(f"invalid ML feature catalog for training: {joined}")
    header_errors = validate_training_headers(headers, catalog)
    if header_errors:
        joined = "; ".join(header_errors)
        raise ValueError(
            "Training data header contract violation: columns must match "
            "config/ml/features.csv ml_name values; "
            f"{joined}"
        )
