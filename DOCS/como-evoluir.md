# Como adicionar e evoluir conteúdo

Toda mudança segue o workflow [`knowledge-evolution`](../GENERIC/WORKFLOWS/knowledge-evolution/WORKFLOW.md). Antes de abrir um arquivo, decida a dimensão:

| Pergunta | Se sim |
|---|---|
| Vale em qualquer empresa ou projeto? | `GENERIC/RULES` ou `GENERIC/WORKFLOWS` |
| É uma competência técnica (linguagem, framework, cloud, testes...)? | `GENERIC/SKILLS` |
| Só vale num ambiente (empresa, pessoal)? | `PROFILES/<AMBIENTE>/...` |
| É um papel de agente? | `AGENTS/<persona>` (genérico; o modelo vai no perfil) |

## Nova skill

1. Pesquise primeiro: registre as candidatas em [avaliacao-de-skills.md](avaliacao-de-skills.md), com licença, atividade e risco.
2. `Copy-Item TEMPLATES/SKILL.md GENERIC/SKILLS/<nome>/SKILL.md`. O `<nome>` vai em minúsculas com hífens e deve ser igual ao `name`.
3. Escreva uma `description` que diga **o que faz e quando usar**, com palavras-chave. Preencha `applies-to`, `sources` e `reviewed`.
4. Conteúdo em inglês, com menos de 500 linhas, num **único arquivo**. Exemplos executáveis vão em `EXAMPLES/` ou `TESTS/` e são referenciados por link.
5. Rode `uv run harness lint --strict` e `uv run pytest`, e faça `compose` na demo.

## Nova regra

1. Use `TEMPLATES/RULE.md`. Declare em `harness.decides` as chaves que a regra decide.
2. Se ela divergir de uma regra genérica, **não edite a genérica**. Declare `harness.overrides: "generic/rule/<x>#<chave>"` na regra do perfil.
3. Regras de segurança ou autorização que nada pode relaxar recebem `harness.enforcement: mandatory`.

## Novo workflow ou persona

- Workflow: `TEMPLATES/WORKFLOW.md`, com as seções obrigatórias `## Inputs`, `## Outputs` e `## Done when`.
- Persona: `TEMPLATES/AGENT.md`, com as seções `## Responsibilities`, `## Never` e `## Handoff`. Use `harness.edits-code: "false"` para personas somente leitura. Acrescente a persona à tabela de roteamento do `orchestrator` e a `models` em cada perfil.

## Novo perfil ou ambiente

1. Crie `PROFILES/<NOME>/PROFILE.md` a partir de `TEMPLATES/PROFILE.md`. O nome vai em MAIÚSCULAS.
2. Preencha `models` (persona → ferramenta e modelo), `tools` e `budgets`, todos com `confirmed: false` até verificar.
3. Acrescente só as regras **fornecidas ou verificadas** para aquele ambiente. Nunca invente convenções, e para empresas comece pelo workflow de inventário (veja `PROFILES/ITAU/WORKFLOWS/instructions-inventory`).
4. Termos sensíveis que não podem aparecer em lugar nenhum (nomes internos, hosts) vão em `.harness/denylist.local`, que fica fora do git, e o lint passa a bloqueá-los.
5. Use em um projeto com `uv run harness compose <projeto> --profile <NOME> --task <tipo>`.

## Promover um aprendizado

Uma descoberta feita num ambiente corporativo só vai para `GENERIC/` se o princípio técnico puder ser separado de qualquer detalhe interno. Caso contrário, fica no perfil, ou fora do harness.

## Verificações automáticas (CI)

`harness lint` cobre:
- schema e `name` igual à pasta, um arquivo canônico por pasta, IDs duplicados;
- possíveis duplicatas (aviso), alvos de override, conflitos por perfil;
- links internos quebrados (`--online` também verifica os externos), skills sem fontes, obsolescência depois de 6 meses (aviso);
- segredos, e-mails e hosts e IPs internos nos perfis de empresa, além da denylist.

`harness drift` cobre a edição manual de arquivos gerados.
