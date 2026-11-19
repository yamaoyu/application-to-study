"""
返却する金額を小数点第2位で統一する
"""


from decimal import Decimal
from typing import Annotated

from pydantic import Field, PlainSerializer


def serialize_modey(value: Decimal):
    return format(value.quantize(Decimal("0.01")), "f")


Money = Annotated[
    Decimal,
    Field(max_digits=10, decimal_places=2),
    PlainSerializer(
        serialize_modey,
        return_type=str,
        when_used="json"
    )
]
