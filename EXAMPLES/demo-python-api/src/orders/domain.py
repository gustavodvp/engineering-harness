from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

VOLUME_DISCOUNT_THRESHOLD = Decimal("100.00")
VOLUME_DISCOUNT_RATE = Decimal("0.10")
_CENT = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class OrderLine:
    sku: str
    quantity: int
    unit_price: Decimal

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.unit_price < 0:
            raise ValueError("unit_price must not be negative")

    @property
    def total(self) -> Decimal:
        return self.unit_price * self.quantity


def order_total(lines: list[OrderLine]) -> Decimal:
    return sum((line.total for line in lines), Decimal("0"))


@dataclass(frozen=True, slots=True)
class Quote:
    total: Decimal
    discount: Decimal
    payable: Decimal


def quote(lines: list[OrderLine]) -> Quote:
    total = order_total(lines)
    if total >= VOLUME_DISCOUNT_THRESHOLD:
        discount = (total * VOLUME_DISCOUNT_RATE).quantize(_CENT, rounding=ROUND_HALF_UP)
    else:
        discount = Decimal("0.00")
    return Quote(total=total, discount=discount, payable=total - discount)
