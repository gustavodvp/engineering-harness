---
name: sonar-quality-gate
description: Itaú quality target - more than 90% coverage on new code under Sonar Way and the project's effective quality gate, distinguishing line coverage, condition coverage and the other gate metrics. Approval is declared only from the real gate status. Use when finishing development and in QA.
license: MIT
metadata:
  harness.type: rule
  harness.scope: profile
  harness.profile: ITAU
  harness.version: 1.0.0
  harness.status: active
  harness.enforcement: default
  harness.applies-to: "task:feature,bugfix,refactor,review"
  harness.decides: "quality.new-code-coverage-target=>90%; quality.gate-source=sonar-real-status"
  harness.sources: "https://docs.sonarsource.com/sonarqube-server/latest/user-guide/code-metrics/metrics-definition/, https://docs.sonarsource.com/sonarqube-server/latest/quality-standards-administration/managing-quality-gates/introduction-to-quality-gates/"
  harness.reviewed: "2026-10-12"
  harness.tags: "sonar,coverage,quality-gate,itau"
---

# Itaú: Sonar quality gate

Source: target stated by the owner on 2026-10-12. This applies **only** to the ITAU profile: it isn't a generic rule and doesn't apply to personal projects or other companies.

## Target

- **Coverage on new code above 90%**, following Sonar Way plus whatever the project's effective quality gate configures. If the project's gate is stricter or different, the project's gate wins.

## Know the metrics (SonarQube definitions)

| Metric | What it measures |
|---|---|
| Coverage on new code (`new_coverage`) | a mix of line and condition coverage on new or changed code. This is usually what the gate checks |
| Line coverage on new code (`new_line_coverage`) | the share of new executable lines that ran in tests |
| Condition coverage on new code (`new_branch_coverage`) | the share of boolean conditions in new code evaluated both true and false |
| Duplicated lines on new code, new issues, security hotspots reviewed, reliability, security and maintainability ratings | the other conditions Sonar Way commonly includes; check the effective gate |

Report each metric separately and by name. "Coverage 92%" with no metric named isn't evidence.

## Rules

1. Before closing a story, get the **real** quality gate status of the analysis (the dashboard, or the `api/qualitygates/project_status` endpoint, with the authorized credentials of the environment, which never go into files) and record it in `05-tests.md`.
2. Local coverage (JaCoCo, coverage.py) is only an early signal. It never replaces the gate result.
3. When the gate fails, list the failing conditions with their values, then write meaningful tests for the uncovered new code, especially the uncovered **conditions**. Never use exclusions, `@Generated` tricks or trivial asserts to inflate coverage.
4. Never declare the gate approved, even when the local numbers look good, unless the gate itself reports `OK`.
