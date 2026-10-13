# Engineering Harness

Base canônica e versionada de **skills, regras, workflows e personas** para engenharia de software assistida por IA. Ela atende ao ambiente pessoal e ao corporativo sem misturar as convenções dos dois.

> Conteúdo das unidades em inglês, documentação em português.

## Princípios

1. **Três dimensões separadas**:
   - conhecimento genérico (`GENERIC/RULES`, `GENERIC/WORKFLOWS`, `AGENTS`);
   - skills técnicas especializadas (`GENERIC/SKILLS`);
   - regras específicas de ambiente (`PROFILES/<AMBIENTE>`).
2. **Uma unidade por pasta, um único Markdown canônico** (`SKILL.md`, `RULE.md`, `WORKFLOW.md`, `AGENT.md`). O `harness lint` impõe isso.
3. **Formato aberto**: o frontmatter segue a especificação [Agent Skills](https://agentskills.io/specification), e os campos do harness ficam em `metadata`. Nenhum formato proprietário.
4. **Arquivos de cada ferramenta são gerados**, nunca editados à mão: `harness compose` gera, `harness drift` detecta edição manual.
5. **Seleção por tarefa, stack e perfil**: nada é carregado "por via das dúvidas", e cada carga é explicada em `.harness/resolution.md`.
6. **Melhoria contínua medida**: depois de cada história, o `harness-curator` mede o consumo real e os erros e propõe mudanças nas unidades canônicas (`run-retrospective`).

## Estrutura

```text
GENERIC/RULES/<nome>/RULE.md          regras universais (git, segurança, evidência, confidencialidade...)
GENERIC/SKILLS/<nome>/SKILL.md        skills técnicas (Java/Spring, Python/pytest, testes, arquitetura...)
GENERIC/WORKFLOWS/<nome>/WORKFLOW.md  story-delivery, support-ticket, knowledge-evolution
AGENTS/<persona>/AGENT.md             orchestrator, analyst, developer, reviewer, qa, support, harness-curator
PROFILES/<AMBIENTE>/PROFILE.md        modelos por persona, orçamentos, ferramentas (com confirmed: true/false)
PROFILES/<AMBIENTE>/RULES|WORKFLOWS   regras e workflows do ambiente (ITAU, PERSONAL)
TOOLS/harness/                        CLI: lint, list, compose, drift + adapters + schemas JSON
TEMPLATES/                            modelos para novas unidades
TESTS/                                pytest + fixtures
EXAMPLES/demo-python-api/             projeto sintético de demonstração
DOCS/                                 arquitetura, schema, composição, Maestri, ledger de skills, ADRs
```

## Uso rápido

```powershell
uv sync                                   # instala o CLI `harness` (Python 3.11+)
uv run harness lint                       # estrutura, schema, conflitos, links, segredos
uv run harness list                       # unidades e perfis
uv run harness compose <projeto> --profile PERSONAL --task feature [--story STORY.md] [--dry-run]
uv run harness drift <projeto>            # arquivos gerados editados à mão?
uv run harness usage --maestri-workspace "<ws>" --floor "<floor>" --out .harness/runs/<id>/08-usage.md   # consumo real por agente
uv run pytest                             # testes do próprio harness
```

O `compose` grava no projeto alvo:

| Arquivo gerado | Quem lê |
|---|---|
| `.agents/skills/<skill>/SKILL.md` | OpenCode, Devin CLI, Codex |
| `.claude/skills/<skill>/SKILL.md` | Claude Code, OpenCode |
| `AGENTS.md` (bloco `harness:begin/end`) + `CLAUDE.md` (`@AGENTS.md`) | todos (regras sempre ativas) |
| `.claude/agents/<persona>.md` / `.opencode/agents/<persona>.md` | subagentes com o modelo do perfil |
| `.harness/personas/*.md` + `.harness/maestri-roles.ps1` | roles e recrutas do Maestri |
| `.harness/resolution.md/.json` | o que foi carregado, por quê, de onde, overrides e conflitos |

Detalhes em [DOCS/composicao.md](DOCS/composicao.md).

## Estado da compatibilidade

Ver [DOCS/compatibilidade.md](DOCS/compatibilidade.md). Em resumo (2026-10-12):
- **Verificados com as ferramentas reais**: validador oficial `skills-ref`, Claude Code e OpenCode.
- **Maestri**: verificado na DEMO-1 (Maestro + 4 recrutas com o modelo fixado, 7 etapas com evidências). Ver [DOCS/maestri.md](DOCS/maestri.md).
- **Devin**: **pendente**, só pode ser verificado no ambiente corporativo.

## Documentação

- [Arquitetura e decisões](DOCS/arquitetura.md) · [ADR-0001](DOCS/adr/0001-harness-canonico.md)
- [Schema de metadados](DOCS/schema.md)
- [Composição e resolução de conflitos](DOCS/composicao.md)
- [Maestri: integração, personas e modelos](DOCS/maestri.md)
- [Como adicionar skills, regras, perfis e ambientes](DOCS/como-evoluir.md)
- [Avaliação de skills de terceiros (ledger)](DOCS/avaliacao-de-skills.md)
- [Compatibilidade verificada](DOCS/compatibilidade.md)
- [Uso no ambiente do Itaú (passo a passo depois do clone)](DOCS/uso-no-itau.md)
