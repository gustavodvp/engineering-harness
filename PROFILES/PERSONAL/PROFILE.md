---
name: PERSONAL
description: Personal environment (home PC and homelab). Personal workflow preferences and the agent and model setup used with Maestri, Claude Code and OpenCode.
status: active
extends: []
reviewed: "2026-10-13"
models:
  orchestrator:
    tool: claude-code
    model: claude-sonnet-5-5
    confirmed: true
    note: The Maestro (Claude Code, Maestro Mode) coordinates the Maestri canvas. Owner rule (2026-10-13) - the orchestrator always runs on the lighter model; only the analyst uses Opus.
  analyst:
    tool: claude-code
    model: claude-opus-5-5
    confirmed: true
    note: The only persona on Opus - planning and requirements are where the stronger model pays off.
  developer:
    tool: opencode
    model: opencode-go/deepseek-v4.1-flash
    confirmed: true
    note: ADR-0007 in the vault. It is the best cost-benefit for bulk code. Claude Code recruits get stuck on the trust prompt; OpenCode doesn't.
  reviewer:
    tool: claude-code
    model: claude-sonnet-5-5
    confirmed: true
    note: A different vendor from the developer, so the review stays independent.
  qa:
    tool: opencode
    model: opencode-go/deepseek-v4.1-flash
    confirmed: true
  support:
    tool: claude-code
    model: claude-sonnet-5-5
    confirmed: true
  harness-curator:
    tool: claude-code
    model: claude-sonnet-5-5
    confirmed: true
    note: Judgment over logs and rules; Sonnet balances quality and cost. Runs after delivery.
tools:
  claude-code:
    available: true
    confirmed: true
  opencode:
    available: true
    confirmed: true
  maestri:
    available: true
    confirmed: true
    note: Maestri 0.22.1 is in use on Windows with the Vault workspace; the 0.23.0 portable is kept as a Release asset.
  devin:
    available: false
    confirmed: true
    note: Devin is a corporate-only tool.
---

# Profile PERSONAL

Personal projects (Atlas, homelab, portfolio, studies). Rules here are **preferences of the owner** and don't apply to any company.

## Rules in this profile

- `personal-git-flow`: sync before starting, squash merge with a friendly message, clean up branches and worktrees, update the control-plane submodule pointer.
- `owner-validation`: run the local stack and get the owner's validation before committing or pushing on Atlas projects, using real round trips and isolated test databases.
- `personal-code-style`: few dependencies, strong typing, the stack chosen for the load.

The vault (`D:\00_Vault`) points here for engineering standards; this profile is canonical.
