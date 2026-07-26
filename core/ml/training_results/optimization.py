"""Core ML RFECV, Optuna, evaluation, and feature-importance semantics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import optuna
from sklearn.feature_selection import RFECV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from xgboost import XGBRegressor


@dataclass(frozen=True)
class TrainingOptimizationConfig:
    """Bounded production configuration with established defaults."""

    cv_folds: int = 5
    optuna_trials: int = 30
    n_estimators_min: int = 100
    n_estimators_max: int = 500
    n_jobs: int = -1
    optuna_sampler_seed: int | None = None

    def validate(self) -> None:
        if self.cv_folds < 2:
            raise ValueError("training cv_folds must be at least 2")
        if self.optuna_trials < 1:
            raise ValueError("training optuna_trials must be positive")
        if (
            self.n_estimators_min < 1
            or self.n_estimators_max < self.n_estimators_min
        ):
            raise ValueError("training estimator range is invalid")


def optimize_and_train(
    X,
    y,
    mandatory_features,
    use_rfe,
    log_callback=None,
    *,
    optimization_config: TrainingOptimizationConfig | None = None,
    training_started_callback: Callable[[], None] | None = None,
):
    """Run target-local selection, tuning, evaluation, and final training."""
    config = optimization_config or TrainingOptimizationConfig()
    config.validate()

    def custom_log(message):
        if log_callback:
            log_callback(message)
        else:
            print(message)

    original_cols = list(X.columns)
    selected_cols = list(original_cols)
    rfecv_result = _not_used_rfecv(original_cols, config.cv_folds)
    if training_started_callback is not None:
        training_started_callback()
    if use_rfe:
        custom_log("       🔍 [RFE] 최적의 피처 개수와 조합 탐색 중...")
        rfecv = RFECV(
            estimator=XGBRegressor(
                random_state=42,
                n_jobs=config.n_jobs,
                n_estimators=config.n_estimators_min,
            ),
            step=1,
            cv=config.cv_folds,
            scoring="neg_root_mean_squared_error",
            n_jobs=config.n_jobs,
        )
        rfecv.fit(X, y)
        selected_cols = [
            column
            for column, selected in zip(X.columns, rfecv.support_)
            if selected
        ]
        for feature in mandatory_features:
            if feature in X.columns and feature not in selected_cols:
                selected_cols.append(feature)
        rfecv_result = _used_rfecv(
            original_cols, selected_cols, rfecv.ranking_, config.cv_folds
        )
        custom_log(
            f"       ✅ [RFE 완료] 총 {X.shape[1]}개 중 "
            f"{len(selected_cols)}개 피처 생존"
        )
        X = X[selected_cols]

    study = _optimize(X, y, custom_log, config)
    best_params = {
        **study.best_params,
        "random_state": 42,
        "n_jobs": config.n_jobs,
    }
    folds = _evaluate_folds(X, y, best_params, config.cv_folds)
    metrics = summarize_fold_metrics(
        folds, sample_count=len(y), cv_folds=config.cv_folds
    )
    custom_log(
        f"       🏆 [성능 요약] R² Score: {metrics['r2']:.4f} | "
        f"MAE: {metrics['mae']:.4f} | RMSE: {metrics['rmse']:.4f}"
    )
    final_model = XGBRegressor(**best_params)
    final_model.fit(X, y)
    ranking, importance = _feature_importance(final_model, selected_cols)
    top_features = ", ".join(
        f"{feature} ({value * 100:.1f}%)"
        for feature, value in ranking[: min(5, len(ranking))]
    )
    custom_log(f"       🌟 [Top 피처] {top_features}")
    return final_model, selected_cols, ranking, {
        "metrics": metrics,
        "rfecv": rfecv_result,
        "feature_importance": importance,
        "optuna": _optuna_result(study, best_params, config.cv_folds),
    }


def summarize_fold_metrics(folds, *, sample_count, cv_folds: int = 5):
    """Preserve the established mean-of-fold ML evaluation semantics."""
    values = {
        name: [float(item[name]) for item in folds]
        for name in ("r2", "mae", "rmse")
    }
    return {
        "evaluation_scope": f"shuffled_{cv_folds}_fold_cross_validation",
        "sample_count": int(sample_count),
        "fold_count": len(folds),
        "seed": 42,
        **{name: float(np.mean(items)) for name, items in values.items()},
        **{
            f"{name}_std": float(np.std(items))
            for name, items in values.items()
        },
        "folds": [
            {
                "fold": index,
                **{
                    name: float(item[name])
                    for name in ("r2", "mae", "rmse")
                },
            }
            for index, item in enumerate(folds, start=1)
        ],
    }


def _optimize(X, y, custom_log, config):  # noqa: ANN001
    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int(
                "n_estimators",
                config.n_estimators_min,
                config.n_estimators_max,
            ),
            "max_depth": trial.suggest_int("max_depth", 3, 7),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float(
                "colsample_bytree", 0.6, 1.0
            ),
            "random_state": 42,
            "n_jobs": config.n_jobs,
        }
        rmses = []
        splitter = KFold(
            n_splits=config.cv_folds, shuffle=True, random_state=42
        )
        for train_index, validation_index in splitter.split(X):
            model = XGBRegressor(**params)
            model.fit(X.iloc[train_index], y.iloc[train_index])
            prediction = model.predict(X.iloc[validation_index])
            rmses.append(
                np.sqrt(mean_squared_error(y.iloc[validation_index], prediction))
            )
        return np.mean(rmses)

    def callback(study, trial):
        if trial.number % 5 == 0 or trial.number == config.optuna_trials - 1:
            custom_log(
                f"       ⏳ [Optuna] Trial {trial.number + 1}/"
                f"{config.optuna_trials} 완료 "
                f"(Best RMSE: {study.best_value:.4f})"
            )

    custom_log(
        "       ⚙️ [Optuna] 하이퍼파라미터 튜닝 시작 "
        f"(총 {config.optuna_trials} Trials)..."
    )
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(
        direction="minimize",
        sampler=(
            optuna.samplers.TPESampler(seed=config.optuna_sampler_seed)
            if config.optuna_sampler_seed is not None
            else None
        ),
    )
    study.optimize(objective, n_trials=config.optuna_trials, callbacks=[callback])
    return study


def _evaluate_folds(X, y, parameters, cv_folds):  # noqa: ANN001
    folds = []
    splitter = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
    for train_index, validation_index in splitter.split(X):
        model = XGBRegressor(**parameters)
        model.fit(X.iloc[train_index], y.iloc[train_index])
        truth = y.iloc[validation_index]
        prediction = model.predict(X.iloc[validation_index])
        folds.append({
            "r2": r2_score(truth, prediction),
            "mae": mean_absolute_error(truth, prediction),
            "rmse": np.sqrt(mean_squared_error(truth, prediction)),
        })
    return folds


def _feature_importance(model, selected_cols):  # noqa: ANN001
    importances = model.feature_importances_
    ranking = sorted(
        zip(selected_cols, importances), key=lambda item: item[1], reverse=True
    )
    total = float(sum(float(value) for value in importances))
    rows = [
        {
            "feature": feature,
            "method": "xgboost_gain",
            "raw_value": float(value),
            "normalized_value": float(value) / total if total else 0.0,
            "rank": rank,
        }
        for rank, (feature, value) in enumerate(ranking, start=1)
    ]
    return ranking, rows


def _optuna_result(study, best_params, cv_folds):  # noqa: ANN001
    best_number = study.best_trial.number
    return {
        "status": "used",
        "direction": "minimize",
        "score_context": f"mean {cv_folds}-fold CV RMSE",
        "selected_parameters": dict(best_params),
        "trials": [
            {
                "trial_number": trial.number,
                "parameters": dict(trial.params),
                "score": float(trial.value) if trial.value is not None else None,
                "state": trial.state.name,
                "duration_seconds": (
                    trial.duration.total_seconds() if trial.duration else None
                ),
                "best_trial": trial.number == best_number,
            }
            for trial in study.trials
        ],
    }


def _not_used_rfecv(features, cv_folds):
    return {
        "status": "not_used",
        "score_context": (
            f"neg_root_mean_squared_error; {cv_folds}-fold CV"
        ),
        "feature_count_before": len(features),
        "feature_count_after": len(features),
        "features": [
            {
                "feature": feature,
                "selected": True,
                "rank": 1,
                "selection_order": None,
            }
            for feature in features
        ],
    }


def _used_rfecv(original, selected, ranking, cv_folds):
    return {
        "status": "used",
        "score_context": (
            f"neg_root_mean_squared_error; {cv_folds}-fold CV"
        ),
        "feature_count_before": len(original),
        "feature_count_after": len(selected),
        "features": [
            {
                "feature": feature,
                "selected": feature in selected,
                "rank": int(rank),
                "selection_order": None,
            }
            for feature, rank in zip(original, ranking)
        ],
    }
