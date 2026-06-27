import ast
import json
from pathlib import Path


CALCULATOR_FILES = sorted(Path("core").glob("calculator_*.py"))
REGION_CONFIG_FILES = sorted(Path("data/region_configs").glob("*.json"))

BANNED_IMPORT_ROOTS = {
    "numpy",
    "pandas",
    "sklearn",
    "ui",
}
BANNED_IMPORT_MODULES = {
    "core.models",
}
BANNED_IMPORT_NAMES = {
    "COLUMNS",
    "MODEL_REGISTRY",
}
BANNED_REGION_RUNTIME_KEYS = {
    "candidate",
    "candidate_id",
    "prediction",
    "predicted_points",
    "model_version",
    "raw_result",
    "calculator_input",
    "calculator_result",
    "ranking",
    "ranking_features",
}
ADAPTER_ONLY_TERMS = {
    "PredictedPointsEnvelope",
    "CalculatorInputEnvelope",
    "CalculatorResultEnvelope",
    "RankingCandidateEnvelope",
    "raw_result",
    "model_version",
    "prediction",
    "predicted_points",
    "calculator_input",
    "calculator_result",
    "ranking_features",
}
ADAPTER_MODULES = {
    Path("core/calculators/adapters/result_adapter.py"),
    Path("core/calculators/adapters/input_adapter.py"),
    Path("core/calculators/adapters/prediction_adapter.py"),
    Path("core/calculators/adapters/ranking_adapter.py"),
    Path("core/calculators/adapters/unit_adapter.py"),
}


def _iter_import_violations(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in BANNED_IMPORT_ROOTS or alias.name in BANNED_IMPORT_MODULES:
                    yield f"{path}: banned import {alias.name!r}"
                if alias.name in BANNED_IMPORT_NAMES:
                    yield f"{path}: banned import name {alias.name!r}"
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = module.split(".", 1)[0]
            if root in BANNED_IMPORT_ROOTS or module in BANNED_IMPORT_MODULES:
                yield f"{path}: banned import from {module!r}"
            for alias in node.names:
                if alias.name in BANNED_IMPORT_NAMES:
                    yield f"{path}: banned import name {alias.name!r} from {module!r}"


def _iter_json_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _iter_json_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_json_keys(child)


def test_calculator_modules_do_not_import_ui_ml_or_numeric_stack_schema():
    violations = []
    for path in CALCULATOR_FILES:
        violations.extend(_iter_import_violations(path))

    assert violations == []


def test_region_configs_do_not_contain_runtime_or_ml_result_keys():
    violations = []
    for path in REGION_CONFIG_FILES:
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in _iter_json_keys(data):
            if key.casefold() in BANNED_REGION_RUNTIME_KEYS:
                violations.append(f"{path}: banned runtime key {key!r}")

    assert violations == []


def test_envelope_runtime_terms_stay_outside_core_calculators_except_adapter():
    violations = []
    for path in CALCULATOR_FILES:
        if path in ADAPTER_MODULES:
            continue
        source = path.read_text(encoding="utf-8")
        for term in ADAPTER_ONLY_TERMS:
            if term in source:
                violations.append(f"{path}: adapter-owned term {term!r}")

    assert violations == []
