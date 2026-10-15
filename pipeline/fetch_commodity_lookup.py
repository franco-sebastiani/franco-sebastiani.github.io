"""Fetch the full HMRC commodity lookup (CN8/HS codes and descriptions).

Run from the repo root:  python pipeline/fetch_commodity_lookup.py
Output: data/raw/hmrc_commodity_lookup.json  (records saved untouched; overwritten on each run)
Log:    data/raw/retrieval_log.jsonl  (one line appended per run, success or failure,
        with a SHA-256 hash identifying the exact file version saved)
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

# Paths are built from this file's location, so the script works from any folder
REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
LOG_FILE = RAW_DIR / "retrieval_log.jsonl"

SOURCE = "HMRC uktradeinfo API - Commodity lookup"
START_URL = "https://api.uktradeinfo.com/Commodity"


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
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_file = RAW_DIR / "hmrc_commodity_lookup.json"

    records, pages, status, sha256 = [], 0, "success", None
    try:
        records, pages = fetch_all(START_URL)
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=1)
        # Fingerprint of the saved file: matches it to a git commit and shows when the data changed
        sha256 = hashlib.sha256(out_file.read_bytes()).hexdigest()
    except Exception as err:
        status = f"error: {err}"

    log_record = {
        "timestamp": retrieved_at.isoformat(),
        "source": SOURCE,
        "url": START_URL,
        "mineral": "lookup",
        "file": str(out_file.relative_to(REPO_ROOT)) if status == "success" else None,
        "rows": len(records),
        "pages": pages,
        "sha256": sha256,
        "status": status,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_record) + "\n")

    print(f"{status}: {len(records)} rows in {pages} pages")


if __name__ == "__main__":
    main()
