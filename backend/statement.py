"""Build an income statement for a date range from the ledger."""

import datetime
from decimal import Decimal

from backend.ledger import Ledger


def account_amounts(
    ledger: Ledger, start: datetime.date, end: datetime.date
) -> dict[str, Decimal]:
    """Net amount per revenue and expense account, from posted entries dated from start
    to end, both included.

    Revenue accounts count credit minus debit, and expense accounts count debit minus
    credit, so an account's usual balance comes out positive. Asset, liability, and
    equity accounts are left out. Each entry's date is checked on its own, so the order
    of entries in the file does not matter. Accounts with no activity are not in the
    result.
    """
    amounts = {}
    for entry in ledger.entries:
        if entry.status != "posted":
            continue
        if not start <= entry.date <= end:
            continue
        for line in entry.lines:
            account = ledger.accounts[line.account]
            if account.type == "revenue":
                amount = line.credit - line.debit
            elif account.type == "expense":
                amount = line.debit - line.credit
            else:
                continue
            amounts[account.number] = amounts.get(account.number, Decimal("0.00")) + amount
    return amounts
