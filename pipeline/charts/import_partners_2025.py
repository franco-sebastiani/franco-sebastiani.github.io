"""Chart table: UK imports by partner country in 2025, with the number of minerals each supplies.

Week 01.
Question:  which countries supply the UK, and is each one a broad supplier (many minerals) or a
           concentrated one (few)?
Decisions: imports only; calendar year 2025; real countries only (no confidential, stores or UK
           partners); value counts records under shared codes once; minerals_supplied counts
           minerals with positive imports, so a shared code counts for each of its minerals;
           value in GBP million.
Output:    data/processed/import_partners_2025.csv
           (country_name, country_iso2, value_gbp_m, minerals_supplied)

Run on its own from the repo root: python pipeline/charts/import_partners_2025.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # pipeline/, for the shared modules

from processing import load_interim, save_processed, unique_records

CHART_ID = "import_partners_2025"


def build(ots):
    """Build the table from the interim trade data."""
    partners = ots[(ots["direction"] == "import") & (ots["year"] == 2025) & (ots["partner_type"] == "country")]

    value = unique_records(partners).groupby(["country_name", "country_iso2"], as_index=False)["Value"].sum()
    minerals = (partners[partners["Value"] > 0]
                .groupby("country_name")["mineral"].nunique()
                .rename("minerals_supplied").reset_index())

    table = value.merge(minerals, on="country_name", how="left")
    table["minerals_supplied"] = table["minerals_supplied"].fillna(0).astype(int)
    table["value_gbp_m"] = (table["Value"] / 1e6).round(2)
    return (table[["country_name", "country_iso2", "value_gbp_m", "minerals_supplied"]]
            .sort_values("value_gbp_m", ascending=False))


if __name__ == "__main__":
    print(f"saved {save_processed(build(load_interim()), CHART_ID)}")
