"""Owned immutable run records and atomic campaign state."""

from __future__ import annotations

import json
import os
import re
import stat
from pathlib import Path
from typing import Any

_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")


class ExperimentStore:
    def __init__(self, lifecycle_root: str | Path) -> None:
        self.root = Path(os.path.abspath(lifecycle_root)) / "experiments"
        self.runs = self.root / "runs"
        self.campaigns = self.root / "campaigns"

    def write_run(self, run_id: str, payload: dict[str, Any]) -> Path:
        path = self._identity_path(self.runs, run_id)
        path.mkdir(parents=True, exist_ok=False)
        self._require_owned_directory(path)
        self._write_exclusive(path / "record.json", payload)
        return path / "record.json"

    def update_run(self, run_id: str, payload: dict[str, Any]) -> Path:
        path = self._identity_path(self.runs, run_id)
        self._replace_json(path / "record.json", payload)
        return path / "record.json"

    def append_run_event(self, run_id: str, payload: dict[str, Any]) -> str:
        directory = self._identity_path(self.runs, run_id, create_parent=False)
        self._require_owned_directory(directory)
        path = directory / "events.jsonl"
        flags = (
            os.O_WRONLY
            | os.O_APPEND
            | os.O_CREAT
            | getattr(os, "O_NOFOLLOW", 0)
        )
        descriptor = os.open(path, flags, 0o600)
        try:
            encoded = (
                json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n"
            ).encode("utf-8")
            os.write(descriptor, encoded)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        self._require_owned_file(path)
        return f"experiments/runs/{run_id}/events.jsonl"

    def read_run(self, run_id: str) -> dict[str, Any]:
        return self._read_json(
            self._identity_path(self.runs, run_id, create_parent=False) / "record.json"
        )

    def read_run_events(self, run_id: str) -> tuple[dict[str, Any], ...]:
        path = (
            self._identity_path(self.runs, run_id, create_parent=False)
            / "events.jsonl"
        )
        if not path.exists():
            return ()
        self._require_owned_file(path)
        events = []
        for line in path.read_text(encoding="utf-8").splitlines():
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError("persisted run event must be an object")
            events.append(payload)
        return tuple(events)

    def create_campaign(self, campaign_id: str, payload: dict[str, Any]) -> Path:
        path = self._identity_path(self.campaigns, campaign_id)
        path.mkdir(parents=True, exist_ok=False)
        self._require_owned_directory(path)
        self._write_exclusive(path / "record.json", payload)
        return path / "record.json"

    def update_campaign(
        self, campaign_id: str, payload: dict[str, Any]
    ) -> Path:
        path = self._identity_path(self.campaigns, campaign_id)
        self._replace_json(path / "record.json", payload)
        return path / "record.json"

    def read_campaign(self, campaign_id: str) -> dict[str, Any]:
        return self._read_json(
            self._identity_path(
                self.campaigns, campaign_id, create_parent=False
            ) / "record.json"
        )

    def write_campaign_evidence(
        self,
        campaign_id: str,
        collection: str,
        identity: str,
        filename: str,
        payload: dict[str, Any],
    ) -> str:
        if collection not in {
            "proposals",
            "iterations",
            "recommendations",
            "budget_extensions",
        }:
            raise ValueError("unsupported campaign evidence collection")
        if _SAFE_ID.fullmatch(identity) is None or _SAFE_ID.fullmatch(filename) is None:
            raise ValueError("campaign evidence identity is not safe")
        campaign = self._identity_path(
            self.campaigns, campaign_id, create_parent=False
        )
        self._require_owned_directory(campaign)
        collection_path = campaign / collection
        collection_path.mkdir(exist_ok=True)
        self._require_owned_directory(collection_path)
        directory = collection_path / identity
        directory.mkdir(exist_ok=True)
        self._require_owned_directory(directory)
        path = directory / filename
        self._write_exclusive(path, payload)
        return (
            f"experiments/campaigns/{campaign_id}/{collection}/"
            f"{identity}/{filename}"
        )

    def read_campaign_evidence(
        self,
        campaign_id: str,
        collection: str,
        identity: str,
        filename: str,
    ) -> dict[str, Any]:
        campaign = self._identity_path(
            self.campaigns, campaign_id, create_parent=False
        )
        path = campaign / collection / identity / filename
        return self._read_json(path)

    def list_campaigns(self) -> tuple[dict[str, Any], ...]:
        if not self.campaigns.exists():
            return ()
        self._require_owned_directory(self.campaigns)
        records = []
        for path in sorted(self.campaigns.iterdir()):
            if path.name.startswith("."):
                continue
            self._require_owned_directory(path)
            records.append(self._read_json(path / "record.json"))
        return tuple(sorted(
            records,
            key=lambda item: (
                str(item.get("updated_at", "")),
                str(item.get("campaign_id", "")),
            ),
        ))

    def request_control(self, campaign_id: str, action: str) -> Path:
        if action not in {"pause", "cancel"}:
            raise ValueError("unsupported campaign control action")
        path = self._identity_path(self.campaigns, campaign_id, create_parent=False)
        self._replace_json(
            path / "control.json",
            {"schema_version": "predictor_v3.campaign_control.v1", "action": action},
            allow_missing=True,
        )
        return path / "control.json"

    def read_control(self, campaign_id: str) -> str:
        path = self._identity_path(
            self.campaigns, campaign_id, create_parent=False
        ) / "control.json"
        if not path.exists():
            return ""
        payload = self._read_json(path)
        action = payload.get("action", "")
        return action if action in {"pause", "cancel"} else ""

    def clear_control(self, campaign_id: str) -> None:
        path = self._identity_path(
            self.campaigns, campaign_id, create_parent=False
        ) / "control.json"
        if path.exists():
            self._require_owned_file(path)
            path.unlink()

    def _identity_path(
        self, parent: Path, identity: str, *, create_parent: bool = True
    ) -> Path:
        if _SAFE_ID.fullmatch(identity) is None:
            raise ValueError("experiment identity is not safe")
        if create_parent:
            parent.mkdir(parents=True, exist_ok=True)
        if parent.exists():
            self._require_owned_directory(parent)
        return parent / identity

    def _read_json(self, path: Path) -> dict[str, Any]:
        self._require_owned_file(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("persisted experiment record must be an object")
        return payload

    def _write_exclusive(self, path: Path, payload: dict[str, Any]) -> None:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags, 0o600)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", closefd=False) as target:
                json.dump(payload, target, ensure_ascii=False, sort_keys=True, indent=2)
                target.write("\n")
                target.flush()
                os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def _replace_json(
        self,
        path: Path,
        payload: dict[str, Any],
        *,
        allow_missing: bool = False,
    ) -> None:
        self._require_owned_directory(path.parent)
        if not allow_missing:
            self._require_owned_file(path)
        elif path.exists():
            self._require_owned_file(path)
        temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
        self._write_exclusive(temporary, payload)
        os.replace(temporary, path)

    def _require_owned_directory(self, path: Path) -> None:
        entry = path.lstat()
        if stat.S_ISLNK(entry.st_mode) or not stat.S_ISDIR(entry.st_mode):
            raise ValueError("experiment storage directory is unsafe")
        path.resolve(strict=True).relative_to(self.root.resolve(strict=True))

    def _require_owned_file(self, path: Path) -> None:
        entry = path.lstat()
        if stat.S_ISLNK(entry.st_mode) or not stat.S_ISREG(entry.st_mode):
            raise ValueError("experiment storage file is unsafe")
        path.resolve(strict=True).relative_to(self.root.resolve(strict=True))
