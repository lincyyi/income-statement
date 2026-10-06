"""End to end: start the app in its own uvicorn process, the way the README runs it, and
send it real HTTP requests.

Coverage does not see code run in that process. test_app.py covers the same code in
process.
"""

import socket
import subprocess
import sys
import time

import httpx
import pytest

from backend.ledger import LEDGER_PATH

REPO_ROOT = LEDGER_PATH.parent


@pytest.fixture(scope="module")
def server():
    """An HTTP client for the app running in its own uvicorn process."""
    port = free_port()
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app:app", "--port", str(port)],
        cwd=REPO_ROOT,
    )
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{port}") as client:
            wait_until_up(client)
            yield client
    finally:
        process.terminate()
        process.wait()


def free_port() -> int:
    """A TCP port nothing is listening on, so the test never clashes with a running app."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_until_up(client: httpx.Client) -> None:
    """Return once the server answers, or raise after 10 seconds."""
    deadline = time.monotonic() + 10
    while True:
        try:
            client.get("/docs")
            return
        except httpx.ConnectError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.1)


def section_totals(response: httpx.Response) -> dict[str, str]:
    """Each section's total in the response, by section key."""
    return {section["key"]: section["total"] for section in response.json()["sections"]}


def test_q1_2026(server):
    response = server.get("/income-statement?start=2026-01-01&end=2026-03-31")

    # The totals checked in test_income_statement_for_q1_2026 in test_statement.py.
    assert response.status_code == 200
    assert section_totals(response) == {
        "revenue": "37,850.50",
        "cost_of_goods_sold": "14,272.75",
        "gross_profit": "23,577.75",
        "operating_expenses": "68,100.07",
        "operating_income": "(44,522.32)",
        "other_income": "42.18",
        "net_income": "(44,480.14)",
    }


def test_single_day_2026_01_01(server):
    response = server.get("/income-statement?start=2026-01-01&end=2026-01-01")

    # Only JE-007 (rent, 9000.00) is dated 2026-01-01.
    assert response.status_code == 200
    assert section_totals(response) == {
        "revenue": "0.00",
        "cost_of_goods_sold": "0.00",
        "gross_profit": "0.00",
        "operating_expenses": "9,000.00",
        # 0.00 - 9000.00
        "operating_income": "(9,000.00)",
        "other_income": "0.00",
        "net_income": "(9,000.00)",
    }


def test_april_2026(server):
    response = server.get("/income-statement?start=2026-04-01&end=2026-04-30")

    # Only JE-024 (product sales, 9100.00) is dated in April.
    assert response.status_code == 200
    assert section_totals(response) == {
        "revenue": "9,100.00",
        "cost_of_goods_sold": "0.00",
        "gross_profit": "9,100.00",
        "operating_expenses": "0.00",
        "operating_income": "9,100.00",
        "other_income": "0.00",
        "net_income": "9,100.00",
    }


@pytest.mark.parametrize(
    "query",
    [
        "start=2026-01-01",
        "start=0&end=2026-03-31",
        "start=2026-02-30&end=2026-03-31",
        "start=2026-03-31&end=2026-01-01",
    ],
)
def test_rejects_bad_dates(server, query):
    response = server.get(f"/income-statement?{query}")

    assert response.status_code == 422
