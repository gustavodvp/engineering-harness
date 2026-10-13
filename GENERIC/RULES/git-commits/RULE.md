---
name: git-commits
description: Commit message and history hygiene. Conventional Commits, small coherent commits, no secrets or generated noise. Use whenever creating commits or preparing a branch for review.
license: MIT
metadata:
  harness.type: rule
  harness.scope: generic
  harness.version: 1.0.0
  harness.status: active
  harness.enforcement: default
  harness.decides: "git.commit-style=conventional-commits; git.merge-strategy=repository-policy"
  harness.sources: "https://www.conventionalcommits.org/en/v1.0.0/, https://git-scm.com/docs/git-commit"
  harness.reviewed: "2026-10-12"
  harness.tags: "git,commits"
---

# Git commits

## Rules

1. Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/): `type(scope): summary`, where type is one of `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore` or `revert`. Mark breaking changes with `!` or a `BREAKING CHANGE:` footer.
2. The summary says **what changed for a reader of the history**, in the imperative mood, under 72 characters. The body explains *why* when the reason isn't obvious.
3. Each commit is one coherent change that builds and passes tests. Don't mix refactoring and behaviour changes when you can separate them.
4. Never commit secrets, credentials, `.env` files, local paths with personal data, build output or editor files. Check `git diff --staged` before committing.
5. Don't rewrite history that others have already fetched (no force-push to shared branches) unless the repository policy allows it and the user asked for it.
6. Merge strategy follows the repository policy (`git.merge-strategy=repository-policy`). Profiles may override it explicitly (for example, squash).
7. Before starting work on a shared repository, `git fetch` and update the working branch. If local changes conflict, stop and report; never discard them.

## Checklist before committing

- [ ] `git status` shows only intended files.
- [ ] Tests relevant to the change ran and their output was inspected.
- [ ] Message follows the convention and explains why.
