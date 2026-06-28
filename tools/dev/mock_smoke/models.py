"""Importable DEV-only mock estimators for joblib artifacts."""

from __future__ import annotations

import time

from sklearn.dummy import DummyRegressor


class SlowDummyRegressor(DummyRegressor):
    """DummyRegressor variant that sleeps during predict for cancel smoke."""

    def __init__(self, *, delay_ms: int = 0, strategy: str = "mean") -> None:
        super().__init__(strategy=strategy)
        self.delay_ms = delay_ms

    def predict(self, X, return_std: bool = False):  # noqa: ANN001, N803
        if self.delay_ms > 0:
            time.sleep(self.delay_ms / 1000.0)
        return super().predict(X, return_std=return_std)
