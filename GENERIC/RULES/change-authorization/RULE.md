---
name: change-authorization
description: Outward-facing or irreversible actions (push, PR, merge, release, deploy, delete, disabling checks) require explicit human authorization. Use before any action that leaves the local working copy.
license: MIT
metadata:
  harness.type: rule
  harness.scope: generic
  harness.version: 1.0.0
  harness.status: active
  harness.enforcement: mandatory
  harness.decides: "change.publish=explicit-authorization; ci.disable-checks=forbidden"
  harness.sources: "https://owasp.org/www-project-top-10-for-large-language-model-applications/"
  harness.reviewed: "2026-10-12"
  harness.tags: "safety,git,ci"
---

# Change authorization

This rule is **mandatory**. No profile, project or story can relax it.

## Rules

1. These actions need an explicit "yes" from the responsible human **for this specific change**: `git push`, opening or updating a pull request, merging, tagging or releasing, deploying, deleting branches, files or data outside the task's scratch area, and changing shared configuration. Approval of one change doesn't carry over to another.
2. Never disable, skip or weaken CI checks, required reviews, branch protections, hooks (`--no-verify`) or quality gates to get a change through. If a check blocks the work, report the failure and its output.
3. Before deleting or overwriting anything, look at it and say what will be lost.
4. Run production checks **read-only**. Never write to production data from an agent session.
5. When unsure whether an action is reversible, treat it as irreversible.
