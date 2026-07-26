# core/ml/training.py — 학습 파이프라인 및 하이퍼파라미터/피처 최적화
import os
import joblib
import pandas as pd
import datetime
from datetime import timezone
from pathlib import Path
from time import monotonic

from core.ml.artifacts import TRAIN_DATA_FILE
from core.ml.catalog_fingerprint import attach_catalog_fingerprint
from core.ml.feature_catalog import load_feature_catalog, validate_feature_catalog
from core.ml.feature_catalog_projection import validate_training_headers
from core.ml.registry import compatibility_registry_snapshot
from core.data_definition.target_registry.runtime import (
    ModelRegistrySnapshot,
    apply_target_policy,
)
from core.ml.preprocessing import (
    calculate_derived_features,
    load_and_preprocess,
    prepare_pipeline,
)
from core.ml.training_results import (
    CoreTrainingEvidence,
    CoreTrainingOutput,
    TrainingOptimizationConfig,
    optimize_and_train,
)

def train_all_models(
    data_path=None, log_callback=None, model_output_path=None,
    *, registry_snapshot: ModelRegistrySnapshot | None = None,
):
    """Compatibility wrapper returning the established natural-language summary."""
    return train_all_models_with_analysis(
        data_path=data_path,
        log_callback=log_callback,
        model_output_path=model_output_path,
        registry_snapshot=registry_snapshot,
    ).summary


def train_all_models_with_analysis(
    data_path=None, log_callback=None, model_output_path=None,
    *, registry_snapshot: ModelRegistrySnapshot | None = None,
    optimization_config: TrainingOptimizationConfig | None = None,
    derived_evaluation_snapshot=None,  # noqa: ANN001
):
    if not model_output_path:
        raise ValueError("Training caller must provide a staging model_output_path.")

    def custom_log(msg):
        if log_callback: log_callback(msg)
        else: print(msg)

    started_clock = monotonic()
    started_at = datetime.datetime.now(timezone.utc).isoformat()
    file = data_path or TRAIN_DATA_FILE
    custom_log(f"📦 데이터 로드 및 전처리 시작... ({os.path.basename(file)})")
    raw_df = pd.read_csv(file)
    df = load_and_preprocess(file)
    quality_df = calculate_derived_features(
        df, definitions=derived_evaluation_snapshot
    )
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
    target_results = []
    failed_targets = []
    target_usage: dict[str, set[str]] = {}

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

        X_full, y_full = prepare_pipeline(
            df,
            config,
            registry_snapshot=snapshot,
            derived_evaluation_snapshot=derived_evaluation_snapshot,
        )
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

            for feature in X_target.columns:
                target_usage.setdefault(str(feature), set()).add(
                    target_definition.identity
                )
            try:
                final_model, final_features, feature_ranking, analysis = (
                    optimize_and_train(
                        X_target,
                        y_target,
                        mandatory_features,
                        use_rfe,
                        log_callback=log_callback,
                        optimization_config=optimization_config,
                    )
                )
            except Exception as exc:
                reason = str(exc).splitlines()[0]
                failed_targets.append({
                    "target_identity": target_definition.identity,
                    "target_ml_name": target,
                    "reason": reason,
                })
                target_results.append({
                    "target_identity": target_definition.identity,
                    "target_ml_name": target,
                    "status": "failed",
                    "blocking_reason": reason,
                })
                custom_log(f"       ❌ [{target}] 학습 실패: {reason}")
                continue

            model_data["models"][target] = final_model
            model_data["features"][target] = final_features
            top_3 = ", ".join([f[0] for f in feature_ranking[:3]])
            metrics = analysis["metrics"]
            summary_report += (
                f"✅ {target}\n   - R²: {metrics['r2']:.4f} | "
                f"MAE: {metrics['mae']:.4f} | RMSE: {metrics['rmse']:.4f}\n"
                f"   - 주요 피처: {top_3}\n\n"
            )
            target_results.append({
                "target_identity": target_definition.identity,
                "target_ml_name": target,
                "status": "complete",
                **analysis,
            })

    output_path = model_output_path
    output_dir = os.path.dirname(output_path) or "."
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    joblib.dump(model_data, output_path)
    custom_log(f"\n🎉 모든 모델 학습이 완료되었습니다!")

    finished_at = datetime.datetime.now(timezone.utc).isoformat()
    status = "complete" if not failed_targets else (
        "partial" if len(failed_targets) < len(target_results) else "failed"
    )
    resolved_optimization = optimization_config or TrainingOptimizationConfig()
    evidence = CoreTrainingEvidence(
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=monotonic() - started_clock,
        training_data_sha256=_sha256_file(Path(file)),
        training_data_rows=len(df),
        evaluation_context={
            "scope": (
                f"shuffled_{resolved_optimization.cv_folds}_fold_cross_validation"
            ),
            "fold_count": resolved_optimization.cv_folds,
            "seed": 42,
            "splitter": "KFold",
        },
        targets=tuple(target_results),
        preprocessing={
            "status": "applied",
            "steps": [{
                "name": "drop_missing_base_features",
                "rows_before": len(raw_df),
                "rows_after": len(df),
                "rows_removed": len(raw_df) - len(df),
            }, {
                "name": "canonical_derived_feature_evaluation",
                "version": snapshot.preprocessing_version,
            }],
            "feature_data_quality": tuple(
                _feature_quality(
                    raw_df if feature in raw_df.columns else quality_df,
                    feature,
                    target_usage.get(feature, set()),
                    quality_collection_stage=(
                        "raw_training_input"
                        if feature in raw_df.columns
                        else "post_preprocessing_derived_features"
                    ),
                )
                for feature in snapshot.input_ml_names
                if feature in raw_df.columns or feature in quality_df.columns
            ),
        },
        status=status,
        blocking_reasons=tuple(
            f"{item['target_identity']}: {item['reason']}"
            for item in failed_targets
        ),
    )
    return CoreTrainingOutput(
        summary=summary_report,
        evidence=evidence,
        failed_targets=tuple(failed_targets),
    )


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _feature_quality(
    frame: pd.DataFrame,
    feature: str,
    target_usage: set[str],
    *,
    quality_collection_stage: str,
) -> dict:
    series = frame[feature]
    missing_count = int(series.isna().sum())
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    outlier_count = 0
    if len(numeric):
        q1, q3 = numeric.quantile(0.25), numeric.quantile(0.75)
        iqr = q3 - q1
        if iqr > 0:
            outlier_count = int(
                ((numeric < q1 - 1.5 * iqr) | (numeric > q3 + 1.5 * iqr)).sum()
            )
    unique_count = int(series.nunique(dropna=True))
    return {
        "feature": feature,
        "missing_count": missing_count,
        "missing_rate": missing_count / len(series) if len(series) else 0.0,
        "unique_count": unique_count,
        "low_variance": unique_count <= 1,
        "outlier_method": "iqr_1.5",
        "outlier_count": outlier_count,
        "target_usage": tuple(sorted(target_usage)),
        "quality_collection_stage": quality_collection_stage,
        "target_usage_stage": "post_target_policy_pre_rfecv",
    }


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
