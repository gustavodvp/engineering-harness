---
name: pull-requests
description: Itaú PR and merge procedure - keep history free of unnecessary intermediate commits, use squash and merge when the approved procedure allows it, never create PRs, merge or publish without authorization. Use when integrating a change.
license: MIT
metadata:
  harness.type: rule
  harness.scope: profile
  harness.profile: ITAU
  harness.version: 1.0.0
  harness.status: active
  harness.enforcement: default
  harness.decides: "git.merge-strategy=squash-when-procedure-allows; git.intermediate-commits=avoid"
  harness.overrides: "generic/rule/git-commits#git.merge-strategy"
  harness.reviewed: "2026-10-12"
  harness.tags: "git,pull-requests,itau"
---

# Itaú: pull requests and merges

Source: conventions stated by the owner on 2026-10-12, pending confirmation (`instructions-inventory`).

## Rules

1. **History hygiene**: don't pollute the history with unnecessary intermediate commits ("wip", "fix typo", "try again"). Group the work into meaningful commits before pushing, and squash locally if needed. This rule wins over any habit of committing every small step.
2. **Squash and merge** when the approved procedure for the repository allows it. This overrides the generic `git.merge-strategy=repository-policy`. If the repository's real procedure says otherwise, the real procedure wins: record the conflict in `.harness/resolution.md` and report it.
3. **Never create PRs, merge or publish** (push, release, deploy) without the required authorization. This complements the generic `change-authorization` rule, which is mandatory anyway.
4. PR descriptions and commit messages contain only technical information about the change: no customer data, no internal links in harness files.
