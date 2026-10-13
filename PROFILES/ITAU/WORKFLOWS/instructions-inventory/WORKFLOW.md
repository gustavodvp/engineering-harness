---
name: instructions-inventory
description: Inside the authorized corporate environment, inventory the real instructions and conventions of the monorepo (AGENTS.md, CONTRIBUTING, CI, Sonar, branch rules) and report conflicts with the ITAU profile before proposing any change. Use the first time the harness is used with the corporate repository, and when conventions seem to differ.
license: MIT
metadata:
  harness.type: workflow
  harness.scope: profile
  harness.profile: ITAU
  harness.version: 1.0.0
  harness.status: active
  harness.applies-to: "task:analysis,docs"
  harness.reviewed: "2026-10-12"
  harness.tags: "workflow,discovery,itau"
---

# Itaú: instructions inventory

The ITAU profile was written **without access** to the corporate repository. This workflow replaces assumptions with facts and never invents rules.

## Inputs

- Read access to the corporate monorepo in the authorized environment.
- The harness composed with `--profile ITAU --task analysis` (dry-run is enough).

## Stages

1. **Collect** (read-only): `AGENTS.md`, `CLAUDE.md`, `.github/` (workflows, CODEOWNERS, PR templates), `CONTRIBUTING*`, `sonar-project.properties` or the build's Sonar config, branch protection as visible in the UI or API, README sections on process, and existing agent or Devin configuration.
2. **Tabulate** them in the inventory, kept **in the corporate environment and not in the harness**. For each convention give its source file, the rule and whether it matches, extends or contradicts an ITAU profile rule.
3. **Report conflicts** to the owner. When the profile and the repository disagree, the repository wins for that repository. Record that with `.harness/resolution.md`, and don't edit the generic rules.
4. **Propose profile updates** only for conventions that are technical, operational **and** authorized to leave the corporate environment. Use the `knowledge-evolution` workflow, set `confirmed: true` where a value was verified, and never copy file contents, names or internal URLs.

## Outputs

- An internal inventory (in the corporate environment).
- A list of conflicts with the ITAU profile, and approved proposals for profile changes.

## Done when

- [ ] Every ITAU rule is marked confirmed, contradicted or unknown, citing the internal source by its location only.
- [ ] Conflicts were reported to the owner before any change was proposed.
- [ ] No confidential content left the corporate environment.
