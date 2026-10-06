import datetime
from decimal import Decimal

from backend.ledger import LEDGER_PATH, load_ledger
from backend.statement import account_amounts


def test_account_amounts_for_q1_2026():
    ledger = load_ledger(LEDGER_PATH)

    amounts = account_amounts(ledger, datetime.date(2026, 1, 1), datetime.date(2026, 3, 31))

    assert amounts == {
        # JE-002 + JE-010 + JE-016 = 12450.75 + 8200.00 + 15000.00 (void JE-009 left out)
        "4000": Decimal("35650.75"),
        # JE-005 + JE-014 + JE-021 = 1000.00 * 3
        "4100": Decimal("3000.00"),
        # contra revenue, debits: -(JE-012 + JE-016) = -(650.25 + 150.00)
        "4900": Decimal("-800.25"),
        # JE-003 + JE-011 + JE-017 = 4980.30 + 3280.00 + 6012.45
        "5000": Decimal("14272.75"),
        # JE-006 + JE-015 + JE-022 = 18500.00 * 3 (draft JE-019 left out)
        "6000": Decimal("55500.00"),
        # JE-007 on the start date
        "6100": Decimal("9000.00"),
        # JE-018 - JE-020 = 1199.97 - 100.00 (vendor credit)
        "6200": Decimal("1099.97"),
        # JE-008, inactive account
        "6300": Decimal("2500.10"),
        # JE-023 on the end date
        "7000": Decimal("42.18"),
    }


def test_account_amounts_does_not_rely_on_entry_order():
    ledger = load_ledger(LEDGER_PATH)

    # JE-007 is the only entry dated 2026-01-01, and it is listed after JE-002 (2026-01-05).
    amounts = account_amounts(ledger, datetime.date(2026, 1, 1), datetime.date(2026, 1, 1))

    assert amounts == {"6100": Decimal("9000.00")}
