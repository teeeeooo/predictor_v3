"""Structured runtime-generation participant failures."""


class ParticipantPrepareError(RuntimeError):
    def __init__(
        self,
        code: str,
        message: str,
        recommended_action: str = "Retry Apply",
        details: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)
        self.code = code
        self.recommended_action = recommended_action
        self.details = details
