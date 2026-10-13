# Retrospective — DEMO-1
- persona / tool / model: harness-curator (Ledger) / claude-code / claude-sonnet-5-5
- workflow: `run-retrospective` v1.0.0 (stage 8 of `story-delivery`)
- inputs: `00..07-*.md`, `08-usage.md` / `08-usage.json` (measured), `.harness/resolution.md`, persona headers, `maestri-roles.ps1`
- earlier retrospectives: none in `.harness/runs/` (this is the first), so no recurrence can be assessed yet
- status: **proposals only**. Nothing was applied; the owner decides each one (stage 5 of the workflow).

## Summary

The run delivered the story correctly and cheaply: 9/9 ACs proven, 16/16 tests, 100% line and branch coverage, an independent review (Sonnet 5.5 vs DeepSeek) and a fix loop that respected the loop rule. The model assignments of the PERSONAL profile were honoured for all four personas.

The waste and risk are in the surroundings of the code:

1. Two environment faults in the floor (a copied `.venv` with launchers pointing at the ground, and a copy that lost the `coverage/` package) cost a false-green risk and a stage-3 deviation.
2. The Maestri QA role was not created by the generator (already fixed after the run, see F2).
3. Cache reads are large in absolute terms (7.58 M tokens) and the two bulk executors read the most per unit of output.
4. The orchestration evidence says cost is "not measured", which `harness usage` now contradicts.

## Measured usage (from `08-usage.md`)

Window: 2026-10-13T00:47:16Z → the time `harness usage` ran. It therefore includes the closing turns of the orchestrator, the relay agent and this retrospective (Ledger).

| Agent | Persona | Tool / model | Turns | Output | Cache read | Cache write | Cost (USD) | Tool calls | Tool errors |
|---|---|---|---|---|---|---|---|---|---|
| Lodestar | analyst | claude-code / opus-5-5 | 20 | 17,718 | 1,366,042 | 54,164 | n/a (tokens only) | 17 | 4 |
| Rivet | developer | opencode / deepseek-v4.1-flash | 50 | 25,709 | 2,086,528 | 0 | 0.0322 | 59 | 2 |
| Plumb | reviewer | claude-code / sonnet-5-5 | 8 | 4,887 | 481,291 | 45,511 | n/a | 7 | 0 |
| Sieve | qa | opencode / deepseek-v4.1-flash | 25 | 10,978 | 869,760 | 0 | 0.0170 | 35 | 0 |
| Claude Code (Maestro) | orchestrator | claude-code / opus-5-5 | 25 | 17,823 | 2,181,785 | 40,233 | n/a | 23 | 1 |
| Claude Code #2 | relay | claude-code / opus-5-5 | 10 | 2,885 | 513,591 | 26,883 | n/a | 10 | 0 |
| Ledger | curator (this run) | claude-code / sonnet-5-5 | 2 | 551 | 77,295 | 18,514 | n/a | 3 | 0 |
| **Total** | | | 140 | 80,551 | 7,576,292 | 185,305 | **0.0492 (OpenCode only)** | 154 | 7 |

- **Cost.** Only OpenCode reports a price: **USD 0.0492** for Rivet and Sieve. Claude Code reports tokens, not cost (subscription or API billing is not visible), so the five Claude Code agents are **measured in tokens and not priced**. No price was estimated.
- **Not measured.** Every agent of the run was measured. None used a tool without a usage source.
- **Cross-check.** The orchestrator noted "about $0.02" for Rivet during stage 3 (`00-orchestration.md`, Cost). The measured total for Rivet over the whole run is USD 0.0322, which is consistent.

## Findings

Severity is `high`, `medium` or `low`. Descriptions are blameless: they state the conditions, not who acted.

### F1 — Copied `.venv` gives a false green (high, environment + missing instruction)
- Evidence: `01-analysis.md` risk R1 and its probe (`uv run pytest` imports `src/orders` from the ground checkout; `uv run python -m pytest` imports the floor's); `00-orchestration.md` Decisions R1; `07-close.md` Pending 2.
- Impact: tests on unchanged code would have passed and the stage evidence would have looked valid. It was caught only because the analyst probed it. The workaround ("always use `python -m uv run python -m pytest`") had to be repeated in the plan and in the header of 03, 05 and 06, and the reviewer's allowed command was limited to that form.
- Which unit would have prevented it: none; this is a gap. No rule or workflow tells a floor-based run to verify which interpreter and source tree the tests import.

### F2 — QA role not created by the role generator (high when it happened; already fixed)
- Evidence: `00-orchestration.md` Setup notes (the `(?m)\bQA\b` check matched the global role "QA Frontend Atlas", `role write 'QA'` returned "No role named 'QA'", and the script exited 0); `07-close.md` Pending 1.
- Impact: the QA stage would have had no role. The orchestrator created it by hand.
- Current state: `EXAMPLES/demo-python-api/.harness/maestri-roles.ps1` (commit `95c2064`, after the run) now uses `role write` then falls back to `role create` when `$LASTEXITCODE -ne 0` or the output matches `No role named`, and throws if `create` fails. The generated script no longer shows the `\bQA\b` match. This looks resolved. I did not run it, so the proposal below asks for a regression test instead of a fix.
- Classification: tool limitation (silent success on failure) plus wrong command (substring match on a role name).

### F3 — Floor copy of `.venv` lost `coverage/` (medium, environment)
- Evidence: `03-development.md` Commands (`ModuleNotFoundError: No module named 'coverage'`) and Deviations 1; `00-orchestration.md` Decisions (repair with `uv sync --reinstall-package coverage`); `05-tests.md` command (b) confirms the repair.
- Impact: the plan's coverage step was blocked and recorded as "pending" in stage 3, a reviewer note ("Not reviewed / not run") and a second stage-5 pass. The dev had to choose between installing a dependency (forbidden by A5) and reporting a deviation; the deviation was the right call but it cost a round trip.
- Same root cause as F1 (the floor creation copies untracked files imperfectly). Recurs with F1 in the same run.

### F4 — Tool errors (7 in total), classified
| Agent | Error text (from `08-usage.md`) | Class | Notes |
|---|---|---|---|
| Rivet | `bash: RTK_DISABLED=1 git diff -- src tests (exit 1)` | wrong command | PowerShell/POSIX mixed syntax in OpenCode's bash tool on Windows. The `exit 1` may also be `git diff --exit-code` semantics, which the usage report does not distinguish. |
| Rivet | `bash: maestri check "Rivet" 2>&1 \| Select-Object -Last 30 (exit 1)` | wrong command | A PowerShell pipe (`Select-Object`) inside a bash tool. The same shell mix as above. |
| Claude Code (Maestro) | `Blocked: sleep 150 followed by: maestri check "Plumb" tail -25 ...` | tool limitation | The harness blocks foreground `sleep`; the orchestrator was polling a teammate. The tool's own message points to Monitor. |
| Lodestar | `Exit code 2`, `Exit code 1` ×3 | not classifiable | The usage report keeps only the exit code, not the command. The analyst's evidence lists only commands that exited 0 and throwaway probes. These are likely probes, but that is not proven. |
- Recurrence: the shell-syntax mix (2 of 7) and polling (1 of 7) are the patterns to watch in the next run.
- Gap in the measurement itself: for 4 of 7 errors the report cannot tell what failed. See proposal P4.

### F5 — Cache-read volume is high relative to output (medium, waste)
- Evidence: `08-usage.md` — total cache read 7,576,292 vs output 80,551 (94:1). The ratio per agent: Rivet 81:1 (2,086,528 / 25,709), Sieve 79:1, Lodestar 77:1, Plumb 98:1, Maestro 122:1.
- Impact: Rivet (50 turns, 59 tool calls) and Sieve (25 turns, 35 tool calls) are the cheap executor, so the price is small (USD 0.0492 for both). The cost to watch is the Claude Code side, which is not priced but is token-heavy: the orchestrator alone read 2.18 M tokens for 25 turns, mostly waiting on teammates.
- Caveat: cache reads are re-reads of the same growing conversation, so this number is mostly turns × context size. It is a signal about turn count and context size, not about files read. The usage report does not break down repeated file reads, so I make no claim about duplicate reads.
- Candidate causes visible in the evidence: Sieve was verification-only (no edits) yet took 25 turns; it read nine input files (`05-tests.md` header) including the whole run history.

### F6 — Orchestrator polls teammates instead of waiting on an event (low, waste)
- Evidence: the blocked `sleep 150 && maestri check "Plumb"` (F4); the orchestrator's 25 turns and 2.18 M cache read versus 17 tool calls of useful work in `00-orchestration.md`.
- Impact: unknown in tokens (one blocked call is the only direct evidence). Recorded as low until the next run shows whether it recurs.

### F7 — Orchestration evidence says cost is not measurable (low, stale instruction)
- Evidence: `00-orchestration.md` Cost: "Not measured: Maestri doesn't expose per-agent token cost to the orchestrator". `harness usage --maestri-workspace ... --floor ...` did produce per-agent tokens and OpenCode cost for this run.
- Impact: the orchestrator's stage 0 evidence is wrong after the fact, and a reader may think cost is unavailable. The sentence is true of the orchestrator's own tooling at the time, not of the harness.

### F8 — Timestamps in the evidence are inconsistent (low, evidence quality)
- Evidence: `00-orchestration.md` Stage log shows 6 (fix) starting at 00:56Z while 4 (review) finishes at 00:58Z; `03-development.md` says started 00:52Z while the stage log says 00:51Z.
- Impact: durations cannot be computed reliably from the stage log, so stage durations (item 2 of the workflow) are not reported here. The cause is either overlapping work (the developer started the fix from the reviewer's verbal findings) or hand-entered times; the evidence does not say which.

### F9 — Process conformance (no finding; for the record)
- Routing followed the table: analyst/orchestrator on Opus, developer/QA on the cheap model, reviewer on Sonnet; `04-review.md` header confirms an independent model.
- Every stage 0–7 left evidence. The fix (test-only) correctly skipped a second review under the loop rule (`00-orchestration.md` decision). Nothing was pushed (`07-close.md`). The nit dispute in `06-fix.md` has a recorded reason.
- Parallelism: stage 3 started at 00:51 while stage 1–2 finished at 00:51/00:52; the other stages were sequential by dependency. No missed parallelism is visible.
- The `owner-validation` gate was recorded as pending, not skipped.

## Proposals

Grouped by target file. Each one needs the owner's decision (accept / reject / defer) and then the `knowledge-evolution` workflow on a branch of the harness repository, with `harness lint --strict` and `pytest`. Priority is the order I suggest. Targets were checked to exist in this repository at the time of writing, except where noted.

### P1 — Verify the interpreter and source tree before testing in a floor (priority 1, from F1, F3)
- Target: `GENERIC/WORKFLOWS/story-delivery/WORKFLOW.md` (stage 1, "Analyse").
- Classification: generic (applies to any run in a worktree or Maestri floor, any stack).
- Change (add one bullet to the analysis stage; minor version bump, e.g. 1.x.0 → 1.(x+1).0):
  > In a worktree, a floor or any copied checkout, prove that the test command imports the code of **this** checkout before recording a baseline: run a throwaway probe that prints the interpreter path and the package `__file__`. If either points outside the checkout, record it as a risk in `01-analysis.md` and write the corrected command in `02-plan.md`. Every later stage uses that command.
  > Also run the coverage tool once (`--version` or a dry import) to detect a missing package before stage 3.
- Expected measurable effect: next run has zero stage-3 "pending" deviations caused by tooling, and `01-analysis.md` contains a probe with the paths. Test: count deviations tagged "tooling" in `03-development.md` (this run: 1).
- Not proposed: forbidding `uv run pytest`. That is a stack-specific fact (Python/uv); if the owner wants it written down, it belongs in a Python skill or in `DOCS/maestri.md`, not in a generic rule.

### P2 — Document the floor-copy limits and the command form (priority 2, from F1, F3)
- Target: `DOCS/maestri.md`.
- Classification: environment (Maestri adapter documentation).
- Change: add a short "Known limits of floors" section: (a) a floor copy of untracked files can carry launchers that point at the ground; use `python -m uv run python -m pytest`; (b) a floor copy can omit packages inside `.venv` (seen: `coverage/`); repair with `python -m uv sync --reinstall-package <name>` when the lock already contains it; (c) do not mix PowerShell and POSIX syntax in OpenCode's bash tool (F4).
- Version bump: none declared for docs in this repository; keep the `knowledge-evolution` record in the commit message.
- Expected effect: the orchestrator's `00-orchestration.md` no longer needs to rediscover (a) and (b); `07-close.md` "Floor environment" item disappears from Pending. Related: `07-close.md` Pending 2 already suggests this.

### P3 — Regression test for the role generator (priority 3, from F2)
- Target: `TOOLS/harness/adapters.py` (the source of `maestri-roles.ps1`), with a test in the repository test suite.
- Classification: environment (Maestri adapter tool).
- Change: the generated script already handles the failure (commit `95c2064`). Add a test that renders the script and asserts that every `role write` is followed by the `-ne 0 -or ... 'No role named'` check and a `create` fallback that throws; and that no role name is matched by a word-boundary regex. This keeps the F2 fix from regressing.
- Expected effect: a regression of F2 fails `pytest` instead of silently exiting 0 at team setup.
- Note: if the test already exists, close this proposal as `no_change_needed`; I did not search the test directory for it.

### P4 — Keep the failing command in the usage report's tool errors (priority 4, from F4)
- Target: `TOOLS/harness/` usage module (the code behind `harness usage`; I did not open it, so the exact file must be confirmed before the proposal is accepted) and `GENERIC/WORKFLOWS/run-retrospective/WORKFLOW.md` stage 1 (one sentence).
- Classification: generic (the tool and the workflow).
- Change: when a Claude Code tool result is an error that only carries `Exit code N`, join it with the `tool_use` input (command, truncated to about 160 characters) the way OpenCode errors already show `bash: <command> (exit 1)`. This makes the classification of F4 possible for every agent.
- Expected effect: next run's `08-usage.md` has a command for 100% of tool errors (this run: 3 of 7 have one; the 4 Lodestar errors do not).

### P5 — Tell the orchestrator how to wait for teammates (priority 5, from F4, F6)
- Target: `AGENTS/orchestrator/AGENT.md`.
- Classification: generic.
- Change: add to the stage-waiting guidance: "Do not wait with a foreground `sleep` followed by `maestri check`. Wait for the teammate's `maestri ask` reply, or poll with a Monitor `until` loop, and cap the check interval."
- Expected effect: zero blocked-`sleep` tool errors for the orchestrator next run (this run: 1). A fall in the orchestrator's turn count (25) is a hoped-for secondary effect, but this run does not prove polling was its cause, so I do not claim one.
- Priority is low because the evidence is one error; the proposal should be deferred if the owner prefers to wait for a second occurrence.

### P6 — Fix the stale cost sentence and the timestamp convention in the orchestrator's stage log (priority 6, from F7, F8)
- Target: `AGENTS/orchestrator/AGENT.md` (the template section for `00-orchestration.md`; if the template lives in `TEMPLATES/`, change it there).
- Classification: generic.
- Change: (a) replace the "Cost: not measured" convention with "Cost: see `08-usage.md` after stage 8; do not estimate." (b) State that stage-log times are copied from each stage file's header, not written from memory, and that overlapping stages are marked as overlapping.
- Expected effect: `00-orchestration.md` Cost points to `08-usage.md`; stage log times are consistent with the headers in the next run (this run: at least 2 mismatches).

### Not proposed (explicitly)
- Changing the model assignments: they were respected and the cost of the cheap executors is USD 0.0492 for the whole run; the evidence gives no reason to move work between models.
- Reducing the number of stages or merging the QA stage into the developer's: the QA pass caught nothing new, but the review (independent model) found a real test gap (F-04-1, multi-line aggregation through the API), and the `owner-validation` gates depend on this separation. One run does not justify removing a stage.
- Anything about the product code: the review's nit #3 and the sub-cent rounding follow-up (A2) are product decisions, recorded in `07-close.md` Pending for the owner.

## Handoff (for the owner)

- Retrospective: `EXAMPLES/demo-python-api/.harness/runs/DEMO-1/08-retrospective.md`; usage: `08-usage.md` and `08-usage.json` in the same folder.
- Total measured cost: **USD 0.0492** (OpenCode: Rivet 0.0322, Sieve 0.0170). Claude Code agents measured in tokens only: 7.58 M cache read and 80.6 k output across the whole window, no price.
- Top three by expected impact: **P1** (floor false-green check), **P2** (floor limits documented), **P3** (role generator regression test).
- Files that the proposals would change: `GENERIC/WORKFLOWS/story-delivery/WORKFLOW.md`, `DOCS/maestri.md`, `TOOLS/harness/adapters.py` (plus a test), the `harness usage` module and `GENERIC/WORKFLOWS/run-retrospective/WORKFLOW.md`, and `AGENTS/orchestrator/AGENT.md`.

## Owner decisions

| Proposal | Decision (accept / reject / defer) | Reason |
|---|---|---|
| P1 | accept | applied: `story-delivery` 1.2.0, "Checkout check (stage 1)" |
| P2 | accept (part c only) | (a) and (b) were already in `DOCS/maestri.md` after the run; (c), mixed shell syntax, was added |
| P3 | no_change_needed | the regression test already exists (`TESTS/test_export.py`, asserts there is no `(?m)` regex, the `No role named` fallback and `role create 'QA'`) |
| P4 | accept | applied: `harness usage` joins each Claude Code `tool_result` error with its `tool_use` input. Re-run on DEMO-1: 7/7 errors now show the command. It also revealed that a recruit ran `maestri-roles.ps1` (role commands are Maestro-only), so the script now fails fast with a clear message |
| P5 | accept | applied: `orchestrator` 1.2.0, responsibility 8 (wait on the ask-back reply, no `sleep` + `check`) |
| P6 | accept | applied: `orchestrator` 1.2.0, responsibility 9 (times copied from the evidence headers, cost points to `08-usage.md`) |

Decided by the owner on 2026-10-13; applied through `knowledge-evolution` (lint --strict and 43 tests green).
