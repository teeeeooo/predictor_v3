"""Cleanup generated DEV-only mock smoke outputs from a manifest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.dev.mock_smoke.generators import (  # noqa: E402
    MANIFEST_NAME,
    cleanup_from_manifest,
    resolve_output_dir,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", help="Mock output directory. Defaults outside the repo.")
    parser.add_argument("--manifest-path", help="Explicit manifest path.")
    parser.add_argument("--remove-local-model", action="store_true")
    parser.add_argument("--remove-local-mapping", action="store_true")
    parser.add_argument("--remove-local-train-data", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest_path) if args.manifest_path else (
        resolve_output_dir(args.output_dir) / MANIFEST_NAME
    )
    removed = cleanup_from_manifest(
        manifest_path,
        remove_local_model=args.remove_local_model,
        remove_local_mapping=args.remove_local_mapping,
        remove_local_train_data=args.remove_local_train_data,
    )
    for path in removed:
        print(f"removed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
