---
name: ai-usage-budget
description: Itaú AI tool usage - corporate Claude (approx. USD 100 limit) and Devin (approx. USD 180 limit, several models via CLI) are configurable, unconfirmed parameters. Choose the cheapest adequate model per stage and log usage. Use when planning or delegating agent work.
license: MIT
metadata:
  harness.type: rule
  harness.scope: profile
  harness.profile: ITAU
  harness.version: 1.0.0
  harness.status: active
  harness.enforcement: default
  harness.decides: "ai.model-selection=cheapest-adequate; ai.usage-logging=per-stage"
  harness.reviewed: "2026-10-12"
  harness.tags: "ai,budget,models,itau"
---

# Itaú: AI usage budget

Source: stated by the owner on 2026-10-12. The values are in `PROFILES/ITAU/PROFILE.md` (`budgets`, `models`, `tools`) and all of them are `confirmed: false`.

## What is known (to be confirmed)

- **Claude** (corporate account): approximate limit of USD 100.
- **Devin**: approximate limit of USD 180, with several models available through the CLI.
- The unit, period and enforcement of these limits are **not** known yet. Don't assume they are API credits, a balance or interchangeable amounts.
- These tools exist only in the corporate environment, and nothing here applies to personal machines.

## Rules

1. Use the persona → model assignment from the profile: Opus for analysis and planning, Sonnet for orchestration, review and support, and a cheap Devin model for bulk implementation and test runs. When a cheaper model would do, use it, and escalate only with a stated reason (for example, two failed attempts or an architectural question).
2. Keep context small: load only the skills that `harness compose` selected, pass file paths instead of pasting whole files, and summarise between stages.
3. Log the tool, the model and the estimated usage of every stage in `00-orchestration.md`. When the remaining budget looks insufficient for the plan, stop and ask before continuing.
4. Never store account identifiers, tokens or invoices in the harness.
5. Once the real limits are confirmed, update `PROFILE.md`: set `confirmed: true` and record the unit and period, then bump this rule's version.
