---
name: story-delivery
description: End-to-end delivery of a story with personas - analysis, plan, development, independent review, tests and quality gates, fixes and closure, each stage leaving verifiable evidence. Use for features, bugfixes and refactors.
license: MIT
metadata:
  harness.type: workflow
  harness.scope: generic
  harness.version: 1.2.0
  harness.status: active
  harness.applies-to: "task:feature,bugfix,refactor"
  harness.sources: "https://github.com/obra/superpowers, https://google.github.io/eng-practices/"
  harness.reviewed: "2026-10-13"
  harness.tags: "workflow,delivery,orchestration"
---

# Story delivery

The `orchestrator` drives this workflow. Every stage writes its evidence to `.harness/runs/<story-id>/`, and **a stage without its evidence file has not happened** (rule `evidence-before-claims`).

## Inputs

- A story: an id, a goal and, if available, acceptance criteria (a ticket text, `story.md` or a chat request).
- The target repository with the harness composed for the active profile (`harness compose`), so AGENTS.md, the skills and the personas are in place.
- The active profile's persona and model assignments (see `.harness/resolution.md` and `.harness/personas/`).

## Stages

| # | Stage | Persona | Evidence file | Exit criterion |
|---|---|---|---|---|
| 1 | Analysis | analyst | `01-analysis.md` | testable acceptance criteria, open questions answered or explicitly assumed |
| 2 | Plan | analyst | `02-plan.md` | small steps, each with the files, tests and proving command |
| 3 | Development | developer | `03-development.md` | every plan step done, tests added and run locally |
| 4 | Independent review | reviewer (on a different model from the developer) | `04-review.md` | verdict recorded; no open `blocker` or `major` |
| 5 | Tests and gates | qa | `05-tests.md` | all criteria verified, profile gates pass **as reported by the gate itself** |
| 6 | Fix (loop to 4 or 5) | developer | `06-fix.md` | each finding fixed, disputed with a reason, or deferred with approval |
| 7 | Close | orchestrator | `07-close.md` | summary, evidence links, pending items, authorization requests |
| 8 | Retrospective (after delivery, non-blocking) | harness-curator | `08-usage.md`, `08-retrospective.md` | measured cost per agent, findings with evidence, proposals for the harness (workflow `run-retrospective`) |

**Checkout check (stage 1).** In a worktree, a Maestri floor or any copied checkout, prove that the test command runs the code of **this** checkout before you record a baseline. Run a throwaway probe that prints the interpreter or toolchain path and where the module under test is loaded from. Also run the coverage tool once (`--version` or a dry import) to catch a missing package before stage 3. If anything points outside the checkout or is missing, record it as a risk in `01-analysis.md` and write the corrected command in `02-plan.md`, and every later stage uses that command. (From the DEMO-1 retrospective: a copied `.venv` resolved to the ground checkout and lacked `coverage`.)

Rules for the loop:
- After a fix, return to stage 4 when the code changed materially; otherwise go to stage 5.
- After three loops without convergence, stop and escalate to the human with a summary.
- The human may skip stages 1–2 for trivial changes. The orchestrator records the skip in `00-orchestration.md`.

### Evidence file format

```markdown
# <stage> — <story-id>
- persona / tool / model: developer / opencode / deepseek-v4.1-flash
- started / finished: 2026-10-12T14:03Z / 2026-10-12T14:41Z
## Commands
$ uv run pytest -q          (exit 0)
<last lines of output>
## Result
<what was done or found; links to reports>
```

## Outputs

- The code change in an isolated branch, with focused commits following the profile's git rules.
- `.harness/runs/<story-id>/00..07-*.md` evidence files.
- A closing report for the human: what was delivered, the real gate numbers, pending items, and the actions that need authorization (push, PR, merge).

## Done when

- [ ] Every acceptance criterion maps to a test or check that ran in stage 5 and passed.
- [ ] The review verdict is `approve` or `approve-with-nits`, from a reviewer independent of the developer.
- [ ] The profile's quality gates pass according to their own reports (no estimates).
- [ ] Nothing was pushed, merged or published without explicit authorization.
- [ ] `07-close.md` exists and lists the pending items, or says "none".
