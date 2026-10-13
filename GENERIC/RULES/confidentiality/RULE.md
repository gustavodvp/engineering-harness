---
name: confidentiality
description: Keep proprietary code, business knowledge, customer data and internal details out of the harness and out of unapproved tools. Use when capturing learnings, writing rules or sharing context with any AI tool.
license: MIT
metadata:
  harness.type: rule
  harness.scope: generic
  harness.version: 1.0.0
  harness.status: active
  harness.enforcement: mandatory
  harness.decides: "confidentiality.business-data-in-harness=forbidden"
  harness.sources: "https://owasp.org/www-project-top-10-for-large-language-model-applications/"
  harness.reviewed: "2026-10-12"
  harness.tags: "confidentiality,privacy"
---

# Confidentiality

This rule is **mandatory**.

## Rules

1. The harness stores only **technical and operational practices**. It never stores business rules, proprietary code, customer or employee names, internal hostnames, IPs, URLs, ticket contents, credentials or confidential documentation.
2. A company profile (`PROFILES/<COMPANY>`) holds only conventions that the company authorizes you to keep outside its systems. When in doubt, leave it out and write the rule generically.
3. Before you promote a learning from a company context into `GENERIC/`, strip every company-specific detail and keep only the general technical principle. If the principle can't be separated from the context, it doesn't get promoted.
4. Only send code or data to the AI tools and accounts approved for that environment. Personal accounts and tools are never used with company code, and company tools are never used for personal work.
5. In support work, never paste customer data into prompts, notes or evidence files. Use anonymised reproductions instead.
6. `harness lint` scans for secrets, e-mail addresses, internal hosts and terms from the local `.harness/denylist.local`. A clean lint is necessary but **not sufficient**, so review it yourself as well.
