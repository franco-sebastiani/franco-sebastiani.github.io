"""Rebuild every chart table in data/processed/ from the interim data.

Run from the repo root:  python pipeline/build_charts.py
Each script in pipeline/charts/ defines CHART_ID and build(ots). This runs them all, loading the
interim data once, and saves each table to data/processed/<CHART_ID>.csv.
"""

import importlib.util
from pathlib import Path

from processing import REPO_ROOT, load_interim, save_processed

CHARTS_DIR = Path(__file__).resolve().parent / "charts"


def load_chart(script):
    """Import a chart script as a module, so its CHART_ID and build() can be used."""
    spec = importlib.util.spec_from_file_location(script.stem, script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    ots = load_interim()
    for script in sorted(CHARTS_DIR.glob("*.py")):
        chart = load_chart(script)
        table = chart.build(ots)
        path = save_processed(table, chart.CHART_ID)
        print(f"{chart.CHART_ID}: {len(table):,} rows -> {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
