# Income statement take-home

Spec: https://github.com/Campfire-eng/income-statement-take-home (README.md and
ACCOUNTING_PRIMER.md). The data is `ledger.json`, copied unchanged from the README.
Time limit: 2 hours. The user will later change this code by hand without AI, so keep it
small and plain.

## Stack

- Python 3.13, FastAPI, pytest, pytest-cov.
- Backend: `backend/`. Frontend: one static `frontend/index.html` with plain JS, served by
  the same FastAPI app at `/`.
- Money is `decimal.Decimal`, parsed from the JSON strings. Never `float`.
- The API returns each amount only as a string formatted for an accountant, such as
  `"35,650.75"`, `"(800.25)"` and `"0.00"`. One backend function does this, at the API
  boundary. The statement code works only in `Decimal`.

## How we work

- One change per commit. Every commit includes its tests and keeps backend coverage at
  100%, line and branch. Run `pytest` before proposing a commit. The frontend has no
  tests; the user checks it by hand in the browser.
- The user reviews every commit. Do not commit until they say so.
- The user checks every number by hand before a test uses it. When you add an expected
  amount to a test, show the arithmetic it came from (for example `12450.75 + 8200.00 +
  15000.00 = 35650.75`) in the message or in a short comment.
- Tests for the numbers run on `ledger.json`, with the ranges the user has checked by hand:
  Q1 2026 line by line, January, April, and the single day 2026-01-01 (JE-007 is out of
  date order in the file). Use a small inline ledger only for a case the
  real data can't show, such as an unbalanced entry.
- All logic lives in the backend. The frontend only sends the dates, calls the API, and
  shows what comes back. No sums, signs, sorting, or number formatting in JS.
- Spell things out: name the rule in the code (for example `INCOME_STATEMENT_LAYOUT`)
  instead of hiding it in a clever expression. Don't repeat yourself.
- Section names and their order are not hard-coded anywhere but the layout. The code, the
  API, and the frontend walk the list of sections.
- Every class gets a docstring.
- No features beyond the README list. No database, auth, Docker, or styling work.
- When AI gets something wrong, note it for the "Where AI helped" part of `NOTES.md`.

## Accounting rules the code follows

- Loading fails if any entry, whatever its status, doesn't balance or has a line with an
  unknown account.
- Only `posted` entries count. `draft` and `void` are ignored.
- The date range includes both `start` and `end`. Don't assume entries are sorted by date.
- The amount on a line is `credit - debit` for `type: revenue` and `debit - credit` for
  `type: expense`. The type sets the sign; the subtype sets the section.
- `INCOME_STATEMENT_LAYOUT` in `backend/statement.py` defines the statement, top to bottom.
  An `AccountSection` lists the accounts of its subtypes. A `DerivedSection` (gross profit,
  operating income, net income) adds and subtracts the totals of sections above it.
  Sections refer to each other by `key` (such as `operating_income`), never by the
  display `name`.
- `balance_sheet` accounts are left out. A subtype that no section lists raises an error
  instead of being skipped.
- Each section lists every account with a matching subtype, active or not, in
  chart-of-accounts order. An account with no activity in the range shows 0.00.
- Report entries as recorded. Don't spread prepaid rent or re-accrue anything.

## Commit plan

About 85 minutes, which leaves a buffer inside the 2 hours.

1. Scaffold: `git init`, `ledger.json`, `pyproject.toml` with the coverage gate, README
   stub, `.gitignore`, this file. (5 min)
2. Load the ledger into dataclasses (`Decimal`, `date`). (10)
3. Load-time validation: balanced entries, known accounts. (5)
4. `account_amounts`: posted only, inclusive dates, sign by type. (15)
5. `build_income_statement` from `INCOME_STATEMENT_LAYOUT`: account sections with 0.00
   rows, and derived sections. (15)
6. `format_amount`: thousands separators, two decimals, negatives in parentheses. (5)
7. `GET /income-statement`, with 422 for missing, malformed, or reversed dates. (10)
8. Frontend page at `/`. (10)
9. README commands and versions, and `NOTES.md`. (10)

At 1h45 on the clock, stop coding and write `NOTES.md`, listing what's left.

## Commands

- Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- Tests: `.venv/bin/pytest` (fails below 100% backend coverage)
- Run the app: added in commit 7.
