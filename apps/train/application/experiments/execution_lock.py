"""Workspace-wide non-stealable training writer lock with diagnostics."""

from __future__ import annotations

import json
import errno
import os
import stat
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ExecutionLockConflict(RuntimeError):
    def __init__(self, metadata: dict[str, Any]) -> None:
        super().__init__("Another workspace training writer owns execution.")
        self.metadata = metadata


class WorkspaceExecutionLock:
    """Hold one OS advisory lock and publish best-effort liveness metadata."""

    def __init__(
        self,
        workspace_root: str | Path,
        *,
        owner: str,
        run_id: str,
        campaign_id: str = "",
    ) -> None:
        self._root = Path(os.path.abspath(workspace_root))
        self._path = self._root / ".training-execution.lock"
        self._owner = owner
        self._run_id = run_id
        self._campaign_id = campaign_id
        self._descriptor: int | None = None
        self._started_at = ""
        self._stage = "preflight"
        self._write_guard = threading.Lock()
        self._heartbeat_stop = threading.Event()
        self._heartbeat_thread: threading.Thread | None = None

    @property
    def metadata(self) -> dict[str, Any]:
        return {
            "schema_version": "predictor_v3.execution_lock.v1",
            "execution_owner": self._owner,
            "process_id": os.getpid(),
            "started_at": self._started_at,
            "heartbeat_at": datetime.now(timezone.utc).isoformat(),
            "current_stage": self._stage,
            "run_id": self._run_id,
            "campaign_id": self._campaign_id,
        }

    def acquire(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True)
        _require_owned_root(self._root)
        flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(self._path, flags, 0o600)
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode):
                raise RuntimeError("execution lock is not a regular file")
            _try_lock(descriptor)
        except OSError as exc:
            os.close(descriptor)
            if isinstance(exc, BlockingIOError) or exc.errno in {
                errno.EACCES, errno.EAGAIN,
            }:
                raise ExecutionLockConflict(
                    read_lock_metadata(self._path)
                ) from exc
            raise
        except BaseException:
            os.close(descriptor)
            raise
        self._descriptor = descriptor
        self._started_at = datetime.now(timezone.utc).isoformat()
        self.update("acquired")
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            name=f"training-lock-heartbeat-{self._run_id}",
            daemon=True,
        )
        self._heartbeat_thread.start()

    def update(self, stage: str) -> None:
        if self._descriptor is None:
            return
        with self._write_guard:
            if self._descriptor is None:
                return
            self._stage = stage
            encoded = (
                json.dumps(self.metadata, ensure_ascii=False, sort_keys=True, indent=2)
                + "\n"
            ).encode("utf-8")
            os.lseek(self._descriptor, 0, os.SEEK_SET)
            os.ftruncate(self._descriptor, 0)
            os.write(self._descriptor, encoded)
            os.fsync(self._descriptor)

    def release(self) -> None:
        if self._descriptor is None:
            return
        self._heartbeat_stop.set()
        if self._heartbeat_thread is not None:
            self._heartbeat_thread.join(timeout=2)
            self._heartbeat_thread = None
        with self._write_guard:
            descriptor, self._descriptor = self._descriptor, None
            if descriptor is not None:
                try:
                    _unlock(descriptor)
                finally:
                    os.close(descriptor)

    def _heartbeat_loop(self) -> None:
        while not self._heartbeat_stop.wait(5):
            self.update(self._stage)


def read_lock_metadata(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        entry = source.lstat()
        if stat.S_ISLNK(entry.st_mode) or not stat.S_ISREG(entry.st_mode):
            return {"status": "invalid_lock_artifact"}
        payload = json.loads(source.read_text(encoding="utf-8") or "{}")
        return payload if isinstance(payload, dict) else {"status": "invalid_metadata"}
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {"status": "metadata_unavailable"}


def execution_lock_is_held(path: str | Path) -> bool:
    source = Path(path)
    if not source.exists():
        return False
    flags = os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(source, flags)
    try:
        try:
            _try_lock(descriptor)
        except (BlockingIOError, OSError):
            return True
        _unlock(descriptor)
        return False
    finally:
        os.close(descriptor)


def _require_owned_root(root: Path) -> None:
    entry = root.lstat()
    if stat.S_ISLNK(entry.st_mode) or not stat.S_ISDIR(entry.st_mode):
        raise RuntimeError("execution workspace is not an owned directory")


def _try_lock(descriptor: int) -> None:
    if os.name == "nt":
        import msvcrt

        os.lseek(descriptor, 0, os.SEEK_SET)
        if os.fstat(descriptor).st_size == 0:
            os.write(descriptor, b"\0")
        msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
    else:
        import fcntl

        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock(descriptor: int) -> None:
    if os.name == "nt":
        import msvcrt

        os.lseek(descriptor, 0, os.SEEK_SET)
        msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(descriptor, fcntl.LOCK_UN)
