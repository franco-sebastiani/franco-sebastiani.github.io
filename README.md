# franco-sebastiani.github.io

Portfolio for PP434 Automated Data Visualisation for Policymaking (LSE), published with GitHub Pages at
https://franco-sebastiani.github.io. The final project examines UK critical minerals supply dependence,
measured against the UK Critical Minerals Strategy (Vision 2035).

## Repository layout

| Path | Contents |
| --- | --- |
| `index.html` | Hub page linking to each weekly assignment and the final project |
| `weekly_assignments/` | One page per weekly assignment |
| `final_project.html` | Final project page |
| `assets/` | Shared stylesheet and site icons |
| `specs/` | Vega-Lite chart specifications |
| `config/minerals.toml` | The 38 UK critical and growth minerals with their HS (CN8) codes |
| `pipeline/` | Scripts that retrieve the data |
| `data/raw/` | Raw data as retrieved (kept local, not committed) and the retrieval log |
| `data/processed/` | Processed data the charts load |
| `notebooks/` | Exploratory notebooks |

## Data sources

- **HMRC Overseas Trade Statistics**, via the [uktradeinfo API](https://www.uktradeinfo.com/api-documentation/).
- **Critical Minerals technical annex** (Department for Business and Trade): mineral lists from Annex 1 and HS code
  definitions from Annex 5, Table 3, transcribed into `config/minerals.toml`. Open Government Licence v3.0.

## Reproducing the data

Raw data is not committed to this repository. It is rebuilt by running the pipeline scripts. Requires Python 3.11+
(check with `python3 --version` before creating the environment).

```
python3 -m venv .venv --prompt pp434
source .venv/bin/activate
pip install -r requirements.txt
python pipeline/fetch_commodity_lookup.py
```

Every pipeline retrieval appends a line to `data/raw/retrieval_log.jsonl` (committed) with the timestamp, source,
query URL, row and page counts, and a SHA-256 hash of the saved file. Rerunning a script and comparing hashes shows
whether the source data has changed since the original pull. Saving and logging are handled by the shared module
`pipeline/retrieval.py`, which every pipeline script uses.
