from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from orders.api import app
from orders.domain import OrderLine, order_total, quote

client = TestClient(app)


def test_total_sums_lines():
    lines = [OrderLine("A", 2, Decimal("10.00")), OrderLine("B", 1, Decimal("5.50"))]
    assert order_total(lines) == Decimal("25.50")


@pytest.mark.parametrize("quantity, price", [(0, "1"), (1, "-1")])
def test_rejects_invalid_lines(quantity, price):
    with pytest.raises(ValueError):
        OrderLine("A", quantity, Decimal(price))


@pytest.mark.parametrize(
    "units, expected_total, expected_discount, expected_payable",
    [
        ([(1, "100.00")], Decimal("100.00"), Decimal("10.00"), Decimal("90.00")),
        ([(1, "99.99")], Decimal("99.99"), Decimal("0.00"), Decimal("99.99")),
        ([(1, "100.05")], Decimal("100.05"), Decimal("10.01"), Decimal("90.04")),
        ([(2, "50.00"), (1, "23.45")], Decimal("123.45"), Decimal("12.35"), Decimal("111.10")),
    ],
)
def test_quote_applies_volume_discount(units, expected_total, expected_discount, expected_payable):
    lines = [OrderLine(f"SKU{i}", quantity, Decimal(price)) for i, (quantity, price) in enumerate(units)]
    result = quote(lines)
    assert result.total == expected_total
    assert result.discount == expected_discount
    assert result.payable == expected_payable
    assert str(result.discount) == f"{expected_discount:.2f}"
    assert result.payable == result.total - result.discount
    assert Decimal("0") <= result.discount <= result.total


def test_quote_endpoint_returns_total():
    response = client.post("/quotes", json={"lines": [{"sku": "A", "quantity": 3, "unit_price": "2.00"}]})
    assert response.status_code == 200
    assert Decimal(response.json()["total"]) == Decimal("6.00")


def test_quote_endpoint_returns_discount_and_payable():
    response = client.post("/quotes", json={"lines": [{"sku": "A", "quantity": 1, "unit_price": "100.00"}]})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"total", "discount", "payable"}
    assert all(isinstance(value, str) for value in body.values())
    assert Decimal(body["total"]) == Decimal("100.00")
    assert Decimal(body["discount"]) == Decimal("10.00")
    assert Decimal(body["payable"]) == Decimal("90.00")


@pytest.mark.parametrize(
    "units, expected_discount, expected_payable",
    [
        ([(1, "99.99")], "0.00", "99.99"),
        ([(1, "100.05")], "10.01", "90.04"),
        ([(2, "50.00"), (1, "23.45")], "12.35", "111.10"),
    ],
)
def test_quote_endpoint_applies_discount(units, expected_discount, expected_payable):
    payload = {
        "lines": [
            {"sku": f"SKU{i}", "quantity": quantity, "unit_price": price}
            for i, (quantity, price) in enumerate(units)
        ]
    }
    response = client.post("/quotes", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["discount"] == expected_discount
    assert Decimal(body["payable"]) == Decimal(expected_payable)


@pytest.mark.parametrize(
    "payload",
    [
        {"lines": [{"sku": "A", "quantity": 0, "unit_price": "2.00"}]},
        {"lines": [{"sku": "A", "quantity": 1, "unit_price": "-1"}]},
        {"lines": [{"sku": "A", "quantity": 1, "unit_price": "abc"}]},
        {"lines": []},
    ],
)
def test_quote_endpoint_rejects_invalid_payload(payload):
    response = client.post("/quotes", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert not {"total", "discount", "payable"} & set(response.json())
