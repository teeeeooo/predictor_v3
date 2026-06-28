"""Generate DEV-only synthetic training data for smoke testing."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.dev.mock_smoke.generators import (  # noqa: E402
    DEFAULT_ROWS,
    DEFAULT_SEED,
    write_mock_training_data,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", help="Mock output directory. Defaults outside the repo.")
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = write_mock_training_data(
        output_dir=args.output_dir,
        rows=args.rows,
        seed=args.seed,
    )
    print(f"mock training data: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
