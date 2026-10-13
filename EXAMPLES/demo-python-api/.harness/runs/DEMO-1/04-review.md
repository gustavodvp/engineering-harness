# Review — DEMO-1
- persona / tool / model: reviewer (Plumb) / claude-code / claude-sonnet-5-5 (independent of the developer's opencode / deepseek-v4.1-flash)
- started / finished: 2026-10-13T00:55Z / 2026-10-13T00:58Z

## Commands
$ git status --short .                                   (exit 0)
 M src/orders/api.py / M src/orders/domain.py / M tests/test_quotes.py / ?? .harness/runs/
$ git diff -- src tests                                  (exit 0)   full diff read (3 files)
$ python -m uv run python -m pytest -q                   (exit 0)   after the last change, floor interpreter (risk R1 form)
15 passed, 1 warning in 0.25s
    (warning: pre-existing Starlette/httpx deprecation from the floor `.venv`, present in baseline)

## Result

**Verdict: approve-with-nits** — 0 blocker, 0 major, 1 minor, 2 nit.

### Correctness (checked, no defects)
- Money is `Decimal` end to end; no float. Constants `Decimal("100.00")` / `Decimal("0.10")` (`src/orders/domain.py:5-7`).
- Boundary `total >= VOLUME_DISCOUNT_THRESHOLD` on the **unrounded** total (`domain.py:41`), matching A3. 100.00 -> discount, 99.99 -> none.
- Rounding `quantize(_CENT, rounding=ROUND_HALF_UP)` explicit (`domain.py:42`), so R2 (banker's rounding) is avoided: 100.05 -> 10.005 -> 10.01.
- `payable = total - discount` exact (`domain.py:45`); invariant holds. Below threshold `discount` is `Decimal("0.00")` (2 decimals, AC6).
- 422 paths: domain `ValueError` still mapped to 422 (`api.py`), pydantic handles `"abc"` and `lines: []`. Unchanged, and now regression-tested.
- API contract: `QuoteOut` adds `discount` and `payable`; pydantic v2 serialises `Decimal` as JSON strings. `total` stays a string, key kept, so the change is additive and backward compatible.
- Security baseline: input still validated at the boundary, no secrets, no new dependency, no new logging.
- Diff is focused (3 files, no unrelated edits), style matches surrounding code (frozen slotted dataclass, same idiom as `OrderLine`).

### Test adequacy (AC -> proof)
Mentally mutated the code: `>` instead of `>=` fails the 100.00 cases; `ROUND_HALF_EVEN` fails 100.05 (10.00 != 10.01); float rate fails exact comparisons; `payable = total` fails 90.00. Each AC has a test that fails without the change: AC1 `test_quote_endpoint_returns_discount_and_payable`, AC2-AC5 domain parametrized + endpoint tests, AC6 `str(discount)` check and `body["discount"] == "0.00"`, AC7 invariant assertions, AC8 parametrized 422 test, AC9 domain tests without `TestClient`.

### Findings

| # | Severity | Location | Finding |
|---|---|---|---|
| 1 | minor | `tests/test_quotes.py:66-72` (`test_quote_endpoint_applies_discount`) | The HTTP-level discount case 123.45 (AC5, 2 x 50.00 + 1 x 23.45) and the exact boundary at the endpoint with a multi-line total are only proven at domain level. The endpoint test covers 99.99 and 100.05 (plus 100.00 in the shape test). A regression that breaks only multi-line aggregation through the API would pass. Fix: add `("123.45", ...)`-equivalent case with three lines, or a second payload shape, to the endpoint test. |
| 2 | nit | `tests/test_quotes.py:84-87` (`test_quote_endpoint_rejects_invalid_payload`) | Asserts only status 422 and absence of amount keys; it does not distinguish the domain `ValueError` path (`{"detail": "<msg>"}`, A6) from pydantic validation. A change of the error body would go unnoticed. Optional: assert `"detail" in response.json()`. |
| 3 | nit | `src/orders/domain.py:44` | `Decimal("0.00")` is a second inline literal next to the named `_CENT`; could be `_CENT * 0` or a named zero. Purely cosmetic, no behaviour change. |

Not a finding (documented, accepted): `total`/`payable` are not rounded (A2), so sub-cent unit prices give `payable` with more than 2 decimals, e.g. 3 x 33.335 -> total 100.005, discount 10.00, payable 90.005. This is the analyst's accepted assumption with a recommended follow-up story to restrict `unit_price` to 2 decimals; not a defect of this diff.

## Not reviewed / not run
- Coverage (line and branch) was **not run**: development reported `ModuleNotFoundError: No module named 'coverage'`; the orchestrator later repaired the floor venv (see `00-orchestration.md`). I did not run `--cov` because my allowed command is only `python -m uv run python -m pytest -q`. Coverage is left pending for QA (stage 5), and I make no coverage claim.
- No real HTTP round trip against a running server (owner-validation rule applies to Atlas projects; this is a synthetic demo, validation by the owner before any commit still applies).
- Generated files under `.harness/` (other than the evidence files read) and `.maestri/` were out of scope.
- Behaviour with JSON numeric `unit_price` (e.g. `100.05` unquoted) was not examined; outside the ACs.

## Handoff
Verdict `approve-with-nits` (`changes-required` not needed). Counts: blocker 0, major 0, minor 1, nit 2. Next: QA (Sieve) for the full suite and coverage numbers; the developer may optionally address finding 1. No code or test file was edited by the reviewer.
