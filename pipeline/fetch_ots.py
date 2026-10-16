"""Fetch HMRC overseas trade statistics (OTS) for every mineral in config/minerals.toml.

Run from the repo root:  python pipeline/fetch_ots.py
Output:   data/raw/hmrc_ots_<mineral>.json, one file per mineral, records saved untouched
          (all flows, countries and ports; overwritten on each run)
Logging:  one line per mineral in data/raw/retrieval_log.jsonl (via retrieval.py),
          listing every URL requested for that mineral
Coverage: from START_MONTH onwards; DATA.md explains the choice
"""

import tomllib
from datetime import datetime, timezone

from hmrc_api import BASE_URL, code_batches, fetch_all
from retrieval import REPO_ROOT, log_retrieval, save_and_log

START_MONTH = 202201  # January 2022: see DATA.md, 'Time coverage'
SOURCE = "HMRC uktradeinfo API - Overseas Trade Statistics (OTS)"
CONFIG = REPO_ROOT / "config" / "minerals.toml"


def fetch_mineral(codes):
    """Fetch all OTS rows for a mineral's CN8 codes, in batches small enough for the API's filter limit."""
    records, pages, urls = [], 0, []
    for clause in code_batches(codes):
        params = {"$filter": f"({clause}) and MonthId ge {START_MONTH}"}
        batch, batch_pages, url = fetch_all("OTS", params)
        records.extend(batch)
        pages += batch_pages
        urls.append(url)
    return records, pages, urls


def main():
    with open(CONFIG, "rb") as f:
        minerals = tomllib.load(f)["minerals"]

    failed = []
    for i, (key, mineral) in enumerate(minerals.items(), start=1):
        print(f"[{i}/{len(minerals)}] {key}: {len(mineral['cn8'])} codes")
        started = datetime.now(timezone.utc)
        try:
            records, pages, urls = fetch_mineral(mineral["cn8"])
            record = save_and_log(records, f"hmrc_ots_{key}.json", SOURCE, urls, key,
                                  pages=pages, timestamp=started)
            print(f"  saved {record['rows']:,} rows -> {record['file']}")
        except Exception as err:
            # Log the failure and carry on with the next mineral
            log_retrieval(SOURCE, f"{BASE_URL}/OTS", key, status=f"error: {err}", timestamp=started)
            print(f"  error: {err}")
            failed.append(key)

    if failed:
        raise SystemExit(f"failed: {', '.join(failed)}")  # non-zero exit, so automated runs show it


if __name__ == "__main__":
    main()
