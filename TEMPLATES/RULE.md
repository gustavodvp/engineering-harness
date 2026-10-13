---
name: <folder-name>
description: <What the rule enforces and when it applies.>
license: MIT
metadata:
  harness.type: rule
  harness.scope: <generic|profile>
  harness.profile: <PROFILE - remove for generic rules>
  harness.version: 0.1.0
  harness.status: draft
  harness.enforcement: <default|mandatory>
  harness.applies-to: "task:<...>"
  harness.decides: "<area.key>=<value>"
  harness.overrides: "<generic/rule/x#area.key - only when diverging from a lower layer>"
  harness.reviewed: "<YYYY-MM-DD>"
  harness.tags: "<tags>"
---

# <Title>

Source: <where the rule comes from; for company profiles, who stated it and when>.

## Rules

1. ...
