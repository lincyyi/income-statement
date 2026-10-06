import datetime
from decimal import Decimal

from backend.ledger import LEDGER_PATH, Account, JournalLine, load_ledger


def test_loads_company_accounts_and_entries():
    ledger = load_ledger(LEDGER_PATH)

    assert ledger.company == "Northwind Coffee Roasters"
    assert ledger.currency == "USD"
    assert len(ledger.accounts) == 15
    assert len(ledger.entries) == 25


def test_accounts_are_keyed_by_number_in_chart_order():
    ledger = load_ledger(LEDGER_PATH)

    assert list(ledger.accounts)[0] == "1000"
    assert list(ledger.accounts)[-1] == "7000"
    assert ledger.accounts["6300"] == Account(
        number="6300",
        name="Marketing (legacy)",
        type="expense",
        subtype="operating_expense",
        is_active=False,
    )


def test_entry_has_a_date_and_exact_decimal_amounts():
    ledger = load_ledger(LEDGER_PATH)
    entry = next(entry for entry in ledger.entries if entry.id == "JE-016")

    assert entry.date == datetime.date(2026, 3, 2)
    assert entry.status == "posted"
    assert entry.lines == [
        JournalLine(account="1100", debit=Decimal("14850.00"), credit=Decimal("0.00")),
        JournalLine(account="4900", debit=Decimal("150.00"), credit=Decimal("0.00")),
        JournalLine(account="4000", debit=Decimal("0.00"), credit=Decimal("15000.00")),
    ]
