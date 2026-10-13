---
name: run-retrospective
description: After a story or ticket closes, the harness-curator measures real token use, cost and tool errors per agent, checks workflow and rule conformance, and proposes evidence-backed changes to skills, rules, personas or workflows. Use as stage 8 of story-delivery and support-ticket, or periodically across several runs.
license: MIT
metadata:
  harness.type: workflow
  harness.scope: generic
  harness.version: 1.0.0
  harness.status: active
  harness.applies-to: "task:feature,bugfix,refactor,support,incident,review"
  harness.sources: "https://sre.google/workbook/postmortem-culture/, https://martinfowler.com/articles/retrospective-antipatterns.html"
  harness.reviewed: "2026-10-13"
  harness.tags: "workflow,retrospective,cost,continuous-improvement"
---

# Run retrospective

It runs **after** the closing stage, so it never delays delivery. It closes the loop between real runs and the canonical harness.

## Inputs

- A finished run: `.harness/runs/<id>/00..07-*.md`, `.harness/resolution.md`, and the branch or floor git log.
- Access to the agents' local transcripts: Claude Code under `~/.claude/projects`, OpenCode sessions. With Maestri, also the workspace and floor names.
- The harness repository (to run `harness usage` and read the canonical units).

## Stages

1. **Measure**: `harness usage --maestri-workspace "<ws>" --floor "<floor>" --out .harness/runs/<id>/08-usage.md`, or `--dir` per agent without Maestri. Agents whose tool has no supported usage source (for example Devin) get listed as "not measured" together with whatever the tool's own dashboard shows. Never estimate them.
2. **Read** every evidence file and the usage report, and list the facts: stage durations, the model per stage, cost per agent, tool errors and deviations.
3. **Analyse** with the `harness-curator` checklist: waste, errors, process conformance, rule and skill gaps. Check earlier `08-retrospective.md` files for recurrence.
4. **Propose**: write `08-retrospective.md` with findings and proposals. Each proposal is targeted at one canonical file, classified (generic, skill or environment) and gives the exact text, the version bump and the expected measurable effect.
5. **Decide**: the owner accepts, rejects or defers each proposal. Accepted proposals are implemented through `knowledge-evolution`, on a branch of the harness repository, with lint and tests. Rejections are recorded with the reason, so the same proposal doesn't come back.

## Outputs

- `08-usage.md` and `08-usage.json`: measured usage per agent.
- `08-retrospective.md`: findings with evidence, plus proposals.
- After approval: commits to the harness that change the canonical units, with version bumps.

## Done when

- [ ] Every agent of the run is either measured or explicitly listed as not measurable.
- [ ] Every finding cites evidence (an evidence file, a usage row or the error text).
- [ ] Every proposal names its target file, classification, exact change and expected effect.
- [ ] No business or confidential data appears in the retrospective.
- [ ] The owner's decision is recorded for each proposal.
