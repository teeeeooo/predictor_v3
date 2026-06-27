"""CLI utility for converting an Excel/CSV mapping table to JSON."""

import argparse
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.mapping.update import update_mapping_to_json  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert an Excel/CSV mapping table to data/mapping.json."
    )
    parser.add_argument(
        "mapping_source",
        help="Path to an .xlsx, .xls, or .csv mapping source file.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the mapping conversion utility."""
    args = parse_args(argv)
    print("=" * 50)
    print("Mapping table update started")
    print("=" * 50)

    update_mapping_to_json(args.mapping_source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
