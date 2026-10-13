# 0001. Harness canônico com formato Agent Skills

- Status: aceito (2026-10-12, plano aprovado pelo Gustavo)

## Contexto

O conhecimento de engenharia precisa servir a vários agentes (Claude Code, OpenCode, Devin, Codex, Maestri) e a dois ambientes (pessoal e Itaú), que não podem se contaminar. Cada ferramenta lê arquivos diferentes. Cópias mantidas à mão divergem.

## Opções

1. Formato próprio, com um conversor para cada ferramenta.
2. **Agent Skills como formato base de todas as unidades**, com campos do harness em `metadata` e arquivos de ferramenta gerados.
3. Manter um arquivo por ferramenta, sincronizado à mão.

## Decisão

Opção 2. O frontmatter de `SKILL.md`, `RULE.md`, `WORKFLOW.md` e `AGENT.md` é Agent Skills válido (validado pelo `skills-ref`). As regras vão para `AGENTS.md`, as personas para subagentes e roles do Maestri, e as skills para `.agents/skills` e `.claude/skills`, tudo gerado por `harness compose` com lock de hash. O harness passa a ser a fonte canônica dos padrões de engenharia; o vault aponta para ele.

## Consequências

- Positivas: nenhuma cópia editável, compatibilidade verificável com o validador oficial, seleção por tarefa, perfis isolados por construção, conflitos detectados em CI.
- Negativas: o conteúdo de cada unidade fica num único arquivo (sem `references/`), o que limita skills muito extensas; elas precisam ser condensadas ou apontar para links.
- A acompanhar: se o padrão Agent Skills ganhar um campo oficial para regras ou personas, migrar os campos de `metadata`.
