"""Fetch the full HMRC commodity lookup (CN8/HS codes and descriptions).

Run from the repo root:  python pipeline/fetch_commodity_lookup.py
Output:  data/raw/hmrc_commodity_lookup.json  (records saved untouched; overwritten on each run)
Logging: handled by retrieval.py (one line per run in data/raw/retrieval_log.jsonl)
"""

from datetime import datetime, timezone

import requests

from retrieval import log_retrieval, save_and_log

SOURCE = "HMRC uktradeinfo API - Commodity lookup"
START_URL = "https://api.uktradeinfo.com/Commodity"
FILENAME = "hmrc_commodity_lookup.json"


def fetch_all(url):
    """Request every page, following @odata.nextLink until the API stops sending one."""
    records, pages = [], 0
    while url:
        response = requests.get(url, timeout=60)
        response.raise_for_status()  # stop on HTTP errors instead of saving a broken file
        page = response.json()
        records.extend(page["value"])
        pages += 1
        print(f"page {pages}: {len(records)} rows so far")
        url = page.get("@odata.nextLink")
    return records, pages


def main():
    retrieved_at = datetime.now(timezone.utc)
    try:
        records, pages = fetch_all(START_URL)
        record = save_and_log(records, FILENAME, SOURCE, START_URL, "lookup",
                              pages=pages, timestamp=retrieved_at)
    except Exception as err:
        log_retrieval(SOURCE, START_URL, "lookup", status=f"error: {err}", timestamp=retrieved_at)
        print(f"error: {err}")
        raise SystemExit(1)  # non-zero exit, so automated runs show the failure

    print(f"success: {record['rows']} rows in {record['pages']} pages -> {record['file']}")


if __name__ == "__main__":
    main()
