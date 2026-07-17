"""Validation result DTOs for the canonical Unified Feature contract."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ContractValidationIssue:
    code: str
    message: str
