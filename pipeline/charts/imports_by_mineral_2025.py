"""Chart table: UK imports by mineral in 2025.

Week 01.
Question:  which critical and growth minerals does the UK import the most of, by value?
Decisions: imports only; calendar year 2025; all partners, including confidential; each mineral's
           own total, so records under shared codes count towards each of their minerals;
           value in GBP million.
Output:    data/processed/imports_by_mineral_2025.csv (mineral, mineral_name, value_gbp_m)

Run on its own from the repo root: python pipeline/charts/imports_by_mineral_2025.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # pipeline/, for the shared modules

from processing import load_interim, load_minerals, save_processed

CHART_ID = "imports_by_mineral_2025"


def build(ots):
    """Build the table from the interim trade data."""
    names = {key: mineral["name"] for key, mineral in load_minerals().items()}

    imports = ots[(ots["direction"] == "import") & (ots["year"] == 2025)]
    table = imports.groupby("mineral", as_index=False)["Value"].sum()
    table["mineral_name"] = table["mineral"].map(names)
    table["value_gbp_m"] = (table["Value"] / 1e6).round(2)
    return (table[["mineral", "mineral_name", "value_gbp_m"]]
            .sort_values("value_gbp_m", ascending=False))


if __name__ == "__main__":
    print(f"saved {save_processed(build(load_interim()), CHART_ID)}")
