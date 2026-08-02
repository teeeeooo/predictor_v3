"""Case-scoped Target selection over the full runtime Target contract."""

from __future__ import annotations

from apps.predict.application.target_outcome import PredictionTargetDescriptor


COOLING_POWER_TARGET_ID = "ufm_target_df11df5180785a149e85f5f228aaa7e1"
HEATING_POWER_TARGET_ID = "ufm_target_78b4bbb97725586a97e41ae0ad04c561"
REFRIGERANT_QUANTITY_TARGET_ID = "ufm_target_330e4539dc7e5bb583132943914a5df5"
COOLING_FREQUENCY_TARGET_ID = "ufm_target_4e8d07df9558577a94701a10cdeabf71"
HEATING_FREQUENCY_TARGET_ID = "ufm_target_e73ce9f258985ccf8ce1d3774cc108ce"

_ALL_TARGET_IDS = frozenset({
    COOLING_POWER_TARGET_ID,
    HEATING_POWER_TARGET_ID,
    REFRIGERANT_QUANTITY_TARGET_ID,
    COOLING_FREQUENCY_TARGET_ID,
    HEATING_FREQUENCY_TARGET_ID,
})
_REQUESTED_IDS = {
    (True, True): _ALL_TARGET_IDS,
    (True, False): frozenset({
        COOLING_POWER_TARGET_ID,
        REFRIGERANT_QUANTITY_TARGET_ID,
        COOLING_FREQUENCY_TARGET_ID,
    }),
    (False, True): frozenset({
        HEATING_POWER_TARGET_ID,
        REFRIGERANT_QUANTITY_TARGET_ID,
        HEATING_FREQUENCY_TARGET_ID,
    }),
    (False, False): frozenset({REFRIGERANT_QUANTITY_TARGET_ID}),
}


def requested_target_descriptors(
    full_runtime_targets: tuple[PredictionTargetDescriptor, ...],
    *,
    cooling_present: bool,
    heating_present: bool,
) -> tuple[PredictionTargetDescriptor, ...]:
    """Select one Case subset while preserving runtime identity and order."""
    identities = tuple(item.target_identity for item in full_runtime_targets)
    if len(identities) != len(set(identities)) or set(identities) != _ALL_TARGET_IDS:
        raise ValueError("Predict full runtime Target contract is not applicable")
    requested = _REQUESTED_IDS[(cooling_present, heating_present)]
    return tuple(
        descriptor
        for descriptor in full_runtime_targets
        if descriptor.target_identity in requested
    )


def requested_target_contract_reason(
    requested: tuple[PredictionTargetDescriptor, ...],
    full_runtime_targets: tuple[PredictionTargetDescriptor, ...],
) -> str:
    """Reject forged, reordered, empty, or non-runtime requested contracts."""
    if not requested:
        return "missing_requested_target_contract"
    requested_ids = tuple(item.target_identity for item in requested)
    if len(requested_ids) != len(set(requested_ids)):
        return "duplicate_requested_target_identity"
    full_by_id = {
        item.target_identity: (index, item)
        for index, item in enumerate(full_runtime_targets)
    }
    try:
        positions = tuple(full_by_id[identity][0] for identity in requested_ids)
    except KeyError:
        return "unknown_requested_target_identity"
    if positions != tuple(sorted(positions)):
        return "requested_target_order_mismatch"
    if any(
        descriptor != full_by_id[descriptor.target_identity][1]
        for descriptor in requested
    ):
        return "requested_target_descriptor_mismatch"
    return ""


def requested_target_identity_contract_reason(
    requested_identities: tuple[str, ...],
    full_runtime_targets: tuple[PredictionTargetDescriptor, ...],
) -> str:
    """Validate ordered stable-identity evidence against one full runtime."""
    full_by_id = {
        item.target_identity: index
        for index, item in enumerate(full_runtime_targets)
    }
    if not requested_identities:
        return "missing_requested_target_contract"
    if len(requested_identities) != len(set(requested_identities)):
        return "duplicate_requested_target_identity"
    try:
        positions = tuple(full_by_id[item] for item in requested_identities)
    except KeyError:
        return "unknown_requested_target_identity"
    return (
        "requested_target_order_mismatch"
        if positions != tuple(sorted(positions))
        else ""
    )


def descriptors_for_requested_identities(
    requested_identities: tuple[str, ...],
    full_runtime_targets: tuple[PredictionTargetDescriptor, ...],
) -> tuple[PredictionTargetDescriptor, ...]:
    """Resolve validated stable identities to current runtime descriptors."""
    reason = requested_target_identity_contract_reason(
        requested_identities, full_runtime_targets
    )
    if reason:
        raise ValueError(f"Predict requested Target contract is invalid: {reason}")
    requested = set(requested_identities)
    return tuple(
        item for item in full_runtime_targets if item.target_identity in requested
    )
