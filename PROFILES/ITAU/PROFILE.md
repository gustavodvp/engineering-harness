---
name: ITAU
description: Corporate environment profile (Itaú). Holds only technical and operational conventions provided by the owner, with no business knowledge. Every value is pending confirmation in the authorized environment.
status: active
extends: []
reviewed: "2026-10-12"
models:
  orchestrator:
    tool: claude-code
    model: claude-sonnet-5-5
    confirmed: false
    note: Sonnet is enough for routing and tracking; confirm the model list of the corporate Claude account.
  analyst:
    tool: claude-code
    model: claude-opus-5-5
    confirmed: false
    note: Best for planning and requirements. Most expensive, so reserve it for stages 1-2.
  developer:
    tool: devin
    model: deepseek-v4.1-flash
    confirmed: false
    note: Bulk implementation on the Devin CLI with a cheap model. Confirm which models the corporate Devin CLI offers.
  reviewer:
    tool: claude-code
    model: claude-sonnet-5-5
    confirmed: false
    note: Independent from the developer (different vendor/model).
  qa:
    tool: devin
    model: deepseek-v4.1-flash
    confirmed: false
  support:
    tool: claude-code
    model: claude-sonnet-5-5
    confirmed: false
  harness-curator:
    tool: claude-code
    model: claude-sonnet-5-5
    confirmed: false
    note: Consumes the Claude budget; run per story only when the budget allows, otherwise weekly over several runs.
  frontend:
    tool: claude-code
    model: claude-sonnet-5-5
    confirmed: false
  devops:
    tool: claude-code
    model: claude-sonnet-5-5
    confirmed: false
  dba:
    tool: claude-code
    model: claude-sonnet-5-5
    confirmed: false
budgets:
  claude:
    approx-limit: "100"
    unit: USD (to confirm - not assumed to be API credits or a balance)
    period: to confirm
    confirmed: false
  devin:
    approx-limit: "180"
    unit: USD (to confirm - not assumed to be API credits or a balance)
    period: to confirm
    confirmed: false
    note: Different models are accessible through the CLI. The limits are not interchangeable with the Claude one.
tools:
  claude-code:
    available: true
    confirmed: false
  devin:
    available: true
    confirmed: false
  maestri:
    available: false
    confirmed: false
    note: Corporate approval unknown. The binary is unsigned (0.23.0 portable). Without it, the orchestrator runs Claude Code subagents.
  opencode:
    available: false
    confirmed: false
---

# Profile ITAU

The corporate environment. This profile contains **only** the rules the owner provided on 2026-10-12. It is not an inventory of the company's requirements. Real conventions get discovered with the `instructions-inventory` workflow inside the authorized environment.

## Boundaries

- No business knowledge, proprietary code, customer names, internal hosts, URLs or credentials (rule `confidentiality`).
- The AI resources listed above belong to the corporate context and are **not** available on personal machines. The reverse also holds: personal tools and accounts are never used here.
- Every `confirmed: false` value must be checked against the real accounts before being relied on.

## Rules in this profile

- `git-branches`: branch naming and PRs to `develop`.
- `pull-requests`: PR and merge procedure, history hygiene.
- `ci-and-branch-protection`: never disable Actions or protections.
- `sonar-quality-gate`: >90% coverage on new code under the real quality gate.
- `ai-usage-budget`: tool limits and model choice.
- Workflow `instructions-inventory`: how to discover the real conventions of the monorepo.
