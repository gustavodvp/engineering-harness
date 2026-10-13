---
name: git-branches
description: Itaú branch convention - work on feature/<name> branches and never open pull requests targeting develop, because those PRs are created automatically when all Actions pass. Use when creating branches or preparing a change for integration.
license: MIT
metadata:
  harness.type: rule
  harness.scope: profile
  harness.profile: ITAU
  harness.version: 1.0.0
  harness.status: active
  harness.enforcement: mandatory
  harness.decides: "git.branch-pattern=feature/<name>; pr.target-develop=automatic-only"
  harness.reviewed: "2026-10-12"
  harness.tags: "git,branches,itau"
---

# Itaú: git branches

Source: conventions stated by the owner on 2026-10-12, pending confirmation against the real repository (`instructions-inventory`).

## Rules

1. Work on branches named `feature/<name>`, where `<name>` is short, lower-case and hyphenated, and describes the change. The `instructions-inventory` workflow confirms or extends the exact naming and any other prefixes.
2. **Never open a pull request targeting `develop`.** The PR to `develop` is created automatically from the `feature/...` branch once all GitHub Actions pass.
3. So "ready" means: the branch is pushed **with authorization** (rule `change-authorization`) and every Action is green. Then wait for the automatic PR instead of creating one.
4. If the Actions fail, fix the branch. Don't work around the automation.
