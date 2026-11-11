#!/usr/bin/env bash
# Every check of the Checks workflow in one command, from the repository root.
set -euo pipefail
cd "$(dirname "$0")/.."

uv sync --frozen
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q
uv run pytest plugins/agent-flow .claude/skills -q --no-cov -p no:cacheprovider
echo "All checks passed."
