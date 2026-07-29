"""Qt-free killable subprocess adapter for headless training."""

from __future__ import annotations

import queue
import subprocess
import sys
import threading
from pathlib import Path

from apps.train.adapters.qprocess_command import (
    default_temporary_artifact,
    training_process_arguments,
)
from apps.train.adapters.qprocess_terminal import process_result
from apps.train.adapters.training_process_events import parse_training_event
from apps.train.ports.training_execution_port import TrainingExecutionCallbacks
from apps.train.state.training_run_state import TrainingRequest, TrainingResult


class SubprocessTrainingRunner:
    """Run the established child job without importing a UI toolkit."""

    def __init__(
        self,
        *,
        python_executable: str | None = None,
        job_module: str = "apps.train.jobs.train_job",
        extra_args: tuple[str, ...] = (),
        cancellation_requested=None,  # noqa: ANN001
    ) -> None:
        self._python = python_executable or sys.executable
        self._job_module = job_module
        self._extra_args = extra_args
        self._cancellation_requested = cancellation_requested or (lambda: False)
        self._process: subprocess.Popen[str] | None = None
        self._cancel_requested = False
        self._temporary: Path | None = None

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(
        self,
        request: TrainingRequest,
        callbacks: TrainingExecutionCallbacks | None = None,
    ) -> None:
        if self.is_running:
            raise RuntimeError("Training process already in progress.")
        callbacks = callbacks or _empty_callbacks()
        self._temporary = default_temporary_artifact(request)
        arguments = training_process_arguments(
            request, self._temporary, self._job_module, self._extra_args
        )
        process = subprocess.Popen(
            [self._python, *arguments],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        self._process = process
        events: queue.Queue[str | None] = queue.Queue()
        reader = threading.Thread(
            target=_read_lines, args=(process, events), daemon=True
        )
        reader.start()
        pending: TrainingResult | None = None
        while process.poll() is None or not events.empty():
            if self._cancellation_requested() and not self._cancel_requested:
                self.cancel()
            try:
                line = events.get(timeout=0.1)
            except queue.Empty:
                continue
            if line is None:
                continue
            try:
                event_type, event = parse_training_event(line, request)
            except (TypeError, ValueError) as exc:
                self._abort_protocol(process)
                raise RuntimeError(
                    "Training child protocol rejected: "
                    f"{str(exc).splitlines()[0]}"
                ) from exc
            if event_type == "training_start_requested":
                if callbacks.start_requested is None:
                    self._abort_protocol(process)
                    raise RuntimeError(
                        "Training start permit authority is unavailable."
                    )
                try:
                    callbacks.start_requested(event)
                except Exception:
                    self._abort_protocol(process)
                    raise
            elif event_type == "training_started":
                callbacks.started(request)
            elif event_type == "progress":
                callbacks.progress(event)
            elif event_type == "result":
                pending = event
            else:
                callbacks.log(event)
        return_code = process.wait()
        self._process = None
        if self._cancel_requested:
            self._cleanup_temporary()
            callbacks.cancelled(
                process_result(request, "cancelled", "Training process cancelled.")
            )
        elif pending is not None and pending.status == "complete":
            callbacks.finished(pending)
        elif pending is not None and pending.status == "cancelled":
            self._cleanup_temporary()
            callbacks.cancelled(pending)
        else:
            self._cleanup_temporary()
            callbacks.failed(
                pending
                or process_result(
                    request,
                    "error",
                    f"Training process exited with code {return_code}.",
                )
            )

    def cancel(self) -> bool:
        if not self.is_running or self._process is None:
            return False
        self._cancel_requested = True
        self._process.terminate()
        try:
            self._process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self._process.kill()
        return True

    def dispose(self) -> None:
        if self.is_running and self._process is not None:
            self._process.kill()
            self._process.wait(timeout=2)
        self._process = None

    def _cleanup_temporary(self) -> None:
        if self._temporary is not None:
            self._temporary.unlink(missing_ok=True)

    def _abort_protocol(self, process: subprocess.Popen[str]) -> None:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        self._process = None
        self._cleanup_temporary()


def _read_lines(
    process: subprocess.Popen[str], events: queue.Queue[str | None]
) -> None:
    assert process.stdout is not None
    for line in process.stdout:
        if line.strip():
            events.put(line.strip())
    events.put(None)


def _empty_callbacks() -> TrainingExecutionCallbacks:
    return TrainingExecutionCallbacks(
        started=lambda _request: None,
        log=lambda _event: None,
        progress=lambda _event: None,
        finished=lambda _result: None,
        failed=lambda _result: None,
        cancelled=lambda _result: None,
    )
