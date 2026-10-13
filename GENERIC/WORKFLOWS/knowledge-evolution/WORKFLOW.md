---
name: knowledge-evolution
description: Controlled improvement of the harness itself - capture a better practice, classify it (generic, specialized, environment), source it, validate it, scrub confidential data, version it and integrate it with review. Use when proposing a new or changed skill, rule, workflow or profile.
license: MIT
metadata:
  harness.type: workflow
  harness.scope: generic
  harness.version: 1.0.0
  harness.status: active
  harness.applies-to: "task:docs,analysis"
  harness.sources: "https://agentskills.io/specification, https://semver.org/"
  harness.reviewed: "2026-10-12"
  harness.tags: "workflow,governance,harness"
---

# Knowledge evolution

## Inputs

- A discovery: a better practice, a recurring mistake, a new tool, or a stale or contradictory rule.
- The harness repository (a clone with `uv run harness lint` working).

## Stages

1. **Record** the discovery: the problem it solves, where it came from and the date. If no concrete problem exists, stop here, because "new" is not a reason to change.
2. **Classify** it. One of the three cases applies:
   - **generic** (true in any company) → `GENERIC/`;
   - **specialized technical skill** → `GENERIC/SKILLS/`;
   - **environment-specific** → `PROFILES/<ENV>/`.
   
   A company rule never moves into `GENERIC/` just because it was discovered while working there.
3. **Source** it: official documentation > verifiable code > a maintained project > a reproducible report. Record the URLs in `harness.sources`. For third-party skills, record the licence and add the candidate to `DOCS/avaliacao-de-skills.md`.
4. **Assess impact**: which units, profiles and decisions (`harness.decides`) are affected? Does it conflict with anything? Use `harness compose --dry-run` on a sample project for every profile.
5. **Propose** the change **in the canonical file** on a branch. Never edit generated files.
6. **Validate**: `uv run harness lint --strict` and `uv run pytest`, and for skills, `skills-ref validate` on the export.
7. **Scrub**: confirm there is no business data, code, names, hosts or credentials (rule `confidentiality`). Lint helps, but a human reads it too.
8. **Version** it: bump `harness.version` (patch = wording, minor = new guidance, major = changed or removed behaviour) and update `harness.reviewed`. Git keeps the history, and the commit message explains why.
9. **Fix references**: links, overrides that point at the unit, the README/DOCS indexes.
10. **Integrate** through review and squash merge, with an explicit approval from the owner. Then re-run `harness compose` in the projects that use the unit.

## Outputs

- A reviewed change to one or more canonical files, a version bump and passing validation.

## Done when

- [ ] The classification is justified and the unit lives in the matching tree.
- [ ] Sources are cited, and the licence is compatible for adapted third-party content.
- [ ] `harness lint --strict` and the tests pass, and their output is recorded in the PR/commit description.
- [ ] No confidential content (lint plus human check).
- [ ] The version has been bumped, and the dependent references and projects have been updated.
