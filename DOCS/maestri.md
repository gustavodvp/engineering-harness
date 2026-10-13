# Maestri: integração, personas e modelos

## O que é e como entra no harness

O [Maestri](https://www.themaestri.app/pt-br) é um canvas para orquestrar agentes de IA:
- **terminais** rodam Claude Code, Codex, OpenCode ou shell;
- **roles** são prompts reutilizáveis;
- **floors** são cópias isoladas (worktree/clone) com branch própria e status;
- **routines** agendam comandos e lembretes;
- **notes** são Markdown local.

A configuração é JSON local (`~/.maestri`), e o CLI `maestri` (`ask`, `check`, `recruit`, `role`, `floor`...) **só funciona dentro dos terminais do Maestri** (variável `MAESTRI_PIPE`).

O Maestri é a camada de **execução e coordenação**. O conhecimento continua no harness:

| Harness (canônico) | Maestri (gerado ou derivado) |
|---|---|
| `AGENTS/<persona>/AGENT.md` | role `<Persona>` (prompt curto que aponta para `.harness/personas/<persona>.md`) |
| `PROFILES/<P>/PROFILE.md` → `models` | comando do recruta (`claude --model ...`, `opencode -m ...`) |
| `GENERIC/WORKFLOWS/story-delivery` | sequência de `maestri ask` do Maestro, com um floor por história |
| regras (`AGENTS.md` gerado) | lidas pelos recrutas no diretório do projeto |

Se o Maestri sair de cena, nada se perde: as mesmas personas existem como subagentes do Claude Code (`.claude/agents`) e do OpenCode (`.opencode/agents`).

## Personas, modelos e roteamento

O `orchestrator` (o Maestro) decide quem chamar pela tabela de roteamento de [`AGENTS/orchestrator/AGENT.md`](../AGENTS/orchestrator/AGENT.md). Os modelos vêm do perfil:

| Persona | PERSONAL | ITAU (a confirmar) |
|---|---|---|
| orchestrator (Maestro) | Claude Code · claude-opus-5-5 | Claude Code · claude-sonnet-5-5 |
| analyst | Claude Code · claude-opus-5-5 | Claude Code · claude-opus-5-5 |
| developer | OpenCode · opencode-go/deepseek-v4.1-flash | Devin CLI · modelo barato (fora do canvas) |
| reviewer | Claude Code · claude-sonnet-5-5 | Claude Code · claude-sonnet-5-5 |
| qa | OpenCode · opencode-go/deepseek-v4.1-flash | Devin CLI |
| support | Claude Code · claude-sonnet-5-5 | Claude Code · claude-sonnet-5-5 |

O Devin não tem preset no Maestri. No ITAU, o script gerado marca essas personas como "run it outside the canvas", e o Maestro delega por terminal shell (`devin ...`) ou o humano roda. Isso ainda precisa ser verificado no ambiente corporativo.

## Gerar e aplicar os roles

```powershell
uv run harness compose <projeto> --profile PERSONAL --task feature
# dentro de um terminal do Maestri, na raiz do projeto:
pwsh -File .harness/maestri-roles.ps1            # roles do workspace atual
pwsh -File .harness/maestri-roles.ps1 -Scope global
```

O script cria ou atualiza os roles e lista, em comentários, o `maestri recruit` de cada persona com o modelo já fixado.

Cuidados, vindos de uso real (padrao-fluxo-dev):
- Os recrutas iniciam em `.maestri/roles/<id>`. O prompt manda dar `cd` na raiz do projeto e nunca commitar `.maestri/`.
- O `recruit` do Claude Code pode parar no prompt de confiança da pasta. Basta aceitar uma vez no terminal; o OpenCode não tem isso.
- Recruta travado: `maestri recruit --replace "<nome>"`.
- **Floors e `.venv` (DEMO-1)**: o floor copia os arquivos não versionados do ground, e a cópia do `.venv` veio incompleta (sem o pacote `coverage/`). Além disso, os launchers do `.venv` podem apontar para o ground. Em floors, rode Python como `python -m uv run python -m pytest ...`, e se um import falhar, rode `python -m uv sync --reinstall-package <pacote>`.
- **Shell misto no OpenCode (DEMO-1)**: no Windows, a ferramenta `bash` do OpenCode roda POSIX. Não misture sintaxe PowerShell (`| Select-Object`, `$env:X=...`) com POSIX (`VAR=1 cmd`, `| tail`) no mesmo comando: os dois erros do Developer na DEMO-1 vieram disso. E um recruta não roda `maestri check` sobre si mesmo.
- **Roles só no Maestro**: `maestri role ...` só funciona no terminal com Maestro Mode. Rodado por um recruta, o script de roles para logo no início, com a mensagem `Run this script in the Maestro terminal` (aconteceu na DEMO-1).
- **Roles com nomes parecidos**: o script gerado usa o nome exato (tenta `role write` e, se o role não existir, `role create`), porque um role global "QA Frontend Atlas" fez o "QA" deixar de ser criado na DEMO-1.

## Demo DEMO-1 (verificação de ponta a ponta)

Pré-requisito: o branch do harness com a demo já commitado (floors clonam o estado do git).

**Passo 1, no Maestri (Gustavo).** Abra o workspace **Engineering Harness** (diretório `D:\00_Vault\.dados\repos\projects\engineering-harness`). Se ele ainda não existir, peça ao Maestro do workspace Vault: `maestri workspace create "Engineering Harness" --dir D:\00_Vault\.dados\repos\projects\engineering-harness`. Depois abra um terminal **Claude Code** com **Maestro Mode** e diga:

> Leia DOCS/maestri.md e execute a seção "Demo DEMO-1, passo 2" como orchestrator.

**Passo 2, pelo Maestro (orchestrator).**

1. Rode `maestri list`, `maestri role list` e `maestri floor list`, sem duplicar nada que já exista.
2. Rode `pwsh -File EXAMPLES/demo-python-api/.harness/maestri-roles.ps1`.
3. Rode `maestri floor create "DEMO-1" --branch demo/demo-1`.
4. Recrute no floor DEMO-1, com codinomes à sua escolha e os comandos listados no fim do script:
   - Analyst: `--role "Analyst" --command "claude --model claude-opus-5-5"`;
   - Developer: `--role "Developer" --command "opencode -m opencode-go/deepseek-v4.1-flash"`;
   - Reviewer: `--role "Reviewer" --command "claude --model claude-sonnet-5-5"`;
   - QA: `--role "QA" --command "opencode -m opencode-go/deepseek-v4.1-flash"`.
5. Conduza o workflow [`story-delivery`](../GENERIC/WORKFLOWS/story-delivery/WORKFLOW.md) para `EXAMPLES/demo-python-api/STORY.md`:
   - cada `maestri ask` dá o caminho do projeto (`EXAMPLES/demo-python-api` no floor), a etapa, o arquivo de evidência esperado em `.harness/runs/DEMO-1/` e termina com a linha de retorno (`maestri ask "<seu nome>" "<resultado>"`);
   - comandos Python: `python -m uv run pytest ...` (o `uv` pode não estar no PATH dos terminais);
   - mantenha `00-orchestration.md` com etapa, persona, ferramenta/modelo e horário, e `maestri floor status` atualizado;
   - o reviewer **não edita**, e o QA registra a cobertura de linha e de branch com a saída real.
6. No fim, o Developer faz **commit local** no branch do floor (sem push), e o Maestro escreve `07-close.md` e marca o floor como `--state review`. **Não fazer land, push nem PR**: essa decisão é do Gustavo.

**Passo 3, verificação.** Fora do canvas, um agente confere as evidências no clone do floor, roda os testes de novo e registra o resultado em [compatibilidade.md](compatibilidade.md).

## Curador do harness (retrospectiva depois de cada história)

A persona `harness-curator` roda o workflow [`run-retrospective`](../GENERIC/WORKFLOWS/run-retrospective/WORKFLOW.md) depois do `07-close.md`. É a etapa 8, que não bloqueia a entrega. O curador:

1. **mede** o consumo real com `harness usage --maestri-workspace "<ws>" --floor "<floor>" --out .harness/runs/<id>/08-usage.md`: tokens, custo, chamadas de ferramenta e erros de cada recruta e do Maestro, lidos dos transcripts locais do Claude Code e das sessões do OpenCode;
2. **analisa** desperdício (modelo caro em trabalho braçal, polling, releituras, retrabalho), erros de ferramenta, conformidade do orquestrador (roteamento, revisão independente, evidências, autorizações) e lacunas ou conflitos de regras e skills;
3. **propõe** mudanças nos arquivos canônicos (persona, regra, skill ou workflow), com a evidência, a classificação (genérico, skill ou ambiente), o texto exato e o efeito esperado, em `08-retrospective.md`;
4. **não aplica nada**: você aprova, e a mudança entra pelo `knowledge-evolution`, com lint e testes.

No Maestri, o Maestro recruta no floor: `maestri recruit "<codinome>" --role "Harness Curator" --command "claude --model claude-sonnet-5-5" --floor "<story>"`. Para rodar ao longo de várias histórias, crie uma routine semanal que peça ao curador para consolidar os `08-retrospective.md` recorrentes.

No ITAU, o curador gasta orçamento Claude. Ele roda por história só quando o orçamento permite; caso contrário, uma vez por semana sobre várias. O Devin ainda não tem fonte de consumo suportada, e aparece como "not measured".

## Maestri portable e o ambiente corporativo

- **Binário**: `Maestri-Portable-latest.exe`, versão **0.23.0**, publicado por Evercraft Labs, 201.697.401 bytes, SHA-256 `185e10b1521282ef1d6c45ee0d16fa145b4ec0750036180fa706b185b6567afc`. **Não tem assinatura digital** (Authenticode `NotSigned`).
- **Onde fica**: asset da Release do repositório privado (fora do histórico git). Confira o hash depois de baixar: `Get-FileHash .\Maestri-Portable-latest.exe -Algorithm SHA256`.
- **Antes de usar no Itaú**:
  - O Maestri é software comercial (licença Pro, com trial), então confirme se a licença permite o uso no equipamento corporativo.
  - Levar um executável por um canal que contorna o bloqueio de downloads pode violar a política de segurança da empresa. Confirme com a TI ou o gestor.
  - Binários sem assinatura costumam ser bloqueados por EDR ou AppLocker.
  - Por isso o perfil ITAU registra `tools.maestri.available: false, confirmed: false` até haver aprovação. O fallback é o Claude Code com subagentes.
