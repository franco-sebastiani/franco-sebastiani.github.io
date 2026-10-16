"""Fetch the HMRC lookup tables needed to read the trade data.

Run from the repo root:  python pipeline/fetch_lookups.py
Output (data/raw/, saved untouched, overwritten on each run):
  hmrc_commodity_lookup.json  CN8/HS codes and descriptions
  hmrc_country_lookup.json    country IDs and names
  hmrc_flowtype_lookup.json   flow type IDs (EU/non-EU imports/exports)
Logging: one line per lookup in data/raw/retrieval_log.jsonl (via retrieval.py)
"""

from datetime import datetime, timezone

from hmrc_api import BASE_URL, fetch_all
from retrieval import log_retrieval, save_and_log

LOOKUPS = {
    # endpoint: (source label for the log, raw filename)
    "Commodity": ("HMRC uktradeinfo API - Commodity lookup", "hmrc_commodity_lookup.json"),
    "Country": ("HMRC uktradeinfo API - Country lookup", "hmrc_country_lookup.json"),
    "FlowType": ("HMRC uktradeinfo API - FlowType lookup", "hmrc_flowtype_lookup.json"),
}


def main():
    failed = []
    for endpoint, (source, filename) in LOOKUPS.items():
        print(endpoint)
        started = datetime.now(timezone.utc)
        try:
            records, pages, url = fetch_all(endpoint)
            record = save_and_log(records, filename, source, url, "lookup", pages=pages, timestamp=started)
            print(f"  saved {record['rows']:,} rows -> {record['file']}")
        except Exception as err:
            log_retrieval(source, f"{BASE_URL}/{endpoint}", "lookup", status=f"error: {err}", timestamp=started)
            print(f"  error: {err}")
            failed.append(endpoint)

    if failed:
        raise SystemExit(f"failed: {', '.join(failed)}")  # non-zero exit, so automated runs show it


if __name__ == "__main__":
    main()
