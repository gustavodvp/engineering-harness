# Tests and gates — DEMO-1
- persona / tool / model: qa (Sieve) / opencode / opencode-go/deepseek-v4.1-flash
- started / finished: 2026-10-13T00:58Z / 2026-10-13T01:00Z
- branch / worktree: demo/demo-1 in the DEMO-1 Maestri floor; run from `EXAMPLES/demo-python-api`
- mandatory test command (risk R1): `python -m uv run python -m pytest ...` — never `uv run pytest`
- inputs read: `STORY.md`, `.harness/personas/qa.md`, `AGENTS.md`, `.harness/resolution.md`,
  `00-orchestration.md`, `01-analysis.md`, `02-plan.md`, `03-development.md`, `04-review.md`, `06-fix.md`
- code/tests: read-only for this stage; no file under `src/` or `tests/` was edited

## Commands

### (a) Full suite
$ python -m uv run python -m pytest -q                                  (exit 0)
................                                                         [100%]
16 passed, 1 warning in 0.26s
    (warning: pre-existing Starlette/httpx deprecation from the floor venv,
     `fastapi\testclient.py:1` StarletteDeprecationWarning; present in the baseline too)

### (b) Full suite with line + branch coverage
$ python -m uv run python -m pytest -q --cov=orders --cov-branch --cov-report=term-missing   (exit 0)
................                                                         [100%]
=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.14.7-final-0 _______________

Name                     Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------
src\orders\__init__.py       0      0      0      0   100%
src\orders\api.py           24      0      0      0   100%
src\orders\domain.py        32      0      6      0   100%
--------------------------------------------------------------------
TOTAL                       56      0      6      0   100%
16 passed, 1 warning in 0.35s

### (c) Per-test result list (for the AC map below)
$ python -m uv run python -m pytest -v                                  (exit 0)
tests/test_quotes.py::test_total_sums_lines PASSED                       [  6%]
tests/test_quotes.py::test_rejects_invalid_lines[0-1] PASSED             [ 12%]
tests/test_quotes.py::test_rejects_invalid_lines[1--1] PASSED            [ 18%]
tests/test_quotes.py::test_quote_applies_volume_discount[units0-...] PASSED   [ 25%]   (1 x 100.00)
tests/test_quotes.py::test_quote_applies_volume_discount[units1-...] PASSED   [ 31%]   (1 x 99.99)
tests/test_quotes.py::test_quote_applies_volume_discount[units2-...] PASSED   [ 37%]   (1 x 100.05)
tests/test_quotes.py::test_quote_applies_volume_discount[units3-...] PASSED   [ 43%]   (2 x 50.00 + 1 x 23.45)
tests/test_quotes.py::test_quote_endpoint_returns_total PASSED           [ 50%]
tests/test_quotes.py::test_quote_endpoint_returns_discount_and_payable PASSED [ 56%]
tests/test_quotes.py::test_quote_endpoint_applies_discount[units0-0.00-99.99] PASSED   [ 62%]
tests/test_quotes.py::test_quote_endpoint_applies_discount[units1-10.01-90.04] PASSED  [ 68%]
tests/test_quotes.py::test_quote_endpoint_applies_discount[units2-12.35-111.10] PASSED [ 75%]
tests/test_quotes.py::test_quote_endpoint_rejects_invalid_payload[payload0] PASSED     [ 81%]
tests/test_quotes.py::test_quote_endpoint_rejects_invalid_payload[payload1] PASSED     [ 87%]
tests/test_quotes.py::test_quote_endpoint_rejects_invalid_payload[payload2] PASSED     [ 93%]
tests/test_quotes.py::test_quote_endpoint_rejects_invalid_payload[payload3] PASSED     [100%]
======================== 16 passed, 1 warning in 0.30s ========================

## Result

**Verdict: pass.** 16/16 tests pass (exit 0) on the floor interpreter (risk R1 form); coverage is
**100% line and 100% branch** for the `orders` package, with **no missing lines and no partial branches**,
as reported by the tool (`coverage: platform win32, python 3.14.7-final-0`). All nine acceptance criteria
from `01-analysis.md` map to a test that ran and passed. No production or test file was modified by QA.

### AC → test → result
| AC | What it requires | Test (ran) | Result |
|---|---|---|---|
| AC1 | 200 with keys exactly `total`, `discount`, `payable`, each a `str` | `test_quote_endpoint_returns_discount_and_payable` (key set + `all(isinstance(value, str))`) | PASSED |
| AC2 | boundary: 1 x 100.00 -> total 100.00, discount 10.00, payable 90.00 | domain `test_quote_applies_volume_discount[units0]` + endpoint `test_quote_endpoint_returns_discount_and_payable` | PASSED |
| AC3 | just below: 1 x 99.99 -> discount exact `"0.00"`, payable = total = 99.99 | domain `test_quote_applies_volume_discount[units1]` + endpoint `test_quote_endpoint_applies_discount[units0-0.00-99.99]` | PASSED |
| AC4 | half-up: 1 x 100.05 -> discount 10.01, payable 90.04 | domain `test_quote_applies_volume_discount[units2]` + endpoint `test_quote_endpoint_applies_discount[units1-10.01-90.04]` | PASSED |
| AC5 | general: 2 x 50.00 + 1 x 23.45 -> discount 12.35, payable 111.10 | domain `test_quote_applies_volume_discount[units3]` + endpoint `test_quote_endpoint_applies_discount[units2-12.35-111.10]` | PASSED |
| AC6 | discount always 2 decimals | domain `str(result.discount) == f"{expected_discount:.2f}"` (all 4 domain cases) + endpoint `body["discount"]` exact strings `"0.00"`/`"10.01"`/`"12.35"` | PASSED |
| AC7 | invariant `payable == total - discount` and `0 <= discount <= total` | domain `test_quote_applies_volume_discount` lines 39-40 (all 4 cases) | PASSED |
| AC8 | 422 for quantity 0, negative price, `"abc"`, empty lines, and no amount keys | `test_quote_endpoint_rejects_invalid_payload[payload0..payload3]` (status 422, `"detail"` present, no `total`/`discount`/`payable`) | PASSED |
| AC9 | pure domain function testable without HTTP | `test_quote_applies_volume_discount` calls `quote(...)` from `orders.domain`; no `TestClient` | PASSED |

No AC is unproven. The unchanged baseline tests `test_total_sums_lines` and `test_rejects_invalid_lines` also pass.

### Coverage (from the tool, command (b))
| File | Stmts | Miss | Branch | BrPart | Cover | Missing |
|---|---|---|---|---|---|---|
| `src\orders\__init__.py` | 0 | 0 | 0 | 0 | 100% | – |
| `src\orders\api.py` | 24 | 0 | 0 | 0 | 100% | – |
| `src\orders\domain.py` | 32 | 0 | 6 | 0 | 100% | – |
| **TOTAL** | **56** | **0** | **6** | **0** | **100%** | **–** |

- **Line coverage: 100%** (56 statements, 0 missed). **Branch coverage: 100%** (6 branches, 0 partial).
- Missing lines: none. Missing/partial branches: none.
- Coverage tool: `coverage 7.16.2` via `pytest-cov`, run on `platform win32, python 3.14.7-final-0`.
  The floor venv repair from `00-orchestration.md` is confirmed by this run (coverage imports and reports).
- HTML/XML report not generated; the numbers above are the full `term-missing` output.

### Profile gates (`.harness/resolution.md`, profile PERSONAL)
`resolution.md` declares **no Sonar or coverage threshold** for PERSONAL (no `quality.*` gate beyond
`quality.tests-with-change = required`). The gates are therefore:

| Gate | Source | Status |
|---|---|---|
| Full suite green on the floor interpreter (risk R1 form) | `02-plan.md` quality gates; `verification.claims = require-evidence` | **PASS** — 16 passed, exit 0, floor `.venv` |
| Every AC mapped to a passing test | `02-plan.md`; `quality.tests-with-change = required` | **PASS** — AC1–AC9 all mapped and PASSED |
| Review verdict approve / approve-with-nits | `02-plan.md`; `04-review.md` | **PASS** — `approve-with-nits` (0 blocker, 0 major) |
| Coverage threshold | none declared for PERSONAL in `resolution.md` | **N/A** — informational only; 100% line / 100% branch |
| Owner validation before commit/push (`owner-validation`) | `resolution.md` effective decision `verification.owner-validation = before-commit-atlas` | **PENDING (owner)** — nothing committed or pushed; QA pushes nothing |
| Isolated test database (`testing.database = isolated`) | `resolution.md` | **N/A** — no database in this project |

No gate reported a failure. The only warning is the pre-existing Starlette/httpx deprecation, present in the
baseline (see `01-analysis.md`, `03-development.md`), not a gate failure.

### Notes / deviations
- QA did **not** edit any code or test; `git status --short` still shows only the three stage-3 files modified
  (`src/orders/api.py`, `src/orders/domain.py`, `tests/test_quotes.py`) plus untracked `.harness/runs/` and
  `../../.maestri/`. No commit, no push; `.maestri/` untouched.
- The AC map and coverage confirm the fix stage `06-fix.md`: the endpoint now proves AC5 (multi-line
  `2 x 50.00 + 1 x 23.45`) through HTTP, and the 422 test asserts `"detail"` is present.
- Review nit #3 (`src/orders/domain.py:44` inline `Decimal("0.00")`) remains disputed by the developer in
  `06-fix.md`; it is cosmetic and does not affect any AC, gate or coverage (the line is covered).
- No real HTTP round trip against a running server was performed. This is a synthetic demo (`STORY.md`);
  `owner-validation` still requires the owner to validate before any commit, which is outside this stage.

### Handoff
Verdict **pass** for the orchestrator: 16/16 tests, 100% line and 100% branch coverage, every AC1–AC9 proven,
no gate failed. Nothing to send back to the developer; only owner validation before commit remains.
No usable failure to hand over.
