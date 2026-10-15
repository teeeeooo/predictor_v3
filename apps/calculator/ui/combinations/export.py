"""Pure versioned CSV projection; the shared UI export adapter owns I/O."""
from dataclasses import asdict
import json

SCHEMA = "calculator_combinations_v1"


def context_json(snapshot):
    return json.dumps({"context": asdict(snapshot.context), "points": [asdict(p) for p in snapshot.points]},
                      ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def export_rows(run, *, stale):
    snapshot = run.snapshot
    ctx = snapshot.context
    records = []
    provenance = context_json(snapshot)
    for rank, row in run.ranked():
        score = row.score
        record = dict(schema_version=SCHEMA, run_id=snapshot.id, run_status=run.status,
                      input_revision=snapshot.revision, stale=stale, partial=run.partial, run_error=run.failure,
                      planned_count=snapshot.planned, processed_count=run.processed,
                      combination_id=row.ordinal, rank=rank, calculation_status="ok" if score else "error",
                      error_code=row.error_code, error_message=row.error_message,
                      capability=run.adapter.operation(ctx), profile=run.adapter.profile(ctx), metric=score.metric if score else run.adapter.metric(ctx),
                      climate=ctx.climate, product=ctx.product, system_type=ctx.system_type,
                      score_basis=ctx.basis, score=score.value if score else None,
                      score_units=score.units if score else "", raw=score.raw if score else None,
                      published=score.published if score else None)
        for point, pool, index in zip(snapshot.independent_points, snapshot.pools, row.selections):
            value = pool[index]
            for key, data in (("candidate_id", value.id), ("candidate_number", value.number), ("label", value.label), ("capacity", value.capacity),
                              ("power", value.power), ("capacity_unit", point.capacity_unit), ("power_unit", "W")):
                record[f"{point.key}.{key}"] = data
        if score:
            record.update(dict(score.summary))
        record["context_json"] = provenance
        records.append(record)
    headers = tuple(dict.fromkeys(key for record in records for key in record))
    rows = tuple(tuple("" if record.get(key) is None else str(record.get(key, "")) for key in headers) for record in records)
    return headers, rows
