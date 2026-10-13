# Plan — DEMO-1
- persona / tool / model: analyst (Lodestar) / claude-code / claude-opus-5-5
- started / finished: 2026-10-13T00:49Z / 2026-10-13T00:51Z

## Commands
$ python -m uv run python -m pytest -q      (exit 0)   baseline before any change
5 passed, 1 warning in 0.22s

## Result

Test-first, three small steps, run from `EXAMPLES/demo-python-api`. **Use `python -m uv run python -m pytest`**, never
`uv run pytest` (see 01-analysis, risk R1). Each step ends with the full suite green.

### Step 1 — domain calculation (AC2–AC7, AC9)
- Files: `src/orders/domain.py`, `tests/test_quotes.py`.
- Change: add `VOLUME_DISCOUNT_THRESHOLD = Decimal("100.00")`, `VOLUME_DISCOUNT_RATE = Decimal("0.10")`, a frozen slotted
  dataclass `Quote(total: Decimal, discount: Decimal, payable: Decimal)` and `quote(lines: list[OrderLine]) -> Quote` that
  reuses `order_total`, computes `(total * VOLUME_DISCOUNT_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` when
  `total >= VOLUME_DISCOUNT_THRESHOLD`, else `Decimal("0.00")`, and sets `payable = total - discount`. Follow the existing style.
- Tests first (red, then green): one parametrized test over lines -> (total, discount, payable):
  1 x "100.00" -> 10.00 / 90.00; 1 x "99.99" -> 0.00 / 99.99; 1 x "100.05" -> 10.01 / 90.04;
  2 x "50.00" + 1 x "23.45" -> 12.35 / 111.10. In the same test assert `str(discount)` has 2 decimals (AC6) and the
  invariant `payable == total - discount` and `0 <= discount <= total` (AC7).
- Prove: `python -m uv run python -m pytest -q tests/test_quotes.py -k quote`, then `python -m uv run python -m pytest -q`

### Step 2 — endpoint response (AC1–AC5)
- Files: `src/orders/api.py`, `tests/test_quotes.py`.
- Change: `QuoteOut` gets `discount: Decimal` and `payable: Decimal`; `create_quote` builds the `OrderLine`s as today
  (keep the `ValueError` -> 422 mapping) and returns `QuoteOut` built from `quote(lines)`. No new dependency.
- Tests: POST 1 x "100.00" asserting 200, `set(body) == {"total", "discount", "payable"}`, every value is a `str`, and the
  Decimal values; POST 1 x "99.99" asserting `body["discount"] == "0.00"` and payable == total; POST 1 x "100.05" asserting
  discount 10.01 and payable 90.04. `test_quote_endpoint_returns_total` must keep passing unchanged.
- Prove: `python -m uv run python -m pytest -q tests/test_quotes.py -k endpoint`, then `python -m uv run python -m pytest -q`

### Step 3 — 422 regression and coverage (AC8)
- Files: `tests/test_quotes.py` only.
- Tests: parametrize the endpoint 422 test over quantity 0, `unit_price` "-1", `unit_price` "abc" and `lines: []`;
  assert 422 and that none of `total` / `discount` / `payable` is a key of the body.
- Prove: `python -m uv run python -m pytest -q --cov=orders --cov-branch --cov-report=term-missing`
  Expect all tests passing and every new line and branch in `domain.py` / `api.py` covered; report the line and branch
  numbers from the tool, not estimates.

### Quality gates (profile PERSONAL)
- `.harness/resolution.md` declares no Sonar or coverage threshold for this profile, so the gates are: full suite green with
  the floor interpreter, every AC mapped to a passing test, and a review verdict of approve / approve-with-nits.
- Rule `owner-validation`: the owner validates before any commit or push; agents push nothing.

### AC -> test map
| AC | Step | Test |
|---|---|---|
| AC1 | 2 | endpoint shape test |
| AC2–AC5 | 1, 2 | domain parametrized test + endpoint tests |
| AC6 | 1, 2 | `str(discount)` 2-decimal check; `body["discount"] == "0.00"` |
| AC7 | 1 | invariant assertion in the domain test |
| AC8 | 3 | parametrized 422 test |
| AC9 | 1 | domain tests without TestClient |
