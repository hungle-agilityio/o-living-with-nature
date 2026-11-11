#!/usr/bin/env bash
# The one command that checks everything; the loop and CI run it. Stops at the first failure.
set -euo pipefail
cd "$(dirname "$0")/.."

run() {
  echo "+ $*"
  "$@"
}

run uv run ruff check .
run uv run ruff format --check .
if [ -n "$(find src -name '*.py' -print -quit 2>/dev/null)" ]; then
  run uv run mypy .
else
  echo "WARNING: no Python code in src/ yet; mypy skipped."
fi
echo "+ uv run pytest -q --cov=src --cov-report=term-missing"
status=0
uv run pytest -q --cov=src --cov-report=term-missing || status=$?
if [ "$status" -eq 5 ]; then
  echo "WARNING: pytest collected no tests; add tests in src/<feature>/tests/."
elif [ "$status" -ne 0 ]; then
  exit "$status"
fi
# This project's own extras: the flow's tests and the check-in-browser skill's tests.
run uv run pytest .flow/loop/tests .claude/skills -q -p no:cacheprovider
