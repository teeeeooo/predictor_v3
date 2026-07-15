"""Qt-free Data Mapping handoff and coverage application contracts."""

from apps.train.application.data_mapping.contracts import (
    DataMappingCellTarget,
    DataMappingCoverageItem,
    DataMappingIssueTarget,
    DataMappingNavigationRequest,
    DataMappingNavigationResult,
)
from apps.train.application.data_mapping.targeting import (
    row_identity_at_index,
    row_index_for_identity,
    unique_row_identity,
)

__all__ = (
    "DataMappingCellTarget",
    "DataMappingCoverageItem",
    "DataMappingIssueTarget",
    "DataMappingNavigationRequest",
    "DataMappingNavigationResult",
    "row_identity_at_index",
    "row_index_for_identity",
    "unique_row_identity",
)
