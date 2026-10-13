from __future__ import annotations

from decimal import Decimal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .domain import OrderLine, quote

app = FastAPI(title="demo-orders-api")


class LineIn(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    quantity: int
    unit_price: Decimal


class QuoteIn(BaseModel):
    lines: list[LineIn] = Field(min_length=1, max_length=100)


class QuoteOut(BaseModel):
    total: Decimal
    discount: Decimal
    payable: Decimal


@app.post("/quotes", response_model=QuoteOut)
def create_quote(payload: QuoteIn) -> QuoteOut:
    try:
        lines = [OrderLine(line.sku, line.quantity, line.unit_price) for line in payload.lines]
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err)) from err
    result = quote(lines)
    return QuoteOut(total=result.total, discount=result.discount, payable=result.payable)
