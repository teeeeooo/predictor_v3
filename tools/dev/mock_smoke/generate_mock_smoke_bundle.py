"""Generate the full DEV-only mock smoke bundle."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.dev.mock_smoke.generators import (  # noqa: E402
    DEFAULT_SEED,
    generate_mock_smoke_bundle,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", help="Mock output directory. Defaults outside the repo.")
    parser.add_argument("--rows", type=int, default=12)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--predict-delay-ms", type=int, default=0)
    parser.add_argument("--manifest", action="store_true")
    parser.add_argument("--install-local-model", action="store_true")
    parser.add_argument("--install-local-mapping", action="store_true")
    parser.add_argument("--install-local-train-data", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = generate_mock_smoke_bundle(
        output_dir=args.output_dir,
        rows=args.rows,
        seed=args.seed,
        predict_delay_ms=args.predict_delay_ms,
        write_manifest=args.manifest,
        install_model=args.install_local_model,
        install_mapping=args.install_local_mapping,
        install_train_data=args.install_local_train_data,
        force=args.force,
    )
    for name, path in paths.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
