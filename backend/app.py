"""The web app: serves the income statement for a date range as JSON."""

import datetime
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query

from backend.formatting import format_amount
from backend.ledger import LEDGER_PATH, load_ledger
from backend.statement import (
    INCOME_STATEMENT_LAYOUT,
    IncomeStatement,
    build_income_statement,
)

LEDGER = load_ledger(LEDGER_PATH)

app = FastAPI()


# Only YYYY-MM-DD. FastAPI's own date type would also accept Unix timestamps such as 0.
DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"


@app.get("/income-statement")
def get_income_statement(
    start: Annotated[str, Query(pattern=DATE_PATTERN)],
    end: Annotated[str, Query(pattern=DATE_PATTERN)],
) -> dict:
    """The income statement from start to end, both included. FastAPI answers 422 when a
    date is missing or not in YYYY-MM-DD form."""
    start_date = parse_date(start)
    end_date = parse_date(end)
    if start_date > end_date:
        raise HTTPException(status_code=422, detail="start must be on or before end")
    statement = build_income_statement(LEDGER, start_date, end_date, INCOME_STATEMENT_LAYOUT)
    return statement_to_json(statement)


def parse_date(text: str) -> datetime.date:
    """A YYYY-MM-DD string as a date. Answers 422 for a date that does not exist, such as
    2026-02-30."""
    try:
        return datetime.date.fromisoformat(text)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"{text} is not a valid date")


def statement_to_json(statement: IncomeStatement) -> dict:
    """The statement as JSON, with every amount formatted for an accountant."""
    sections = []
    for section in statement.sections:
        lines = []
        for line in section.lines:
            lines.append(
                {
                    "account": line.account,
                    "name": line.name,
                    "amount": format_amount(line.amount),
                }
            )
        sections.append(
            {
                "key": section.key,
                "name": section.name,
                "lines": lines,
                "total": format_amount(section.total),
            }
        )
    return {
        "company": statement.company,
        "currency": statement.currency,
        "start": statement.start.isoformat(),
        "end": statement.end.isoformat(),
        "sections": sections,
    }
