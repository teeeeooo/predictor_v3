"""Feature Catalog fingerprint helpers for ML model compatibility."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from core.ml.feature_catalog import FeatureCatalog, load_feature_catalog

CATALOG_FINGERPRINT_KEY = "feature_catalog_fingerprint"
CATALOG_FINGERPRINT_VERSION_KEY = "feature_catalog_fingerprint_version"
CATALOG_FINGERPRINT_VERSION = "feature_catalog.ml_contract.v2"
ML_CONTRACT_FINGERPRINT_FIELDS = (
    "ml_name",
    "role",
    "one_hot_group",
    "zero_fill_policy",
)


def current_catalog_fingerprint(catalog: FeatureCatalog | None = None) -> str:
    """Return the current Feature Catalog compatibility fingerprint."""
    resolved = catalog or load_feature_catalog()
    payload = {
        "version": CATALOG_FINGERPRINT_VERSION,
        "fields": list(ML_CONTRACT_FINGERPRINT_FIELDS),
        "rows": [_payload_row(row) for row in _sorted_active_rows(resolved)],
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def attach_catalog_fingerprint(
    model_data: dict[str, Any],
    catalog: FeatureCatalog | None = None,
) -> dict[str, Any]:
    """Attach current Feature Catalog fingerprint metadata to model data."""
    model_data[CATALOG_FINGERPRINT_KEY] = current_catalog_fingerprint(catalog)
    model_data[CATALOG_FINGERPRINT_VERSION_KEY] = CATALOG_FINGERPRINT_VERSION
    return model_data


def validate_model_catalog_fingerprint(
    model_data: dict[str, Any],
    catalog: FeatureCatalog | None = None,
) -> None:
    """Raise when a model artifact was trained with a different catalog."""
    actual = model_data.get(CATALOG_FINGERPRINT_KEY)
    if not actual:
        raise ValueError(
            "Model artifact is missing Feature Catalog fingerprint; retraining is required."
        )
    expected = current_catalog_fingerprint(catalog)
    if actual != expected:
        raise ValueError(
            "Model artifact Feature Catalog fingerprint mismatch; retraining is required."
        )


def _value_for(row, header: str) -> str:  # noqa: ANN001
    value = getattr(row, header)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _payload_row(row) -> dict[str, str]:  # noqa: ANN001
    return {field: _value_for(row, field) for field in ML_CONTRACT_FINGERPRINT_FIELDS}


def _sorted_active_rows(catalog: FeatureCatalog):  # noqa: ANN001
    return sorted(
        (row for row in catalog.rows if row.active),
        key=lambda row: (
            row.role,
            row.ml_name,
            row.one_hot_group,
            row.zero_fill_policy,
        ),
    )
