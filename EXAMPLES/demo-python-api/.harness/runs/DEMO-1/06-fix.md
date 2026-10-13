# Fix — DEMO-1
- persona / tool / model: developer (Rivet) / opencode / opencode-go/deepseek-v4.1-flash
- started / finished: 2026-10-13T00:56Z / 2026-10-13T00:58Z
- branch / worktree: demo/demo-1 in the DEMO-1 Maestri floor; run from `EXAMPLES/demo-python-api`
- source of findings: `.harness/runs/DEMO-1/04-review.md` (verdict approve-with-nits: 0 blocker, 0 major, 1 minor, 2 nit)
- scope: tests only (no production behaviour change); test command `python -m uv run python -m pytest -q` (risk R1)

## Findings

### #1 — minor — FIXED
`tests/test_quotes.py` `test_quote_endpoint_applies_discount` only exercised single-line payloads, so multi-line
aggregation through the API (AC5) was proven only at domain level. Reworked the parametrization to take `units`
(a list of quantity/price pairs) and added the three-line case `[(2, "50.00"), (1, "23.45")] -> discount "12.35",
payable "111.10"`. The 99.99 and 100.05 single-line cases are kept. Endpoint now covers AC2–AC5 through HTTP.

### #2 — nit — FIXED
`tests/test_quotes.py` `test_quote_endpoint_rejects_invalid_payload` asserted only status 422 and the absence of
amount keys. Added `assert "detail" in response.json()`, so a change that dropped the error body (both the domain
`ValueError` mapping to `{"detail": "<msg>"}` and the pydantic `{"detail": [...]}` path) would now be caught.

### #3 — nit — DISPUTED (not applied)
`src/orders/domain.py:44` uses `Decimal("0.00")` next to the named `_CENT`. Disputed for two reasons:
1. This fix stage is restricted to test files and must not change production behaviour; applying the nit would
   require editing `src/orders/domain.py`, which is out of scope for the findings assigned to this stage.
2. The literal is intentional, not accidental duplication: `Decimal("0.00")` states the required 2-decimal money
   scale (AC6) directly, while `_CENT * 0` is an indirection that adds no clarity. Purely cosmetic, zero behavioural
   impact. Can be folded into a future non-functional cleanup if the owner wants it.

## Commands

$ python -m uv run python -m pytest -q tests/test_quotes.py -k "endpoint_applies_discount or invalid_payload"   (exit 0)
.......                                                                  [100%]
7 passed, 9 deselected, 1 warning in 0.25s
    (3 endpoint discount cases incl. the new 123.45 three-line case + 4 parametrized 422 cases with the `detail` assertion)

$ python -m uv run python -m pytest -q                                   (exit 0)   full suite after the last change
................                                                         [100%]
16 passed, 1 warning in 0.25s
    (was 15 before this stage; +1 for the added 123.45 endpoint case. The single warning is the pre-existing
     Starlette/httpx deprecation from the floor `.venv`, present in the baseline.)

## Result

Both test findings addressed, nit #3 disputed. No production file was modified in this stage: `git status --short`
still shows only the three stage-3 files as modified, and the only edit made here is to `tests/test_quotes.py`.
`git diff --stat` (cumulative, unchanged head): 3 files, 93 insertions(+), 6 deletions(-).

### Finding outcomes
| # | Severity | Outcome | Where |
|---|---|---|---|
| 1 | minor | fixed | `tests/test_quotes.py` `test_quote_endpoint_applies_discount` (added 2 x 50.00 + 1 x 23.45 -> 12.35 / 111.10) |
| 2 | nit | fixed | `tests/test_quotes.py` `test_quote_endpoint_rejects_invalid_payload` (`assert "detail" in response.json()`) |
| 3 | nit | disputed | `src/orders/domain.py:44` cosmetic literal; see reason above |

### Deviations
- None. Test suite green (16 passed) on the mandatory floor command; no commit, no push; `.maestri/` untouched.

### Handoff
Ready for QA (stage 5). Nothing committed (owner validation before any commit still applies).
