# Notes

## Q1 2026 net income

**(44,480.14)**, a net loss, for 2026-01-01 to 2026-03-31.

## Decisions and assumptions

- Only `posted` entries count. This leaves out the void duplicate JE-009, the draft bonus
  JE-019, and the void JE-025.
- Both dates are included. Entries are filtered by date, never by their order in the file
  (JE-007 and JE-025 are out of order).
- The account type sets the sign: credit − debit for revenue, debit − credit for expense.
  The subtype sets the section, so Interest Income (type revenue) goes under Other income.
- Contra revenue (4900) is a negative line inside Revenue, so the Revenue total is net
  revenue.
- Entries are reported as recorded: all three months of rent (JE-007) land on Jan 1, and
  the annual subscription billing (JE-004) is deferred revenue, not revenue.
- The inactive account 6300 still shows its history. Every income statement account is
  listed for every range, with 0.00 when it has no activity.
- Net income = operating income + other income. The data has no other-expense subtype.
- Loading fails if any entry, whatever its status, doesn't balance or uses an unknown
  account, or if an account's subtype has no section.
- Amounts are `Decimal` from start to finish. The API returns them formatted for an
  accountant, such as `(800.25)`, so the page does no math or formatting.
- Dates must be `YYYY-MM-DD`. A missing date, a malformed one, or a start after the end
  gets a 422 with a plain message.
- The statement is defined as a list of sections in `backend/statement.py`. Gross profit,
  operating income, and net income list the sections they are built from as lines.

## How I checked the numbers

- Worked out Q1 by hand, line by line, entry by entry. The AI did the same separately,
  plus a script with exact decimals, and the results matched.
- Cross-check: January + February + March = −21,529.65 − 13,230.25 − 9,720.24 =
  −44,480.14, the Q1 figure.
- Every expected number was checked by hand before a test used it. The tests run on the
  real ledger for Q1, January, April, and the single day 2026-01-01. Each data trap
  changes a specific line: counting the void duplicate, the draft, an exclusive end date,
  a flipped contra sign, and so on.
- 100% line and branch coverage, plus end-to-end tests against a running server, and the
  page checked by hand in the browser.

## AI

**Where it helped:** reading the spec and listing the data traps, recomputing the numbers
independently, scaffolding, writing tests, and catching a negative-zero formatting case.

**Where it got something wrong:**

- Its first design hard-coded the sections, then linked them by display name. I asked
  for a section layout and separate keys.
- FastAPI's built-in date type accepted `start=0` as 1970-01-01. It now accepts only
  `YYYY-MM-DD`.
- FastAPI's own errors and ours came back in two shapes. Every error is now one string.
- While splitting commits, the page's bold and spacing styles were left out. I found
  this in the browser after being told it was done.

**Where I did not trust it:** I checked every number and test assertion by hand, asked
whether the unordered dates were covered (which added the 2026-01-01 test), had it run
the real server instead of relying on unit tests, checked the page myself, and reviewed
every commit.

## Next, with more time

- Validate that each account's subtype fits its type, and reject amounts with more than
  two decimals.
- Drill down from an account line to its journal entries.
- Compare two periods side by side.
- A small browser test for the page.
