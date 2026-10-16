"""Shared processing for chart tables: loading the interim data, plus the decisions all charts share.

Used by the chart scripts and by the weekly notebooks, so exploration and the final charts apply
exactly the same rules. Decisions are added here as they are made, and documented in DATA.md.
"""

import tomllib

import pandas as pd

from retrieval import REPO_ROOT

INTERIM_FILE = REPO_ROOT / "data" / "interim" / "ots_minerals.parquet"
CONFIG_FILE = REPO_ROOT / "config" / "minerals.toml"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"

# The original HMRC fields that identify one trade record
RECORD_COLUMNS = ["MonthId", "FlowTypeId", "SuppressionIndex", "CommodityId", "CommoditySitcId",
                  "CountryId", "PortId", "Value", "NetMass", "SuppUnit"]


def load_interim(columns=None):
    """Load the interim trade table built by build_interim.py, optionally only some columns."""
    return pd.read_parquet(INTERIM_FILE, columns=columns)


def load_minerals():
    """Load the minerals config: names, list membership and CN8 codes, keyed by mineral."""
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)["minerals"]


def save_processed(table, chart_id):
    """Save a chart's table to data/processed/<chart_id>.csv and return the path."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / f"{chart_id}.csv"
    table.to_csv(path, index=False)
    return path


def unique_records(df):
    """Keep one copy of each trade record, so totals across minerals count shared codes once.

    Records under the four shared codes appear once per mineral in the interim table (see DATA.md).
    """
    return df.drop_duplicates(subset=RECORD_COLUMNS)
