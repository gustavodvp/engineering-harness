---
name: support-ticket
description: Handle a customer support ticket or production incident - triage, anonymised reproduction, diagnosis, answer and follow-up, handing code changes to story-delivery. Use for support, incident and product-behaviour questions.
license: MIT
metadata:
  harness.type: workflow
  harness.scope: generic
  harness.version: 1.1.0
  harness.status: active
  harness.applies-to: "task:support,incident"
  harness.sources: "https://sre.google/sre-book/effective-troubleshooting/, https://sre.google/sre-book/managing-incidents/"
  harness.reviewed: "2026-10-13"
  harness.tags: "workflow,support,incident"
---

# Support ticket

The `orchestrator` routes the ticket to `support`. Evidence goes to `.harness/runs/<ticket-id>/` and must be **anonymised** (rule `confidentiality`).

## Inputs

- The ticket: symptom, when it started, who is affected, urgency. Customer data stays in the ticketing system and gets replaced by placeholders.
- Read-only access to the code, the logs and the dashboards the environment authorizes.

## Stages

1. **Triage** (`01-triage.md`): classify it (bug, usage question, configuration, data issue, incident), set impact and urgency, and decide whether incident handling is needed (a timeline, a single coordinator, regular updates).
2. **Reproduce** (`02-reproduction.md`): write the minimal steps and environment needed to reproduce the issue, using synthetic data. If you can't reproduce it, list the data still missing.
3. **Diagnose** (`03-diagnosis.md`): state the hypotheses, the evidence for and against each one (log lines, metrics, code paths with `file:line`) and the root cause or the most likely cause with your confidence. Use the `systematic-debugging` skill.
4. **Respond** (`04-response.md`): a customer-facing answer in plain language (what happens, why, workaround, next step) and a separate internal technical note. A human approves the answer before it is sent.
5. **Hand off**: if code must change, open a story whose acceptance criteria include the reproduction, and run `story-delivery`. For incidents, add a blameless post-incident summary.
6. **Retrospective** (non-blocking): the `harness-curator` runs `run-retrospective` on this ticket.

## Outputs

- A classified ticket with its reproduction and diagnosis.
- An approved response draft.
- A story for `story-delivery` when a fix is needed.

## Done when

- [ ] The ticket is classified, and the diagnosis cites evidence (or states clearly that it is a hypothesis).
- [ ] The response was approved by a human before being sent.
- [ ] No customer data appears in any evidence file or prompt.
- [ ] Every code change needed is tracked as a story.
