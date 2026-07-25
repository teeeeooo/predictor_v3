"""Qt-free Train GUI adapter over the shared training lifecycle boundary."""

from __future__ import annotations

from apps.train.application.training_lifecycle import TrainingLifecycleService
from apps.train.application.model_management import ModelManagementService
from apps.common.model_lifecycle.promotion import ModelPromotionService
from apps.train.services.training_service import TrainingService


class TrainController:
    """Preserve the UI-facing API while delegating workflow ownership."""

    def __init__(
        self,
        service: TrainingService | None = None,
        execution=None,  # noqa: ANN001
        execution_factory=None,  # noqa: ANN001
        registry_provider=None,  # noqa: ANN001
        lifecycle_repository=None,  # noqa: ANN001
        candidate_publisher=None,  # noqa: ANN001
        lifecycle_service: TrainingLifecycleService | None = None,
        model_management_service: ModelManagementService | None = None,
    ) -> None:
        self._lifecycle = lifecycle_service or TrainingLifecycleService(
            validation=service,
            execution=execution,
            execution_factory=execution_factory,
            registry_provider=registry_provider,
            repository=lifecycle_repository,
            publisher=candidate_publisher,
        )
        self._validation = service or TrainingService()
        self._model_management = model_management_service
        if (
            self._model_management is None
            and lifecycle_repository is not None
            and registry_provider is not None
        ):
            self._model_management = ModelManagementService(
                lifecycle_repository,
                ModelPromotionService(lifecycle_repository, registry_provider),
                training_running=lambda: self._lifecycle.is_running,
            )

    @property
    def _execution(self):  # noqa: ANN202
        return self._lifecycle._execution

    @_execution.setter
    def _execution(self, value) -> None:  # noqa: ANN001
        self._lifecycle._execution = value

    @property
    def is_running(self) -> bool:
        return self._lifecycle.is_running

    @property
    def last_result(self):  # noqa: ANN201
        return self._lifecycle.last_result

    @property
    def active_request(self):  # noqa: ANN201
        return self._lifecycle.active_request

    def resource_status(self, data_path=None, model_output_path=None):  # noqa: ANN001, ANN201
        return self._lifecycle.resource_status(data_path, model_output_path)

    def registry_snapshot(self):  # noqa: ANN201
        return self._lifecycle.registry_snapshot()

    def start(self, request=None, **kwargs):  # noqa: ANN001, ANN201
        return self._lifecycle.start(request, **kwargs)

    def cancel(self) -> bool:
        return self._lifecycle.cancel()

    def inspect_models(self):  # noqa: ANN201
        if self._model_management is None:
            return None
        return self._model_management.inspect()

    def promote_candidate(
        self,
        candidate_id: str,
        *,
        expected_revision: int,
    ):  # noqa: ANN201
        if self._model_management is None:
            raise RuntimeError("Model lifecycle management is unavailable.")
        return self._model_management.promote(
            candidate_id,
            expected_revision=expected_revision,
        )

    def export_active_model(
        self,
        destination_parent: str,
        *,
        expected_revision: int,
    ):  # noqa: ANN201
        if self._model_management is None:
            raise RuntimeError("Model lifecycle management is unavailable.")
        return self._model_management.export_active(
            destination_parent,
            expected_revision=expected_revision,
        )
