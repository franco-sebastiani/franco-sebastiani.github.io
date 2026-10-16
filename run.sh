#!/usr/bin/env bash
# Run a pipeline script or notebook and save everything it prints to output.txt (replaced on each run).
# Usage:  ./run.sh pipeline/fetch_ots.py
#         ./run.sh notebooks/explore_raw.ipynb
set -o pipefail

case "$1" in
  *.py)
    python "$1" 2>&1 | tee output.txt
    ;;
  *.ipynb)
    # Executes the whole notebook in a fresh kernel and writes cells and outputs as markdown
    jupyter nbconvert --to markdown --execute --stdout --ExecutePreprocessor.timeout=1800 "$1" 2>&1 | tee output.txt
    ;;
  *)
    echo "usage: ./run.sh <script.py | notebook.ipynb>"
    exit 1
    ;;
esac
