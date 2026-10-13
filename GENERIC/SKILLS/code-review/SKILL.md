---
name: code-review
description: How to review a code change - what to look for in order (correctness, security, design, tests, readability), how to write actionable findings with severity and failure scenarios, and how to receive review feedback. Use when reviewing a diff or PR, or when responding to review comments.
license: MIT
metadata:
  harness.type: skill
  harness.scope: generic
  harness.version: 1.0.0
  harness.status: active
  harness.applies-to: "task:review,feature,bugfix,refactor"
  harness.sources: "https://google.github.io/eng-practices/review/reviewer/, https://github.com/obra/superpowers/tree/main/skills/requesting-code-review, https://github.com/obra/superpowers/tree/main/skills/receiving-code-review, https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html"
  harness.reviewed: "2026-10-12"
  harness.tags: "review,quality"
---

# Code review

The standard (Google eng-practices) is to approve once the change **improves the overall health of the code**, even if it isn't perfect.

## Prepare

1. Read the story and its acceptance criteria. Without knowing the intent you can't judge correctness.
2. Get the full diff against the real base (`git diff <base>...HEAD`) and the list of files. Look at the code around the changed lines, not only the hunks.
3. Note what you can run (tests, the app) and what you can't. Say so in the review.

## Look for, in this order

1. **Correctness**: does it do what the story says? Edge cases (empty, null, max, concurrent, retries, time zones), error paths, off-by-one errors, resource leaks, transactions and idempotency.
2. **Security**: input validation, authorization on every path, injection, secrets, sensitive data in logs, unsafe deserialization, SSRF, dependency risk. See `application-security-owasp`.
3. **Design**: does it fit the existing architecture, put responsibilities in the right place and avoid duplication? Is there anything speculative? Is the API easy to misuse?
4. **Tests**: would they fail without the change? Do they cover new conditions both ways and the failure paths? Are they at the right level?
5. **Readability**: names, size, comments explaining *why*, consistency with the surrounding code.
6. **Operability**: logs, metrics, migrations being reversible and safe for live data, config, backward compatibility of APIs and events.

## Write findings that can be acted on

Each finding should have:
- **severity**: `blocker` (wrong or unsafe, must fix), `major` (should fix before merge), `minor` (worth fixing) or `nit` (optional, style);
- **location**: `path:line`;
- **the problem and a concrete failure scenario**: "with an empty list, `items[0]` throws → 500 on `/orders`";
- **a suggested fix**, when it isn't obvious.

Comment on the code, not the author. Ask questions when you're unsure instead of asserting. Say what is good when it's notable. Leave out findings you can't support with a scenario, or mark them as questions.

## Receiving review

- Verify every comment against the code before acting. Reviewers can be wrong.
- Fix, or answer with a reason, or agree to defer with the approver's consent. Never silently ignore a comment.
- Don't argue style that a linter or the surrounding convention settles; follow the convention.
- After the fixes, re-run the tests and reply with what changed.
