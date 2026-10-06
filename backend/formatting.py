"""Show amounts the way an accountant reads them."""

from decimal import Decimal


def format_amount(amount: Decimal) -> str:
    """Two decimals and thousands separators, with negatives in parentheses: (800.25).

    This is the only place an amount is rounded, and with two-decimal data it never
    changes a value. The absolute value is formatted first, so a negative zero shows as
    0.00, not (0.00) or -0.00.
    """
    text = f"{abs(amount):,.2f}"
    if amount < 0:
        return f"({text})"
    return text
