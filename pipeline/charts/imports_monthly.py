"""Chart table: total UK imports of critical and growth minerals, by month.

Week 01.
Question:  how has the value of UK imports of these minerals changed since January 2022?
Decisions: imports only; all partners, including confidential; records under shared codes
           counted once; value in GBP million.
Output:    data/processed/imports_monthly.csv (month, value_gbp_m)

Run on its own from the repo root: python pipeline/charts/imports_monthly.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # pipeline/, for the shared modules

from processing import load_interim, save_processed, unique_records

CHART_ID = "imports_monthly"


def build(ots):
    """Build the table from the interim trade data."""
    imports = unique_records(ots[ots["direction"] == "import"])
    table = imports.groupby("month", as_index=False)["Value"].sum()
    table["value_gbp_m"] = (table["Value"] / 1e6).round(2)
    return table[["month", "value_gbp_m"]]


if __name__ == "__main__":
    print(f"saved {save_processed(build(load_interim()), CHART_ID)}")
