# AGENTS.md: editing this repository

Instructions for AI agents that change **the harness itself**. Projects that *use* the harness get their own generated AGENTS.md from `harness compose`.

## Golden rules

1. One knowledge unit per folder, with a single canonical file: `SKILL.md`, `RULE.md`, `WORKFLOW.md` or `AGENT.md`. Never add `README.md`, `notes.md`, `references/` or other files inside a unit folder.
2. The folder name equals `name`. Frontmatter follows `TOOLS/harness/schema/unit.schema.json`: Agent Skills fields at the top level, harness fields under `metadata` as **quoted strings**. Start new units from `TEMPLATES/`.
3. Put content in the right dimension: universal → `GENERIC/`, a technical specialty → `GENERIC/SKILLS/`, environment-specific → `PROFILES/<ENV>/`. Company rules never move into `GENERIC/`.
4. Never write business knowledge, proprietary code, customer or employee names, internal hosts or credentials (rule `GENERIC/RULES/confidentiality`).
5. To change behaviour declared in a lower layer, use `harness.decides` and `harness.overrides`. Never edit a generic rule to fit one environment.
6. Follow the `knowledge-evolution` workflow: sources in `harness.sources`, licence checked, version bumped (semver), `harness.reviewed` updated.
7. Never edit generated files under `EXAMPLES/*/.agents`, `.claude`, `.opencode` or `.harness`. Re-run `harness compose` instead.

## Before you finish

```powershell
uv run harness lint --strict
uv run pytest -q
uv run harness compose EXAMPLES/demo-python-api --profile PERSONAL --task feature --story EXAMPLES/demo-python-api/STORY.md
```

Unit content is written in English; README and DOCS in Brazilian Portuguese.
