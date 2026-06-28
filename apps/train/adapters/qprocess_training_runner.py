"""PySide QProcess adapter for killable production training execution."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, QTimer, Signal

from apps.train.adapters.training_process_events import parse_training_event
from apps.train.state.training_run_state import (
    TrainingLogEvent,
    TrainingProgress,
    TrainingRequest,
    TrainingResult,
)


class QProcessTrainingRunner(QObject):
    """Run training in a child process and emit Qt-friendly payloads."""

    log_event = Signal(object)
    progress = Signal(object)
    finished = Signal(object)
    failed = Signal(object)
    cancelled = Signal(object)

    def __init__(
        self,
        *,
        parent: QObject | None = None,
        python_executable: str | None = None,
        job_module: str = "apps.train.jobs.train_job",
        extra_args: tuple[str, ...] = (),
        terminate_timeout_ms: int = 1500,
    ) -> None:
        super().__init__(parent)
        self._python_executable = python_executable or sys.executable
        self._job_module = job_module
        self._extra_args = tuple(extra_args)
        self._terminate_timeout_ms = terminate_timeout_ms
        self._process: QProcess | None = None
        self._request: TrainingRequest | None = None
        self._stdout_buffer = ""
        self._stderr_buffer = ""
        self._cancel_requested = False
        self._terminal_emitted = False
        self._pending_result: TrainingResult | None = None
        self._kill_timer: QTimer | None = None
        self._temp_artifact_path: Path | None = None

    @property
    def is_running(self) -> bool:
        """Return whether the child process is active."""
        return self._process is not None and self._process.state() != QProcess.NotRunning

    def start(self, request: TrainingRequest) -> None:
        """Start the child training job."""
        if self.is_running:
            raise RuntimeError("Training process already in progress.")
        self._request = request
        self._cancel_requested = False
        self._terminal_emitted = False
        self._pending_result = None
        self._stdout_buffer = ""
        self._stderr_buffer = ""
        self._temp_artifact_path = self._default_temp_artifact_path(request)

        process = QProcess(self)
        process.setProgram(self._python_executable)
        process.setArguments(self._arguments_for(request))
        process.readyReadStandardOutput.connect(self._read_stdout)
        process.readyReadStandardError.connect(self._read_stderr)
        process.finished.connect(self._handle_finished)
        process.errorOccurred.connect(self._handle_error)
        self._process = process
        process.start()

    def cancel(self) -> bool:
        """Terminate and then kill the child process if needed."""
        if not self.is_running or self._process is None:
            return False
        self._cancel_requested = True
        self._process.terminate()
        self._kill_timer = QTimer(self)
        self._kill_timer.setSingleShot(True)
        self._kill_timer.timeout.connect(self._kill_if_running)
        self._kill_timer.start(self._terminate_timeout_ms)
        return True

    def _arguments_for(self, request: TrainingRequest) -> list[str]:
        return [
            "-B",
            "-m",
            self._job_module,
            "--run-id",
            request.run_id,
            "--data-path",
            request.data_path,
            "--model-output-path",
            request.model_output_path,
            "--temp-model-output-path",
            str(self._temp_artifact_path),
            *self._extra_args,
        ]

    def _read_stdout(self) -> None:
        if self._process is None:
            return
        self._stdout_buffer += bytes(self._process.readAllStandardOutput()).decode(
            "utf-8", errors="replace"
        )
        self._drain_stdout_lines()

    def _read_stderr(self) -> None:
        if self._process is None:
            return
        self._stderr_buffer += bytes(self._process.readAllStandardError()).decode(
            "utf-8", errors="replace"
        )
        while "\n" in self._stderr_buffer:
            line, self._stderr_buffer = self._stderr_buffer.split("\n", 1)
            if line.strip() and self._request is not None:
                self.log_event.emit(
                    TrainingLogEvent(
                        run_id=self._request.run_id,
                        message=line.strip(),
                        level="error",
                    )
                )

    def _drain_stdout_lines(self) -> None:
        while "\n" in self._stdout_buffer:
            line, self._stdout_buffer = self._stdout_buffer.split("\n", 1)
            if line.strip():
                self._handle_event_line(line.strip())

    def _handle_event_line(self, line: str) -> None:
        if self._request is None:
            return
        event_type, payload = parse_training_event(line, self._request)
        if event_type == "progress":
            self.progress.emit(payload)
        elif event_type == "result":
            self._pending_result = payload
        else:
            self.log_event.emit(payload)

    def _handle_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        self._stop_kill_timer()
        self._read_stdout()
        self._read_stderr()
        self._drain_stdout_lines()
        if self._stderr_buffer.strip() and self._request is not None:
            self.log_event.emit(
                TrainingLogEvent(self._request.run_id, self._stderr_buffer.strip(), "error")
            )
        if self._pending_result is not None:
            self._emit_terminal(self._pending_result)
        elif not self._terminal_emitted and self._request is not None:
            if self._cancel_requested:
                self._cleanup_temp_artifact()
                self.cancelled.emit(
                    TrainingResult(
                        run_id=self._request.run_id,
                        status="cancelled",
                        model_path=self._request.model_output_path,
                        message="Training process cancelled.",
                    )
                )
            elif exit_code == 0:
                self.finished.emit(
                    TrainingResult(
                        run_id=self._request.run_id,
                        status="complete",
                        model_path=self._request.model_output_path,
                        message="Training process completed.",
                    )
                )
            else:
                self._cleanup_temp_artifact()
                self.failed.emit(
                    TrainingResult(
                        run_id=self._request.run_id,
                        status="error",
                        model_path=self._request.model_output_path,
                        message=f"Training process exited with code {exit_code}.",
                    )
                )
        self._process = None

    def _handle_error(self, _error: QProcess.ProcessError) -> None:
        if self._terminal_emitted or self._request is None:
            return
        if self._process is not None and self._process.state() != QProcess.NotRunning:
            return
        self._cleanup_temp_artifact()
        self._terminal_emitted = True
        self.failed.emit(
            TrainingResult(
                run_id=self._request.run_id,
                status="error",
                model_path=self._request.model_output_path,
                message="Training process failed to start.",
            )
        )

    def _emit_terminal(self, result: TrainingResult) -> None:
        if self._terminal_emitted:
            return
        self._terminal_emitted = True
        if result.status == "complete":
            self.finished.emit(result)
        elif result.status == "cancelled":
            self._cleanup_temp_artifact()
            self.cancelled.emit(result)
        else:
            self._cleanup_temp_artifact()
            self.failed.emit(result)

    def _kill_if_running(self) -> None:
        if self._process is not None and self._process.state() != QProcess.NotRunning:
            self._process.kill()

    def _stop_kill_timer(self) -> None:
        if self._kill_timer is not None:
            self._kill_timer.stop()
            self._kill_timer.deleteLater()
            self._kill_timer = None

    def _cleanup_temp_artifact(self) -> None:
        if self._temp_artifact_path is not None:
            self._temp_artifact_path.unlink(missing_ok=True)

    def _default_temp_artifact_path(self, request: TrainingRequest) -> Path:
        model_path = Path(request.model_output_path)
        return model_path.with_name(f".{model_path.name}.{request.run_id}.tmp")
