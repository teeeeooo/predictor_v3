"""PySide QProcess adapter for killable production training execution."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, QTimer, Signal

from apps.train.adapters.qprocess_command import (
    default_temporary_artifact,
    training_process_arguments,
)
from apps.train.adapters.qprocess_terminal import process_result
from apps.train.adapters.training_process_events import parse_training_event
from apps.train.ports.training_execution_port import TrainingExecutionCallbacks
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
        self._callbacks: TrainingExecutionCallbacks | None = None

    @property
    def is_running(self) -> bool:
        """Return whether the child process is active."""
        return self._process is not None and self._process.state() != QProcess.NotRunning

    def start(
        self,
        request: TrainingRequest,
        callbacks: TrainingExecutionCallbacks | None = None,
    ) -> None:
        """Start the child training job."""
        if self.is_running:
            raise RuntimeError("Training process already in progress.")
        self._request = request
        self._cancel_requested = False
        self._terminal_emitted = False
        self._pending_result = None
        self._stdout_buffer = ""
        self._stderr_buffer = ""
        self._temp_artifact_path = default_temporary_artifact(request)
        self._callbacks = callbacks
        self._connect_callbacks(callbacks)

        process = QProcess(self)
        process.setProgram(self._python_executable)
        process.setArguments(training_process_arguments(
            request,
            self._temp_artifact_path,
            self._job_module,
            self._extra_args,
        ))
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
        if self._cancel_requested:
            return True
        self._cancel_requested = True
        self._process.terminate()
        self._kill_timer = QTimer(self)
        self._kill_timer.setSingleShot(True)
        self._kill_timer.timeout.connect(self._kill_if_running)
        self._kill_timer.start(self._terminate_timeout_ms)
        return True

    def dispose(self) -> None:
        """Release Qt-owned runner resources after terminal cleanup."""
        process = self._process
        if process is not None and process.state() != QProcess.NotRunning:
            self._terminal_emitted = True
            process.kill()
            process.waitForFinished(max(self._terminate_timeout_ms, 1000))
            self._cleanup_temp_artifact()
        self._release_process()
        self._stop_kill_timer()
        self.deleteLater()

    def _connect_callbacks(
        self,
        callbacks: TrainingExecutionCallbacks | None,
    ) -> None:
        if callbacks is None:
            return
        self.log_event.connect(callbacks.log)
        self.progress.connect(callbacks.progress)
        self.finished.connect(callbacks.finished)
        self.failed.connect(callbacks.failed)
        self.cancelled.connect(callbacks.cancelled)

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
        if self._terminal_emitted:
            self._release_process()
            return
        self._stop_kill_timer()
        self._read_stdout()
        self._read_stderr()
        self._drain_stdout_lines()
        if self._stderr_buffer.strip() and self._request is not None:
            self.log_event.emit(
                TrainingLogEvent(self._request.run_id, self._stderr_buffer.strip(), "error")
            )
        if self._request is None:
            self._release_process()
            return
        if self._cancel_requested:
            result = process_result(self._request, "cancelled", "Training process cancelled.")
        elif self._pending_result is not None:
            result = self._pending_result
        elif exit_code == 0:
            result = process_result(
                self._request,
                "complete", "Training process completed."
            )
        else:
            result = process_result(
                self._request,
                "error", f"Training process exited with code {exit_code}."
            )
        self._release_process()
        self._emit_terminal(result)

    def _handle_error(self, error: QProcess.ProcessError) -> None:
        if self._terminal_emitted or self._request is None:
            return
        if error != QProcess.FailedToStart:
            return
        if self._process is not None and self._process.state() != QProcess.NotRunning:
            return
        result = (
            process_result(self._request, "cancelled", "Training process cancelled.")
            if self._cancel_requested
            else process_result(
                self._request, "error", "Training process failed to start."
            )
        )
        self._release_process()
        self._emit_terminal(result)

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

    def _release_process(self) -> None:
        self._stop_kill_timer()
        process, self._process = self._process, None
        if process is not None:
            process.deleteLater()

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
