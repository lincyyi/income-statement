from decimal import Decimal

import pytest

from backend.formatting import format_amount


@pytest.mark.parametrize(
    "amount, expected",
    [
        (Decimal("35650.75"), "35,650.75"),
        (Decimal("-800.25"), "(800.25)"),
        (Decimal("-44480.14"), "(44,480.14)"),
        (Decimal("42.18"), "42.18"),
        (Decimal("0.00"), "0.00"),
        # Zero without decimals still shows two.
        (Decimal("0"), "0.00"),
        # Multiplying 0.00 by -1 gives a negative zero.
        (Decimal("-0.00"), "0.00"),
    ],
)
def test_format_amount(amount, expected):
    assert format_amount(amount) == expected
