from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_income_statement_for_q1_2026():
    response = client.get("/income-statement?start=2026-01-01&end=2026-03-31")

    # The numbers are the ones checked in test_income_statement_for_q1_2026 in
    # test_statement.py, formatted by format_amount.
    assert response.status_code == 200
    assert response.json() == {
        "company": "Northwind Coffee Roasters",
        "currency": "USD",
        "start": "2026-01-01",
        "end": "2026-03-31",
        "sections": [
            {
                "key": "revenue",
                "name": "Revenue",
                "lines": [
                    {"account": "4000", "name": "Product Revenue", "amount": "35,650.75"},
                    {"account": "4100", "name": "Subscription Revenue", "amount": "3,000.00"},
                    {"account": "4900", "name": "Sales Returns & Discounts", "amount": "(800.25)"},
                ],
                "total": "37,850.50",
            },
            {
                "key": "cost_of_goods_sold",
                "name": "Cost of goods sold",
                "lines": [
                    {"account": "5000", "name": "Cost of Goods Sold", "amount": "14,272.75"},
                ],
                "total": "14,272.75",
            },
            {"key": "gross_profit", "name": "Gross profit", "lines": [], "total": "23,577.75"},
            {
                "key": "operating_expenses",
                "name": "Operating expenses",
                "lines": [
                    {"account": "6000", "name": "Salaries", "amount": "55,500.00"},
                    {"account": "6100", "name": "Rent", "amount": "9,000.00"},
                    {"account": "6200", "name": "Software", "amount": "1,099.97"},
                    {"account": "6300", "name": "Marketing (legacy)", "amount": "2,500.10"},
                ],
                "total": "68,100.07",
            },
            {
                "key": "operating_income",
                "name": "Operating income",
                "lines": [],
                "total": "(44,522.32)",
            },
            {
                "key": "other_income",
                "name": "Other income",
                "lines": [
                    {"account": "7000", "name": "Interest Income", "amount": "42.18"},
                ],
                "total": "42.18",
            },
            {"key": "net_income", "name": "Net income", "lines": [], "total": "(44,480.14)"},
        ],
    }


def test_start_equal_to_end_is_one_day():
    response = client.get("/income-statement?start=2026-01-01&end=2026-01-01")

    # Only JE-007 (rent, 9000.00) is dated 2026-01-01: 0.00 - 0.00 - 9000.00 + 0.00
    assert response.status_code == 200
    assert response.json()["sections"][-1]["total"] == "(9,000.00)"


def test_rejects_a_missing_date():
    response = client.get("/income-statement?start=2026-01-01")

    assert response.status_code == 422
    assert response.json() == {"detail": "end is required"}


def test_lists_every_missing_date():
    response = client.get("/income-statement")

    assert response.status_code == 422
    assert response.json() == {"detail": "start is required; end is required"}


def test_rejects_a_date_not_in_yyyy_mm_dd_form():
    # 1767225600 is 2026-01-01 as a Unix timestamp.
    response = client.get("/income-statement?start=1767225600&end=2026-03-31")

    assert response.status_code == 422
    assert response.json() == {"detail": "start must be a date in YYYY-MM-DD form"}


def test_rejects_a_date_that_does_not_exist():
    response = client.get("/income-statement?start=2026-02-30&end=2026-03-31")

    assert response.status_code == 422
    assert response.json() == {"detail": "2026-02-30 is not a valid date"}


def test_rejects_start_after_end():
    response = client.get("/income-statement?start=2026-03-31&end=2026-01-01")

    assert response.status_code == 422
    assert response.json() == {"detail": "start must be on or before end"}


def test_serves_the_frontend_page():
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "<title>Income statement</title>" in response.text
