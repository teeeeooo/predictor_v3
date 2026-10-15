"""Bounded preflight, lazy execution, stable ranking and snapshot-only replay."""
from itertools import product
from math import isfinite, prod
from time import perf_counter
from uuid import uuid4

from .models import Measurement, Result, Snapshot

LIMIT = 10_000


class ValidationError(ValueError):
    pass


def validate_candidate(candidate, point, row):
    if not candidate.included:
        return None
    if not (candidate.capacity.strip() or candidate.power.strip() or candidate.label.strip()):
        return None
    numbers = []
    for field in ("capacity", "power"):
        text = getattr(candidate, field).strip()
        try:
            # AHRI's current application parser accepts thousands separators.
            value = float(text.replace(",", "") if point.capacity_unit == "Btu/h" else text)
            if not isfinite(value) or value <= 0:
                raise ValueError()
        except ValueError:
            raise ValidationError(f"{point.key} · 행 {row} · {field}: 양의 유한 숫자 필요") from None
        numbers.append(value)
    return Measurement(candidate.id, candidate.label, *numbers)


def preflight(session, adapter):
    points = tuple(adapter.points(session.context))
    pools = []
    for point in points:
        if not point.independent:
            continue
        values = tuple(value for row, draft in enumerate(session.pools.get(point.key, ()), 1)
                       if (value := validate_candidate(draft, point, row)) is not None)
        if not values:
            raise ValidationError(f"{point.key}: 포함된 완전한 시험값이 필요합니다")
        if len({v.id for v in values}) != len(values):
            raise ValidationError(f"{point.key}: 중복 시험 ID")
        pools.append(values)
    count = prod(map(len, pools)) if pools else 0
    if not 0 < count <= LIMIT:
        raise ValidationError(f"조합 {count:,}개: 실행당 1–{LIMIT:,}개만 허용됩니다. 후보를 제외하거나 시험점을 후보 1개로 고정하세요.")
    snapshot = Snapshot(uuid4().hex, session.revision, session.context, points, tuple(pools), count)
    # Request construction validates common options without any engine execution.
    adapter.request(snapshot.context, selected_values(snapshot, (0,) * len(pools)))
    return snapshot


def selected_values(snapshot, selections):
    values = dict(snapshot.context.values)
    for point, pool, index in zip(snapshot.independent_points, snapshot.pools, selections):
        candidate = pool[index]
        values[point.capacity_field] = str(candidate.capacity)
        values[point.power_field] = str(candidate.power)
    return values


class Run:
    def __init__(self, snapshot, adapter):
        if not 0 < snapshot.planned <= LIMIT or snapshot.planned != prod(map(len, snapshot.pools)):
            raise ValidationError("잘못된 조합 수")
        self.snapshot = snapshot
        self.adapter = adapter
        self.results = []
        self.status = "running"
        self.failure = ""
        self._cancelled = False
        self._iterator = iter(product(*(range(len(pool)) for pool in snapshot.pools)))

    @property
    def processed(self):
        return len(self.results)

    @property
    def succeeded(self):
        return sum(row.score is not None for row in self.results)

    @property
    def failed(self):
        return self.processed - self.succeeded

    @property
    def partial(self):
        return self.status in ("cancelled", "failed", "running")

    def cancel(self):
        self._cancelled = True

    def step(self, *, budget_seconds=0.015, max_cases=100):
        if self.status != "running":
            return
        deadline = perf_counter() + budget_seconds
        try:
            for _ in range(max_cases):
                if self._cancelled:
                    self.status = "cancelled"
                    break
                if self.processed == self.snapshot.planned:
                    self.status = "completed-with-errors" if self.failed else "completed"
                    break
                selection = next(self._iterator)
                ordinal = self.processed + 1
                try:
                    result = self.adapter.execute(self.snapshot.context, selected_values(self.snapshot, selection))
                    score = self.adapter.project(self.snapshot.context, result)
                    if not isfinite(score.value):
                        raise ValueError("계산 결과가 유한 숫자가 아닙니다")
                    row = Result(ordinal, selection, score)
                except (ValueError, TypeError, KeyError, ArithmeticError) as exc:
                    row = Result(ordinal, selection, error_code=type(exc).__name__, error_message=str(exc))
                self.results.append(row)
                if perf_counter() >= deadline:
                    break
            if self.processed == self.snapshot.planned and self.status == "running":
                self.status = "completed-with-errors" if self.failed else "completed"
        except Exception as exc:
            self.status = "failed"
            self.failure = f"{type(exc).__name__}: {exc}"

    def ranked(self):
        ordered = sorted(self.results, key=lambda r: (r.score is None, -r.score.value if r.score else 0, r.ordinal))
        rank, previous = None, None
        rows = []
        for position, row in enumerate(ordered, 1):
            if row.score is None:
                rows.append((None, row))
                continue
            if previous is None or previous != row.score.value:
                rank = position
            previous = row.score.value
            rows.append((rank, row))
        return rows

    def detail(self, row):
        if not any(item is row for item in self.results):
            raise ValueError("다른 실행의 결과입니다")
        return self.adapter.execute(self.snapshot.context, selected_values(self.snapshot, row.selections))


def start(session, adapter):
    if session.run is not None and session.run.status == "running":
        raise ValidationError("이미 실행 중입니다")
    snapshot = preflight(session, adapter)
    session.run = Run(snapshot, adapter)
    return session.run
