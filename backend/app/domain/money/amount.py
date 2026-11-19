from decimal import Decimal


def round_money_amount(amount: Decimal) -> Decimal:
    return round(amount, 2)
