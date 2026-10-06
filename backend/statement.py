"""Build an income statement for a date range from the ledger."""

import datetime
from dataclasses import dataclass
from decimal import Decimal

from backend.ledger import Account, Ledger

BALANCE_SHEET_SUBTYPE = "balance_sheet"


@dataclass
class StatementLine:
    """One account's amount for the period."""

    account: str
    name: str
    amount: Decimal


@dataclass
class StatementSection:
    """One section as it appears on the statement. A derived section has no lines."""

    key: str
    name: str
    lines: list[StatementLine]
    total: Decimal


@dataclass
class AccountSection:
    """A section that lists every account whose subtype is in `subtypes`, and their total.
    `key` identifies the section in code; `name` is only what the statement shows."""

    key: str
    name: str
    subtypes: list[str]

    def build(
        self, accounts: dict[str, Account], amounts: dict[str, Decimal]
    ) -> StatementSection:
        """One line per matching account, in chart order, with 0.00 for an account that
        has no amount."""
        lines = []
        for account in accounts.values():
            if account.subtype in self.subtypes:
                amount = amounts.get(account.number, Decimal("0.00"))
                lines.append(
                    StatementLine(account=account.number, name=account.name, amount=amount)
                )
        total = sum((line.amount for line in lines), Decimal("0.00"))
        return StatementSection(key=self.key, name=self.name, lines=lines, total=total)


@dataclass
class DerivedSection:
    """A section calculated from earlier sections: the totals of the sections keyed in
    `add`, minus those keyed in `subtract`. `name` is only what the statement shows."""

    key: str
    name: str
    add: list[str]
    subtract: list[str]

    def build(self, totals: dict[str, Decimal]) -> StatementSection:
        """`totals` holds the total of every earlier section, by section key."""
        added = sum((totals[key] for key in self.add), Decimal("0.00"))
        subtracted = sum((totals[key] for key in self.subtract), Decimal("0.00"))
        return StatementSection(
            key=self.key, name=self.name, lines=[], total=added - subtracted
        )


# The income statement, top to bottom. A derived section can only use sections above it.
INCOME_STATEMENT_LAYOUT = [
    AccountSection(
        key="revenue",
        name="Revenue",
        subtypes=["operating_revenue", "contra_revenue"],
    ),
    AccountSection(
        key="cost_of_goods_sold",
        name="Cost of goods sold",
        subtypes=["cogs"],
    ),
    DerivedSection(
        key="gross_profit",
        name="Gross profit",
        add=["revenue"],
        subtract=["cost_of_goods_sold"],
    ),
    AccountSection(
        key="operating_expenses",
        name="Operating expenses",
        subtypes=["operating_expense"],
    ),
    DerivedSection(
        key="operating_income",
        name="Operating income",
        add=["gross_profit"],
        subtract=["operating_expenses"],
    ),
    AccountSection(
        key="other_income",
        name="Other income",
        subtypes=["other_income"],
    ),
    DerivedSection(
        key="net_income",
        name="Net income",
        add=["operating_income", "other_income"],
        subtract=[],
    ),
]


@dataclass
class IncomeStatement:
    """The statement for one date range, with its sections in layout order."""

    company: str
    currency: str
    start: datetime.date
    end: datetime.date
    sections: list[StatementSection]


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


def build_income_statement(
    ledger: Ledger,
    start: datetime.date,
    end: datetime.date,
    layout: list[AccountSection | DerivedSection],
) -> IncomeStatement:
    """The income statement from start to end, both included, built section by section
    in layout order."""
    check_every_subtype_has_a_section(ledger, layout)
    amounts = account_amounts(ledger, start, end)
    sections = []
    totals = {}
    for definition in layout:
        if isinstance(definition, AccountSection):
            section = definition.build(ledger.accounts, amounts)
        else:
            section = definition.build(totals)
        sections.append(section)
        totals[section.key] = section.total
    return IncomeStatement(
        company=ledger.company,
        currency=ledger.currency,
        start=start,
        end=end,
        sections=sections,
    )


def check_every_subtype_has_a_section(
    ledger: Ledger, layout: list[AccountSection | DerivedSection]
) -> None:
    """Raise ValueError if an account's subtype is neither balance_sheet nor listed by an
    account section, so that no account silently drops off the statement."""
    known_subtypes = {BALANCE_SHEET_SUBTYPE}
    for definition in layout:
        if isinstance(definition, AccountSection):
            known_subtypes.update(definition.subtypes)
    for account in ledger.accounts.values():
        if account.subtype not in known_subtypes:
            raise ValueError(
                f"Account {account.number} has subtype {account.subtype}, "
                "which no section of the statement lists"
            )
