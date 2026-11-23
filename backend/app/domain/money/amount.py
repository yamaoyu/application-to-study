from decimal import Decimal

MONEY_QUNATUM = Decimal("0.01")


def round_money_amount(amount: Decimal) -> Decimal:
    return amount.quantize(MONEY_QUNATUM)
