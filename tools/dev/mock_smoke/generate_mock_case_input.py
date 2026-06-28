"""Generate paste-ready DEV-only Predict case input TSV."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.dev.mock_smoke.generators import write_mock_case_input  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", help="Mock output directory. Defaults outside the repo.")
    parser.add_argument("--rows", type=int, default=12)
    parser.add_argument("--manifest", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = write_mock_case_input(
        args.output_dir,
        rows=args.rows,
        write_manifest=args.manifest,
    )
    print(f"mock case input TSV: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
