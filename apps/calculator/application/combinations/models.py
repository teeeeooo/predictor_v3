"""Toolkit-free, session-local combination contracts (never persisted core schema)."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True)
class Candidate:
    id: str = field(default_factory=lambda: uuid4().hex)
    label: str = ""
    capacity: str = ""
    power: str = ""
    included: bool = True


@dataclass(frozen=True)
class Point:
    key: str
    capacity_field: str
    power_field: str
    capacity_unit: str = "W"
    role: str = "required"
    source: str = ""
    allow_thousands: bool = False

    @property
    def independent(self):
        return self.role in ("required", "optional")


@dataclass(frozen=True)
class Context:
    kind: str
    profile: str = ""
    climate: str = ""
    product: str = ""
    system_type: str = ""
    mode: str = ""
    basis: str = "public"
    values: tuple[tuple[str, str], ...] = ()
    options: tuple[tuple[str, str | float | int | bool | None], ...] = ()

    def __post_init__(self):
        # Defensive copies make even list-backed callers safe to freeze in runs.
        object.__setattr__(self, "values", tuple(tuple(item) for item in self.values))
        object.__setattr__(self, "options", tuple(tuple(item) for item in self.options))
        if any(not isinstance(value, str) for _, value in self.values):
            raise TypeError("Context values must be raw text")
        if any(value is not None and not isinstance(value, (str, int, float, bool)) for _, value in self.options):
            raise TypeError("Context options must be immutable scalar values")

    @property
    def identity(self):
        return (self.kind, self.profile, self.climate, self.product,
                self.system_type, self.mode, self.options)


@dataclass(frozen=True)
class Measurement:
    id: str
    label: str
    capacity: float
    power: float


@dataclass(frozen=True)
class Snapshot:
    id: str
    revision: int
    context: Context
    points: tuple[Point, ...]
    pools: tuple[tuple[Measurement, ...], ...]
    planned: int

    @property
    def independent_points(self):
        return tuple(p for p in self.points if p.independent)


@dataclass(frozen=True)
class Score:
    value: float
    metric: str
    units: str
    raw: float | None = None
    published: float | None = None
    summary: tuple[tuple[str, object], ...] = ()


@dataclass(frozen=True)
class Result:
    ordinal: int
    selections: tuple[int, ...]
    score: Score | None = None
    error_code: str = ""
    error_message: str = ""


@dataclass
class Session:
    context: Context
    pools: dict[str, list[Candidate]] = field(default_factory=dict)
    revision: int = 0
    run: object | None = None

    def changed(self):
        self.revision += 1

    @property
    def stale(self):
        return self.run is not None and self.run.snapshot.revision != self.revision
