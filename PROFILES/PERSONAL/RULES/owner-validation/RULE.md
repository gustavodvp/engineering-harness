---
name: owner-validation
description: For Atlas projects, run the real local stack and ask the owner to validate before any commit or push. Test with real HTTP round trips and load for cache or concurrency changes, against an isolated test database. Use when finishing development in personal projects.
license: MIT
metadata:
  harness.type: rule
  harness.scope: profile
  harness.profile: PERSONAL
  harness.version: 1.0.0
  harness.status: active
  harness.enforcement: default
  harness.applies-to: "task:feature,bugfix,refactor"
  harness.decides: "verification.owner-validation=before-commit-atlas; testing.database=isolated"
  harness.reviewed: "2026-10-12"
  harness.tags: "testing,validation,personal"
---

# Owner validation (personal projects)

Migrated from the vault note `padrao-fluxo-dev` (2026-10-12).

## Rules

1. **Atlas projects**: once the automated tests pass, start the local stack and **ask the owner to validate before `git commit`/`push`**. Automated tests have let through bugs that only show up in a real HTTP round trip (for example a `LazyInitializationException` in production).
2. **Cache and concurrency changes** need a real load test: log in and load the dashboard in a browser, not only `/health`.
3. **Isolated test database**: tests never point at the database the application uses. Use one fixed, reused test container rather than an anonymous container per test.
4. **Production checks are read-only**, and session cookies stay in memory only. The Claude Code permission classifier blocks sensitive production reads; ask the owner to grant them via `/permissions` instead of working around it.
5. Don't propose passive features (reminders, due-date alerts, goal bars) on your own initiative.
