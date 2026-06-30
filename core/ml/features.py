"""ML feature and target constants projected from the feature catalog."""

from core.ml.feature_catalog import load_feature_catalog, validate_feature_catalog


def _load_validated_catalog():
    catalog = load_feature_catalog()
    errors = validate_feature_catalog(catalog)
    if errors:
        joined = "; ".join(errors)
        raise RuntimeError(f"invalid ML feature catalog: {joined}")
    return catalog


_CATALOG = _load_validated_catalog()

BASE_FEATURES = _CATALOG.base_features()
DERIVED_FEATURES = _CATALOG.derived_features()
TARGETS = _CATALOG.targets()
