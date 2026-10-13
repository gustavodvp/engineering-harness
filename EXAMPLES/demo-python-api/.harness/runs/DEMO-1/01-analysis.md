# Analysis — DEMO-1
- persona / tool / model: analyst (Lodestar) / claude-code / claude-opus-5-5
- started / finished: 2026-10-13T00:47Z / 2026-10-13T00:51Z

## Commands
$ python -m uv run pytest -q                (exit 0)
5 passed, 1 warning in 0.25s
    (the warning path is ...\projects\engineering-harness\EXAMPLES\demo-python-api\.venv\..., NOT this floor; see Risk R1)

$ python -m uv run python -m pytest -q      (exit 0)
5 passed, 1 warning in 0.22s

$ probe: interpreter and `orders` package each form imports (throwaway test in %TEMP%, deleted)
  uv run pytest            -> EXE    ...\projects\engineering-harness\EXAMPLES\demo-python-api\.venv\Scripts\python.exe
                              ORDERS ...\projects\engineering-harness\EXAMPLES\demo-python-api\src\orders\__init__.py
  uv run python -m pytest  -> EXE    ...\floors\engineering-harness--demodemo-1\EXAMPLES\demo-python-api\.venv\Scripts\python.exe
                              ORDERS ...\floors\engineering-harness--demodemo-1\EXAMPLES\demo-python-api\src\orders\__init__.py

$ probe: current POST /quotes behaviour (TestClient, throwaway script, deleted)
  1 x unit_price "100"       -> 200 {"total":"100"}
  3 x unit_price "33.335"    -> 200 {"total":"100.005"}
  unit_price "abc"           -> 422 (pydantic decimal_parsing)
  "lines": []                -> 422 (pydantic too_short)
  unit_price "-1"            -> 422 {"detail":"unit_price must not be negative"}
  versions: pydantic 2.14.1, fastapi 0.143.0

## Result

### Problem
`POST /quotes` returns only `{"total": ...}`. The story asks for a volume discount: when the quote total is at
least 100.00 the buyer gets 10% off, and the response must expose `total` (before discount), `discount` and
`payable`. Invalid input must keep returning 422. Money is already `Decimal` end to end (`OrderLine.unit_price`,
`order_total`), and pydantic v2 serialises `Decimal` as a JSON **string**, so no float is involved today.

### Acceptance criteria (testable)
Amounts are `decimal.Decimal`; JSON amounts are strings; "equals" means `Decimal(json_value) == Decimal(expected)`
unless the criterion says "exact string".

- **AC1 — response shape.** Given any valid quote request, when I `POST /quotes`, then the status is 200 and the body is a
  JSON object with exactly the keys `total`, `discount`, `payable`, each a string parseable as `Decimal` (no JSON numbers).
- **AC2 — boundary: the discount applies at exactly 100.00.** Given lines totalling exactly 100.00 (1 x "100.00"),
  then `total` = 100.00, `discount` = 10.00, `payable` = 90.00.
- **AC3 — just below the boundary.** Given lines totalling 99.99 (1 x "99.99"), then `discount` is the exact string
  `"0.00"` and `payable` = `total` = 99.99.
- **AC4 — half-up rounding, not banker's.** Given lines totalling 100.05 (1 x "100.05"), then `discount` = 10.01
  (10% = 10.005, half-up -> 10.01; `ROUND_HALF_EVEN` would give 10.00) and `payable` = 90.04.
- **AC5 — general case.** Given lines totalling 123.45 (2 x "50.00" + 1 x "23.45"), then `discount` = 12.35
  (12.345 -> 12.35) and `payable` = 111.10.
- **AC6 — discount always has 2 decimals.** `discount` is quantized to `Decimal("0.01")` with `ROUND_HALF_UP`, so its JSON
  is always a 2-decimal string (`"0.00"`, `"10.00"`, `"10.01"`).
- **AC7 — invariant.** For every 200 response, `Decimal(payable) == Decimal(total) - Decimal(discount)` and
  `0 <= discount <= total`.
- **AC8 — 422 unchanged.** Each of these returns 422 and the body has no `total` / `discount` / `payable`:
  quantity 0; negative `unit_price`; non-decimal `unit_price` ("abc"); empty `lines`.
- **AC9 — domain level.** A pure domain function (no FastAPI) computes total / discount / payable from `list[OrderLine]`
  and is covered by unit tests for AC2–AC7, so the rule is testable without HTTP.

### Assumptions (explicit; the orchestrator may overturn them)
- **A1 — money type:** `Decimal` everywhere (domain and API), never `float`. Threshold `Decimal("100.00")`, rate `Decimal("0.10")`.
- **A2 — `total` is not rounded.** The story specifies rounding only for `discount`, and today `total` is the exact sum
  ("100.005" is returned as is). We keep that; `payable = total - discount` is exact `Decimal` subtraction.
  Consequence: with sub-cent prices `payable` can have more than 2 decimals. Recommended follow-up (out of scope):
  restrict `unit_price` to 2 decimals (`decimal_places=2`) in a separate story.
- **A3 — the threshold compares the unrounded total** with `>=`: 99.995 -> no discount; 100.00 -> discount.
- **A4 — serialisation:** keep the pydantic default `Decimal` -> JSON string. `total` / `payable` keep the input scale
  (1 x "100" -> `"100"`), so tests compare via `Decimal(...)`; only `discount` is guaranteed 2-decimal (AC6).
- **A5 — no new dependency** and no config flag or rate parameter; rate and threshold are module constants (code-quality rule 4).
- **A6 — 422 body shape** stays as today (pydantic detail list, or `{"detail": "<msg>"}` from a domain `ValueError`).

### Open questions (recommended answer applied as an assumption)
- Q1: Should `total` and `payable` also be rounded to 2 decimals? -> **Recommended: not in this story** (A2).
- Q2: Is the discount tiered or capped? -> **Assumed: single tier, 10%, no cap** (the story states one rule only).
- Q3: Do zero-price lines count? -> **Yes**, domain validation unchanged (`unit_price >= 0`).

### Out of scope
Currency handling, tiered or configurable discounts, rounding of `total`, restricting input precision, persistence, auth.

### Affected components
- `src/orders/domain.py`: new quote calculation (constants, `Quote` dataclass, function).
- `src/orders/api.py`: `QuoteOut` gains `discount` and `payable`; the endpoint uses the domain function.
- `tests/test_quotes.py`: new unit and endpoint tests; existing tests stay green.

### Risks
- **R1 (high, process) — false green in this floor.** `python -m uv run pytest` launches the *main checkout's* `.venv`
  (`projects\engineering-harness\...`) and imports the main checkout's `src/orders`, not this floor's. The floor `.venv`
  looks copied, so its `Scripts\pytest.exe` launcher keeps an absolute path to the original interpreter, and tests would
  run against unchanged code. **Every stage must use `python -m uv run python -m pytest ...`** (verified above to use the
  floor interpreter and source). Harness follow-up: recreate the venv per floor, or document the `python -m pytest` form.
- R2 — banker's rounding slip: `Decimal.quantize` without `rounding=` uses the context default `ROUND_HALF_EVEN`. AC4 catches it.
- R3 — float creep (`0.1` instead of `Decimal("0.10")`). AC1 and AC4 catch it.

### Handoff
Plan: `02-plan.md`. Recommended next persona: **developer**. No ADR needed (no lasting architectural decision).
