# Income statement

A small app that shows the income statement of Northwind Coffee Roasters for any date
range, built from `ledger.json` (copied unchanged from the take-home README).

## Versions

Tested on macOS 12.7 with Python 3.13.16.

| Package | Version | Used for |
| --- | --- | --- |
| fastapi | 0.142.2 | the API and serving the page |
| uvicorn | 0.54.0 | running the app |
| pytest | 9.1.1 | tests |
| pytest-cov | 7.1.0 | the coverage gate |
| httpx | 0.28.1 | HTTP calls in tests |

The same versions are pinned in `requirements.txt`. The frontend is one HTML page with
plain JavaScript, so it needs no build step and no Node.

## Setup

Run these from the repository root. If `python3 --version` shows an older Python, install
3.13 first, for example with `brew install python@3.13`.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

One command serves both the backend and the frontend:

```sh
uvicorn backend.app:app --reload
```

- Frontend: http://127.0.0.1:8000/ (opens on Q1 2026)
- API: http://127.0.0.1:8000/income-statement?start=2026-01-01&end=2026-03-31

If port 8000 is taken, add `--port 8001` and use that port in the URLs.

## Tests

```sh
pytest
```

The run fails if backend coverage (line and branch) is below 100%.
`tests/test_end_to_end.py` starts the app in its own uvicorn process and sends it
real HTTP requests.

## Code

- `backend/ledger.py`: loads `ledger.json` and rejects unbalanced entries or unknown
  accounts.
- `backend/statement.py`: `INCOME_STATEMENT_LAYOUT` defines the statement, and
  `build_income_statement` builds it for a date range.
- `backend/formatting.py`: formats amounts for an accountant.
- `backend/app.py`: the API and the page.
- `frontend/index.html`: date inputs, and the statement as the API returns it.
