---
name: personal-code-style
description: Owner's code style preferences - the simplest code the next agent can resume, strong typing, minimal dependencies (stdlib before frameworks), stack chosen for the load and the existing toolchain. Use for implementation in personal projects.
license: MIT
metadata:
  harness.type: rule
  harness.scope: profile
  harness.profile: PERSONAL
  harness.version: 1.0.0
  harness.status: active
  harness.enforcement: default
  harness.applies-to: "task:feature,bugfix,refactor,review"
  harness.decides: "deps.policy=stdlib-first"
  harness.reviewed: "2026-10-12"
  harness.tags: "style,personal,go"
---

# Personal code style

Migrated from the vault note `padrao-estilo-de-codigo` (2026-10-12). It complements the generic `code-quality` rule.

## Rules

1. Write code the next agent can resume without re-deriving context. No abstraction "for later".
2. Strong typing and testability are required even under time pressure: real structs and types, not loose maps.
3. Keep dependencies minimal: stdlib and simple code before frameworks, ORMs or heavy libraries. The Atlas Go pattern is `net/http`, `pgx` with hand-written SQL, and its own migrations.
4. Choose the stack that is most efficient **for the load**, weighing fit with the existing stack. One toolchain is worth more than a language that is "better on paper" (a new service in Go because Atlas is already Go).
5. Go projects follow the vault learning `aprendizado-go-module-layout`.
6. Dates without a time are `date`, not `timestamptz` (Atlas Go convention).
