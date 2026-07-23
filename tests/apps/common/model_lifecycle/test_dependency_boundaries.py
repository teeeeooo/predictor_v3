"""Lifecycle dependency-direction and Predict runtime import guards."""

import subprocess
import sys
from pathlib import Path


def test_core_ml_does_not_import_lifecycle_infrastructure():
    sources = tuple(Path("core/ml").glob("*.py"))
    assert sources
    assert all("model_lifecycle" not in path.read_text(encoding="utf-8") for path in sources)


def test_predict_startup_does_not_import_train_only_dependencies():
    script = """
import sys
import apps.predict.app
for forbidden in ('optuna', 'shap', 'matplotlib'):
    assert forbidden not in sys.modules, forbidden
"""
    subprocess.run(
        [sys.executable, "-B", "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )
