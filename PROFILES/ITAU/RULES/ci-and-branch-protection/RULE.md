---
name: ci-and-branch-protection
description: Itaú CI policy - never disable, skip or weaken GitHub Actions, branch protections or required checks. Use whenever a pipeline or protection blocks a change.
license: MIT
metadata:
  harness.type: rule
  harness.scope: profile
  harness.profile: ITAU
  harness.version: 1.0.0
  harness.status: active
  harness.enforcement: mandatory
  harness.decides: "ci.disable-checks=forbidden"
  harness.reviewed: "2026-10-12"
  harness.tags: "ci,github-actions,itau"
---

# Itaú: CI and branch protection

Source: conventions stated by the owner on 2026-10-12.

This complements the generic `change-authorization` rule (same decision, `ci.disable-checks=forbidden`) and is **mandatory**.

## Rules

1. Never disable, skip, re-run-until-green or edit GitHub Actions workflows, required checks or branch protection rules to get a change through.
2. Workflow files under `.github/` get changed only when the story is explicitly about CI, and with authorization.
3. When an Action fails, collect its log, diagnose the cause (`systematic-debugging`) and fix the code or the test.
