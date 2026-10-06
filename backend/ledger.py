"""Load the chart of accounts and the journal entries from ledger.json."""

import datetime
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

LEDGER_PATH = Path(__file__).resolve().parent.parent / "ledger.json"


@dataclass
class Account:
    """One account in the chart of accounts. Journal lines refer to it by number."""

    number: str
    name: str
    type: str
    subtype: str
    is_active: bool


@dataclass
class JournalLine:
    """One debit or one credit to one account. The other amount is zero."""

    account: str
    debit: Decimal
    credit: Decimal


@dataclass
class JournalEntry:
    """One recorded business event, with an accounting date and two or more lines."""

    id: str
    date: datetime.date
    status: str
    memo: str
    lines: list[JournalLine]


@dataclass
class Ledger:
    """The company's books: accounts keyed by number in chart order, and every entry."""

    company: str
    currency: str
    accounts: dict[str, Account]
    entries: list[JournalEntry]


def load_ledger(path: Path) -> Ledger:
    """Read a ledger file. Amounts become Decimal and dates become datetime.date."""
    data = json.loads(path.read_text())
    accounts = {}
    for account in data["accounts"]:
        accounts[account["number"]] = Account(
            number=account["number"],
            name=account["name"],
            type=account["type"],
            subtype=account["subtype"],
            is_active=account["is_active"],
        )
    entries = []
    for entry in data["journal_entries"]:
        lines = []
        for line in entry["lines"]:
            lines.append(
                JournalLine(
                    account=line["account"],
                    debit=Decimal(line["debit"]),
                    credit=Decimal(line["credit"]),
                )
            )
        entries.append(
            JournalEntry(
                id=entry["id"],
                date=datetime.date.fromisoformat(entry["date"]),
                status=entry["status"],
                memo=entry["memo"],
                lines=lines,
            )
        )
    return Ledger(
        company=data["company"],
        currency=data["currency"],
        accounts=accounts,
        entries=entries,
    )
