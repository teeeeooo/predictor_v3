"""Generate DEV-only mock mapping JSON for smoke testing."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.dev.mock_smoke.generators import (  # noqa: E402
    install_local_mapping,
    write_mock_mapping,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", help="Mock output directory. Defaults outside the repo.")
    parser.add_argument("--manifest", action="store_true")
    parser.add_argument("--install-local-mapping", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = write_mock_mapping(args.output_dir, write_manifest=args.manifest)
    print(f"mock mapping: {output_path}")
    if args.install_local_mapping:
        installed_path = install_local_mapping(output_path, force=args.force)
        print(f"installed DEV mock mapping: {installed_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
