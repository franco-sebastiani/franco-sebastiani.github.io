"""Helpers for the HMRC uktradeinfo API (OData): pagination, retries and batched code filters.

Anything specific to this API lives here, so every HMRC fetch script behaves the same way.
"""

import time

import requests

BASE_URL = "https://api.uktradeinfo.com"
MAX_FILTER_CODES = 10  # filters with many more 'or' clauses are rejected with 400 Bad Request
RETRIES = 3
PAUSE = 0.5  # seconds between page requests, to be gentle with the API


def get_with_retries(url, params=None, timeout=120):
    """GET a URL, retrying network errors, rate limits (429) and server errors (5xx)."""
    for attempt in range(1, RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout) as err:
            problem = str(err)
        else:
            if response.status_code != 429 and response.status_code < 500:
                response.raise_for_status()  # other 4xx: the request itself is wrong, retrying won't help
                return response
            problem = f"HTTP {response.status_code}"
        if attempt == RETRIES:
            raise RuntimeError(f"gave up after {RETRIES} attempts: {problem} ({url})")
        wait = 10 * attempt
        print(f"  {problem}; retrying in {wait}s")
        time.sleep(wait)


def fetch_all(path, params=None):
    """Request every page of an endpoint, following @odata.nextLink.

    Returns the records, the number of pages and the exact first URL requested (for the log).
    """
    response = get_with_retries(f"{BASE_URL}/{path}", params=params)
    first_url = response.url  # includes the encoded query, so the log shows exactly what was asked
    records, pages = [], 0
    while True:
        page = response.json()
        records.extend(page["value"])
        pages += 1
        print(f"  page {pages}: {len(records):,} rows so far")
        next_url = page.get("@odata.nextLink")
        if not next_url:
            return records, pages, first_url
        time.sleep(PAUSE)
        response = get_with_retries(next_url)


def code_batches(codes, size=MAX_FILTER_CODES):
    """Yield OData filter clauses covering at most `size` commodity codes each."""
    for i in range(0, len(codes), size):
        yield " or ".join(f"CommodityId eq {int(c)}" for c in codes[i:i + size])
