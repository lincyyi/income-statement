import datetime
from decimal import Decimal

import pytest

from backend.ledger import LEDGER_PATH, Account, Ledger, load_ledger
from backend.statement import (
    INCOME_STATEMENT_LAYOUT,
    IncomeStatement,
    StatementLine,
    StatementSection,
    account_amounts,
    build_income_statement,
)


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


def test_income_statement_for_q1_2026():
    ledger = load_ledger(LEDGER_PATH)

    statement = build_income_statement(
        ledger, datetime.date(2026, 1, 1), datetime.date(2026, 3, 31), INCOME_STATEMENT_LAYOUT
    )

    # Line amounts are the ones checked in test_account_amounts_for_q1_2026.
    assert statement == IncomeStatement(
        company="Northwind Coffee Roasters",
        currency="USD",
        start=datetime.date(2026, 1, 1),
        end=datetime.date(2026, 3, 31),
        sections=[
            StatementSection(
                key="revenue",
                name="Revenue",
                lines=[
                    StatementLine("4000", "Product Revenue", Decimal("35650.75")),
                    StatementLine("4100", "Subscription Revenue", Decimal("3000.00")),
                    StatementLine("4900", "Sales Returns & Discounts", Decimal("-800.25")),
                ],
                # 35650.75 + 3000.00 - 800.25
                total=Decimal("37850.50"),
            ),
            StatementSection(
                key="cost_of_goods_sold",
                name="Cost of goods sold",
                lines=[StatementLine("5000", "Cost of Goods Sold", Decimal("14272.75"))],
                total=Decimal("14272.75"),
            ),
            # 37850.50 - 14272.75
            StatementSection(
                key="gross_profit", name="Gross profit", lines=[], total=Decimal("23577.75")
            ),
            StatementSection(
                key="operating_expenses",
                name="Operating expenses",
                lines=[
                    StatementLine("6000", "Salaries", Decimal("55500.00")),
                    StatementLine("6100", "Rent", Decimal("9000.00")),
                    StatementLine("6200", "Software", Decimal("1099.97")),
                    StatementLine("6300", "Marketing (legacy)", Decimal("2500.10")),
                ],
                # 55500.00 + 9000.00 + 1099.97 + 2500.10
                total=Decimal("68100.07"),
            ),
            # 23577.75 - 68100.07
            StatementSection(
                key="operating_income",
                name="Operating income",
                lines=[],
                total=Decimal("-44522.32"),
            ),
            StatementSection(
                key="other_income",
                name="Other income",
                lines=[StatementLine("7000", "Interest Income", Decimal("42.18"))],
                total=Decimal("42.18"),
            ),
            # -44522.32 + 42.18
            StatementSection(
                key="net_income", name="Net income", lines=[], total=Decimal("-44480.14")
            ),
        ],
    )


def test_income_statement_for_january_keeps_rent_as_recorded():
    ledger = load_ledger(LEDGER_PATH)

    statement = build_income_statement(
        ledger, datetime.date(2026, 1, 1), datetime.date(2026, 1, 31), INCOME_STATEMENT_LAYOUT
    )

    operating_expenses = statement.sections[3]
    # JE-007 expensed all three months of rent on 2026-01-01. It is not spread.
    assert operating_expenses.lines[1] == StatementLine("6100", "Rent", Decimal("9000.00"))
    totals = {section.key: section.total for section in statement.sections}
    assert totals == {
        # JE-002 + JE-005 + no returns = 12450.75 + 1000.00 + 0.00
        "revenue": Decimal("13450.75"),
        # JE-003
        "cost_of_goods_sold": Decimal("4980.30"),
        # 13450.75 - 4980.30
        "gross_profit": Decimal("8470.45"),
        # JE-006 + JE-007 + no software + JE-008 = 18500.00 + 9000.00 + 0.00 + 2500.10
        "operating_expenses": Decimal("30000.10"),
        # 8470.45 - 30000.10
        "operating_income": Decimal("-21529.65"),
        "other_income": Decimal("0.00"),
        # -21529.65 + 0.00
        "net_income": Decimal("-21529.65"),
    }


def test_income_statement_lists_accounts_with_no_activity_as_zero():
    ledger = load_ledger(LEDGER_PATH)

    statement = build_income_statement(
        ledger, datetime.date(2026, 4, 1), datetime.date(2026, 4, 30), INCOME_STATEMENT_LAYOUT
    )

    lines = [
        (line.account, line.amount)
        for section in statement.sections
        for line in section.lines
    ]
    # JE-024 is the only entry in April.
    assert lines == [
        ("4000", Decimal("9100.00")),
        ("4100", Decimal("0.00")),
        ("4900", Decimal("0.00")),
        ("5000", Decimal("0.00")),
        ("6000", Decimal("0.00")),
        ("6100", Decimal("0.00")),
        ("6200", Decimal("0.00")),
        ("6300", Decimal("0.00")),
        ("7000", Decimal("0.00")),
    ]
    assert statement.sections[-1] == StatementSection(
        key="net_income", name="Net income", lines=[], total=Decimal("9100.00")
    )


def test_income_statement_rejects_a_subtype_no_section_lists():
    ledger = Ledger(
        company="Test Co",
        currency="USD",
        accounts={
            "8000": Account("8000", "Interest Expense", "expense", "other_expense", True),
        },
        entries=[],
    )

    with pytest.raises(ValueError, match="Account 8000 has subtype other_expense"):
        build_income_statement(
            ledger, datetime.date(2026, 1, 1), datetime.date(2026, 1, 31), INCOME_STATEMENT_LAYOUT
        )
