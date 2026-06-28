"""Generate a DEV-only mock prediction artifact for smoke testing."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.dev.mock_smoke.generators import (  # noqa: E402
    DEFAULT_ROWS,
    DEFAULT_SEED,
    install_local_model,
    write_mock_prediction_artifact,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", help="Mock output directory. Defaults outside the repo.")
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--install-local-model",
        action="store_true",
        help="Copy the generated artifact to model/model.pkl for DEV smoke only.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow replacing an existing local model/model.pkl during DEV smoke.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    artifact_path = write_mock_prediction_artifact(
        output_dir=args.output_dir,
        rows=args.rows,
        seed=args.seed,
    )
    print(f"mock prediction artifact: {artifact_path}")
    if args.install_local_model:
        installed_path = install_local_model(artifact_path, force=args.force)
        print(f"installed DEV mock model: {installed_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
