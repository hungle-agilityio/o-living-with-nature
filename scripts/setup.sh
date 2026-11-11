#!/usr/bin/env bash
# Install what the project needs to run and to be checked.
set -euo pipefail
cd "$(dirname "$0")/.."

uv sync --frozen
