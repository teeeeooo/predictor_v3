"""Generate the deterministic canonical manifest from current repository owners."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.data_definition.contract import bootstrap_manifest, dump_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    dump_manifest(bootstrap_manifest(), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
