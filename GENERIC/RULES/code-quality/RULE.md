---
name: code-quality
description: Readability, simplicity and testability rules for any language - small focused units, explicit types, minimal dependencies, tests with every behaviour change. Use on implementation, refactoring and review tasks.
license: MIT
metadata:
  harness.type: rule
  harness.scope: generic
  harness.version: 1.0.0
  harness.status: active
  harness.enforcement: default
  harness.applies-to: "task:feature,bugfix,refactor,review"
  harness.decides: "quality.tests-with-change=required"
  harness.sources: "https://google.github.io/eng-practices/review/reviewer/looking-for.html, https://martinfowler.com/bliki/BeckDesignRules.html"
  harness.reviewed: "2026-10-12"
  harness.tags: "quality,maintainability"
---

# Code quality

## Rules

1. Write for the **next reader**, human or agent. Clear names, small functions with one job, and no cleverness that needs a comment to be understood.
2. Follow the surrounding code: its idioms, naming, error handling, comment density and layout. Consistency beats personal preference.
3. Use strong typing: real types, records, structs or dataclasses at boundaries instead of loose maps or dictionaries.
4. Keep it simple ([Beck's rules](https://martinfowler.com/bliki/BeckDesignRules.html)): passes the tests, reveals intention, no duplication, fewest elements. Don't add speculative abstractions, flags or extension points "for later".
5. Every behaviour change ships with tests at the cheapest level that proves it (see the `testing-strategy` skill). A bug fix starts with a test that fails without the fix.
6. Handle errors deliberately: no swallowed exceptions or silent defaults. Errors carry context.
7. Delete dead code instead of commenting it out, because git keeps the history.
8. Keep the diff focused on the task. Unrelated clean-ups go in a separate commit or story.
