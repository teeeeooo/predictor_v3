"""Predict app mapping repository boundary."""

from core.mapping.paths import MAPPING_JSON_FILE
from core.mapping.repository import load_mapping_data


class PredictMappingRepository:
    """Load mapping data for Predict UI controllers."""

    def __init__(self, mapping_file: str = MAPPING_JSON_FILE) -> None:
        self._mapping_file = mapping_file
        self._mapping_data: dict | None = None

    @property
    def mapping_file(self) -> str:
        """Return the configured mapping JSON path."""
        return self._mapping_file

    def load(self) -> dict:
        """Return cached mapping data, loading it on first use."""
        if self._mapping_data is None:
            self._mapping_data = load_mapping_data(self._mapping_file)
        return self._mapping_data

    def reload(self) -> dict:
        """Reload mapping data from disk."""
        self._mapping_data = load_mapping_data(self._mapping_file)
        return self._mapping_data
