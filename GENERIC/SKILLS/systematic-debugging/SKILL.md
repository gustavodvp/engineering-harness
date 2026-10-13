---
name: systematic-debugging
description: Root-cause-first debugging - read the error, reproduce, check recent changes, instrument component boundaries, form and test one hypothesis at a time, fix at the source with a regression test. Use for any bug, test failure, CI failure, incident or unexpected behaviour, before proposing a fix.
license: MIT (adapted from obra/superpowers systematic-debugging, MIT, Copyright (c) Jesse Vincent)
metadata:
  harness.type: skill
  harness.scope: generic
  harness.version: 1.0.0
  harness.status: active
  harness.applies-to: "task:bugfix,incident,support,feature,refactor"
  harness.sources: "https://github.com/obra/superpowers/tree/main/skills/systematic-debugging, https://sre.google/sre-book/effective-troubleshooting/"
  harness.reviewed: "2026-10-12"
  harness.tags: "debugging,troubleshooting"
---

# Systematic debugging

**Iron law: no fix without root-cause investigation first.** A fix aimed at the symptom is a failure, even when the test turns green.

## Phase 1: Investigate

1. **Read the error completely**: the message, the full stack trace, the file:line references and error codes. Warnings before the error matter.
2. **Reproduce it reliably**: write down the exact steps, inputs and environment. If you can't reproduce it, gather more data (logs, metrics, request ids) instead of guessing.
3. **Check what changed**: `git log`/`git diff` since it last worked, dependency bumps, config, environment, data.
4. **Multi-component systems** (CI → build → deploy, API → service → DB → queue): instrument **each boundary** once by logging what enters and leaves, and whether config and environment propagate. Then find *where* it breaks before asking *why*.
5. **Trace the data flow backwards** from the bad value to where it originates, and fix it there.

## Phase 2: Compare

- Find similar code in the same codebase that works and list **every** difference, however small.
- When implementing a known pattern, read the reference implementation completely.

## Phase 3: Hypothesis and test

1. Write down one hypothesis: "X is the root cause because Y".
2. Make the **smallest** change or experiment that tests it, changing one variable at a time.
3. If it's confirmed, go to phase 4. If not, form a new hypothesis and **revert** the experiment. Don't stack fixes.
4. After three failed hypotheses, step back: question the architecture or your assumptions, and ask for help or a second opinion (another persona or model).

## Phase 4: Fix

1. Write a test that reproduces the bug and fails.
2. Fix the root cause, at the source.
3. Run the new test and the whole relevant suite, and inspect the output.
4. Look for the same bug elsewhere (same pattern, same misuse).
5. Record the cause, the evidence and the fix in the evidence file (`03-development.md` or `03-diagnosis.md`).

## Red flags (stop and go back to phase 1)

- "Let me just try…", or changing several things at once.
- Adding retries, sleeps, `try/catch` or null checks without knowing why the value is wrong.
- The fix works, but you can't explain why.
- Disabling a test or a check to get past the failure.
