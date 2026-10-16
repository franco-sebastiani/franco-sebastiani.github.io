"""Build the interim dataset: every mineral's OTS trade records in one labelled table.

Run from the repo root:  python pipeline/build_interim.py
Input:   data/raw/hmrc_ots_<mineral>.json and the HMRC lookups (from fetch_ots.py and fetch_lookups.py)
Output:  data/interim/ots_minerals.parquet (local, not committed; overwritten on each run)

Every raw record is kept with its original fields unchanged: nothing is aggregated or filtered.
Added columns (lowercase): mineral, cn8_description, country_name, country_iso2, partner_type,
flow, direction, partner_group, month, year.
Records under shared codes appear once per mineral (see DATA.md, 'Shared codes').
"""

import json
import tomllib

import pandas as pd

from retrieval import RAW_DIR, REPO_ROOT

CONFIG = REPO_ROOT / "config" / "minerals.toml"
OUT_FILE = REPO_ROOT / "data" / "interim" / "ots_minerals.parquet"

# Partners that are not foreign countries, by CountryId in the HMRC Country lookup (see DATA.md)
SPECIAL_PARTNERS = {977: "confidential", 951: "stores_provisions", 952: "stores_provisions", 6: "uk"}


def load_raw(filename):
    """Load a raw JSON file (a list of records) into a DataFrame."""
    with open(RAW_DIR / filename, encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))


def main():
    with open(CONFIG, "rb") as f:
        minerals = tomllib.load(f)["minerals"]

    # 1. All trade records, tagged with their mineral
    frames = [load_raw(f"hmrc_ots_{key}.json").assign(mineral=key) for key in minerals]
    raw_rows = sum(len(frame) for frame in frames)
    ots = pd.concat(frames, ignore_index=True)

    # 2. Commodity descriptions
    commodity = load_raw("hmrc_commodity_lookup.json")[["CommodityId", "Cn8LongDescription"]]
    commodity = commodity.rename(columns={"Cn8LongDescription": "cn8_description"})
    ots = ots.merge(commodity, on="CommodityId", how="left", validate="many_to_one")

    # 3. Country names and ISO codes, and the type of partner
    country = load_raw("hmrc_country_lookup.json")[["CountryId", "CountryName", "CountryCodeAlpha"]]
    country = country.rename(columns={"CountryName": "country_name", "CountryCodeAlpha": "country_iso2"})
    ots = ots.merge(country, on="CountryId", how="left", validate="many_to_one")
    ots["partner_type"] = ots["CountryId"].map(SPECIAL_PARTNERS).fillna("country")

    # 4. Flow type, split into direction (import/export) and partner group (EU/non-EU).
    #    The EU split comes from the flow type, not the Country lookup's historic area fields (see DATA.md).
    flowtype = load_raw("hmrc_flowtype_lookup.json")[["FlowTypeId", "FlowTypeDescription"]]
    flowtype["flow"] = flowtype["FlowTypeDescription"].str.strip()  # descriptions are padded with spaces
    flowtype["direction"] = flowtype["flow"].str.contains("Imports").map({True: "import", False: "export"})
    flowtype["partner_group"] = flowtype["flow"].str.startswith("Non-EU").map({True: "non-EU", False: "EU"})
    ots = ots.merge(flowtype.drop(columns="FlowTypeDescription"), on="FlowTypeId", how="left",
                    validate="many_to_one")

    # 5. Dates
    ots["month"] = pd.to_datetime(ots["MonthId"].astype(str), format="%Y%m")
    ots["year"] = ots["month"].dt.year

    # Checks: nothing lost or duplicated by the joins, and every record labelled
    assert len(ots) == raw_rows, f"row count changed: {raw_rows:,} raw, {len(ots):,} interim"
    for column in ["cn8_description", "country_name", "flow"]:
        missing = ots[column].isna().sum()
        assert missing == 0, f"{missing:,} rows without {column}"

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ots.to_parquet(OUT_FILE, index=False)
    print(f"{len(ots):,} rows, {ots['mineral'].nunique()} minerals, "
          f"{ots['MonthId'].min()} to {ots['MonthId'].max()} -> {OUT_FILE.relative_to(REPO_ROOT)}")
    print(ots["partner_type"].value_counts().to_string())


if __name__ == "__main__":
    main()
