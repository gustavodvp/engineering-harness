---
name: personal-git-flow
description: Personal repository flow - fetch and pull before starting, one worktree or Maestri floor per task, squash merge with a friendly Conventional Commit message, delete the branch and worktree, and update the control-plane submodule pointer. Use for any task in the owner's GitHub repositories.
license: MIT
metadata:
  harness.type: rule
  harness.scope: profile
  harness.profile: PERSONAL
  harness.version: 1.0.0
  harness.status: active
  harness.enforcement: default
  harness.decides: "git.merge-strategy=squash; git.task-isolation=worktree-or-floor"
  harness.overrides: "generic/rule/git-commits#git.merge-strategy"
  harness.reviewed: "2026-10-12"
  harness.tags: "git,personal,maestri"
---

# Personal git flow

Migrated from the vault note `padrao-fluxo-dev` (2026-10-12).

## Rules

1. **Before starting**: `git fetch` + `git pull --ff-only` (or `--rebase` on a task branch). In the control-plane (`D:\00_Vault\.dados\repos`), also run `git submodule update --init`. If there are conflicts or uncommitted local changes, stop and report; discard nothing.
2. **Isolation**: every task gets its own worktree (`scripts/create-worktree.sh` of the control-plane) or Maestri floor. Never switch the branch of a shared checkout in `projects/<name>`.
3. **Finishing**: squash merge the task branch into the main branch (`git merge --squash` or "Squash and merge") as **one** commit with a friendly, descriptive message in Portuguese, in the style `feat(dashboard): mostra quando a fatura foi paga`. No "wip", "fix 2" or branch names.
4. **Clean-up**: delete the branch, both local and remote (`git branch -D`, `git push origin --delete`), and the worktree or floor (`git worktree remove` / `maestri floor delete`). Leave no branch, worktree or pending commit behind. On Windows, first remove `node_modules` junctions with `cmd /c rmdir`.
5. **After the merge**: in the control-plane, `git add projects/<name>` and commit `chore(meta): atualiza ponteiro de submodule <name>`.
6. **Pushing** follows `change-authorization` and `owner-validation`.
7. **Several agents in one tree**: check `git status` and `git log --stat` before assuming what has been committed.
8. **Maestri agents** start in `.maestri/roles/<id>`. Tell them to `cd` to the repository root and never to commit `.maestri/`. Restart a stuck recruit with `--replace`.
9. **Post-graduation repository (18SOAT)**: write commits in a team voice, **without** an AI `Co-Authored-By` trailer.
