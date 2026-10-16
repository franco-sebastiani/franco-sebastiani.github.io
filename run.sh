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
    # 1. Execute the whole notebook in a fresh kernel, into a temporary copy (the .ipynb on disk is not changed).
    #    --allow-errors keeps going past a failing cell, so the error appears in the output.
    # 2. Print each cell's code and plain-text output, so tables show as aligned text rather than HTML.
    tmp_dir=$(mktemp -d)
    {
      jupyter nbconvert --to notebook --execute --allow-errors --ExecutePreprocessor.timeout=1800 \
        --output-dir "$tmp_dir" --output executed "$1" &&
      python tools/nb_to_text.py "$tmp_dir/executed.ipynb"
    } 2>&1 | tee output.txt
    rm -rf "$tmp_dir"
    ;;
  *)
    echo "usage: ./run.sh <script.py | notebook.ipynb>"
    exit 1
    ;;
esac
