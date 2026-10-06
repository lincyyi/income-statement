# Income statement

A small app that shows the income statement of Northwind Coffee Roasters for any date
range, built from `ledger.json`.

Python 3.13.16. Package versions are pinned in `requirements.txt`.

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```sh
uvicorn backend.app:app --reload
```

Then open http://127.0.0.1:8000/income-statement?start=2026-01-01&end=2026-03-31

## Tests

```sh
pytest
```

The run fails if backend coverage (line and branch) is below 100%.
