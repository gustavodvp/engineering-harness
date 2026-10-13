---
name: evidence-before-claims
description: Never report tests, coverage, builds, reviews or quality gates as passing without real, inspected output. Use whenever stating that work is done, fixed, tested or approved.
license: MIT (adapted from obra/superpowers verification-before-completion, MIT)
metadata:
  harness.type: rule
  harness.scope: generic
  harness.version: 1.0.0
  harness.status: active
  harness.enforcement: mandatory
  harness.decides: "verification.claims=require-evidence"
  harness.sources: "https://github.com/obra/superpowers/tree/main/skills/verification-before-completion"
  harness.reviewed: "2026-10-12"
  harness.tags: "verification,testing,honesty"
---

# Evidence before claims

This rule is **mandatory**.

## Rules

1. A claim such as "tests pass", "coverage is 92%", "the build is green", "review approved" or "the bug is fixed" needs **fresh evidence from this session**: the command you ran, its exit code and the relevant part of its output.
2. Run the verification **after** the last change. Evidence from before an edit doesn't count.
3. If you couldn't run something (no access, no tool, no environment), say so plainly and list it as pending. Never infer a pass.
4. Report failures with their output. "Mostly passing" means failing.
5. When a workflow asks for evidence files (for example `.harness/runs/<story>/NN-<stage>.md`), write the command, the date/time, the exit code and the output excerpt, plus links to full reports (JUnit XML, coverage XML, Sonar dashboard).
6. Coverage numbers come from the tool's report, and you name the metric: line, branch/condition, or new code versus overall.
