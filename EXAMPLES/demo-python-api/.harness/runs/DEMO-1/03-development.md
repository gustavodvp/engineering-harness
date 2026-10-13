# Development — DEMO-1
- persona / tool / model: developer (Rivet) / opencode / opencode-go/deepseek-v4.1-flash
- started / finished: 2026-10-13T00:52Z / 2026-10-13T00:54Z
- branch / worktree: demo/demo-1 in the DEMO-1 Maestri floor; tests run from `EXAMPLES/demo-python-api`
- mandatory test command (risk R1): `python -m uv run python -m pytest -q` — never `uv run pytest`

## Commands

### Baseline (before any change)
$ python -m uv run python -m pytest -q                                       (exit 0)
5 passed, 1 warning in 0.23s

### Step 1 — domain calculation (AC2–AC7, AC9)
$ python -m uv run python -m pytest -q tests/test_quotes.py -k quote     (exit 2)   RED
=========================== short test summary info ===========================
ERROR tests/test_quotes.py
E   ImportError: cannot import name 'quote' from 'orders.domain' (...\src\orders\domain.py)
1 warning, 1 error in 0.33s

$ python -m uv run python -m pytest -q tests/test_quotes.py -k quote     (exit 0)   GREEN
9 passed, 1 warning in 0.23s

$ python -m uv run python -m pytest -q                                   (exit 0)   full suite
9 passed, 1 warning in 0.23s

### Step 2 — endpoint response (AC1–AC5)
$ python -m uv run python -m pytest -q tests/test_quotes.py -k endpoint  (exit 1)   RED
E   AssertionError: assert {'total'} == {'discount', 'payable', 'total'}
E   KeyError: 'discount'
FAILED tests/test_quotes.py::test_quote_endpoint_returns_discount_and_payable
FAILED tests/test_quotes.py::test_quote_endpoint_applies_discount[99.99-0.00-99.99]
FAILED tests/test_quotes.py::test_quote_endpoint_applies_discount[100.05-10.01-90.04]
3 failed, 2 passed, 7 deselected, 1 warning in 0.30s

$ python -m uv run python -m pytest -q tests/test_quotes.py -k endpoint  (exit 0)   GREEN
5 passed, 7 deselected, 1 warning in 0.24s

$ python -m uv run python -m pytest -q                                   (exit 0)   full suite
12 passed, 1 warning in 0.24s

### Step 3 — 422 regression (AC8)
$ python -m uv run python -m pytest -q tests/test_quotes.py -k invalid   (exit 0)
6 passed, 9 deselected, 1 warning in 0.25s
    (regression guard for already-working 422 behaviour; parametrized over quantity 0, unit_price "-1", unit_price "abc", lines [])

$ python -m uv run python -m pytest -q --cov=orders --cov-branch --cov-report=term-missing   (exit 1)   PENDING
ModuleNotFoundError: No module named 'coverage'
    (pytest-cov is installed but the `coverage` package is not; adding it would be a new dependency, forbidden by assumption A5.
     Per `.harness/resolution.md` there is no coverage threshold for profile PERSONAL, so this is not a blocking gate — see deviations.)

### Final full suite (after the last change)
$ python -m uv run python -m pytest -q                                   (exit 0)   GREEN
15 passed, 1 warning in 0.24s

## Result

All three plan steps implemented test-first (red seen for the right reason, then green), full suite green on the
floor interpreter (15 passed). The only warning is a pre-existing Starlette/httpx deprecation from
`.venv\Lib\site-packages\fastapi\testclient.py`, present in the baseline too.

Files changed (`git diff --stat`): 3 files, 85 insertions(+), 6 deletions(-)

- `src/orders/domain.py`: added `VOLUME_DISCOUNT_THRESHOLD = Decimal("100.00")`, `VOLUME_DISCOUNT_RATE = Decimal("0.10")`,
  `_CENT = Decimal("0.01")`, the frozen slotted `Quote` dataclass and `quote(lines) -> Quote`. Reuses `order_total`;
  applies `(total * RATE).quantize(_CENT, rounding=ROUND_HALF_UP)` when `total >= THRESHOLD`, else `Decimal("0.00")`;
  `payable = total - discount`. Money stays `Decimal` end to end.
- `src/orders/api.py`: `QuoteOut` now exposes `total`, `discount`, `payable`; `create_quote` keeps the `ValueError` → 422
  mapping and builds the response from `quote(lines)`. No new dependency.
- `tests/test_quotes.py`: added a parametrized domain test (AC2–AC7, AC9), an endpoint shape test (AC1/AC6) and a
  parametrized endpoint discount test (AC2–AC5), and replaced the single 422 test with a parametrized regression test
  over the four AC8 cases asserting the body has no `total`/`discount`/`payable`.

### AC → test map (proved by the run above)
| AC | Test |
|---|---|
| AC1 | `test_quote_endpoint_returns_discount_and_payable` (key set + all values `str`) |
| AC2–AC5 | `test_quote_applies_volume_discount` (domain) + `test_quote_endpoint_applies_discount` (HTTP) |
| AC6 | `str(result.discount) == f"{expected_discount:.2f}"`; `body["discount"] == "0.00"` |
| AC7 | invariant `payable == total - discount` and `0 <= discount <= total` |
| AC8 | `test_quote_endpoint_rejects_invalid_payload` (4 cases, 422, no amount keys) |
| AC9 | domain tests call `quote(...)` directly, no `TestClient` |

### Deviations from the plan
1. **Coverage report pending (tooling, not code).** Plan Step 3 asks for `--cov=orders --cov-branch --cov-report=term-missing`.
   `pytest-cov` is present but its `coverage` dependency is not installed in the floor venv, and no new dependency is
   allowed (A5). Reported as pending rather than installing anything. The declared gate for PERSONAL has no coverage
   threshold; the gate is "full suite green + every AC mapped to a passing test", both satisfied. QA may confirm coverage
   with whatever runner the floor has.
2. **`_CENT` named constant.** The plan wrote `Decimal("0.01")` inline; used a private module constant to avoid repeating
   the literal. No behaviour change.
3. **422 test parametrized.** The plan's Step 3 explicitly asked to parametrize the endpoint 422 test, so the previous
   single `test_quote_endpoint_rejects_invalid_quantity` was folded into `test_quote_endpoint_rejects_invalid_payload`.
   `test_quote_endpoint_returns_total` (AC baseline) was left unchanged and still passes.

### Handoff
Next stages per `story-delivery`: independent review, then QA. Nothing committed or pushed (owner validation required
before any commit). `.maestri/` untouched.
