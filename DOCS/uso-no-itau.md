# Uso no ambiente do Itaú

Guia para usar o harness na máquina corporativa. Vale para qualquer ambiente de empresa; troque `ITAU` pelo perfil correspondente.

## 0. Antes de clonar: confirmar o que é permitido

Este repositório é privado e pertence a uma conta pessoal do GitHub. Confirme com a TI ou com o gestor:

- se é permitido clonar um repositório pessoal na máquina corporativa;
- se é permitido **enviar** algo de lá para cá. Regras do perfil ITAU escritas no ambiente corporativo são informação que sai da empresa.

Se uma das duas não for permitida, leve uma cópia apenas de `GENERIC/`, `AGENTS/`, `PROFILES/ITAU/` e `TOOLS/` para um repositório interno, e trate essa cópia como a versão corporativa.

## 1. Instalar e conferir

Pré-requisitos: git e Python 3.11 ou mais novo.

```powershell
git clone https://github.com/gustavodvp/engineering-harness.git
cd engineering-harness
pip install uv            # ou pelo espelho interno de pacotes (Artifactory), se a internet for bloqueada
uv sync
uv run harness lint
uv run pytest -q
```

Sem `uv`:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

O harness depende só de `pyyaml` e `jsonschema`.

## 2. Proteger contra vazamento (antes de qualquer outra coisa)

Crie `.harness/denylist.local` dentro do harness. O arquivo fica fora do git. Coloque nele, um por linha, os termos que nunca podem aparecer no harness: nomes de sistemas, domínios e hosts internos, nomes de produtos. O `harness lint` passa a bloquear qualquer alteração que contenha esses termos. Em `PROFILES/ITAU`, o lint também já bloqueia segredos, e-mails, hosts `.corp`/`.internal` e IPs privados.

## 3. Aplicar no repositório de trabalho sem sujar o monorepo

Primeiro veja o que seria carregado, sem gravar nada:

```powershell
uv run --project C:\caminho\engineering-harness harness compose C:\caminho\monorepo\<servico> --profile ITAU --task analysis --dry-run
```

O `compose` grava `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.agents/`, `.opencode/` e `.harness/` no projeto. **Não commite esses arquivos no monorepo** sem aprovação. Para mantê-los só na sua máquina, adicione-os a `.git/info/exclude` do monorepo (ignore local, não versionado):

```text
.harness/
.claude/
.agents/
.opencode/
CLAUDE.md
```

- Se o monorepo já tiver um `AGENTS.md` versionado, o `compose` acrescenta um bloco no fim dele. Prefira uma pasta de serviço sem `AGENTS.md`, ou desfaça com `git checkout AGENTS.md` antes de qualquer commit.
- Rode o `compose` por serviço, não na raiz do monorepo: a detecção de stack (Java, SQL...) é feita por pasta.
- Valores de `--task`: `feature`, `bugfix`, `refactor`, `review`, `support`, `incident`, `analysis`, `docs`.

## 4. Primeira tarefa: inventariar as regras reais

Rode o `compose` com `--task analysis` (sem `--dry-run`) e peça ao Claude Code (Sonnet):

> Execute o workflow `instructions-inventory` do harness neste repositório.

Ele lê `AGENTS.md`, `.github/` (workflows, CODEOWNERS, templates de PR), `CONTRIBUTING`, a configuração do Sonar e as proteções de branch, compara com as regras do perfil ITAU e lista o que bate, o que contradiz e o que falta.

- **O inventário fica no ambiente do Itaú.**
- No harness entram só regras técnicas que você esteja autorizado a guardar fora, sem nomes, links ou trechos de arquivos internos.
- Quando o repositório e o perfil divergirem, vale o repositório. O conflito fica registrado em `.harness/resolution.md`.

## 5. Confirmar o perfil

Em `PROFILES/ITAU/PROFILE.md`, troque `confirmed: false` por `true` à medida que for verificando:

| Item | O que confirmar |
|---|---|
| Claude | limite real (unidade e período) e modelos disponíveis na conta (Opus 5.5? Sonnet 5.5?) |
| Devin | limite real e modelos que o CLI oferece. Se não houver `deepseek-v4.1-flash`, escolha o mais barato que resolva |
| Maestri | se foi aprovado. Até lá, `available: false` |

Ao confirmar, aumente a versão da regra `ai-usage-budget` se ela mudar (workflow `knowledge-evolution`).

## 6. Testar o Devin (compatibilidade ainda pendente)

Depois do `compose`, abra o Devin CLI na pasta do serviço e pergunte quais skills e regras ele está vendo. Pela documentação ele lê `AGENTS.md` e `.agents/skills/`.

Descubra também se o Devin tem um modo não interativo que o orquestrador consiga chamar. Sem isso, ele fica como executor manual: você leva o `02-plan.md` até ele.

Registre o resultado em [compatibilidade.md](compatibilidade.md).

## 7. Trabalhar no dia a dia

**Sem Maestri** (o mais provável no começo):
- Orquestrador: `claude --model claude-sonnet-5-5` na pasta do serviço; peça para seguir o workflow `story-delivery` para a história.
- As personas estão em `.claude/agents/` com o modelo do perfil. O analista usa Opus. As personas atribuídas ao Devin aparecem com `model: inherit` e indicam o Devin como executor preferido.

**Com Maestri aprovado:**
- O binário está na Release `v0.1.0`. Confira o hash depois de baixar: `Get-FileHash .\Maestri-Portable-latest.exe -Algorithm SHA256` deve dar `185e10b1521282ef1d6c45ee0d16fa145b4ec0750036180fa706b185b6567afc`.
- No Maestro, rode `pwsh -File .harness/maestri-roles.ps1` e recrute pelos comandos listados no fim do script.
- `land` e `delete` de floor só funcionam no **Maestro do ground**. Rodados de dentro de um floor, a 0.22.1 responde `malformed floorLifecycleVerdictResult frame`.
- Detalhes em [maestri.md](maestri.md).

**Depois de cada história:**
- `harness usage` + workflow `run-retrospective` com o `harness-curator`.
- O consumo do Claude é medido. O do Devin ainda não: anote o que o painel do Devin mostrar.
- Por causa do orçamento, faça a retrospectiva por história só quando couber; caso contrário, semanalmente sobre várias.
- Os arquivos de evidência (`.harness/runs/`) ficam no ambiente do Itaú.

## 8. Melhorar o harness a partir do Itaú

Siga o workflow `knowledge-evolution`:

| O que você descobriu | Para onde vai |
|---|---|
| Regra técnica da empresa, sem dados de negócio, que você está autorizado a guardar fora | `PROFILES/ITAU/` |
| Aprendizado que vale em qualquer empresa, sem nenhum contexto interno | `GENERIC/` |
| Qualquer coisa com nome, link, código, cliente ou detalhe interno | **não entra no harness** |

Só envie depois de `uv run harness lint --strict` passar com a denylist ativa e de você mesmo revisar o diff. Na dúvida, não envie: escreva a regra de forma genérica ou mantenha-a só no ambiente corporativo.
