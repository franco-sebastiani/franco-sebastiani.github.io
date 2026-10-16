"""Shared helpers for pipeline scripts: save raw data untouched and log every retrieval.

Every pipeline script that writes to data/raw/ goes through save_and_log() (or
log_retrieval() when a retrieval fails), so the retrieval log is complete and every
line has the same fields.

Log: data/raw/retrieval_log.jsonl (JSON Lines: one record per retrieval, never edited)
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

# Paths are built from this file's location, so scripts work from any folder
REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
LOG_FILE = RAW_DIR / "retrieval_log.jsonl"


def log_retrieval(source, url, mineral, file=None, rows=0, pages=0, sha256=None,
                  status="success", timestamp=None):
    """Append one record to the retrieval log and return it."""
    record = {
        "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat(),
        "source": source,
        "url": url,
        "mineral": mineral,
        "file": str(Path(file).relative_to(REPO_ROOT)) if file else None,
        "rows": rows,
        "pages": pages,
        "sha256": sha256,
        "status": status,
    }
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record


def save_and_log(records, filename, source, url, mineral, pages=0, timestamp=None):
    """Save records to data/raw/<filename> exactly as received, hash the file, and log it."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_file = RAW_DIR / filename
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=1)
    # Fingerprint of the saved file: matches it to a git commit and shows when the data changed
    sha256 = hashlib.sha256(out_file.read_bytes()).hexdigest()
    return log_retrieval(source, url, mineral, file=out_file, rows=len(records), pages=pages,
                         sha256=sha256, timestamp=timestamp)
