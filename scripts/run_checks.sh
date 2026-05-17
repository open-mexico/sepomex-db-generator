#!/usr/bin/env bash
set -euo pipefail

RUN_NOTEBOOKS="${RUN_NOTEBOOKS:-0}"

echo "[1/4] Running ruff check"
ruff check .

echo "[2/4] Running ruff format check"
ruff format --check .

echo "[3/4] Running tests with coverage"
pytest

if [[ "$RUN_NOTEBOOKS" == "1" ]]; then
  echo "[4/4] Executing notebooks"
  if find . -type f -name "*.ipynb" | grep -q .; then
    find . -type f -name "*.ipynb" -print0 | \
      xargs -0 -I{} jupyter nbconvert --execute --to notebook --inplace "{}"
  else
    echo "No notebooks found. Skipping notebook execution."
  fi
else
  echo "[4/4] Notebook execution skipped (set RUN_NOTEBOOKS=1 to enable)"
fi
