# Close — DEMO-1
- persona / tool / model: orchestrator / claude-code (Maestro Mode) / claude-opus-5-5
- started / finished: 2026-10-13T01:01Z / 2026-10-13T01:01Z
- floor / branch: `DEMO-1` / `demo/demo-1`, local commit `aa6791e` (on top of `216375a`)

## Commands
$ python -m uv run python -m pytest -q --cov=orders --cov-branch --cov-report=term-missing   (exit 0, re-run by orchestrator)
TOTAL                       56      0      6      0   100%
16 passed, 1 warning in 0.32s
$ git log --oneline -1   ->  aa6791e feat(demo): desconto de volume de 10% em cotações a partir de 100.00 (DEMO-1)
$ git log origin/demo/demo-1   ->  fatal: unknown revision (branch never pushed)

## Delivered
10% volume discount on quotes with a total >= 100.00 (`ROUND_HALF_UP` to 2 decimals). The response is now
`{total, discount, payable}`, and 422 still applies to invalid input. Changed files: `src/orders/domain.py`,
`src/orders/api.py`, `tests/test_quotes.py` (+93/-6).

## Evidence
| Stage | File | Outcome |
|---|---|---|
| 0 | [00-orchestration.md](00-orchestration.md) | team, decisions, stage log |
| 1–2 | [01-analysis.md](01-analysis.md), [02-plan.md](02-plan.md) | 9 ACs, 3-step plan, risk R1 |
| 3 | [03-development.md](03-development.md) | 15 passed |
| 4 | [04-review.md](04-review.md) | approve-with-nits (0 blocker, 0 major, 1 minor, 2 nit), independent model (Sonnet 5.5 vs DeepSeek) |
| 6 | [06-fix.md](06-fix.md) | #1 and #2 fixed, #3 disputed (cosmetic); tests only, so no new review |
| 5 | [05-tests.md](05-tests.md) | pass: 16/16, **100% line (56/56), 100% branch (6/6)**, AC1–AC9 proven |

## Done when (story-delivery)
- [x] Every AC maps to a test that ran in stage 5 and passed.
- [x] Review verdict `approve-with-nits` from a reviewer independent of the developer.
- [x] Profile gates pass according to their own reports (PERSONAL declares no coverage threshold).
- [x] Nothing pushed, merged or published.
- [x] This file lists the pending items.

## Pending
1. **Harness bug, `maestri-roles.ps1` generator**: the `(?m)\bQA\b` check matches the global role
   "QA Frontend Atlas". The script then runs `role write 'QA'`, which fails, and still exits 0, so the QA role
   is never created. Suggested fix: match the exact role name in quotes (`"QA"`) and stop on a non-zero exit of
   the CLI. Here the orchestrator created the role by hand.
2. **Floor environment**: the Maestri floor copy of the ground's untracked files left out `.venv/.../coverage/`
   (the dist-info was copied). Fixed with `python -m uv sync --reinstall-package coverage`. Plain
   `uv run pytest` in a floor may use launchers that point at the ground (R1). Worth documenting in
   `DOCS/maestri.md`.
3. Review nit #3 (`domain.py:44`, inline `Decimal("0.00")`): disputed by the developer, cosmetic, for the owner to decide.
4. Accepted assumption A2: `total`/`payable` aren't rounded, so a sub-cent `unit_price` gives `payable` with more
   than 2 decimals. Possible follow-up story: restrict `unit_price` to 2 decimals.
5. This file and the final `00-orchestration.md` were written after commit `aa6791e` and **aren't committed** yet.

## Authorization requests (Gustavo)
- Owner validation of the change (`owner-validation`).
- Whether to commit `07-close.md` + the final `00-orchestration.md`, and then land / push / PR the
  `demo/demo-1` branch. **Nothing has been done**: those decisions are yours.
- Step 3 of the runbook (outside verification and `compatibilidade.md`).
