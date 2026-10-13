# Orchestration — DEMO-1
- persona / tool / model: orchestrator / claude-code (Maestro Mode) / claude-opus-5-5
- story: `EXAMPLES/demo-python-api/STORY.md` (volume discount on quotes)
- workflow: `story-delivery` (task feature, profile PERSONAL)
- floor: `DEMO-1`, branch `demo/demo-1` (git worktree)

## Team
| Codename | Persona | Tool / model |
|---|---|---|
| Lodestar | analyst | claude-code / claude-opus-5-5 |
| Rivet | developer | opencode / opencode-go/deepseek-v4.1-flash |
| Plumb | reviewer | claude-code / claude-sonnet-5-5 (independent of the developer's model) |
| Sieve | qa | opencode / opencode-go/deepseek-v4.1-flash |

## Setup notes
- `maestri-roles.ps1` created Analyst, Developer, Orchestrator, Reviewer and Support, but **not QA**: its `(?m)\bQA\b` check matched the existing global role "QA Frontend Atlas", so it ran `role write 'QA'` ("No role named 'QA'") and still exited 0. The orchestrator created the QA role by hand with the same generated prompt. Generator bug to fix in the harness.

## Decisions
- R1 (analyst): copied `.venv` launchers may resolve to the ground checkout. All agents must run `python -m uv run python -m pytest ...`; the orchestrator verified that form imports `src/orders` from the floor.
- Floor venv repair (orchestrator, 2026-10-13T00:55Z): the floor `.venv` had `coverage-7.16.2.dist-info` but no `coverage/` package (the ground has both; the Maestri floor copy skipped the folder), so `import coverage` failed. Ran `python -m uv sync --reinstall-package coverage` (already locked; `pyproject.toml` and `uv.lock` unchanged). `coverage 7.16.2` imports now. No new dependency.
- After review (2026-10-13T00:56Z): send minor #1 and nit #2 (tests only) to the developer as stage 6 before QA. The change is not material (no production code), so per the loop rule it goes to stage 5, not back to stage 4. Nit #3 (cosmetic literal) is left to the developer's judgment.

## Stage log
| # | Stage | Persona (codename) | Tool / model | Started (UTC) | Finished (UTC) | Evidence | Outcome |
|---|---|---|---|---|---|---|---|
| 1–2 | Analysis + Plan | analyst (Lodestar) | claude-code / claude-opus-5-5 | 2026-10-13T00:49Z | 2026-10-13T00:52Z | 01-analysis.md, 02-plan.md | done: 9 ACs, 3-step plan, risk R1 (venv) |
| 3 | Development | developer (Rivet) | opencode / opencode-go/deepseek-v4.1-flash | 2026-10-13T00:51Z | 2026-10-13T00:55Z | 03-development.md | done: 3 files, 15 passed (baseline 5); coverage run deferred to QA |
| 4 | Independent review | reviewer (Plumb) | claude-code / claude-sonnet-5-5 | 2026-10-13T00:55Z | 2026-10-13T00:58Z | 04-review.md | approve-with-nits: 0 blocker, 0 major, 1 minor, 2 nit |
| 6 | Fix (review findings) | developer (Rivet) | opencode / opencode-go/deepseek-v4.1-flash | 2026-10-13T00:56Z | 2026-10-13T00:58Z | 06-fix.md | #1 fixed, #2 fixed, #3 disputed (cosmetic, reason recorded); 16 passed (re-run by orchestrator) |
| 5 | Tests and gates | qa (Sieve) | opencode / opencode-go/deepseek-v4.1-flash | 2026-10-13T00:58Z | 2026-10-13T01:00Z | 05-tests.md | pass: 16/16, 100% line, 100% branch (6/6), AC1–AC9 proven; re-run by orchestrator with identical numbers |
| 6b | Local commit | developer (Rivet) | opencode / opencode-go/deepseek-v4.1-flash | 2026-10-13T01:00Z | 2026-10-13T01:01Z | git log demo/demo-1 | aa6791e, 10 files (3 code/test + 7 evidence), local only, no hooks active |
| 7 | Close | orchestrator | claude-code / claude-opus-5-5 | 2026-10-13T01:01Z | 2026-10-13T01:01Z | 07-close.md | floor marked `review`; awaiting owner |

## Cost
Not measured: Maestri doesn't expose per-agent token cost to the orchestrator. Rivet's OpenCode TUI showed about $0.02 during stage 3. Claude Code recruits run on the Pro subscription.
