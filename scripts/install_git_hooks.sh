#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

test -x .githooks/pre-commit || chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
printf 'Installed repository hooks at %s/.githooks (core.hooksPath=.githooks)\n' "$repo_root"
