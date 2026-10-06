import datetime
import json
from decimal import Decimal

import pytest

from backend.ledger import LEDGER_PATH, Account, JournalLine, load_ledger


def write_one_entry_ledger(tmp_path, lines):
    data = {
        "company": "Test Co",
        "currency": "USD",
        "accounts": [
            {"number": "1000", "name": "Cash", "type": "asset",
             "subtype": "balance_sheet", "is_active": True},
            {"number": "4000", "name": "Product Revenue", "type": "revenue",
             "subtype": "operating_revenue", "is_active": True},
        ],
        "journal_entries": [
            {"id": "JE-1", "date": "2026-01-01", "status": "posted", "memo": "Test",
             "lines": lines},
        ],
    }
    path = tmp_path / "ledger.json"
    path.write_text(json.dumps(data))
    return path


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


def test_rejects_an_entry_that_does_not_balance(tmp_path):
    path = write_one_entry_ledger(tmp_path, [
        {"account": "1000", "debit": "100.00", "credit": "0.00"},
        {"account": "4000", "debit": "0.00", "credit": "90.00"},
    ])

    with pytest.raises(ValueError, match="JE-1 does not balance: debits 100.00, credits 90.00"):
        load_ledger(path)


def test_rejects_a_line_with_an_unknown_account(tmp_path):
    path = write_one_entry_ledger(tmp_path, [
        {"account": "1000", "debit": "100.00", "credit": "0.00"},
        {"account": "9999", "debit": "0.00", "credit": "100.00"},
    ])

    with pytest.raises(ValueError, match="JE-1 uses unknown account 9999"):
        load_ledger(path)
